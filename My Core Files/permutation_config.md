config_version: 1.0.0
name: Atlas Forge — Permutation Engine Lever Map
timezone: Europe/London

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL RESOLUTION & RANGING RULES
# ──────────────────────────────────────────────────────────────────────────────
resolution_rules:
  precedence: # how each field’s value is resolved at runtime
    - use manual if provided
    - else if min_max is provided, enumerate [min, max] inclusive using step (range.enabled=true)
    - else if variations/list provided, enumerate those values (deduplicated, rounded per 'precision')
    - else use default
  precision:
    # numeric rounding applied AFTER resolution to keep grids tidy
    percentage: 2
    rate_pct: 2
    dscr: 2
    currency: 0
    bps: 0
    years: 0
    months: 0
  range:
    # engine-level defaults (overridable per field)
    enabled: false
    step_defaults:
      percentage: 0.5
      rate_pct: 0.25 # 25 bps
      dscr: 0.05
      currency: 100000 # £100k
      bps: 25
      years: 1
      months: 1
  guards:
    # hard runtime sanity checks; permutations violating these are dropped
    dscr_min_absolute: 1.00
    lease_term_max_years: 40
    zcis_terms_allowed: [5, 10]

engine_execution_order:
  - ingest_fixed_inputs          # 01–08
  - compute_derived              # 09–16
  - apply_mode_toggles           # 17–26
  - load_market_state            # 27–36
  - size_and_price_senior        # 37–44
  - add_mezzanine                # 45–51
  - add_equity_trs               # 52–56
  - apply_wrap_liquidity         # 57–62
  - shape_cashflows              # 63–74
  - apply_rating_eligibility     # 75–81
  - run_stresses_haircuts        # 82–90
  - apply_derivatives_sidecar    # 91–98
  - build_waterfall_triggers     # 99–106
  - rank_filter_export           # 107–116

# ──────────────────────────────────────────────────────────────────────────────
# FIELD SCHEMA LEGEND (applies to every entry below)
# id: Label_Number
# type: number|string|enum|boolean
# unit: %, x, years, months, bps, £, £/MW, MW, rate, enum
# mode: manual|min_max|range|list|default   (runtime: may be switched)
# manual: (optional) single user value
# min_max: {min, max, step}  (used when mode = min_max or range.enabled=true)
# range: {enabled, min, max, step} (explicit range toggle)
# list/variations: [values...] (used when mode = list)
# default: fallback value
# formula: expression (for derived fields)
# depends_on: [ids used in formula or validation]
# validate: {min, max, allowed, regex}
# comment: free text
# ──────────────────────────────────────────────────────────────────────────────

fields:

  # ───────── 1) PROJECT FIXED INPUTS (CLIENT UPLOADS) ─────────
  Currency_01:
    id: Currency_01
    type: enum
    unit: enum
    allowed: [GBP, EUR, USD, JPY, AED]
    mode: default
    default: GBP
    comment: Drives FX, locale, formatting.

  GrossITLoad_02:
    id: GrossITLoad_02
    type: number
    unit: MW
    validate: {min: 1, max: 3000}
    mode: manual
    manual:
    min_max: {min: 10, max: 1000, step: 10}
    range: {enabled: false}
    default: 100

  PUE_03:
    id: PUE_03
    type: number
    unit: x
    validate: {min: 1.05, max: 1.8}
    mode: manual
    manual:
    min_max: {min: 1.15, max: 1.5, step: 0.05}
    range: {enabled: false}
    default: 1.30

  CapexCostPrice_04:
    id: CapexCostPrice_04
    type: number
    unit: "£/MW"
    validate: {min: 2000000, max: 20000000}
    mode: manual
    min_max: {min: 5000000, max: 12000000, step: 250000}
    range: {enabled: false}
    default: 7500000

  CapexMarketRate_05:
    id: CapexMarketRate_05
    type: number
    unit: "£/MW"
    validate: {min: 3000000, max: 25000000}
    mode: manual
    min_max: {min: 6000000, max: 14000000, step: 250000}
    range: {enabled: false}
    default: 9000000

  LandPurchaseFees_06:
    id: LandPurchaseFees_06
    type: number
    unit: "£"
    validate: {min: 0, max: 500000000}
    mode: manual
    min_max: {min: 0, max: 200000000, step: 1000000}
    range: {enabled: false}
    default: 20000000

  GrossMonthlyRent_07:
    id: GrossMonthlyRent_07
    type: number
    unit: "£/month"
    validate: {min: 100000, max: 200000000}
    mode: manual
    min_max: {min: 500000, max: 100000000, step: 100000}
    range: {enabled: true, min: 500000, max: 5000000, step: 50000}
    default: 2500000
    comment: May be ranged for commercial scenarios.

  OPEX_08:
    id: OPEX_08
    type: number
    unit: "%" # or £ depending on OPEXMode_17
    validate: {min: 0, max: 80}
    mode: manual
    min_max: {min: 10, max: 45, step: 1}
    range: {enabled: true, min: 15, max: 35, step: 1}
    default: 25
    comment: If OPEXMode_17 = Absolute£, interpret as currency not %.

  # ───────── 3) PRE-CALCULATED / DERIVED ─────────
  NetITLoad_09:
    id: NetITLoad_09
    type: number
    unit: MW
    formula: "GrossITLoad_02 / PUE_03"
    depends_on: [GrossITLoad_02, PUE_03]
    validate: {min: 1, max: 3000}

  GrossIncome_10:
    id: GrossIncome_10
    type: number
    unit: "£/year"
    formula: "GrossMonthlyRent_07 * 12"
    depends_on: [GrossMonthlyRent_07]

  NetIncome_11:
    id: NetIncome_11
    type: number
    unit: "£/year"
    formula: |
      "if OPEXMode_17 == 'PercentOfRevenue'
         then GrossIncome_10 * (1 - OPEX_08/100)
       else GrossIncome_10 - OPEX_08"
    depends_on: [GrossIncome_10, OPEX_08, OPEXMode_17]

  DeveloperProfit_12:
    id: DeveloperProfit_12
    type: number
    unit: "£"
    mode: manual
    default: 0
    comment: Optional override; else computed in model inputs tab.

  DeveloperMargin_13:
    id: DeveloperMargin_13
    type: number
    unit: "%"
    formula: "100 * DeveloperProfit_12 / max(TotalProjectMarketCosts_15,1)"
    depends_on: [DeveloperProfit_12, TotalProjectMarketCosts_15]
    validate: {min: 0, max: 80}

  TotalStructuringFees_14:
    id: TotalStructuringFees_14
    type: number
    unit: "£"
    mode: manual
    default: 0

  TotalProjectMarketCosts_15:
    id: TotalProjectMarketCosts_15
    type: number
    unit: "£"
    formula: "(CapexMarketRate_05 * GrossITLoad_02) + LandPurchaseFees_06"
    depends_on: [CapexMarketRate_05, GrossITLoad_02, LandPurchaseFees_06]

  TotalProjectInternalCosts_16:
    id: TotalProjectInternalCosts_16
    type: number
    unit: "£"
    formula: "(CapexCostPrice_04 * GrossITLoad_02) + LandPurchaseFees_06"
    depends_on: [CapexCostPrice_04, GrossITLoad_02, LandPurchaseFees_06]

  # ───────── 4) ACCOUNTING / MODE TOGGLES ─────────
  OPEXMode_17:
    id: OPEXMode_17
    type: enum
    allowed: [PercentOfRevenue, Absolute£]
    default: PercentOfRevenue

  IndexationMode_18:
    id: IndexationMode_18
    type: enum
    allowed: [Flat, CPI_Linked, Partial]
    default: Flat

  IndexationBase_19:
    id: IndexationBase_19
    type: enum
    allowed: [HeadlineCPI, CoreCPI, FixedEscalator]
    default: HeadlineCPI

  RevenueBasis_20:
    id: RevenueBasis_20
    type: enum
    allowed: [Contracted, Underwritten, Conservative]
    default: Contracted

  CapexBasis_21:
    id: CapexBasis_21
    type: enum
    allowed: [MarketRate_05, CostPrice_04, Blend]
    default: MarketRate_05

  LeaseTermYears_22:
    id: LeaseTermYears_22
    type: number
    unit: years
    validate: {min: 5, max: 40}
    mode: manual
    default: 25

  ConstructionToCODMonths_23:
    id: ConstructionToCODMonths_23
    type: number
    unit: months
    validate: {min: 0, max: 36}
    default: 12

  PowerHedgeMode_24:
    id: PowerHedgeMode_24
    type: enum
    allowed: [Unhedged, PPA, FinancialSwap, PPA_Plus_Swap]
    default: Unhedged

  CurrencyPolicy_25:
    id: CurrencyPolicy_25
    type: enum
    allowed: [LocalCurrency, HedgedTo_01, Mixed]
    default: LocalCurrency

  VAT_TaxTreatmentToggle_26:
    id: VAT_TaxTreatmentToggle_26
    type: boolean
    default: false

  # ───────── 5) MARKET STATE LEVERS ─────────
  BaseCurveAnchor_27:
    id: BaseCurveAnchor_27
    type: enum
    allowed: [5Y,7Y,10Y,15Y,20Y,25Y,30Y,40Y]
    default: 10Y

  BaseCurveShift_bps_28:
    id: BaseCurveShift_bps_28
    type: number
    unit: bps
    validate: {min: -300, max: 300}
    range: {enabled: true, min: -100, max: 200, step: 25}
    default: 0

  CreditSpreadAAA_bps_29: {id: CreditSpreadAAA_bps_29, type: number, unit: bps, validate: {min: 0, max: 300}, default: 70}
  CreditSpreadAA_bps_30:  {id: CreditSpreadAA_bps_30,  type: number, unit: bps, validate: {min: 0, max: 400}, default: 90}
  CreditSpreadA_bps_31:   {id: CreditSpreadA_bps_31,   type: number, unit: bps, validate: {min: 0, max: 600}, default: 120}
  CreditSpreadBBB_bps_32: {id: CreditSpreadBBB_bps_32, type: number, unit: bps, validate: {min: 0, max: 900}, default: 180}

  InflationSpot_33:
    id: InflationSpot_33
    type: number
    unit: "%"
    validate: {min: -2, max: 15}
    default: 2.0

  InflationFwdTerm_34:
    id: InflationFwdTerm_34
    type: enum
    allowed: [5Y, 10Y]
    default: 10Y

  FXSpot_35:
    id: FXSpot_35
    type: number
    unit: rate
    validate: {min: 0.2, max: 5}
    default: 1.00

  FXHedgeCost_bps_36:
    id: FXHedgeCost_bps_36
    type: number
    unit: bps
    validate: {min: 0, max: 400}
    default: 50

  # ───────── 6) CAPITAL STACK — SENIOR ─────────
  TargetDSCRSenior_37:
    id: TargetDSCRSenior_37
    type: number
    unit: x
    validate: {min: 1.10, max: 2.50}
    range: {enabled: true, min: 1.20, max: 1.50, step: 0.05}
    default: 1.30

  SeniorCoupon_38:
    id: SeniorCoupon_38
    type: number
    unit: "%"
    validate: {min: 0.5, max: 12}
    range: {enabled: true, min: 3.5, max: 7.0, step: 0.25}
    default: 5.00

  SeniorTenorY_39:
    id: SeniorTenorY_39
    type: number
    unit: years
    validate: {min: 3, max: 40}
    default: 25
    depends_on: [LeaseTermYears_22]
    comment: Runtime check enforces SeniorTenorY_39 ≤ LeaseTermYears_22.

  SeniorAmortType_40:
    id: SeniorAmortType_40
    type: enum
    allowed: [Annuity, Sculpted, Bullet, StepDown]
    default: Annuity

  SeniorGracePeriod_41:
    id: SeniorGracePeriod_41
    type: number
    unit: months
    validate: {min: 0, max: 60}
    default: 0

  SeniorFeesUpfront_bps_42:  {id: SeniorFeesUpfront_bps_42,  type: number, unit: bps, validate: {min: 0, max: 300}, default: 50}
  SeniorOngoingFees_bps_43:  {id: SeniorOngoingFees_bps_43,  type: number, unit: bps, validate: {min: 0, max: 150}, default: 20}
  SeniorRepoEligibleFlag_44: {id: SeniorRepoEligibleFlag_44, type: boolean, default: true}

  # ───────── 7) CAPITAL STACK — MEZZANINE ─────────
  TargetDSCRMezz_45:
    id: TargetDSCRMezz_45
    type: number
    unit: x
    validate: {min: 1.05, max: 1.60}
    default: 1.15

  MezzCoupon_46:         {id: MezzCoupon_46,         type: number, unit: "%", validate: {min: 4,  max: 20}, default: 8.0}
  MezzTenorY_47:         {id: MezzTenorY_47,         type: number, unit: years, validate: {min: 3,  max: 30}, default: 10}
  MezzAmortType_48:      {id: MezzAmortType_48,      type: enum,   allowed: [Annuity, Bullet, PIKWindow], default: Bullet}
  MezzFeesUpfront_bps_49:{id: MezzFeesUpfront_bps_49, type: number, unit: bps, validate: {min: 0,  max: 500}, default: 100}
  MezzOngoingFees_bps_50:{id: MezzOngoingFees_bps_50, type: number, unit: bps, validate: {min: 0,  max: 250}, default: 50}
  IntercreditorStyle_51: {id: IntercreditorStyle_51,  type: enum, allowed: [Sequential, ProRata, OCTriggered], default: Sequential}

  # ───────── 8) EQUITY / FIRST-LOSS / TRS ─────────
  FirstLossPct_52:     {id: FirstLossPct_52,     type: number, unit: "%", validate: {min: 0, max: 20}, default: 5}
  TRS_EquityPct_53:    {id: TRS_EquityPct_53,    type: number, unit: "%", validate: {min: 0, max: 80}, default: 5}
  TRS_CouponOrFee_54:  {id: TRS_CouponOrFee_54,  type: number, unit: "%", validate: {min: 0, max: 15}, default: 3}
  EquityIRRTarget_55:  {id: EquityIRRTarget_55,  type: number, unit: "%", validate: {min: 5, max: 40}, default: 17}
  CallOptionYears_56:  {id: CallOptionYears_56,  type: number, unit: years, validate: {min: 0, max: 15}, default: 5}

  # ───────── 9) INSURANCE / WRAP / LIQUIDITY ─────────
  MonolineWrapFlag_57:     {id: MonolineWrapFlag_57,     type: enum, allowed: [None, SeniorOnly, WholeStack], default: None}
  WrapPremium_bps_58:      {id: WrapPremium_bps_58,      type: number, unit: bps, validate: {min: 0, max: 300}, default: 60}
  DSRA_Months_59:          {id: DSRA_Months_59,          type: number, unit: months, validate: {min: 0, max: 12}, default: 6}
  LiquidityFacilityMonths_60:{id: LiquidityFacilityMonths_60, type: number, unit: months, validate: {min: 0, max: 12}, default: 3}
  InsuranceProgrammeType_61:{id: InsuranceProgrammeType_61, type: enum, allowed: [Construction, Ops, Both], default: Both}
  InsurancePremium_bps_62: {id: InsurancePremium_bps_62, type: number, unit: bps, validate: {min: 0, max: 300}, default: 50}

  # ───────── 10) INDEXATION & CASHFLOW SHAPE ─────────
  CPI_FloorPct_63:        {id: CPI_FloorPct_63,        type: number, unit: "%", validate: {min: 0,   max: 5},  default: 1}
  CPI_CapPct_64:          {id: CPI_CapPct_64,          type: number, unit: "%", validate: {min: 1,   max: 8},  default: 4}
  EscalatorFixedPct_65:   {id: EscalatorFixedPct_65,   type: number, unit: "%", validate: {min: 0.0, max: 5},  default: 2}
  Vacancy_UtilisationPct_66:{id: Vacancy_UtilisationPct_66, type: number, unit: "%", validate: {min: 0, max: 30}, default: 5}
  CollectionLagDays_67:   {id: CollectionLagDays_67,   type: number, unit: days, validate: {min: 0,   max: 90}, default: 30}
  RentFreeMonths_68:      {id: RentFreeMonths_68,      type: number, unit: months, validate: {min: 0, max: 24}, default: 0}
  MaintenanceCapexPct_69: {id: MaintenanceCapexPct_69, type: number, unit: "%", validate: {min: 0,   max: 10}, default: 2}
  PowerPassThroughMode_70:{id: PowerPassThroughMode_70, type: enum, allowed: [Landlord, Tenant, Share], default: Tenant}
  PPA_TermYears_71:       {id: PPA_TermYears_71,       type: number, unit: years, validate: {min: 0, max: 25}, default: 0}
  PPA_Strike_£MWh_72:     {id: PPA_Strike_£MWh_72,     type: number, unit: "£/MWh", validate: {min: 10, max: 400}, default: 80}
  PowerSwapTenorY_73:     {id: PowerSwapTenorY_73,     type: number, unit: years, validate: {min: 0, max: 20}, default: 0}
  PowerHedgeCoveragePct_74:{id: PowerHedgeCoveragePct_74,type: number, unit: "%", validate: {min: 0, max: 100}, default: 0}

  # ───────── 11) RATING & ELIGIBILITY RULES ─────────
  MinSeniorRatingTarget_75:{id: MinSeniorRatingTarget_75, type: enum, allowed: [AAA, AA, A, BBB], default: AAA}
  MinMezzRatingTarget_76:  {id: MinMezzRatingTarget_76,   type: enum, allowed: [A, BBB, BB, Unrated], default: BBB}
  TenantRatingFloor_77:    {id: TenantRatingFloor_77,     type: string, default: "A-"}
  ConcentrationLimitPct_78:{id: ConcentrationLimitPct_78, type: number, unit: "%", validate: {min: 10, max: 100}, default: 50}
  JurisdictionEligibility_79:{id: JurisdictionEligibility_79, type: enum, allowed: [CB_RepoEligible, PPOnly, NA], default: CB_RepoEligible}
  MaxWAL_Senior_80:        {id: MaxWAL_Senior_80,        type: number, unit: years, validate: {min: 1, max: 40}, default: 20}
  HaircutRuleSet_81:       {id: HaircutRuleSet_81,       type: enum, allowed: [RA_Conservative, RA_Base, Internal_Base], default: RA_Base}

  # ───────── 12) STRESS & HAIRCUTS ─────────
  CPI_Scenarios_82:
    id: CPI_Scenarios_82
    type: list
    unit: "%"
    list: [0.0, 1.8, 2.5]
    default: [0.0, 1.8, 2.5]

  Rate_Shock_bps_83:     {id: Rate_Shock_bps_83,     type: number, unit: bps, validate: {min: -300, max: 300}, default: 100}
  OPEX_StressPct_84:     {id: OPEX_StressPct_84,     type: number, unit: "%",  validate: {min: 0,   max: 30},  default: 10}
  Rent_DownsidePct_85:   {id: Rent_DownsidePct_85,   type: number, unit: "%",  validate: {min: 0,   max: 40},  default: 10}
  TenantDefaultProb_86:  {id: TenantDefaultProb_86,  type: number, unit: "%",  validate: {min: 0,   max: 20},  default: 1}
  RecoveryLagMonths_87:  {id: RecoveryLagMonths_87,  type: number, unit: months, validate: {min: 0, max: 24}, default: 6}
  RefinanceSpreadAdd_bps_88:{id: RefinanceSpreadAdd_bps_88, type: number, unit: bps, validate: {min: 0, max: 600}, default: 100}
  CapexOverrunPct_89:    {id: CapexOverrunPct_89,    type: number, unit: "%",  validate: {min: 0,   max: 40},  default: 10}
  COD_DelayMonths_90:    {id: COD_DelayMonths_90,    type: number, unit: months, validate: {min: 0, max: 24}, default: 6}

  # ───────── 13) DERIVATIVES / SIDECAR ─────────
  ZCiS_NotionalPct_91:   {id: ZCiS_NotionalPct_91,   type: number, unit: "%", validate: {min: 0, max: 100}, default: 50}
  ZCiS_TermY_92:
    id: ZCiS_TermY_92
    type: enum
    allowed: [5, 10]
    default: 10
  ZCiS_ImpliedRate_93:   {id: ZCiS_ImpliedRate_93,   type: number, unit: "%", validate: {min: -1, max: 6}, default: 2.0}
  CPI_BasisAdj_bps_94:   {id: CPI_BasisAdj_bps_94,   type: number, unit: bps, validate: {min: 0, max: 80}, default: 15}
  TRS_MarginingFreq_95:  {id: TRS_MarginingFreq_95,  type: enum, allowed: [Monthly, Quarterly], default: Quarterly}
  CCY_SwapTenorY_96:     {id: CCY_SwapTenorY_96,     type: number, unit: years, validate: {min: 0, max: 30}, default: 0}
  CCY_SwapCost_bps_97:   {id: CCY_SwapCost_bps_97,   type: number, unit: bps, validate: {min: 0, max: 400}, default: 60}
  DerivativeCSAType_98:  {id: DerivativeCSAType_98,  type: enum, allowed: [TwoWay, OneWay, Threshold], default: TwoWay}

  # ───────── 14) WATERFALL & TRIGGERS ─────────
  PriorityOfPayments_99: {id: PriorityOfPayments_99, type: enum, allowed: [Std, Enhanced], default: Std}
  OC_TestLevels_100:     {id: OC_TestLevels_100,     type: number, unit: "%", validate: {min: 0, max: 30}, default: 5}
  DSCR_TriggerLevels_101:{id: DSCR_TriggerLevels_101, type: string, default: "1.20|1.05"}
  CashTrapRules_102:     {id: CashTrapRules_102,     type: enum, allowed: [MezzBlock, EquityBlock, SweepPct], default: EquityBlock}
  AmortSwitchRules_103:  {id: AmortSwitchRules_103,  type: enum, allowed: [TurboOnTrap, TimeBased, RatingDowngrade], default: TurboOnTrap}
  ExcessSpreadUse_104:   {id: ExcessSpreadUse_104,   type: enum, allowed: [PayDown, Reserve, DistToEquity], default: PayDown}
  ReinvestmentOption_105:{id: ReinvestmentOption_105,type: enum, allowed: [Off, LeaseBacked, Limited], default: Off}
  FeesPriorityMode_106:  {id: FeesPriorityMode_106,  type: enum, allowed: [SeniorFirst, ProRataFees], default: SeniorFirst}

  # ───────── 15) SELECTION, SORTING & OUTPUT ─────────
  PermutationGranularity_107:
    id: PermutationGranularity_107
    type: object
    default:
      dscr_step: 0.05
      coupon_step_pct: 0.25
      bps_step: 25
      tenor_step_years: 1

  MaxPermutations_108:  {id: MaxPermutations_108,  type: number, unit: count, validate: {min: 1000, max: 1000000}, default: 150000}
  RankingObjective_109: {id: RankingObjective_109, type: enum, allowed: [MaxSeniorRaise, MinWACC, MaxDay1Cash, MaxEquityIRR, Composite], default: Composite}
  CompositeWeights_110:
    id: CompositeWeights_110
    type: object
    default:
      SeniorRaise: 0.35
      WACC: 0.25
      Day1: 0.20
      DSCR: 0.10
      Rating: 0.10

  HardFilters_111:
    id: HardFilters_111
    type: list
    default: ["DSCR>=1.30", "RepoEligible=Yes", "SeniorRating>=AAA"]

  OutputVariants_112:
    id: OutputVariants_112
    type: list
    default: [Flat, Indexed, Hybrid]

  DocumentPackFlags_113:
    id: DocumentPackFlags_113
    type: list
    default: [IM, TermSheets, WaterfallPDF, ModelExport]

  CounterpartyRouting_114:
    id: CounterpartyRouting_114
    type: object
    default:
      AAA_10_20y: ["Insurers", "CB_RepoDesks", "SWFs"]
      A_BBB_10y:  ["PP_Accounts", "Credit_Funds"]

  SensitivityExportSet_115:
    id: SensitivityExportSet_115
    type: list
    default: [CPI, Rates, OPEX, Rent, Delay]

  AuditTraceFlag_116:
    id: AuditTraceFlag_116
    type: boolean
    default: true

# ──────────────────────────────────────────────────────────────────────────────
# DERIVED / SIZING LOGIC SNIPPETS (engine-side, referenced by ids above)
# ──────────────────────────────────────────────────────────────────────────────
logic:

  senior_sizing:
    # Solve for Max Senior Notional so that DSCR (NetCF / DebtService) >= TargetDSCRSenior_37
    debt_service_model:
      amort_type_switch:
        Annuity: "Level debt service over SeniorTenorY_39 (after any SeniorGracePeriod_41)"
        Sculpted: "Match to NetIncome_11 trajectory under IndexationMode_18 within DSCR floor"
        Bullet: "Interest-only until maturity; principal at end"
        StepDown: "Higher early amort, reduce later"
    constraints:
      - "SeniorTenorY_39 <= LeaseTermYears_22"
      - "Repo eligible only if SeniorRepoEligibleFlag_44 == true"
      - "Rating guard: Senior meets MinSeniorRatingTarget_75 under HaircutRuleSet_81"

  mezz_sizing:
    - "Sized after senior; respects IntercreditorStyle_51"
    - "DSCR at mezz level must be >= TargetDSCRMezz_45 (if modelled)"
    - "Tenor MezzTenorY_47 <= LeaseTermYears_22"

  equity_trs:
    - "FirstLossPct_52 applies to total stack; TRS_EquityPct_53 synthetically transfers portion of equity economics"
    - "Equity IRR computed after all fees, wraps, derivatives, and cash traps"

  indexation_effects:
    - "If IndexationMode_18=Flat: annual rent growth = 0"
    - "If CPI_Linked: rent growth = clamp(CPI, CPI_FloorPct_63, CPI_CapPct_64)"
    - "If Partial: blend(IndexationBase_19, EscalatorFixedPct_65)"

  power_costs:
    - "PowerPassThroughMode_70=Tenant → no landlord OPEX impact from power"
    - "Landlord/Share → OPEX includes PPA or swap economics where applicable"

  rating_rules:
    - "Apply HaircutRuleSet_81 to revenue, OPEX, and DSCR per RA matrix"
    - "Enforce TenantRatingFloor_77 and ConcentrationLimitPct_78"

  stress_suite:
    - "Apply CPI_Scenarios_82, Rate_Shock_bps_83, OPEX_StressPct_84, Rent_DownsidePct_85, delays (COD_DelayMonths_90)"
    - "Compute DSCR deltas, refi sensitivities (RefinanceSpreadAdd_bps_88)"

  sidecar_derivatives:
    - "ZCiS only allowed terms: ZCiS_TermY_92 ∈ {5,10}; notional = ZCiS_NotionalPct_91 × indexed leg PV"
    - "Day-1 value = curve-implied PV less CPI_BasisAdj_bps_94"
    - "CCY swap costs added via CCY_SwapCost_bps_97 and FXHedgeCost_bps_36"

  waterfall_triggers:
    - "If DSCR < first threshold in DSCR_TriggerLevels_101 → cash trap per CashTrapRules_102"
    - "If DSCR < second threshold → turbo amort via AmortSwitchRules_103"
    - "Excess spread allocation via ExcessSpreadUse_104"

  ranking_objectives:
    - MaxSeniorRaise: "sort by Senior Notional desc"
    - MinWACC: "sort by WACC asc"
    - MaxDay1Cash: "sort by upfront cash (wrap monetisation + sidecar) desc"
    - MaxEquityIRR: "sort by Equity IRR desc"
    - Composite: "weighted score using CompositeWeights_110"

# ──────────────────────────────────────────────────────────────────────────────
# QUICK START EXAMPLES (flip modes without changing the schema)
# ──────────────────────────────────────────────────────────────────────────────
examples:
  set_manual_value:
    field: TargetDSCRSenior_37
    mode: manual
    manual: 1.35

  switch_to_range:
    field: SeniorCoupon_38
    mode: min_max
    min_max: {min: 4.25, max: 6.50, step: 0.25}

  use_variations_list:
    field: CPI_Scenarios_82
    mode: list
    list: [0.0, 1.8, 2.5, 3.0]

  tighten_repo_rules:
    field: HardFilters_111
    append: ["SeniorRating>=AA", "WAL<=20"]

  indexed_mode:
    fields:
      IndexationMode_18: {mode: manual, manual: CPI_Linked}
      CPI_FloorPct_63: {manual: 1.0}
      CPI_CapPct_64:   {manual: 4.0}
