"""
Phase-1 Data Model v2: Production-Ready with Full Integration
Tightened validation, source tracking, and UI integration
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Literal, Union, Tuple
from datetime import datetime
from enum import Enum
import hashlib
import json

# ==================== CONSTANTS ====================

HOURS_PER_MONTH = 730  # Standard assumption for kWh calculations
CURRENCY_PRECISION = 2  # Display precision for currency
CALC_PRECISION = 6  # Internal calculation precision
MAX_PERMUTATIONS_WARNING = 250_000
DEFAULT_RULESET = "v1.0"

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

class InputSource(str, Enum):
    MANUAL = "manual"
    MIN_MAX = "minmax"
    VARIATIONS = "variations"
    DEFAULT = "default"

# ==================== PROJECT INPUTS ====================

@dataclass
class ProjectInputs:
    """Fixed facts captured at project level with validation"""

    # Required fields (no defaults)
    title: str
    country: str
    currency: Currency
    gross_it_load_mw: float
    pue: float
    lease_years: int
    tenant_rating: TenantRating
    opex_pct: float
    capex_cost_per_mw: float
    land_fees_total: float

    # Optional revenue (one required for validation)
    gross_monthly_rent: Optional[float] = None
    rent_per_kwh_month: Optional[float] = None
    capex_market_per_mw: Optional[float] = None

    # Defaults
    ruleset_version: str = DEFAULT_RULESET
    indexation_basis: IndexationBasis = IndexationBasis.FLAT
    arranger_fee_pct: float = 0.0125
    legal_fee_pct: float = 0.0025
    rating_fee_pct: float = 0.0015
    admin_bps: float = 15
    wrap: bool = False
    wrap_premium_bps: Optional[float] = None
    repo_target: bool = False
    construction_start: Optional[datetime] = None
    construction_months: int = 24
    base_cpi: float = 0.02

    def validate(self) -> Tuple[bool, List[str]]:
        """Comprehensive validation with error collection"""
        errors = []

        # PUE validation
        if not (0.95 <= self.pue <= 1.50):
            errors.append(f"PUE {self.pue} must be between 0.95 and 1.50")

        # OPEX validation
        if not (0 <= self.opex_pct <= 1):
            errors.append(f"OPEX % {self.opex_pct} must be between 0 and 100%")

        # Lease validation
        if self.lease_years < 5:
            errors.append(f"Lease term {self.lease_years} must be >= 5 years")

        # Revenue validation
        if self.gross_monthly_rent is None and self.rent_per_kwh_month is None:
            errors.append("Either gross_monthly_rent or rent_per_kwh_month required")

        if self.gross_monthly_rent is not None and self.rent_per_kwh_month is not None:
            errors.append("Only one of gross_monthly_rent or rent_per_kwh_month should be provided")

        # Currency/country validation
        valid_combos = {
            ("UK", Currency.GBP),
            ("US", Currency.USD),
            ("EU", Currency.EUR),
            ("JP", Currency.JPY)
        }
        if (self.country, self.currency) not in valid_combos:
            errors.append(f"Invalid country/currency combo: {self.country}/{self.currency.value}")

        # Wrap validation
        if self.wrap and self.wrap_premium_bps is None:
            errors.append("Wrap premium BPS required when wrap=True")

        return len(errors) == 0, errors

# ==================== DERIVED FIELDS ====================

@dataclass
class DerivedFields:
    """Auto-computed fields with source tracking"""

    # Core calculations
    net_it_load_mw: float
    gross_income_m: float
    gross_income_source: InputSource
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

    # Metadata
    computed_at: datetime = field(default_factory=datetime.utcnow)
    ruleset_version: str = DEFAULT_RULESET

    @classmethod
    def compute_from_inputs(cls, inputs: ProjectInputs) -> 'DerivedFields':
        """Compute all derived fields with source tracking"""

        # Net IT Load
        net_it_load_mw = round(inputs.gross_it_load_mw / inputs.pue, 2)

        # Monthly income with source tracking
        if inputs.gross_monthly_rent is not None:
            gross_income_m = inputs.gross_monthly_rent
            income_source = InputSource.MANUAL
        elif inputs.rent_per_kwh_month is not None:
            gross_income_m = net_it_load_mw * 1000 * HOURS_PER_MONTH * inputs.rent_per_kwh_month
            income_source = InputSource.VARIATIONS
        else:
            gross_income_m = 0
            income_source = InputSource.DEFAULT

        # OPEX and NOI
        opex_m = round(gross_income_m * inputs.opex_pct, CURRENCY_PRECISION)
        noi_m = round(gross_income_m - opex_m, CURRENCY_PRECISION)

        # Capex and fees
        project_capex = inputs.capex_cost_per_mw * inputs.gross_it_load_mw + inputs.land_fees_total
        upfront_fees = (inputs.arranger_fee_pct + inputs.legal_fee_pct + inputs.rating_fee_pct) * project_capex
        funding_need = project_capex + upfront_fees

        # Tenor cap with buffer
        tenor_cap = inputs.lease_years - 2

        # Rating-based parameters
        rating_params = {
            TenantRating.AAA: {"dscr": 1.45, "dsra": 6, "af": (0.65, 0.80)},
            TenantRating.AA: {"dscr": 1.35, "dsra": 6, "af": (0.60, 0.75)},
            TenantRating.A: {"dscr": 1.25, "dsra": 3, "af": (0.55, 0.70)},
            TenantRating.BBB: {"dscr": 1.15, "dsra": 3, "af": (0.50, 0.65)},
            TenantRating.NR: {"dscr": 1.25, "dsra": 3, "af": (0.45, 0.60)}
        }
        params = rating_params.get(inputs.tenant_rating, rating_params[TenantRating.NR])

        # Repo eligibility
        repo_eligible = (
            inputs.currency in [Currency.EUR, Currency.GBP, Currency.USD] and
            inputs.country in ["UK", "US", "EU"]
        )
        repo_reason = "Eligible" if repo_eligible else f"Currency/Jurisdiction not repo-eligible"

        return cls(
            net_it_load_mw=net_it_load_mw,
            gross_income_m=gross_income_m,
            gross_income_source=income_source,
            opex_m=opex_m,
            noi_m=noi_m,
            project_capex=project_capex,
            upfront_fees=upfront_fees,
            funding_need=funding_need,
            tenor_cap=tenor_cap,
            dscr_floor_by_rating=params["dscr"],
            dsra_months=params["dsra"],
            af_min=params["af"][0],
            af_max=params["af"][1],
            repo_eligible_flag=repo_eligible,
            repo_reason=repo_reason,
            ruleset_version=inputs.ruleset_version
        )

# ==================== RANGE WITH SOURCE ====================

@dataclass
class RangeWithSource:
    """Range definition with source tracking"""
    min_val: float
    max_val: float
    step: float
    source: InputSource = InputSource.DEFAULT

    def to_list(self) -> List[float]:
        """Convert to list of values"""
        values = []
        current = self.min_val
        while current <= self.max_val:
            values.append(round(current, CALC_PRECISION))
            current += self.step
        return values

    def cardinality(self) -> int:
        """Number of values in range"""
        return len(self.to_list())

# ==================== PERMUTATION RANGES ====================

@dataclass
class PermutationRanges:
    """All ranges with source tracking and cardinality calculation"""

    # Senior debt
    senior_dscr_floor: Union[float, RangeWithSource, List[float]]
    senior_coupon: Union[float, RangeWithSource, List[float]]
    senior_tenor: List[int]
    senior_amort: List[AmortType]
    wrap: bool
    senior_callable: bool = False

    # Mezzanine
    mezz_on: bool = False
    mezz_dscr_floor: Optional[Union[float, RangeWithSource, List[float]]] = None
    mezz_coupon: Optional[Union[float, RangeWithSource, List[float]]] = None
    mezz_tenor: Optional[List[int]] = None
    mezz_amort: Optional[List[AmortType]] = None
    mezz_pik: bool = False
    icc_ruleset: ICCRuleset = ICCRuleset.STANDARD

    # Equity & TRS
    equity_trs_pct: Union[float, RangeWithSource, List[float]] = field(
        default_factory=lambda: RangeWithSource(0.10, 0.15, 0.05, InputSource.DEFAULT)
    )
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
    sidecar_haircut_pct: Union[float, RangeWithSource, List[float]] = field(
        default_factory=lambda: RangeWithSource(0.05, 0.25, 0.05, InputSource.DEFAULT)
    )

    # Fees & Reserves
    arranger_fee_pct: float = 0.0125
    legal_fee_pct: float = 0.0025
    rating_fee_pct: float = 0.0015
    admin_bps: float = 15
    liq_reserve_pct: float = 0.25
    dsra_months: int = 3

    # Metadata
    seed: int = 424242
    chunk_size: int = 800

    def calculate_cardinality(self, tenor_cap: Optional[int] = None) -> Dict[str, Any]:
        """Calculate expected permutations with clipping"""

        # Helper to get cardinality
        def get_card(field):
            if isinstance(field, RangeWithSource):
                return field.cardinality()
            elif isinstance(field, list):
                return len(field)
            else:
                return 1

        # Senior cardinality
        senior_card = (
            get_card(self.senior_dscr_floor) *
            get_card(self.senior_coupon) *
            get_card([t for t in self.senior_tenor if t <= (tenor_cap or 100)]) *
            get_card(self.senior_amort)
        )

        # Mezz cardinality (if enabled)
        mezz_card = 1
        if self.mezz_on:
            mezz_card = (
                get_card(self.mezz_dscr_floor or 1) *
                get_card(self.mezz_coupon or 1) *
                get_card(self.mezz_tenor or 1) *
                get_card(self.mezz_amort or 1)
            )

        # Other cardinalities
        equity_card = get_card(self.equity_trs_pct) * get_card(self.equity_irr_band)
        sidecar_card = get_card(self.sidecar_haircut_pct) if self.zcis or self.rate_floor_sale else 1

        total = senior_card * mezz_card * equity_card * sidecar_card

        return {
            "total": total,
            "senior": senior_card,
            "mezz": mezz_card if self.mezz_on else 0,
            "equity": equity_card,
            "sidecar": sidecar_card,
            "warning": total > MAX_PERMUTATIONS_WARNING,
            "chunks_needed": (total + self.chunk_size - 1) // self.chunk_size
        }

    def get_range_signature(self) -> str:
        """Generate hash of range configuration for determinism"""
        config = {
            "senior": str(self.senior_dscr_floor) + str(self.senior_coupon) + str(self.senior_tenor),
            "mezz": str(self.mezz_on) + str(self.mezz_dscr_floor) + str(self.mezz_coupon),
            "equity": str(self.equity_trs_pct) + str(self.equity_irr_band),
            "seed": self.seed
        }
        return hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]

# ==================== VALIDATION GATES ====================

class ValidationGates:
    """Enhanced gate validation with near-miss detection"""

    @staticmethod
    def gate_a_feasibility(
        structure: Dict[str, Any],
        derived: DerivedFields
    ) -> Dict[str, Any]:
        """Gate A with enhanced near-miss detection"""

        result = {
            "pass": False,
            "reason": "",
            "near_miss": False,
            "fix_hints": []
        }

        # Capital coverage
        total_debt = structure.get('senior_amount', 0) + structure.get('mezz_amount', 0)
        coverage = total_debt / derived.funding_need if derived.funding_need > 0 else 0

        if coverage < 0.85:
            result["reason"] = f"Capital coverage {coverage:.1%} < 85%"
            return result

        if coverage < 1.0:
            # Near-miss
            gap_bps = int((1.0 - coverage) * 10000)
            result["near_miss"] = True
            result["fix_hints"] = [
                f"Increase senior spread by {gap_bps}bps",
                f"Add mezz tranche 5-10%",
                "Extend tenor by 2 years"
            ]

        # Tenor check
        if structure['senior_tenor'] > derived.tenor_cap:
            result["reason"] = f"Tenor {structure['senior_tenor']}y > cap {derived.tenor_cap}y"
            return result

        # AF check with pre-pruning
        af = structure.get('advance_factor', 0)
        if not (derived.af_min <= af <= derived.af_max):
            result["reason"] = f"AF {af:.2%} outside band {derived.af_min:.0%}-{derived.af_max:.0%}"
            return result

        result["pass"] = True
        result["reason"] = "Gate A passed" if not result["near_miss"] else "Gate A near-miss"
        return result

    @staticmethod
    def gate_b_credit(
        structure: Dict[str, Any],
        derived: DerivedFields
    ) -> Dict[str, Any]:
        """Gate B credit quality validation"""

        result = {
            "pass": False,
            "reason": "",
            "failures": []
        }

        # DSCR check
        senior_dscr = structure.get('min_dscr_senior', 0)
        if senior_dscr < derived.dscr_floor_by_rating:
            result["failures"].append(f"MIN_DSCR_SENIOR")
            result["reason"] = f"Senior DSCR {senior_dscr:.2f} < floor {derived.dscr_floor_by_rating:.2f}"
            return result

        # CPI stress
        cpi_stress_dscr = structure.get('cpi_0_stress_dscr', 0)
        if cpi_stress_dscr < 1.0:
            result["failures"].append(f"CPI_STRESS")
            result["reason"] = f"CPI 0% stress DSCR {cpi_stress_dscr:.2f} < 1.00"
            return result

        # WAL check
        wal = structure.get('wal_years', 0)
        max_wal = derived.tenor_cap * 0.75
        if wal > max_wal:
            result["failures"].append(f"MAX_WAL")
            result["reason"] = f"WAL {wal:.1f}y > max {max_wal:.1f}y"
            return result

        # DSRA check
        dsra = structure.get('dsra_months', 0)
        if dsra < derived.dsra_months:
            result["failures"].append(f"MIN_DSRA")
            result["reason"] = f"DSRA {dsra}m < required {derived.dsra_months}m"
            return result

        result["pass"] = True
        result["reason"] = "Gate B passed"
        return result

# ==================== PERMUTATION RESULT ====================

@dataclass
class PermutationResult:
    """Enhanced result with full audit trail"""

    # Identification
    permutation_id: str
    seed: int
    chunk_id: str
    ruleset_version: str
    range_signature: str

    # Structure
    senior_dscr: float
    senior_coupon: float
    senior_tenor: int
    senior_amount: float
    senior_source: InputSource

    # Valuation
    day_one_value_core: float
    gross_sidecar_value: float
    sidecar_haircut_pct: float
    net_sidecar_value: float
    tier: ViabilityTier

    # Metrics
    min_dscr_senior: float
    wal_years: float
    advance_factor: float

    # Validation
    gate_a_pass: bool
    gate_a_reason: str
    gate_b_pass: bool
    gate_b_reason: str
    repo_eligible: bool
    repo_reason: str

    # Stress
    cpi_0_dscr: float
    cpi_18_dscr: float
    cpi_25_dscr: float

    # Optional mezz
    mezz_dscr: Optional[float] = None
    mezz_coupon: Optional[float] = None
    mezz_amount: Optional[float] = None
    min_dscr_mezz: Optional[float] = None

    # Optional flags
    wrap_applied: bool = False
    wrap_premium_bps: Optional[float] = None
    near_miss: bool = False
    near_miss_hints: List[str] = field(default_factory=list)

    @property
    def total_day_one_value(self) -> float:
        """Total day-one value (core + net sidecar)"""
        return self.day_one_value_core + self.net_sidecar_value

# ==================== PRESET BUNDLES ====================

class PresetBundles:
    """Enhanced presets with source tracking"""

    @staticmethod
    def repo_first_aaa_aa() -> PermutationRanges:
        """AAA/AA Repo-First configuration"""
        return PermutationRanges(
            senior_dscr_floor=RangeWithSource(1.40, 1.50, 0.05, InputSource.MIN_MAX),
            senior_coupon=RangeWithSource(0.03, 0.05, 0.0025, InputSource.MIN_MAX),
            senior_tenor=[7, 10, 12, 15],
            senior_amort=[AmortType.ANNUITY, AmortType.LEVEL],
            wrap=True,
            equity_trs_pct=RangeWithSource(0.05, 0.10, 0.05, InputSource.MIN_MAX),
            zcis=True,
            zcis_tenor=10,
            rate_floor_sale=True,
            dsra_months=6
        )

    @staticmethod
    def balanced_a() -> PermutationRanges:
        """A-rated Balanced configuration"""
        return PermutationRanges(
            senior_dscr_floor=RangeWithSource(1.25, 1.35, 0.05, InputSource.MIN_MAX),
            senior_coupon=RangeWithSource(0.04, 0.06, 0.0025, InputSource.MIN_MAX),
            senior_tenor=[10, 12, 15, 20],
            senior_amort=[AmortType.LEVEL, AmortType.SCULPTED],
            wrap=False,
            equity_trs_pct=RangeWithSource(0.10, 0.15, 0.05, InputSource.MIN_MAX),
            zcis=True,
            zcis_tenor=5,
            rate_floor_sale=False,
            dsra_months=3
        )

    @staticmethod
    def value_max_bbb() -> PermutationRanges:
        """BBB Value-Max configuration"""
        return PermutationRanges(
            senior_dscr_floor=RangeWithSource(1.15, 1.25, 0.05, InputSource.MIN_MAX),
            senior_coupon=RangeWithSource(0.05, 0.07, 0.0025, InputSource.MIN_MAX),
            senior_tenor=[10, 12, 15],
            senior_amort=[AmortType.SCULPTED, AmortType.BULLET],
            wrap=False,
            mezz_on=True,
            mezz_dscr_floor=RangeWithSource(1.05, 1.15, 0.05, InputSource.MIN_MAX),
            mezz_coupon=RangeWithSource(0.07, 0.12, 0.005, InputSource.MIN_MAX),
            mezz_tenor=[7, 10],
            equity_trs_pct=RangeWithSource(0.15, 0.25, 0.05, InputSource.MIN_MAX),
            zcis=False,
            rate_floor_sale=True,
            dsra_months=3
        )

# ==================== EXPORTS ====================

def export_top_structures(
    results: List[PermutationResult],
    top_n: int = 20
) -> List[Dict[str, Any]]:
    """Export top structures with full details"""

    viable = [r for r in results if r.tier != ViabilityTier.NOT_VIABLE]
    sorted_results = sorted(viable, key=lambda x: x.total_day_one_value, reverse=True)

    top_structures = []
    for i, result in enumerate(sorted_results[:top_n]):
        top_structures.append({
            'rank': i + 1,
            'tier': result.tier.value,
            'day_one_value_core': round(result.day_one_value_core, CURRENCY_PRECISION),
            'day_one_value_sidecar': round(result.net_sidecar_value, CURRENCY_PRECISION),
            'day_one_value_total': round(result.total_day_one_value, CURRENCY_PRECISION),
            'min_dscr_senior': result.min_dscr_senior,
            'min_dscr_mezz': result.min_dscr_mezz,
            'wal': result.wal_years,
            'repo_eligible': 'Y' if result.repo_eligible else 'N',
            'near_miss': 'Y' if result.near_miss else 'N',
            'ruleset_version': result.ruleset_version,
            'seed': result.seed
        })

    return top_structures

# ==================== UI INTEGRATION ====================

class Phase1Integration:
    """Helper class for UI integration"""

    @staticmethod
    def get_derived_preview(inputs: ProjectInputs) -> Dict[str, Any]:
        """Generate derived preview for Projects page"""
        derived = DerivedFields.compute_from_inputs(inputs)
        return {
            "gross_income_m": f"GBP {derived.gross_income_m:,.2f}",
            "income_source": derived.gross_income_source.value,
            "opex_m": f"GBP {derived.opex_m:,.2f}",
            "noi_m": f"GBP {derived.noi_m:,.2f}",
            "project_capex": f"GBP {derived.project_capex:,.0f}",
            "upfront_fees": f"GBP {derived.upfront_fees:,.0f}",
            "funding_need": f"GBP {derived.funding_need:,.0f}",
            "tenor_cap": f"{derived.tenor_cap} years",
            "dscr_floor": f"{derived.dscr_floor_by_rating:.2f}x",
            "dsra_months": f"{derived.dsra_months} months",
            "af_band": f"{derived.af_min:.0%}-{derived.af_max:.0%}",
            "repo_eligible": "Yes" if derived.repo_eligible_flag else "No",
            "repo_reason": derived.repo_reason
        }

    @staticmethod
    def get_cardinality_preview(ranges: PermutationRanges, tenor_cap: int) -> Dict[str, Any]:
        """Generate cardinality preview for Permutations page"""
        card = ranges.calculate_cardinality(tenor_cap)

        # Gate A prune estimate
        prune_estimate = 0.15  # Base 15% prune rate
        if ranges.wrap:
            prune_estimate -= 0.05  # Wrap reduces pruning
        if ranges.mezz_on:
            prune_estimate -= 0.03  # Mezz reduces pruning

        expected_after_prune = int(card["total"] * (1 - prune_estimate))

        return {
            "expected_permutations": card["total"],
            "expected_after_prune": expected_after_prune,
            "prune_estimate_pct": f"{prune_estimate:.0%}",
            "chunks_needed": card["chunks_needed"],
            "warning": card["warning"],
            "warning_message": f"High permutation count ({card['total']:,}). Consider narrowing ranges." if card["warning"] else None,
            "breakdown": {
                "senior": card["senior"],
                "mezz": card["mezz"],
                "equity": card["equity"],
                "sidecar": card["sidecar"]
            },
            "range_signature": ranges.get_range_signature()
        }