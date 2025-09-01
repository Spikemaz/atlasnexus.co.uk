"""
Atlas Forge - Advanced Permutation Engine v2.0.0
Full implementation based on permutation_config.md specifications
"""

import math
import json
from typing import Dict, List, Any, Tuple, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import itertools

# ==================== Configuration Types ====================

class Currency(Enum):
    GBP = "GBP"
    EUR = "EUR"
    USD = "USD"
    JPY = "JPY"
    AED = "AED"

class AmortType(Enum):
    ANNUITY = "Annuity"
    SCULPTED = "Sculpted"
    BULLET = "Bullet"
    STEPDOWN = "StepDown"

class IndexationMode(Enum):
    FLAT = "Flat"
    CPI_LINKED = "CPI_Linked"
    PARTIAL = "Partial"

class RankingObjective(Enum):
    MAX_SENIOR_RAISE = "MaxSeniorRaise"
    MIN_WACC = "MinWACC"
    MAX_DAY1_CASH = "MaxDay1Cash"
    MAX_EQUITY_IRR = "MaxEquityIRR"
    COMPOSITE = "Composite"

class OPEXMode(Enum):
    PERCENT_OF_REVENUE = "PercentOfRevenue"
    ABSOLUTE = "Absolute£"

class Rating(Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    UNRATED = "Unrated"

@dataclass
class ScenarioState:
    """Advanced scenario state with all 116 fields from config"""
    # Project Fixed Inputs [01-08]
    Currency_01: str = "GBP"
    GrossITLoad_02: float = 100.0
    PUE_03: float = 1.30
    CapexCostPrice_04: float = 7500000
    CapexMarketRate_05: float = 9000000
    LandPurchaseFees_06: float = 20000000
    GrossMonthlyRent_07: float = 2500000
    OPEX_08: float = 25.0
    
    # Derived Fields [09-16]
    NetITLoad_09: float = field(default=0)
    GrossIncome_10: float = field(default=0)
    NetIncome_11: float = field(default=0)
    DeveloperProfit_12: float = field(default=0)
    DeveloperMargin_13: float = field(default=0)
    TotalStructuringFees_14: float = field(default=0)
    TotalProjectMarketCosts_15: float = field(default=0)
    TotalProjectInternalCosts_16: float = field(default=0)
    
    # Mode Toggles [17-26]
    OPEXMode_17: str = "PercentOfRevenue"
    IndexationMode_18: str = "Flat"
    IndexationBase_19: str = "HeadlineCPI"
    RevenueBasis_20: str = "Contracted"
    CapexBasis_21: str = "MarketRate_05"
    LeaseTermYears_22: float = 25
    ConstructionToCODMonths_23: float = 12
    PowerHedgeMode_24: str = "Unhedged"
    CurrencyPolicy_25: str = "LocalCurrency"
    VAT_TaxTreatmentToggle_26: bool = False
    
    # Market State [27-36]
    BaseCurveAnchor_27: str = "10Y"
    BaseCurveShift_bps_28: float = 0
    CreditSpreadAAA_bps_29: float = 70
    CreditSpreadAA_bps_30: float = 90
    CreditSpreadA_bps_31: float = 120
    CreditSpreadBBB_bps_32: float = 180
    InflationSpot_33: float = 2.0
    InflationFwdTerm_34: str = "10Y"
    FXSpot_35: float = 1.00
    FXHedgeCost_bps_36: float = 50
    
    # Capital Stack - Senior [37-44]
    TargetDSCRSenior_37: float = 1.30
    SeniorCoupon_38: float = 5.00
    SeniorTenorY_39: float = 25
    SeniorAmortType_40: str = "Annuity"
    SeniorGracePeriod_41: float = 0
    SeniorFeesUpfront_bps_42: float = 50
    SeniorOngoingFees_bps_43: float = 20
    SeniorRepoEligibleFlag_44: bool = True
    
    # Capital Stack - Mezzanine [45-51]
    TargetDSCRMezz_45: float = 1.15
    MezzCoupon_46: float = 8.0
    MezzTenorY_47: float = 10
    MezzAmortType_48: str = "Bullet"
    MezzFeesUpfront_bps_49: float = 100
    MezzOngoingFees_bps_50: float = 50
    IntercreditorStyle_51: str = "Sequential"
    
    # Equity/TRS [52-56]
    FirstLossPct_52: float = 5
    TRS_EquityPct_53: float = 5
    TRS_CouponOrFee_54: float = 3
    EquityIRRTarget_55: float = 17
    CallOptionYears_56: float = 5
    
    # Insurance/Wrap [57-62]
    MonolineWrapFlag_57: str = "None"
    WrapPremium_bps_58: float = 60
    DSRA_Months_59: float = 6
    LiquidityFacilityMonths_60: float = 3
    InsuranceProgrammeType_61: str = "Both"
    InsurancePremium_bps_62: float = 50
    
    # Indexation & Cashflow [63-74]
    CPI_FloorPct_63: float = 1
    CPI_CapPct_64: float = 4
    EscalatorFixedPct_65: float = 2
    Vacancy_UtilisationPct_66: float = 5
    CollectionLagDays_67: float = 30
    RentFreeMonths_68: float = 0
    MaintenanceCapexPct_69: float = 2
    PowerPassThroughMode_70: str = "Tenant"
    PPA_TermYears_71: float = 0
    PPA_Strike_£MWh_72: float = 80
    PowerSwapTenorY_73: float = 0
    PowerHedgeCoveragePct_74: float = 0
    
    # Rating & Eligibility [75-81]
    MinSeniorRatingTarget_75: str = "AAA"
    MinMezzRatingTarget_76: str = "BBB"
    TenantRatingFloor_77: str = "A-"
    ConcentrationLimitPct_78: float = 50
    JurisdictionEligibility_79: str = "CB_RepoEligible"
    MaxWAL_Senior_80: float = 20
    HaircutRuleSet_81: str = "RA_Base"
    
    # Stress & Haircuts [82-90]
    CPI_Scenarios_82: List[float] = field(default_factory=lambda: [0.0, 1.8, 2.5])
    Rate_Shock_bps_83: float = 100
    OPEX_StressPct_84: float = 10
    Rent_DownsidePct_85: float = 10
    TenantDefaultProb_86: float = 1
    RecoveryLagMonths_87: float = 6
    RefinanceSpreadAdd_bps_88: float = 100
    CapexOverrunPct_89: float = 10
    COD_DelayMonths_90: float = 6
    
    # Derivatives/Sidecar [91-98]
    ZCiS_NotionalPct_91: float = 50
    ZCiS_TermY_92: str = "10"
    ZCiS_ImpliedRate_93: float = 2.0
    CPI_BasisAdj_bps_94: float = 15
    TRS_MarginingFreq_95: str = "Quarterly"
    CCY_SwapTenorY_96: float = 0
    CCY_SwapCost_bps_97: float = 60
    DerivativeCSAType_98: str = "TwoWay"
    
    # Waterfall & Triggers [99-106]
    PriorityOfPayments_99: str = "Std"
    OC_TestLevels_100: float = 5
    DSCR_TriggerLevels_101: str = "1.20|1.05"
    CashTrapRules_102: str = "EquityBlock"
    AmortSwitchRules_103: str = "TurboOnTrap"
    ExcessSpreadUse_104: str = "PayDown"
    ReinvestmentOption_105: str = "Off"
    FeesPriorityMode_106: str = "SeniorFirst"
    
    # Output Configuration [107-116]
    MaxPermutations_108: int = 150000
    RankingObjective_109: str = "Composite"
    CompositeWeights_110: Dict[str, float] = field(default_factory=lambda: {
        "SeniorRaise": 0.35,
        "WACC": 0.25,
        "Day1": 0.20,
        "DSCR": 0.10,
        "Rating": 0.10
    })
    HardFilters_111: List[str] = field(default_factory=lambda: ["DSCR>=1.30", "RepoEligible=Yes", "SeniorRating>=AAA"])
    OutputVariants_112: List[str] = field(default_factory=lambda: ["Flat", "Indexed", "Hybrid"])
    DocumentPackFlags_113: List[str] = field(default_factory=lambda: ["IM", "TermSheets", "WaterfallPDF", "ModelExport"])
    CounterpartyRouting_114: Dict[str, List[str]] = field(default_factory=dict)
    SensitivityExportSet_115: List[str] = field(default_factory=lambda: ["CPI", "Rates", "OPEX", "Rent", "Delay"])
    AuditTraceFlag_116: bool = True

@dataclass
class KPI:
    """Key Performance Indicators for a scenario"""
    SeniorNotional: float = 0
    MezzNotional: float = 0
    EquityNotional: float = 0
    WACC: float = 0
    EquityIRR: float = 0
    DSCR_Min: float = 0
    DSCR_Avg: float = 0
    SeniorRating: str = "Unrated"
    MezzRating: str = "Unrated"
    SeniorWAL: float = 0
    RepoEligible: bool = False
    Day1Cash: float = 0
    CompositeScore: float = 0

class AdvancedPermutationEngine:
    """Full implementation of the Atlas Forge Permutation Engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.execution_order = [
            'ingest_fixed_inputs',
            'compute_derived',
            'apply_mode_toggles',
            'load_market_state',
            'size_and_price_senior',
            'add_mezzanine',
            'add_equity_trs',
            'apply_wrap_liquidity',
            'shape_cashflows',
            'apply_rating_eligibility',
            'run_stresses_haircuts',
            'apply_derivatives_sidecar',
            'build_waterfall_triggers',
            'rank_filter_export'
        ]
    
    def compute_derived_fields(self, scenario: ScenarioState) -> ScenarioState:
        """Compute all derived fields [09-16]"""
        # NetITLoad_09
        scenario.NetITLoad_09 = scenario.GrossITLoad_02 / scenario.PUE_03 if scenario.PUE_03 > 0 else 0
        
        # GrossIncome_10
        scenario.GrossIncome_10 = scenario.GrossMonthlyRent_07 * 12
        
        # NetIncome_11
        if scenario.OPEXMode_17 == "PercentOfRevenue":
            scenario.NetIncome_11 = scenario.GrossIncome_10 * (1 - scenario.OPEX_08 / 100)
        else:
            scenario.NetIncome_11 = scenario.GrossIncome_10 - scenario.OPEX_08
        
        # TotalProjectMarketCosts_15
        scenario.TotalProjectMarketCosts_15 = (scenario.CapexMarketRate_05 * scenario.GrossITLoad_02) + scenario.LandPurchaseFees_06
        
        # TotalProjectInternalCosts_16
        scenario.TotalProjectInternalCosts_16 = (scenario.CapexCostPrice_04 * scenario.GrossITLoad_02) + scenario.LandPurchaseFees_06
        
        # DeveloperProfit_12
        if scenario.DeveloperProfit_12 == 0:
            scenario.DeveloperProfit_12 = scenario.TotalProjectMarketCosts_15 - scenario.TotalProjectInternalCosts_16
        
        # DeveloperMargin_13
        if scenario.TotalProjectMarketCosts_15 > 0:
            scenario.DeveloperMargin_13 = 100 * scenario.DeveloperProfit_12 / scenario.TotalProjectMarketCosts_15
        
        return scenario
    
    def size_senior_debt(self, scenario: ScenarioState) -> Tuple[float, float, float]:
        """Size senior debt to meet target DSCR"""
        net_income = scenario.NetIncome_11
        if net_income <= 0:
            return 0, 0, 0
        
        # Calculate debt service capacity
        target_dscr = scenario.TargetDSCRSenior_37
        max_debt_service = net_income / target_dscr
        
        # Calculate senior notional based on amortization type
        if scenario.SeniorAmortType_40 == "Bullet":
            # Interest only
            senior_notional = max_debt_service / (scenario.SeniorCoupon_38 / 100)
        elif scenario.SeniorAmortType_40 == "Annuity":
            # Level payment amortization
            rate = scenario.SeniorCoupon_38 / 100
            periods = scenario.SeniorTenorY_39
            if rate > 0:
                annuity_factor = (1 - (1 + rate) ** -periods) / rate
                senior_notional = max_debt_service * annuity_factor
            else:
                senior_notional = max_debt_service * periods
        else:
            # Simplified for other types
            senior_notional = max_debt_service * scenario.SeniorTenorY_39 * 0.7
        
        # Apply constraints
        max_ltv = 0.85  # Maximum loan-to-value
        max_notional = scenario.TotalProjectMarketCosts_15 * max_ltv
        senior_notional = min(senior_notional, max_notional)
        
        # Calculate actual DSCR
        if senior_notional > 0:
            if scenario.SeniorAmortType_40 == "Bullet":
                debt_service = senior_notional * (scenario.SeniorCoupon_38 / 100)
            else:
                rate = scenario.SeniorCoupon_38 / 100
                periods = scenario.SeniorTenorY_39
                if rate > 0 and periods > 0:
                    debt_service = senior_notional * rate / (1 - (1 + rate) ** -periods)
                else:
                    debt_service = senior_notional / periods if periods > 0 else 0
            
            actual_dscr = net_income / debt_service if debt_service > 0 else 999
        else:
            actual_dscr = 999
        
        return senior_notional, actual_dscr, actual_dscr
    
    def calculate_rating(self, scenario: ScenarioState, dscr: float) -> str:
        """Calculate rating based on DSCR and other metrics"""
        if dscr >= 1.5:
            return "AAA"
        elif dscr >= 1.35:
            return "AA"
        elif dscr >= 1.25:
            return "A"
        elif dscr >= 1.15:
            return "BBB"
        elif dscr >= 1.05:
            return "BB"
        else:
            return "B"
    
    def calculate_wacc(self, scenario: ScenarioState, senior_notional: float, mezz_notional: float = 0) -> float:
        """Calculate Weighted Average Cost of Capital"""
        total_capital = scenario.TotalProjectMarketCosts_15
        if total_capital == 0:
            return 0
        
        senior_weight = senior_notional / total_capital
        mezz_weight = mezz_notional / total_capital
        equity_weight = 1 - senior_weight - mezz_weight
        
        wacc = (senior_weight * scenario.SeniorCoupon_38 + 
                mezz_weight * scenario.MezzCoupon_46 + 
                equity_weight * scenario.EquityIRRTarget_55)
        
        return wacc
    
    def calculate_equity_irr(self, scenario: ScenarioState, senior_notional: float, mezz_notional: float = 0) -> float:
        """Calculate equity IRR"""
        equity_investment = scenario.TotalProjectMarketCosts_15 - senior_notional - mezz_notional
        if equity_investment <= 0:
            return 0
        
        # Annual cash flow to equity
        senior_interest = senior_notional * scenario.SeniorCoupon_38 / 100
        mezz_interest = mezz_notional * scenario.MezzCoupon_46 / 100
        annual_cf_to_equity = scenario.NetIncome_11 - senior_interest - mezz_interest
        
        # Simplified IRR calculation
        if annual_cf_to_equity > 0:
            simple_irr = (annual_cf_to_equity / equity_investment) * 100
            # Adjust for growth if indexed
            if scenario.IndexationMode_18 == "CPI_Linked":
                growth_adj = min(max(scenario.InflationSpot_33, scenario.CPI_FloorPct_63), scenario.CPI_CapPct_64)
                simple_irr += growth_adj
            return simple_irr
        return 0
    
    def calculate_kpis(self, scenario: ScenarioState) -> KPI:
        """Calculate all KPIs for a scenario"""
        kpi = KPI()
        
        # Size senior debt
        senior_notional, dscr_min, dscr_avg = self.size_senior_debt(scenario)
        kpi.SeniorNotional = senior_notional
        kpi.DSCR_Min = dscr_min
        kpi.DSCR_Avg = dscr_avg
        
        # Size mezzanine if applicable
        if scenario.TargetDSCRMezz_45 > 0 and dscr_min > scenario.TargetDSCRMezz_45:
            remaining_capacity = scenario.NetIncome_11 - (senior_notional * scenario.SeniorCoupon_38 / 100)
            if remaining_capacity > 0:
                mezz_notional = remaining_capacity / (scenario.MezzCoupon_46 / 100) * scenario.TargetDSCRMezz_45
                max_mezz = (scenario.TotalProjectMarketCosts_15 - senior_notional) * 0.15  # Max 15% mezz
                kpi.MezzNotional = min(mezz_notional, max_mezz)
        
        # Calculate equity
        kpi.EquityNotional = scenario.TotalProjectMarketCosts_15 - kpi.SeniorNotional - kpi.MezzNotional
        
        # Calculate WACC
        kpi.WACC = self.calculate_wacc(scenario, kpi.SeniorNotional, kpi.MezzNotional)
        
        # Calculate Equity IRR
        kpi.EquityIRR = self.calculate_equity_irr(scenario, kpi.SeniorNotional, kpi.MezzNotional)
        
        # Determine ratings
        kpi.SeniorRating = self.calculate_rating(scenario, dscr_min)
        kpi.MezzRating = "BBB" if kpi.MezzNotional > 0 else "Unrated"
        
        # Calculate Senior WAL
        if scenario.SeniorAmortType_40 == "Bullet":
            kpi.SeniorWAL = scenario.SeniorTenorY_39
        else:
            kpi.SeniorWAL = scenario.SeniorTenorY_39 * 0.55  # Approximation
        
        # Check repo eligibility
        kpi.RepoEligible = (
            scenario.SeniorRepoEligibleFlag_44 and 
            kpi.SeniorRating in ["AAA", "AA"] and
            kpi.SeniorWAL <= scenario.MaxWAL_Senior_80
        )
        
        # Calculate Day 1 cash (wrap monetization + derivatives)
        if scenario.MonolineWrapFlag_57 != "None":
            wrap_value = kpi.SeniorNotional * scenario.WrapPremium_bps_58 / 10000
            kpi.Day1Cash += wrap_value
        
        if scenario.ZCiS_NotionalPct_91 > 0:
            zcis_notional = kpi.SeniorNotional * scenario.ZCiS_NotionalPct_91 / 100
            zcis_value = zcis_notional * 0.02  # Simplified
            kpi.Day1Cash += zcis_value
        
        return kpi
    
    def check_viability(self, scenario: ScenarioState, kpi: KPI) -> bool:
        """Check if scenario meets viability criteria"""
        # Basic viability checks
        if kpi.DSCR_Min < scenario.TargetDSCRSenior_37:
            return False
        
        # Apply hard filters
        for filter_str in scenario.HardFilters_111:
            if "DSCR>=" in filter_str:
                min_dscr = float(filter_str.split(">=")[1])
                if kpi.DSCR_Min < min_dscr:
                    return False
            elif "RepoEligible=Yes" in filter_str:
                if not kpi.RepoEligible:
                    return False
            elif "SeniorRating>=" in filter_str:
                req_rating = filter_str.split(">=")[1]
                rating_order = ["AAA", "AA", "A", "BBB", "BB", "B", "Unrated"]
                if rating_order.index(kpi.SeniorRating) > rating_order.index(req_rating):
                    return False
        
        return True
    
    def calculate_composite_score(self, scenario: ScenarioState, kpi: KPI) -> float:
        """Calculate composite ranking score"""
        weights = scenario.CompositeWeights_110
        score = 0
        
        # Normalize and weight each component
        if "SeniorRaise" in weights:
            # Normalize to 0-100 scale (assume max 1B)
            normalized = min(kpi.SeniorNotional / 1000000000, 1) * 100
            score += normalized * weights["SeniorRaise"]
        
        if "WACC" in weights:
            # Lower WACC is better, invert scale
            normalized = max(0, 100 - kpi.WACC * 10)
            score += normalized * weights["WACC"]
        
        if "Day1" in weights:
            # Normalize to 0-100 scale (assume max 100M)
            normalized = min(kpi.Day1Cash / 100000000, 1) * 100
            score += normalized * weights["Day1"]
        
        if "DSCR" in weights:
            # Higher DSCR is better
            normalized = min(kpi.DSCR_Min * 50, 100)
            score += normalized * weights["DSCR"]
        
        if "Rating" in weights:
            # Map rating to score
            rating_scores = {"AAA": 100, "AA": 85, "A": 70, "BBB": 55, "BB": 40, "B": 25, "Unrated": 0}
            normalized = rating_scores.get(kpi.SeniorRating, 0)
            score += normalized * weights["Rating"]
        
        return score
    
    def generate_scenarios(self, config: Dict[str, Any], mode: str = "all") -> List[Dict[str, Any]]:
        """Generate permutation scenarios based on configuration"""
        scenarios = []
        
        # Extract ranges from config
        rent_values = self._get_range_values(config, "GrossMonthlyRent_07", 500000, 5000000, 50000)
        opex_values = self._get_range_values(config, "OPEX_08", 15, 35, 1)
        dscr_values = self._get_range_values(config, "TargetDSCRSenior_37", 1.20, 1.50, 0.05)
        coupon_values = self._get_range_values(config, "SeniorCoupon_38", 3.5, 7.0, 0.25)
        
        # Limit permutations for quick preview
        if mode == "quick":
            rent_values = rent_values[:3]
            opex_values = opex_values[:3]
            dscr_values = dscr_values[:2]
            coupon_values = coupon_values[:3]
        elif mode == "viable":
            # Focus on likely viable ranges
            opex_values = [x for x in opex_values if 15 <= x <= 30]
            dscr_values = [x for x in dscr_values if 1.20 <= x <= 1.40]
            coupon_values = [x for x in coupon_values if 4.0 <= x <= 6.0]
        
        # Generate permutations
        count = 0
        max_permutations = config.get("MaxPermutations_108", 150000)
        
        for rent, opex, dscr, coupon in itertools.product(rent_values, opex_values, dscr_values, coupon_values):
            if count >= max_permutations:
                break
            
            # Create scenario
            scenario = ScenarioState()
            
            # Apply config values
            for key, value in config.items():
                if hasattr(scenario, key):
                    setattr(scenario, key, value)
            
            # Set permutation values
            scenario.GrossMonthlyRent_07 = rent
            scenario.OPEX_08 = opex
            scenario.TargetDSCRSenior_37 = dscr
            scenario.SeniorCoupon_38 = coupon
            
            # Compute derived fields
            scenario = self.compute_derived_fields(scenario)
            
            # Calculate KPIs
            kpi = self.calculate_kpis(scenario)
            
            # Check viability
            viable = self.check_viability(scenario, kpi)
            
            # Calculate composite score
            kpi.CompositeScore = self.calculate_composite_score(scenario, kpi)
            
            scenarios.append({
                "id": count + 1,
                "scenario": scenario,
                "kpis": kpi,
                "viable": viable,
                "composite_score": kpi.CompositeScore
            })
            
            count += 1
        
        return scenarios
    
    def _get_range_values(self, config: Dict[str, Any], field: str, default_min: float, default_max: float, default_step: float) -> List[float]:
        """Get range values for a field from config"""
        if f"{field}_range" in config and config[f"{field}_range"]:
            min_val = config.get(f"{field}_min", default_min)
            max_val = config.get(f"{field}_max", default_max)
            step = config.get(f"{field}_step", default_step)
        else:
            # Use single value if no range
            return [config.get(field, default_min)]
        
        # Generate range
        values = []
        current = min_val
        while current <= max_val:
            values.append(current)
            current += step
        
        return values
    
    def rank_scenarios(self, scenarios: List[Dict[str, Any]], objective: str = "Composite") -> List[Dict[str, Any]]:
        """Rank scenarios based on objective"""
        if objective == "MaxSeniorRaise":
            return sorted(scenarios, key=lambda x: x["kpis"].SeniorNotional, reverse=True)
        elif objective == "MinWACC":
            return sorted(scenarios, key=lambda x: x["kpis"].WACC)
        elif objective == "MaxDay1Cash":
            return sorted(scenarios, key=lambda x: x["kpis"].Day1Cash, reverse=True)
        elif objective == "MaxEquityIRR":
            return sorted(scenarios, key=lambda x: x["kpis"].EquityIRR, reverse=True)
        else:  # Composite
            return sorted(scenarios, key=lambda x: x["composite_score"], reverse=True)

def run_advanced_permutation_engine(config: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for the advanced permutation engine"""
    engine = AdvancedPermutationEngine(config)
    
    # Generate scenarios
    mode = config.get("mode", "all")
    scenarios = engine.generate_scenarios(config, mode=mode)
    
    # Rank scenarios
    ranking_objective = config.get("RankingObjective_109", "Composite")
    ranked = engine.rank_scenarios(scenarios, ranking_objective)
    
    # Format output
    output = {
        "total_scenarios": len(ranked),
        "viable_count": sum(1 for s in ranked if s["viable"]),
        "scenarios": [],
        "summary": {}
    }
    
    # Include top scenarios
    for scenario in ranked[:1000]:  # Limit output
        output["scenarios"].append({
            "id": scenario["id"],
            "inputs": {
                "monthly_rent": scenario["scenario"].GrossMonthlyRent_07,
                "opex": scenario["scenario"].OPEX_08,
                "target_dscr": scenario["scenario"].TargetDSCRSenior_37,
                "senior_coupon": scenario["scenario"].SeniorCoupon_38
            },
            "outputs": {
                "senior_notional": scenario["kpis"].SeniorNotional,
                "mezz_notional": scenario["kpis"].MezzNotional,
                "equity_notional": scenario["kpis"].EquityNotional,
                "wacc": scenario["kpis"].WACC,
                "equity_irr": scenario["kpis"].EquityIRR,
                "dscr_min": scenario["kpis"].DSCR_Min,
                "dscr_avg": scenario["kpis"].DSCR_Avg,
                "senior_rating": scenario["kpis"].SeniorRating,
                "mezz_rating": scenario["kpis"].MezzRating,
                "senior_wal": scenario["kpis"].SeniorWAL,
                "repo_eligible": scenario["kpis"].RepoEligible,
                "day1_cash": scenario["kpis"].Day1Cash
            },
            "viable": scenario["viable"],
            "composite_score": scenario["composite_score"]
        })
    
    # Calculate summary statistics
    if output["scenarios"]:
        viable_scenarios = [s for s in output["scenarios"] if s["viable"]]
        
        if viable_scenarios:
            output["summary"] = {
                "best_irr": max(s["outputs"]["equity_irr"] for s in viable_scenarios),
                "best_dscr": max(s["outputs"]["dscr_min"] for s in viable_scenarios),
                "avg_senior": sum(s["outputs"]["senior_notional"] for s in viable_scenarios) / len(viable_scenarios),
                "best_wacc": min(s["outputs"]["wacc"] for s in viable_scenarios),
                "max_senior": max(s["outputs"]["senior_notional"] for s in viable_scenarios),
                "max_day1": max(s["outputs"]["day1_cash"] for s in viable_scenarios)
            }
        else:
            # No viable scenarios, use all
            output["summary"] = {
                "best_irr": max(s["outputs"]["equity_irr"] for s in output["scenarios"]) if output["scenarios"] else 0,
                "best_dscr": max(s["outputs"]["dscr_min"] for s in output["scenarios"]) if output["scenarios"] else 0,
                "avg_senior": sum(s["outputs"]["senior_notional"] for s in output["scenarios"]) / len(output["scenarios"]) if output["scenarios"] else 0,
                "best_wacc": min(s["outputs"]["wacc"] for s in output["scenarios"]) if output["scenarios"] else 0,
                "max_senior": max(s["outputs"]["senior_notional"] for s in output["scenarios"]) if output["scenarios"] else 0,
                "max_day1": max(s["outputs"]["day1_cash"] for s in output["scenarios"]) if output["scenarios"] else 0
            }
    
    return output