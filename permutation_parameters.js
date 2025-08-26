// Complete parameter list from PQuery table - 80+ parameters
const permutationParameters = {
    // Project & Basic Parameters (00-03)
    project: [
        { id: 'Currency_00', name: 'Currency', type: 'select', options: ['EUR', 'USD', 'GBP'], default: 'EUR' },
        { id: 'GrossITLoad_01', name: 'Gross IT Load (MW)', type: 'number', min: 0.1, max: 100, step: 0.1, default: 10 },
        { id: 'PUE_02', name: 'PUE', type: 'number', min: 1.0, max: 2.5, step: 0.01, default: 1.15 },
        { id: 'NetITLoad_03', name: 'Net IT Load (MW)', type: 'formula', formula: 'GrossITLoad_01 / PUE_02' }
    ],

    // Income & Cost Parameters (04-15)
    financial: [
        { id: 'GrossMonthlyRent_04', name: 'Gross Monthly Rent (€/kW)', type: 'number', min: 50, max: 500, step: 5, default: 110 },
        { id: 'GrossIncome_05', name: 'Gross Income', type: 'formula', formula: 'GrossMonthlyRent_04 * GrossITLoad_01 * 1000 * 12' },
        { id: 'OPEX_06', name: 'OPEX (%)', type: 'number', min: 0, max: 50, step: 1, default: 15 },
        { id: 'NetIncome_07', name: 'Net Income', type: 'formula', formula: 'GrossIncome_05 * (1 - OPEX_06/100)' },
        { id: 'CapexCostPrice_08', name: 'Capex Cost Price (€/kW)', type: 'number', min: 1000, max: 20000, step: 100, default: 7000 },
        { id: 'CapexMarketRate_09', name: 'Capex Market Rate (€/kW)', type: 'number', min: 1000, max: 25000, step: 100, default: 8000 },
        { id: 'LandPurchaseFees_10', name: 'Land Purchase & Fees (€)', type: 'number', min: 0, max: 100000000, step: 100000, default: 5000000 },
        { id: 'DeveloperProfit_11', name: 'Developer Profit (%)', type: 'number', min: 0, max: 50, step: 1, default: 15 },
        { id: 'DeveloperMargin_12', name: 'Developer Margin (%)', type: 'number', min: 0, max: 50, step: 1, default: 20 },
        { id: 'TotalStructuringFees_13', name: 'Total Structuring Fees (€)', type: 'number', min: 0, max: 10000000, step: 10000, default: 500000 },
        { id: 'TotalProjectMarketCosts_14', name: 'Total Project Market Costs', type: 'formula', formula: 'calculated' },
        { id: 'TotalProjectInternalCosts_15', name: 'Total Project Internal Costs', type: 'formula', formula: 'calculated' }
    ],

    // Senior Debt Parameters (16-32)
    senior: [
        { id: 'TargetDSCRSenior_16', name: 'Target DSCR Senior', type: 'number', min: 1.0, max: 3.0, step: 0.05, default: 1.35 },
        { id: 'SeniorCoupon_17', name: 'Senior Coupon (%)', type: 'number', min: 0, max: 20, step: 0.25, default: 6.5 },
        { id: 'SeniorTenor_18', name: 'Senior Tenor (Years)', type: 'number', min: 1, max: 30, step: 1, default: 7 },
        { id: 'AFSenior_19', name: 'Annuity Factor Senior', type: 'formula', formula: 'calculated' },
        { id: 'AnnualDebtServiceSenior_20', name: 'Annual Debt Service Senior', type: 'formula', formula: 'NetIncome_07 / TargetDSCRSenior_16' },
        { id: 'MaxSeniorDebt_21', name: 'Max Senior Debt', type: 'formula', formula: 'AnnualDebtServiceSenior_20 * AFSenior_19' },
        { id: 'MaxSeniorAsPercentageOfCosts_22', name: 'Max Senior as % of Costs', type: 'formula', formula: 'MaxSeniorDebt_21 / TotalProjectMarketCosts_14 * 100' },
        { id: 'WACDSeniorTranche_23', name: 'WACD Senior Tranche (%)', type: 'formula', formula: 'calculated' },
        { id: 'LeaseTermYears_24', name: 'Lease Term Years', type: 'number', min: 1, max: 30, step: 1, default: 10 },
        { id: 'AFStrategy_25', name: 'AF Strategy', type: 'select', options: ['Bullet', 'Linear', 'Annuity', 'Custom'], default: 'Linear' },
        { id: 'TypeOfAFRun_26', name: 'Type of AF Run', type: 'select', options: ['Standard', 'Conservative', 'Aggressive'], default: 'Standard' },
        { id: 'AFUsedYears_27', name: 'AF Used Years', type: 'number', min: 1, max: 30, step: 1, default: 7 },
        { id: 'AFCeiling_28', name: 'AF Ceiling', type: 'number', min: 0, max: 100, step: 1, default: 80 },
        { id: 'ResidualAFValue_29', name: 'Residual AF Value', type: 'formula', formula: 'calculated' },
        { id: 'PlaceableAt10YAF_30', name: 'Placeable at 10Y AF', type: 'boolean', default: true },
        { id: 'SeniorAmortisationType_31', name: 'Senior Amortisation Type', type: 'select', options: ['Bullet', 'Linear', 'Annuity'], default: 'Linear' },
        { id: 'EffectiveDSCRBuffer_32', name: 'Effective DSCR Buffer (%)', type: 'number', min: 0, max: 50, step: 1, default: 10 }
    ],

    // Mezzanine Debt Parameters (33-47)
    mezzanine: [
        { id: 'TargetDSCRMezz_33', name: 'Target DSCR - Mezz', type: 'number', min: 1.0, max: 2.5, step: 0.05, default: 1.15 },
        { id: 'MezzCoupon_34', name: 'Mezz Coupon (%)', type: 'number', min: 0, max: 30, step: 0.5, default: 12 },
        { id: 'MezzTenorYears_35', name: 'Mezz Tenor Years', type: 'number', min: 1, max: 15, step: 1, default: 5 },
        { id: 'AnnuityFactorMezz_36', name: 'Annuity Factor - Mezz', type: 'formula', formula: 'calculated' },
        { id: 'RemainingNOI_37', name: 'Remaining NOI (£)', type: 'formula', formula: 'NetIncome_07 - AnnualDebtServiceSenior_20' },
        { id: 'AnnualMezzDebtService_38', name: 'Annual Mezz Debt Service (£)', type: 'formula', formula: 'RemainingNOI_37 / TargetDSCRMezz_33' },
        { id: 'MaxMezzDebt_39', name: 'Max Mezz Debt (£)', type: 'formula', formula: 'AnnualMezzDebtService_38 * AnnuityFactorMezz_36' },
        { id: 'MaxMezzAsPercentOfCosts_40', name: 'Max Mezz as % of Costs (%)', type: 'formula', formula: 'MaxMezzDebt_39 / TotalProjectMarketCosts_14 * 100' },
        { id: 'WACDMezz_41', name: 'WACD - Mezz (%)', type: 'formula', formula: 'calculated' },
        { id: 'LeaseTermYearsMezz_42', name: 'Lease Term Years - Mezz', type: 'number', min: 1, max: 30, step: 1, default: 10 },
        { id: 'AFLookupMezzAmortising_43', name: 'AF Lookup - Mezz (Amortising)', type: 'formula', formula: 'calculated' },
        { id: 'AFValueMezzFullyAmortising_44', name: 'AF Value - Mezz (Fully Amortising)', type: 'formula', formula: 'calculated' },
        { id: 'AnnualDebtServiceMezz_45', name: 'Annual Debt Service (£) - Mezz', type: 'formula', formula: 'calculated' },
        { id: 'BlendedSeniorMezzWACD_46', name: 'Blended Senior + Mezz WACD (%)', type: 'formula', formula: 'calculated' },
        { id: 'BlendedDSCR_47', name: 'Blended DSCR', type: 'formula', formula: 'NetIncome_07 / (AnnualDebtServiceSenior_20 + AnnualMezzDebtService_38)' }
    ],

    // Equity & Capital Stack Parameters (48-65)
    equity: [
        { id: 'DebtHeadroom_48', name: 'Debt Headroom (%)', type: 'formula', formula: 'calculated' },
        { id: 'TargetEquityIRR_49', name: 'Target Equity IRR (%)', type: 'number', min: 0, max: 50, step: 1, default: 18 },
        { id: 'MinEquityContribution_50', name: 'Min Equity Contribution (£)', type: 'number', min: 0, max: 1000000000, step: 100000, default: 10000000 },
        { id: 'DeveloperEquityIRR_51', name: 'Developer Equity IRR (%)', type: 'number', min: 0, max: 50, step: 1, default: 25 },
        { id: 'EquityAsPercentOfProjectCost_52', name: 'Equity as % of Project Cost', type: 'formula', formula: 'calculated' },
        { id: 'TotalCapitalStack_53', name: 'Total Capital Stack (£)', type: 'formula', formula: 'MaxSeniorDebt_21 + MaxMezzDebt_39 + MinEquityContribution_50' },
        { id: 'OverraiseAmount_54', name: 'Overraise Amount (£)', type: 'number', min: 0, max: 100000000, step: 100000, default: 0 },
        { id: 'ResidualEquityNeeded_55', name: 'Residual Equity Needed (£)', type: 'formula', formula: 'calculated' },
        { id: 'EffectiveEquityValueMultiple_56', name: 'Effective Equity Value Multiple', type: 'number', min: 1, max: 5, step: 0.1, default: 1.5 },
        { id: 'EquitySaleUplift_57', name: 'Equity Sale Uplift (%)', type: 'number', min: 0, max: 100, step: 5, default: 20 },
        { id: 'EquitySold_58', name: 'Equity Sold (£)', type: 'formula', formula: 'calculated' },
        { id: 'EquityRetained_59', name: 'Equity Retained (£)', type: 'formula', formula: 'calculated' },
        { id: 'EquityRetainedValue_60', name: 'Equity Retained Value (£)', type: 'formula', formula: 'calculated' },
        { id: 'ResidualUpsideCaptureMechanism_61', name: 'Residual Upside Capture Mechanism', type: 'select', options: ['None', 'Promote', 'Waterfall', 'Ratchet'], default: 'Promote' },
        { id: 'TRSApplied_62', name: 'TRS Applied?', type: 'boolean', default: false },
        { id: 'TRSStrikeValue_63', name: 'TRS Strike Value (£)', type: 'number', min: 0, max: 1000000000, step: 100000, default: 0 },
        { id: 'TRSRetainedUpside_64', name: 'TRS Retained Upside (%)', type: 'number', min: 0, max: 100, step: 5, default: 50 },
        { id: 'NotesUseCase_65', name: 'Notes / Use Case', type: 'text', default: '' }
    ],

    // Output & Viability Parameters (66-80)
    outputs: [
        { id: 'EquityIRR_66', name: 'Equity IRR (%)', type: 'formula', formula: 'calculated' },
        { id: 'EquityAsPercentOfProjectCostFinal_67', name: 'EQUITY as % of Project Cost', type: 'formula', formula: 'calculated' },
        { id: 'EquityIRRRanking_68', name: 'Equity IRR Ranking', type: 'formula', formula: 'calculated' },
        { id: 'TotalEquityValue_69', name: 'Total Equity Value (£)', type: 'formula', formula: 'calculated' },
        { id: 'PlatformSaleUplift_70', name: 'Platform Sale Uplift (%)', type: 'number', min: 0, max: 100, step: 5, default: 30 },
        { id: 'PlatformValueRealised_71', name: 'Platform Value Realised (£)', type: 'formula', formula: 'calculated' },
        { id: 'EffectiveTotalValue_72', name: 'Effective Total Value (£)', type: 'formula', formula: 'calculated' },
        { id: 'TotalCapitalStackFinal_73', name: 'Total Capital Stack (£)', type: 'formula', formula: 'calculated' },
        { id: 'SeniorAsPercentOfCapitalStack_74', name: 'Senior as % of Capital Stack', type: 'formula', formula: 'MaxSeniorDebt_21 / TotalCapitalStack_53 * 100' },
        { id: 'MezzAsPercentOfCapitalStack_75', name: 'Mezz as % of Capital Stack', type: 'formula', formula: 'MaxMezzDebt_39 / TotalCapitalStack_53 * 100' },
        { id: 'EquityAsPercentOfCapitalStack_76', name: 'Equity as % of Capital Stack', type: 'formula', formula: 'MinEquityContribution_50 / TotalCapitalStack_53 * 100' },
        { id: 'BlendedWACD_77', name: 'Blended WACD (%)', type: 'formula', formula: 'calculated' },
        { id: 'BlendedDSCRFinal_78', name: 'Blended DSCR', type: 'formula', formula: 'calculated' },
        { id: 'BlendedIRR_79', name: 'Blended IRR (%)', type: 'formula', formula: 'calculated' },
        { id: 'ViabilityFlag_80', name: 'Viability Flag', type: 'formula', formula: 'ALL_CONSTRAINTS_MET' }
    ]
};

// Helper function to get all parameters as flat array
function getAllParameters() {
    const allParams = [];
    Object.values(permutationParameters).forEach(category => {
        allParams.push(...category);
    });
    return allParams;
}

// Helper function to get parameter by ID
function getParameterById(id) {
    const allParams = getAllParameters();
    return allParams.find(p => p.id === id);
}

// Export for use in dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { permutationParameters, getAllParameters, getParameterById };
}