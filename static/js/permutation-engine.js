// Permutation Engine - Complete 83 Input System
// Projects → Permutations → Securitization

const PermutationEngine = {
    // Input categories
    inputs: {
        fixed: {},      // 47 inputs from project data
        variable: {},   // 30 inputs with ranges
        calculated: {}  // 6+ calculated inputs
    },

    // Default ranges (starting with single values for testing)
    defaultRanges: {
        // Financial Parameters
        GrossMonthlyRent_04: { min: 160, max: 160, step: 20, current: [160] }, // Start with 1 value
        OPEX_06: { min: 20, max: 20, step: 5, current: [20] }, // Start with 1 value
        CapexCostPrice_08: { min: 7500000, max: 7500000, step: 3500000, current: [7500000] },
        CapexMarketRate_09: { min: 11000000, max: 11000000, step: 0, current: [11000000] },
        LandPurchaseFees_10: { min: 10000000, max: 10000000, step: 0, current: [10000000] },
        TotalStructuringFees_13: { min: 33305000, max: 33305000, step: 0, current: [33305000] },

        // Senior Debt Parameters
        TargetDSCRSenior_16: { min: 1.65, max: 1.65, step: 0.05, current: [1.65] }, // Start with 1
        SeniorCoupon_17: { min: 4.0, max: 4.0, step: 0.25, current: [4.0] }, // Start with 1
        SeniorTenor_18: { min: 15, max: 15, step: 5, current: [15] }, // Start with 1
        LeaseTermYears_23: { min: 15, max: 15, step: 5, current: [15] }, // Must match tenor

        // Mezzanine Debt Parameters
        EffectiveDSCRBuffer: { min: 42.5, max: 42.5, step: 7.5, current: [42.5] },
        TargetDSCRMezz: { min: 70, max: 70, step: 20, current: [70] },
        MezzCoupon: { min: 7.0, max: 7.0, step: 0.25, current: [7.0] },
        MezzTenorYears: { min: 15, max: 15, step: 5, current: [15] },

        // Equity Parameters
        DebtHeadroom: { min: 20, max: 20, step: 5, current: [20] },
        TargetEquityIRR: { min: 16, max: 16, step: 1, current: [16] }
    },

    // Fixed inputs from project data
    fixedInputs: {
        // From Project Import
        GrossITLoad_01: 100,
        PUE_02: 1.2,
        Currency_00: 'GBP',
        
        // These will be populated from project data
        TotalProjectInternalCosts_15: 0,
        AnnualDebtServiceSenior_20: 0,
        MaxSeniorDebt_21: 0,
        MaxSeniorAsPercentageOfCosts_22: 0,
        WACDSeniorTraunche_23: 0,
        
        // Placeholder values (will be calculated)
        AFStrategy_24: 'Standard',
        TypeOfAFRun_25: 'Full',
        AFUsedYears_26: 0,
        AFCeiling_27: 0,
        AFDeltaYears_28: 0,
        ResidualAFValue_29: 0,
        PlaceableAt10YAF_30: 0
    },

    // Constraint rules
    constraints: {
        // Lease term must match tenor
        leaseTenorMatch: (inputs) => {
            return inputs.LeaseTermYears_23 === inputs.SeniorTenor_18;
        },
        
        // Minimum funding requirement
        minFundingMet: (inputs, minRequired) => {
            const totalFunding = inputs.MaxSeniorDebt_21 + inputs.MaxMezzDebt + inputs.MinEquity;
            return totalFunding >= minRequired;
        },
        
        // DSCR requirements
        dscrRequirementsMet: (inputs) => {
            return inputs.BlendedDSCR >= 1.25; // Minimum viable DSCR
        },
        
        // IRR threshold
        irrThresholdMet: (inputs) => {
            return inputs.EquityIRR >= 8; // Minimum acceptable IRR
        }
    },

    // Core calculation functions
    calculations: {
        // Basic calculations
        NetITLoad_03: (inputs) => {
            return inputs.GrossITLoad_01 / inputs.PUE_02;
        },
        
        GrossIncome_05: (inputs) => {
            return inputs.GrossMonthlyRent_04 * 12;
        },
        
        NetIncome_07: (inputs) => {
            return inputs.GrossIncome_05 * (1 - inputs.OPEX_06 / 100);
        },
        
        // Annuity Factor calculation
        calculateAnnuityFactor: (rate, years) => {
            if (rate === 0) return years;
            const r = rate / 100;
            return (1 - Math.pow(1 + r, -years)) / r;
        },
        
        // Debt capacity calculations
        MaxSeniorDebt: (inputs) => {
            const af = PermutationEngine.calculations.calculateAnnuityFactor(
                inputs.SeniorCoupon_17, 
                inputs.SeniorTenor_18
            );
            return inputs.NetIncome_07 / (inputs.TargetDSCRSenior_16 * (1/af));
        },
        
        MaxMezzDebt: (inputs) => {
            const remainingNOI = inputs.NetIncome_07 - inputs.AnnualDebtServiceSenior_20;
            const af = PermutationEngine.calculations.calculateAnnuityFactor(
                inputs.MezzCoupon,
                inputs.MezzTenorYears
            );
            return remainingNOI / (inputs.TargetDSCRMezz / 100 * (1/af));
        },
        
        // Capital stack calculation
        TotalCapitalStack: (inputs) => {
            return inputs.MaxSeniorDebt_21 + inputs.MaxMezzDebt + inputs.MinEquity;
        },
        
        // IRR calculation (simplified)
        EquityIRR: (inputs) => {
            // Simplified IRR calculation - you'll implement full DCF
            const equityInvestment = inputs.MinEquity;
            const annualCashFlow = inputs.NetIncome_07 - inputs.AnnualDebtServiceSenior_20 - inputs.AnnualMezzDebtService;
            const exitValue = equityInvestment * 2.5; // Example exit multiple
            
            // Simple IRR approximation
            return ((exitValue / equityInvestment) ** (1/10) - 1) * 100;
        }
    },

    // Generate permutations with constraints
    generatePermutations: function(options = {}) {
        const { 
            onlyViable = true, 
            minFunding = 0,
            maxPermutations = 10000 
        } = options;

        let permutations = [];
        let excludedCount = 0;
        
        // Get current ranges
        const ranges = this.getCurrentRanges();
        
        // Calculate total possible permutations
        let totalPossible = 1;
        Object.values(ranges).forEach(range => {
            totalPossible *= range.length;
        });
        
        console.log(`Generating ${totalPossible} permutations...`);
        
        // Generate all combinations
        const combinations = this.cartesianProduct(ranges);
        
        combinations.forEach((combo, index) => {
            if (permutations.length >= maxPermutations) return;
            
            // Create input set
            let inputs = {
                ...this.fixedInputs,
                ...combo
            };
            
            // Apply calculations
            inputs.NetITLoad_03 = this.calculations.NetITLoad_03(inputs);
            inputs.GrossIncome_05 = this.calculations.GrossIncome_05(inputs);
            inputs.NetIncome_07 = this.calculations.NetIncome_07(inputs);
            inputs.MaxSeniorDebt_21 = this.calculations.MaxSeniorDebt(inputs);
            
            // Check constraints
            if (onlyViable) {
                // Check lease-tenor match
                if (!this.constraints.leaseTenorMatch(inputs)) {
                    excludedCount++;
                    return;
                }
                
                // Check minimum funding
                if (minFunding > 0 && !this.constraints.minFundingMet(inputs, minFunding)) {
                    excludedCount++;
                    return;
                }
                
                // Check DSCR
                if (!this.constraints.dscrRequirementsMet(inputs)) {
                    excludedCount++;
                    return;
                }
            }
            
            // Add permutation ID
            inputs.permutationId = index + 1;
            inputs.viable = true;
            
            permutations.push(inputs);
        });
        
        return {
            permutations: permutations,
            totalGenerated: totalPossible,
            viable: permutations.length,
            excluded: excludedCount,
            reductionPercent: ((excludedCount / totalPossible) * 100).toFixed(1)
        };
    },

    // Get current ranges from UI or use defaults
    getCurrentRanges: function() {
        const ranges = {};
        
        Object.keys(this.defaultRanges).forEach(key => {
            const range = this.defaultRanges[key];
            const values = [];
            
            // Generate values from min to max with step
            if (range.step > 0 && range.max > range.min) {
                for (let val = range.min; val <= range.max; val += range.step) {
                    values.push(val);
                }
            } else {
                values.push(range.min); // Single value
            }
            
            ranges[key] = values;
        });
        
        return ranges;
    },

    // Cartesian product for combinations
    cartesianProduct: function(obj) {
        const keys = Object.keys(obj);
        const values = keys.map(k => obj[k]);
        const result = [];
        
        function helper(index, current) {
            if (index === keys.length) {
                const combo = {};
                keys.forEach((key, i) => {
                    combo[key] = current[i];
                });
                result.push(combo);
                return;
            }
            
            for (const value of values[index]) {
                helper(index + 1, [...current, value]);
            }
        }
        
        helper(0, []);
        return result;
    },

    // Update range for a specific variable
    updateRange: function(variable, min, max, step) {
        if (this.defaultRanges[variable]) {
            this.defaultRanges[variable].min = min;
            this.defaultRanges[variable].max = max;
            this.defaultRanges[variable].step = step;
        }
    },

    // Load project data into fixed inputs
    loadProjectData: function(projectData) {
        // Map project data to fixed inputs
        if (projectData.capex_total) {
            this.fixedInputs.TotalProjectInternalCosts_15 = projectData.capex_total;
        }
        if (projectData.power_capacity_mw) {
            this.fixedInputs.GrossITLoad_01 = projectData.power_capacity_mw;
        }
        if (projectData.expected_pue) {
            this.fixedInputs.PUE_02 = projectData.expected_pue;
        }
        
        // Update variable defaults based on project
        if (projectData.offtaker_rent_per_kwh) {
            // Convert kWh rate to monthly rent
            const monthlyRent = projectData.offtaker_rent_per_kwh * this.fixedInputs.GrossITLoad_01 * 1000 * 730;
            this.defaultRanges.GrossMonthlyRent_04.min = monthlyRent * 0.8;
            this.defaultRanges.GrossMonthlyRent_04.max = monthlyRent * 1.2;
        }
        
        console.log('Project data loaded into permutation engine');
    },

    // Export results to CSV
    exportToCSV: function(permutations) {
        const headers = Object.keys(permutations[0]);
        const csv = [
            headers.join(','),
            ...permutations.map(row => 
                headers.map(header => row[header]).join(',')
            )
        ].join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `permutations_${new Date().getTime()}.csv`;
        a.click();
    }
};

// Make it globally available
window.PermutationEngine = PermutationEngine;