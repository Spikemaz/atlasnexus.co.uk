"""
Atlas Forge - Permutation Engine v1.0.0
Based on TypeScript spec but implemented in Python for Flask integration
"""

import math
import json
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

# ==================== Type Definitions ====================

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

@dataclass
class ScenarioState:
    """Holds all resolved field values for a single scenario"""
    # Project Inputs
    Currency_01: str = "GBP"
    GrossITLoad_02: float = 100.0
    PUE_03: float = 1.30
    CapexCostPrice_04: float = 7500000
    CapexMarketRate_05: float = 9000000
    LandPurchaseFees_06: float = 20000000
    GrossMonthlyRent_07: float = 2500000
    OPEX_08: float = 25.0
    
    # Derived Fields
    NetITLoad_09: float = field(init=False)
    GrossIncome_10: float = field(init=False)
    NetIncome_11: float = field(init=False)
    TotalProjectMarketCosts_15: float = field(init=False)
    TotalProjectInternalCosts_16: float = field(init=False)
    
    # Capital Stack
    TargetDSCRSenior_37: float = 1.30
    SeniorCoupon_38: float = 5.00
    SeniorTenorY_39: float = 25
    SeniorAmortType_40: str = "Annuity"
    
    # Accounting/Mode
    OPEXMode_17: str = "PercentOfRevenue"
    IndexationMode_18: str = "Flat"
    LeaseTermYears_22: float = 25
    
    # Market State
    BaseCurveShift_bps_28: float = 0
    CreditSpreadAAA_bps_29: float = 70
    InflationSpot_33: float = 2.0
    
    # Indexation
    CPI_FloorPct_63: float = 1.0
    CPI_CapPct_64: float = 4.0
    EscalatorFixedPct_65: float = 2.0
    
    # Stress Parameters
    OPEX_StressPct_84: float = 10.0
    Rent_DownsidePct_85: float = 10.0
    
    def __post_init__(self):
        """Calculate derived fields"""
        self.NetITLoad_09 = self.GrossITLoad_02 / self.PUE_03
        self.GrossIncome_10 = self.GrossMonthlyRent_07 * 12
        
        if self.OPEXMode_17 == "PercentOfRevenue":
            self.NetIncome_11 = self.GrossIncome_10 * (1 - self.OPEX_08 / 100)
        else:
            self.NetIncome_11 = self.GrossIncome_10 - self.OPEX_08
            
        self.TotalProjectMarketCosts_15 = (self.CapexMarketRate_05 * self.GrossITLoad_02) + self.LandPurchaseFees_06
        self.TotalProjectInternalCosts_16 = (self.CapexCostPrice_04 * self.GrossITLoad_02) + self.LandPurchaseFees_06

@dataclass
class KPI:
    """Key Performance Indicators for a scenario"""
    SeniorNotional: float
    MezzNotional: float = 0
    EquityNotional: float = 0
    Day1Cash: float = 0
    WACC: float = 0
    EquityIRR: float = 0
    SeniorRating: str = "AAA"
    SeniorWAL: float = 0
    DSCR_Min: float = 0
    DSCR_Avg: float = 0
    RepoEligible: bool = True

@dataclass
class WaterfallOutput:
    """Output from waterfall calculations"""
    timeline: List[Dict[str, float]]
    DSCR_Min: float
    DSCR_Avg: float
    SeniorWAL: float
    EquityIRR: float

# ==================== Core Calculation Functions ====================

class PermutationEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_permutations = config.get('MaxPermutations_108', 150000)
        
    def calculate_annuity_payment(self, principal: float, rate: float, periods: int) -> float:
        """Calculate annuity payment (PMT)"""
        if rate == 0:
            return principal / periods
        r = rate / 100 / 12  # Monthly rate
        return principal * (r * (1 + r)**periods) / ((1 + r)**periods - 1)
    
    def calculate_dscr(self, net_income: float, debt_service: float) -> float:
        """Calculate Debt Service Coverage Ratio"""
        if debt_service == 0:
            return float('inf')
        return net_income / debt_service
    
    def size_senior_debt(self, scenario: ScenarioState) -> Tuple[float, float, float]:
        """
        Size senior debt based on target DSCR
        Returns: (SeniorNotional, DSCR_Min, DSCR_Avg)
        """
        # Monthly cash flows
        months = int(scenario.LeaseTermYears_22 * 12)
        monthly_net_income = scenario.NetIncome_11 / 12
        
        # Apply indexation if not Flat
        cashflows = []
        for month in range(months):
            if scenario.IndexationMode_18 == "Flat":
                cf = monthly_net_income
            elif scenario.IndexationMode_18 == "CPI_Linked":
                # Apply CPI growth with floor and cap
                years = month / 12
                cpi_growth = min(max(scenario.InflationSpot_33, scenario.CPI_FloorPct_63), scenario.CPI_CapPct_64)
                cf = monthly_net_income * (1 + cpi_growth/100) ** years
            else:  # Partial
                years = month / 12
                cf = monthly_net_income * (1 + scenario.EscalatorFixedPct_65/100) ** years
            cashflows.append(cf)
        
        # Binary search for maximum senior notional
        min_notional = 0
        max_notional = scenario.TotalProjectMarketCosts_15
        best_notional = 0
        best_dscr_min = 0
        best_dscr_avg = 0
        
        while max_notional - min_notional > 1000:  # £1k precision
            test_notional = (min_notional + max_notional) / 2
            
            # Calculate debt service for this notional
            if scenario.SeniorAmortType_40 == "Annuity":
                monthly_payment = self.calculate_annuity_payment(
                    test_notional, 
                    scenario.SeniorCoupon_38,
                    int(scenario.SeniorTenorY_39 * 12)
                )
                debt_service = [monthly_payment] * min(months, int(scenario.SeniorTenorY_39 * 12))
            elif scenario.SeniorAmortType_40 == "Bullet":
                # Interest only until maturity
                monthly_interest = test_notional * (scenario.SeniorCoupon_38 / 100 / 12)
                debt_service = [monthly_interest] * min(months, int(scenario.SeniorTenorY_39 * 12))
            else:  # Sculpted or StepDown
                # Simplified sculpted: target DSCR throughout
                debt_service = [cf / scenario.TargetDSCRSenior_37 for cf in cashflows[:int(scenario.SeniorTenorY_39 * 12)]]
            
            # Calculate DSCRs
            dscrs = []
            for i in range(len(debt_service)):
                if i < len(cashflows) and debt_service[i] > 0:
                    dscr = cashflows[i] / debt_service[i]
                    dscrs.append(dscr)
            
            if dscrs:
                dscr_min = min(dscrs)
                dscr_avg = sum(dscrs) / len(dscrs)
                
                if dscr_min >= scenario.TargetDSCRSenior_37:
                    # This notional works, try higher
                    best_notional = test_notional
                    best_dscr_min = dscr_min
                    best_dscr_avg = dscr_avg
                    min_notional = test_notional
                else:
                    # Too high, try lower
                    max_notional = test_notional
            else:
                max_notional = test_notional
        
        return best_notional, best_dscr_min, best_dscr_avg
    
    def calculate_wacc(self, scenario: ScenarioState, senior_notional: float) -> float:
        """Calculate Weighted Average Cost of Capital"""
        total_capital = scenario.TotalProjectMarketCosts_15
        if total_capital == 0:
            return 0
        
        senior_weight = senior_notional / total_capital
        equity_weight = 1 - senior_weight
        
        # Simple WACC calculation
        wacc = (senior_weight * scenario.SeniorCoupon_38) + (equity_weight * 15)  # Assume 15% equity cost
        return wacc
    
    def calculate_senior_wal(self, scenario: ScenarioState, senior_notional: float) -> float:
        """Calculate Weighted Average Life of senior debt"""
        if scenario.SeniorAmortType_40 == "Bullet":
            return scenario.SeniorTenorY_39
        elif scenario.SeniorAmortType_40 == "Annuity":
            # Approximate WAL for annuity
            return scenario.SeniorTenorY_39 * 0.55  # Rough approximation
        else:
            return scenario.SeniorTenorY_39 * 0.6
    
    def run_waterfall(self, scenario: ScenarioState, mode: str = "Flat") -> WaterfallOutput:
        """
        Run waterfall calculations for a given mode
        Modes: Flat, Indexed, Hybrid
        """
        months = int(scenario.LeaseTermYears_22 * 12)
        timeline = []
        
        # Get sized senior debt
        senior_notional, dscr_min, dscr_avg = self.size_senior_debt(scenario)
        
        # Calculate monthly cashflows
        for month in range(months):
            month_data = {
                "month": month + 1,
                "gross_income": scenario.GrossMonthlyRent_07,
                "opex": scenario.GrossMonthlyRent_07 * (scenario.OPEX_08 / 100),
                "net_income": scenario.GrossMonthlyRent_07 * (1 - scenario.OPEX_08 / 100)
            }
            
            # Apply indexation based on mode
            if mode == "Indexed":
                years = month / 12
                if scenario.IndexationMode_18 == "CPI_Linked":
                    growth = min(max(scenario.InflationSpot_33, scenario.CPI_FloorPct_63), scenario.CPI_CapPct_64)
                    factor = (1 + growth/100) ** years
                else:
                    factor = (1 + scenario.EscalatorFixedPct_65/100) ** years
                month_data["net_income"] *= factor
            elif mode == "Hybrid":
                # CPI growth for first 10 years, then flat
                if month < 120:  # First 10 years
                    years = month / 12
                    growth = min(max(scenario.InflationSpot_33, scenario.CPI_FloorPct_63), scenario.CPI_CapPct_64)
                    factor = (1 + growth/100) ** years
                    month_data["net_income"] *= factor
            
            timeline.append(month_data)
        
        # Calculate equity IRR (simplified)
        equity_investment = scenario.TotalProjectMarketCosts_15 - senior_notional
        if equity_investment > 0:
            annual_equity_cf = (scenario.NetIncome_11 - senior_notional * scenario.SeniorCoupon_38 / 100)
            equity_irr = (annual_equity_cf / equity_investment) * 100
        else:
            equity_irr = 0
        
        # Calculate Senior WAL
        senior_wal = self.calculate_senior_wal(scenario, senior_notional)
        
        return WaterfallOutput(
            timeline=timeline,
            DSCR_Min=dscr_min,
            DSCR_Avg=dscr_avg,
            SeniorWAL=senior_wal,
            EquityIRR=equity_irr
        )
    
    def calculate_kpis(self, scenario: ScenarioState) -> KPI:
        """Calculate all KPIs for a scenario"""
        # Size senior debt
        senior_notional, dscr_min, dscr_avg = self.size_senior_debt(scenario)
        
        # Calculate WACC
        wacc = self.calculate_wacc(scenario, senior_notional)
        
        # Run waterfall for equity IRR
        waterfall = self.run_waterfall(scenario, "Flat")
        
        # Determine rating based on DSCR
        if dscr_min >= 1.5:
            rating = "AAA"
        elif dscr_min >= 1.35:
            rating = "AA"
        elif dscr_min >= 1.25:
            rating = "A"
        elif dscr_min >= 1.15:
            rating = "BBB"
        else:
            rating = "BB"
        
        # Check repo eligibility
        repo_eligible = rating in ["AAA", "AA"] and waterfall.SeniorWAL <= 20
        
        return KPI(
            SeniorNotional=senior_notional,
            MezzNotional=0,  # Not implemented yet
            EquityNotional=scenario.TotalProjectMarketCosts_15 - senior_notional,
            Day1Cash=senior_notional * 0.95,  # Assume 95% advance rate
            WACC=wacc,
            EquityIRR=waterfall.EquityIRR,
            SeniorRating=rating,
            SeniorWAL=waterfall.SeniorWAL,
            DSCR_Min=dscr_min,
            DSCR_Avg=dscr_avg,
            RepoEligible=repo_eligible
        )
    
    def rank_scenarios(self, results: List[Dict], objective: str = "Composite") -> List[Dict]:
        """Rank scenarios based on objective"""
        if objective == "MaxSeniorRaise":
            return sorted(results, key=lambda x: x['kpis'].SeniorNotional, reverse=True)
        elif objective == "MinWACC":
            return sorted(results, key=lambda x: x['kpis'].WACC)
        elif objective == "MaxDay1Cash":
            return sorted(results, key=lambda x: x['kpis'].Day1Cash, reverse=True)
        elif objective == "MaxEquityIRR":
            return sorted(results, key=lambda x: x['kpis'].EquityIRR, reverse=True)
        else:  # Composite
            # Composite scoring with default weights
            weights = {
                'SeniorRaise': 0.35,
                'WACC': 0.25,
                'Day1': 0.20,
                'DSCR': 0.10,
                'Rating': 0.10
            }
            
            def composite_score(result):
                kpi = result['kpis']
                rating_score = {'AAA': 1.0, 'AA': 0.8, 'A': 0.6, 'BBB': 0.4, 'BB': 0.2}.get(kpi.SeniorRating, 0)
                
                score = (
                    weights['SeniorRaise'] * (kpi.SeniorNotional / 1e8) +  # Normalize to £100M
                    weights['WACC'] * (20 - kpi.WACC) / 20 +  # Lower is better
                    weights['Day1'] * (kpi.Day1Cash / 1e8) +
                    weights['DSCR'] * min(kpi.DSCR_Min / 2, 1) +  # Cap at 2.0
                    weights['Rating'] * rating_score
                )
                return score
            
            for result in results:
                result['composite_score'] = composite_score(result)
            
            return sorted(results, key=lambda x: x.get('composite_score', 0), reverse=True)
    
    def generate_scenarios(self, inputs: Dict[str, Any], mode: str = "all") -> List[Dict]:
        """Generate and evaluate scenarios based on input ranges"""
        results = []
        
        # Simple generation for demo - in production would enumerate all combinations
        num_scenarios = 100 if mode == "all" else 10
        
        for i in range(num_scenarios):
            # Create scenario with some variation
            scenario = ScenarioState(
                GrossMonthlyRent_07=inputs.get('GrossMonthlyRent_07', 2500000) + (i * 50000),
                OPEX_08=inputs.get('OPEX_08', 25) + (i * 0.5 % 10),
                TargetDSCRSenior_37=inputs.get('TargetDSCRSenior_37', 1.30),
                SeniorCoupon_38=inputs.get('SeniorCoupon_38', 5.0) + (i * 0.1 % 3)
            )
            
            # Calculate KPIs
            kpis = self.calculate_kpis(scenario)
            
            # Check viability
            viable = kpis.DSCR_Min >= 1.0 and kpis.EquityIRR >= 10
            
            if mode == "viable" and not viable:
                continue
            
            results.append({
                'id': i + 1,
                'scenario': scenario,
                'kpis': kpis,
                'viable': viable
            })
        
        return results

# ==================== API Interface ====================

def run_permutation_engine(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for running the permutation engine
    Returns structured results for the dashboard
    """
    engine = PermutationEngine(config)
    
    # Generate scenarios
    scenarios = engine.generate_scenarios(config, mode=config.get('mode', 'all'))
    
    # Rank scenarios
    ranking_objective = config.get('RankingObjective_109', 'Composite')
    ranked = engine.rank_scenarios(scenarios, ranking_objective)
    
    # Format for output
    output = {
        'total_scenarios': len(ranked),
        'viable_count': sum(1 for s in ranked if s['viable']),
        'scenarios': []
    }
    
    for scenario in ranked[:1000]:  # Limit output
        output['scenarios'].append({
            'id': scenario['id'],
            'inputs': {
                'monthly_rent': scenario['scenario'].GrossMonthlyRent_07,
                'opex': scenario['scenario'].OPEX_08,
                'target_dscr': scenario['scenario'].TargetDSCRSenior_37,
                'senior_coupon': scenario['scenario'].SeniorCoupon_38
            },
            'outputs': {
                'senior_notional': scenario['kpis'].SeniorNotional,
                'wacc': scenario['kpis'].WACC,
                'equity_irr': scenario['kpis'].EquityIRR,
                'dscr_min': scenario['kpis'].DSCR_Min,
                'dscr_avg': scenario['kpis'].DSCR_Avg,
                'senior_rating': scenario['kpis'].SeniorRating,
                'senior_wal': scenario['kpis'].SeniorWAL,
                'repo_eligible': scenario['kpis'].RepoEligible
            },
            'viable': scenario['viable'],
            'composite_score': scenario.get('composite_score', 0)
        })
    
    # Calculate summary statistics
    if output['scenarios']:
        best_irr = max(s['outputs']['equity_irr'] for s in output['scenarios'])
        best_dscr = max(s['outputs']['dscr_min'] for s in output['scenarios'])
        avg_senior = sum(s['outputs']['senior_notional'] for s in output['scenarios']) / len(output['scenarios'])
        
        output['summary'] = {
            'best_irr': best_irr,
            'best_dscr': best_dscr,
            'avg_senior_raise': avg_senior,
            'ranking_objective': ranking_objective
        }
    
    return output