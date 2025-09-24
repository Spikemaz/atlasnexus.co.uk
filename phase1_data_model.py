"""
Phase-1 Data Model: Inputs, Deriveds, and Ranges
Projects → Permutations → Securitisation
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal, Union
from datetime import datetime
from enum import Enum

# ==================== ENUMS ====================

class Currency(str, Enum):
    GBP = "GBP"
    EUR = "EUR"
    USD = "USD"
    JPY = "JPY"

class TenantRating(str, Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    NR = "NR"

class IndexationBasis(str, Enum):
    FLAT = "flat"
    CPI = "CPI"
    CPI_CAPPED = "CPI_capped"

class AmortType(str, Enum):
    ANNUITY = "Annuity"
    LEVEL = "Level"
    SCULPTED = "Sculpted"
    BULLET = "Bullet"

class ICCRuleset(str, Enum):
    STANDARD = "Standard"
    TIGHT = "Tight"
    EQUITY_FRIENDLY = "Equity-friendly"

class ViabilityTier(str, Enum):
    DIAMOND = "Diamond"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"
    NOT_VIABLE = "Not Viable"

# ==================== PROJECT INPUTS ====================

@dataclass
class ProjectInputs:
    """Fixed facts captured at project level"""

    # Project meta
    title: str
    country: str  # Jurisdiction
    currency: Currency

    # Capacity & lease
    gross_it_load_mw: float
    pue: float  # 0.95-1.5
    lease_years: int
    tenant_rating: TenantRating

    # Costs
    opex_pct: float  # % of gross
    capex_cost_per_mw: float
    land_fees_total: float

    # Revenue (one required)
    gross_monthly_rent: Optional[float] = None
    rent_per_kwh_month: Optional[float] = None
    capex_market_per_mw: Optional[float] = None

    # Structuring fees (defaults)
    ruleset_version: str = "v1.0"
    indexation_basis: IndexationBasis = IndexationBasis.FLAT
    arranger_fee_pct: float = 0.0125
    legal_fee_pct: float = 0.0025
    rating_fee_pct: float = 0.0015
    admin_bps: float = 15

    # Risk toggles
    wrap: bool = False
    wrap_premium_bps: Optional[float] = None
    repo_target: bool = False

    # Stress & timing
    construction_start: Optional[datetime] = None
    construction_months: int = 24
    base_cpi: float = 0.02

    def validate(self) -> List[str]:
        """Validate inputs and return errors"""
        errors = []

        if self.lease_years < 5:
            errors.append("Lease term must be >= 5 years")

        if not (0.95 <= self.pue <= 1.5):
            errors.append("PUE must be between 0.95 and 1.5")

        if not (0 <= self.opex_pct <= 1):
            errors.append("OPEX % must be between 0 and 100%")

        if self.gross_monthly_rent is None and self.rent_per_kwh_month is None:
            errors.append("Either gross_monthly_rent or rent_per_kwh_month required")

        if self.wrap and self.wrap_premium_bps is None:
            errors.append("Wrap premium BPS required when wrap=True")

        return errors

# ==================== DERIVED FIELDS ====================

@dataclass
class DerivedFields:
    """Auto-computed fields from project inputs"""

    # Core calculations
    net_it_load_mw: float
    gross_income_m: float
    opex_m: float
    noi_m: float
    project_capex: float
    upfront_fees: float
    funding_need: float

    # Rule-derived bounds
    tenor_cap: int
    dscr_floor_by_rating: float
    dsra_months: int
    af_min: float
    af_max: float

    # Repo eligibility
    repo_eligible_flag: bool
    repo_reason: str

    @classmethod
    def compute_from_inputs(cls, inputs: ProjectInputs) -> 'DerivedFields':
        """Compute all derived fields from project inputs"""

        # Net IT Load
        net_it_load_mw = inputs.gross_it_load_mw / inputs.pue

        # Monthly income
        if inputs.gross_monthly_rent is not None:
            gross_income_m = inputs.gross_monthly_rent
        elif inputs.rent_per_kwh_month is not None:
            gross_income_m = net_it_load_mw * 1000 * 730 * inputs.rent_per_kwh_month
        else:
            gross_income_m = 0

        # OPEX and NOI
        opex_m = gross_income_m * inputs.opex_pct
        noi_m = gross_income_m - opex_m

        # Capex and fees
        project_capex = inputs.capex_cost_per_mw * inputs.gross_it_load_mw + inputs.land_fees_total
        upfront_fees = (inputs.arranger_fee_pct + inputs.legal_fee_pct + inputs.rating_fee_pct) * project_capex
        funding_need = project_capex + upfront_fees

        # Rule-derived bounds
        tenor_cap = inputs.lease_years - 2  # 2-year buffer

        # DSCR floors by rating
        dscr_floors = {
            TenantRating.AAA: 1.45,
            TenantRating.AA: 1.35,
            TenantRating.A: 1.25,
            TenantRating.BBB: 1.15,
            TenantRating.NR: 1.25
        }
        dscr_floor = dscr_floors.get(inputs.tenant_rating, 1.25)

        # DSRA months by rating
        dsra_map = {
            TenantRating.AAA: 6,
            TenantRating.AA: 6,
            TenantRating.A: 3,
            TenantRating.BBB: 3,
            TenantRating.NR: 3
        }
        dsra_months = dsra_map.get(inputs.tenant_rating, 3)

        # AF bands by rating
        af_bands = {
            TenantRating.AAA: (0.65, 0.80),
            TenantRating.AA: (0.60, 0.75),
            TenantRating.A: (0.55, 0.70),
            TenantRating.BBB: (0.50, 0.65),
            TenantRating.NR: (0.45, 0.60)
        }
        af_min, af_max = af_bands.get(inputs.tenant_rating, (0.50, 0.70))

        # Repo eligibility check
        repo_eligible = inputs.currency in [Currency.EUR, Currency.GBP, Currency.USD]
        repo_reason = "Eligible" if repo_eligible else f"Currency {inputs.currency} not repo-eligible"

        return cls(
            net_it_load_mw=net_it_load_mw,
            gross_income_m=gross_income_m,
            opex_m=opex_m,
            noi_m=noi_m,
            project_capex=project_capex,
            upfront_fees=upfront_fees,
            funding_need=funding_need,
            tenor_cap=tenor_cap,
            dscr_floor_by_rating=dscr_floor,
            dsra_months=dsra_months,
            af_min=af_min,
            af_max=af_max,
            repo_eligible_flag=repo_eligible,
            repo_reason=repo_reason
        )

# ==================== PERMUTATION RANGES ====================

@dataclass
class Range:
    """Generic range definition"""
    min_val: float
    max_val: float
    step: float

    def to_list(self) -> List[float]:
        """Convert range to list of values"""
        values = []
        current = self.min_val
        while current <= self.max_val:
            values.append(round(current, 4))
            current += self.step
        return values

@dataclass
class PermutationRanges:
    """All permutation ranges for the engine"""

    # Senior debt
    senior_dscr_floor: Union[float, Range, List[float]]
    senior_coupon: Union[float, Range, List[float]]
    senior_tenor: List[int]
    senior_amort: List[AmortType]
    wrap: bool
    senior_callable: bool = False

    # Mezzanine (optional)
    mezz_on: bool = False
    mezz_dscr_floor: Optional[Union[float, Range, List[float]]] = None
    mezz_coupon: Optional[Union[float, Range, List[float]]] = None
    mezz_tenor: Optional[List[int]] = None
    mezz_amort: Optional[List[AmortType]] = None
    mezz_pik: bool = False
    icc_ruleset: ICCRuleset = ICCRuleset.STANDARD

    # Equity & TRS
    equity_trs_pct: Union[float, Range, List[float]] = field(default_factory=lambda: Range(0.10, 0.15, 0.05))
    equity_irr_band: List[tuple] = field(default_factory=lambda: [(0.10, 0.12), (0.12, 0.15)])

    # Indexation
    indexation_basis: IndexationBasis = IndexationBasis.CPI_CAPPED
    cpi_floor: float = 0.01
    cpi_cap: float = 0.04
    flatten_core: bool = True

    # Sidecar
    zcis: bool = True
    zcis_tenor: int = 5
    rate_floor_sale: bool = True
    residual_strip: bool = False
    sidecar_haircut_pct: Union[float, Range, List[float]] = field(default_factory=lambda: Range(0.05, 0.25, 0.05))

    # Fees & Reserves
    arranger_fee_pct: float = 0.0125
    legal_fee_pct: float = 0.0025
    rating_fee_pct: float = 0.0015
    admin_bps: float = 15
    liq_reserve_pct: float = 0.25
    dsra_months: int = 3

# ==================== PRESET BUNDLES ====================

class PresetBundles:
    """One-click preset configurations"""

    @staticmethod
    def repo_first_aaa_aa() -> PermutationRanges:
        """AAA/AA Repo-First configuration"""
        return PermutationRanges(
            senior_dscr_floor=Range(1.40, 1.50, 0.05),
            senior_coupon=Range(3.0, 5.0, 0.25),
            senior_tenor=[7, 10, 12, 15],
            senior_amort=[AmortType.ANNUITY, AmortType.LEVEL],
            wrap=True,
            equity_trs_pct=Range(0.05, 0.10, 0.05),
            zcis=True,
            zcis_tenor=10,
            rate_floor_sale=True,
            dsra_months=6
        )

    @staticmethod
    def balanced_a() -> PermutationRanges:
        """A-rated Balanced configuration"""
        return PermutationRanges(
            senior_dscr_floor=Range(1.25, 1.35, 0.05),
            senior_coupon=Range(4.0, 6.0, 0.25),
            senior_tenor=[10, 12, 15, 20],
            senior_amort=[AmortType.LEVEL, AmortType.SCULPTED],
            wrap=False,
            equity_trs_pct=Range(0.10, 0.15, 0.05),
            zcis=True,
            zcis_tenor=5,
            rate_floor_sale=False,
            dsra_months=3
        )

    @staticmethod
    def value_max_bbb() -> PermutationRanges:
        """BBB Value-Max configuration"""
        return PermutationRanges(
            senior_dscr_floor=Range(1.15, 1.25, 0.05),
            senior_coupon=Range(5.0, 7.0, 0.25),
            senior_tenor=[10, 12, 15],
            senior_amort=[AmortType.SCULPTED, AmortType.BULLET],
            wrap=False,
            mezz_on=True,
            mezz_dscr_floor=Range(1.05, 1.15, 0.05),
            mezz_coupon=Range(7.0, 12.0, 0.5),
            mezz_tenor=[7, 10],
            equity_trs_pct=Range(0.15, 0.25, 0.05),
            zcis=False,
            rate_floor_sale=True,
            dsra_months=3
        )

# ==================== VALIDATION GATES ====================

class ValidationGates:
    """Gate A/B validation logic"""

    @staticmethod
    def gate_a_feasibility(
        structure: Dict[str, Any],
        derived: DerivedFields
    ) -> tuple[bool, str, bool]:
        """
        Gate A - Feasibility check
        Returns: (pass, reason, is_near_miss)
        """

        # Capital coverage check
        total_debt = structure.get('senior_amount', 0) + structure.get('mezz_amount', 0)
        coverage = total_debt / derived.funding_need

        if coverage < 0.85:
            return False, f"Capital coverage {coverage:.1%} < 85%", False
        elif coverage < 1.0:
            # Near-miss: 85-100% coverage
            fix_hint = f"Increase senior spread by {int((1.0 - coverage) * 100)}bps"
            return True, f"Near-miss: {coverage:.1%} coverage ({fix_hint})", True

        # Tenor check
        if structure['senior_tenor'] > derived.tenor_cap:
            return False, f"Tenor {structure['senior_tenor']}y > cap {derived.tenor_cap}y", False

        # AF check
        af = structure.get('advance_factor', 0)
        if not (derived.af_min <= af <= derived.af_max):
            return False, f"AF {af:.2%} outside band {derived.af_min:.0%}-{derived.af_max:.0%}", False

        return True, "Gate A passed", False

    @staticmethod
    def gate_b_credit(
        structure: Dict[str, Any],
        derived: DerivedFields
    ) -> tuple[bool, str]:
        """
        Gate B - Credit quality check
        Returns: (pass, reason)
        """

        # DSCR check
        senior_dscr = structure.get('min_dscr_senior', 0)
        if senior_dscr < derived.dscr_floor_by_rating:
            return False, f"Senior DSCR {senior_dscr:.2f} < floor {derived.dscr_floor_by_rating:.2f}"

        # CPI stress check
        cpi_stress_dscr = structure.get('cpi_0_stress_dscr', 0)
        if cpi_stress_dscr < 1.0:
            return False, f"CPI 0% stress DSCR {cpi_stress_dscr:.2f} < 1.00"

        # WAL check (simplified)
        wal = structure.get('wal_years', 0)
        max_wal = derived.tenor_cap * 0.75
        if wal > max_wal:
            return False, f"WAL {wal:.1f}y > max {max_wal:.1f}y"

        # DSRA check
        dsra = structure.get('dsra_months', 0)
        if dsra < derived.dsra_months:
            return False, f"DSRA {dsra}m < required {derived.dsra_months}m"

        return True, "Gate B passed"

# ==================== RESULT STRUCTURE ====================

@dataclass
class PermutationResult:
    """Single permutation result"""

    # Identification
    permutation_id: str
    seed: int
    chunk_id: str

    # Structure details
    senior_dscr: float
    senior_coupon: float
    senior_tenor: int
    senior_amount: float

    # Valuation
    day_one_value_core: float
    day_one_value_sidecar: float
    tier: ViabilityTier

    # Metrics
    min_dscr_senior: float
    wal_years: float
    advance_factor: float

    # Validation
    gate_a_pass: bool
    gate_b_pass: bool
    repo_eligible: bool
    repo_reason: str

    # Stress results
    cpi_0_dscr: float
    cpi_18_dscr: float
    cpi_25_dscr: float

    # Optional mezz fields
    mezz_dscr: Optional[float] = None
    mezz_coupon: Optional[float] = None
    mezz_amount: Optional[float] = None
    min_dscr_mezz: Optional[float] = None

    # Optional fields
    near_miss: bool = False
    near_miss_reason: Optional[str] = None

# ==================== EXPORT ====================

def export_top_structures(
    results: List[PermutationResult],
    top_n: int = 20
) -> List[Dict[str, Any]]:
    """Export top N structures for display"""

    # Filter viable and sort by day-one value
    viable = [r for r in results if r.tier != ViabilityTier.NOT_VIABLE]
    sorted_results = sorted(viable, key=lambda x: x.day_one_value_core + x.day_one_value_sidecar, reverse=True)

    top_structures = []
    for i, result in enumerate(sorted_results[:top_n]):
        top_structures.append({
            'rank': i + 1,
            'tier': result.tier.value,
            'day_one_value_core': f"£{result.day_one_value_core:,.0f}",
            'day_one_value_total': f"£{result.day_one_value_core + result.day_one_value_sidecar:,.0f}",
            'min_dscr_senior': result.min_dscr_senior,
            'min_dscr_mezz': result.min_dscr_mezz,
            'wal': result.wal_years,
            'repo_eligible': 'Y' if result.repo_eligible else 'N'
        })

    return top_structures