"""
Atlas Forge - Optimized Permutation Engine v2.0.0
High-performance engine for handling thousands of scenarios efficiently

Features:
- Multiprocessing for parallel computation
- Batch processing for memory efficiency
- GridFS storage with compression
- Support for continuous and discrete variables
- Memory-optimized scenario generation
- Comprehensive summary statistics
"""

import math
import json
import gzip
import hashlib
import itertools
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import gc
import sys

# Import database modules
from cloud_database import CloudDatabase
from permutation_gridfs_storage import PermutationGridFSStorage

# ==================== Enhanced Type Definitions ====================

class VariableType(Enum):
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"
    CATEGORICAL = "categorical"

@dataclass
class VariableDefinition:
    """Definition of a variable for permutation"""
    name: str
    type: VariableType
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step_size: Optional[float] = None
    values: Optional[List[Union[str, float]]] = None
    priority: int = 1  # Higher priority variables permuted first

@dataclass
class BatchResult:
    """Result from processing a batch of scenarios"""
    batch_id: int
    scenarios: List[Dict[str, Any]]
    summary_stats: Dict[str, float]
    processing_time: float
    memory_usage: float

@dataclass
class PermutationSummary:
    """Summary statistics for permutation run"""
    total_scenarios: int
    viable_scenarios: int
    viability_rate: float
    execution_time: float
    memory_peak_mb: float
    best_scenario: Optional[Dict[str, Any]]
    worst_scenario: Optional[Dict[str, Any]]
    median_metrics: Dict[str, float]
    percentile_95_metrics: Dict[str, float]
    percentile_5_metrics: Dict[str, float]
    distribution_stats: Dict[str, Dict[str, float]]

# Import scenario classes from original engine
from permutation_engine import (
    Currency, AmortType, IndexationMode, RankingObjective,
    ScenarioState, KPI, WaterfallOutput, PermutationEngine
)

# ==================== Optimized Permutation Engine ====================

class PermutationEngineV2:
    """
    High-performance permutation engine with parallel processing
    and efficient memory management
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_permutations = config.get('MaxPermutations_108', 150000)
        self.batch_size = config.get('batch_size', 1000)
        self.max_workers = config.get('max_workers', min(8, mp.cpu_count()))
        self.storage = PermutationGridFSStorage()
        self.db = CloudDatabase()

        # Original engine for calculations
        self.calc_engine = PermutationEngine(config)

        # Performance tracking
        self.start_time = None
        self.peak_memory = 0

        print(f"[ENGINE V2] Initialized with {self.max_workers} workers, batch size {self.batch_size}")

    def execute(self,
                project_id: str,
                user_email: str,
                variables: List[VariableDefinition],
                base_scenario: Dict[str, Any],
                ranking_objective: str = "Composite",
                store_results: bool = True) -> Dict[str, Any]:
        """
        Main execution method for permutation engine

        Args:
            project_id: Unique project identifier
            user_email: User running the permutation
            variables: List of variables to permute
            base_scenario: Base scenario configuration
            ranking_objective: Ranking objective for scenarios
            store_results: Whether to store results in GridFS

        Returns:
            Execution results with summary and storage info
        """
        self.start_time = datetime.now()
        print(f"\n[ENGINE V2] Starting permutation execution")
        print(f"  Project: {project_id}")
        print(f"  Variables: {len(variables)}")
        print(f"  Objective: {ranking_objective}")

        try:
            # Generate scenario combinations
            scenario_generator = self._generate_scenarios(variables, base_scenario)

            # Process in batches
            all_results = []
            batch_summaries = []
            batch_id = 0

            current_batch = []
            total_processed = 0

            for scenario_params in scenario_generator:
                current_batch.append(scenario_params)

                if len(current_batch) >= self.batch_size:
                    # Process batch
                    batch_result = self._process_batch(
                        batch_id, current_batch, ranking_objective
                    )

                    all_results.extend(batch_result.scenarios)
                    batch_summaries.append(batch_result)

                    total_processed += len(current_batch)
                    print(f"[ENGINE V2] Processed batch {batch_id}: {len(current_batch)} scenarios (Total: {total_processed})")

                    current_batch = []
                    batch_id += 1

                    # Memory management
                    gc.collect()

                    # Check limits
                    if total_processed >= self.max_permutations:
                        print(f"[ENGINE V2] Reached maximum permutations limit: {self.max_permutations}")
                        break

            # Process final batch
            if current_batch:
                batch_result = self._process_batch(
                    batch_id, current_batch, ranking_objective
                )
                all_results.extend(batch_result.scenarios)
                batch_summaries.append(batch_result)
                total_processed += len(current_batch)

            # Calculate summary statistics
            summary = self._calculate_summary(all_results, batch_summaries)

            # Store results if requested
            storage_result = None
            if store_results and all_results:
                storage_result = self._store_batch_results(
                    project_id, user_email, all_results, summary
                )

            execution_time = (datetime.now() - self.start_time).total_seconds()

            print(f"\n[ENGINE V2] Execution completed in {execution_time:.2f}s")
            print(f"  Total scenarios: {len(all_results)}")
            print(f"  Viable scenarios: {summary.viable_scenarios}")
            print(f"  Viability rate: {summary.viability_rate:.1f}%")

            return {
                'success': True,
                'total_scenarios': len(all_results),
                'execution_time': execution_time,
                'summary': summary,
                'storage': storage_result,
                'batch_count': len(batch_summaries),
                'ranking_objective': ranking_objective
            }

        except Exception as e:
            print(f"[ENGINE V2] Execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            }

    def _generate_scenarios(self, variables: List[VariableDefinition],
                          base_scenario: Dict[str, Any]):
        """
        Memory-efficient generator for scenario combinations

        Yields scenario parameter dictionaries one at a time
        to avoid loading all combinations into memory
        """
        # Sort variables by priority for better early filtering
        sorted_variables = sorted(variables, key=lambda v: v.priority, reverse=True)

        # Build value ranges for each variable
        variable_ranges = {}
        total_combinations = 1

        for var in sorted_variables:
            if var.type == VariableType.CONTINUOUS:
                if var.min_value is None or var.max_value is None or var.step_size is None:
                    raise ValueError(f"Continuous variable {var.name} missing min/max/step")

                values = []
                current = var.min_value
                while current <= var.max_value:
                    values.append(current)
                    current += var.step_size

                variable_ranges[var.name] = values

            elif var.type == VariableType.DISCRETE:
                if var.values is None:
                    raise ValueError(f"Discrete variable {var.name} missing values list")
                variable_ranges[var.name] = var.values

            elif var.type == VariableType.CATEGORICAL:
                if var.values is None:
                    raise ValueError(f"Categorical variable {var.name} missing values list")
                variable_ranges[var.name] = var.values

            total_combinations *= len(variable_ranges[var.name])

        print(f"[ENGINE V2] Generating {min(total_combinations, self.max_permutations)} scenarios")

        # Generate combinations using itertools.product for memory efficiency
        variable_names = [var.name for var in sorted_variables]
        variable_values = [variable_ranges[name] for name in variable_names]

        count = 0
        for combination in itertools.product(*variable_values):
            if count >= self.max_permutations:
                break

            # Create scenario parameters
            scenario_params = base_scenario.copy()
            for name, value in zip(variable_names, combination):
                scenario_params[name] = value

            yield scenario_params
            count += 1

    def _process_batch(self, batch_id: int, scenarios: List[Dict[str, Any]],
                      ranking_objective: str) -> BatchResult:
        """
        Process a batch of scenarios using multiprocessing
        """
        start_time = datetime.now()

        # Split scenarios among workers
        chunk_size = max(1, len(scenarios) // self.max_workers)
        scenario_chunks = [
            scenarios[i:i + chunk_size]
            for i in range(0, len(scenarios), chunk_size)
        ]

        results = []

        # Use multiprocessing if we have multiple scenarios and workers
        if len(scenarios) > 1 and self.max_workers > 1:
            try:
                with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                    # Submit tasks
                    future_to_chunk = {
                        executor.submit(
                            process_scenario_chunk,
                            chunk,
                            self.config
                        ): chunk
                        for chunk in scenario_chunks
                    }

                    # Collect results
                    for future in as_completed(future_to_chunk):
                        chunk_results = future.result()
                        results.extend(chunk_results)

            except Exception as e:
                print(f"[ENGINE V2] Multiprocessing failed, falling back to sequential: {e}")
                # Fallback to sequential processing
                for chunk in scenario_chunks:
                    chunk_results = process_scenario_chunk(chunk, self.config)
                    results.extend(chunk_results)
        else:
            # Sequential processing for small batches
            for chunk in scenario_chunks:
                chunk_results = process_scenario_chunk(chunk, self.config)
                results.extend(chunk_results)

        # Calculate batch summary statistics
        viable_count = sum(1 for r in results if r.get('viable', False))

        summary_stats = {
            'viable_count': viable_count,
            'viability_rate': (viable_count / len(results)) * 100 if results else 0,
            'avg_senior_notional': np.mean([r['kpis']['SeniorNotional'] for r in results]) if results else 0,
            'avg_equity_irr': np.mean([r['kpis']['EquityIRR'] for r in results]) if results else 0,
            'avg_wacc': np.mean([r['kpis']['WACC'] for r in results]) if results else 0
        }

        processing_time = (datetime.now() - start_time).total_seconds()
        memory_usage = sys.getsizeof(results) / (1024 * 1024)  # MB

        return BatchResult(
            batch_id=batch_id,
            scenarios=results,
            summary_stats=summary_stats,
            processing_time=processing_time,
            memory_usage=memory_usage
        )

    def _calculate_scenario_metrics(self, scenario_params: Dict[str, Any]) -> Tuple[ScenarioState, KPI, bool]:
        """
        Calculate metrics for a single scenario
        This method is called within worker processes
        """
        try:
            # Create scenario state
            scenario = ScenarioState(**scenario_params)

            # Calculate KPIs using original engine
            kpis = self.calc_engine.calculate_kpis(scenario)

            # Determine viability
            viable = (
                kpis.DSCR_Min >= 1.0 and
                kpis.EquityIRR >= 10 and
                kpis.SeniorNotional > 0
            )

            return scenario, kpis, viable

        except Exception as e:
            print(f"[ENGINE V2] Error calculating scenario metrics: {e}")
            # Return default values for failed scenarios
            scenario = ScenarioState()
            kpis = KPI(SeniorNotional=0)
            return scenario, kpis, False

    def _store_batch_results(self, project_id: str, user_email: str,
                            results: List[Dict[str, Any]],
                            summary: PermutationSummary) -> Dict[str, Any]:
        """
        Store batch results using GridFS with compression
        """
        try:
            # Prepare data for storage
            storage_data = {
                'project_id': project_id,
                'user_email': user_email,
                'generated_at': datetime.now().isoformat(),
                'engine_version': '2.0.0',
                'summary': {
                    'total_scenarios': summary.total_scenarios,
                    'viable_scenarios': summary.viable_scenarios,
                    'viability_rate': summary.viability_rate,
                    'execution_time': summary.execution_time,
                    'memory_peak_mb': summary.memory_peak_mb
                },
                'scenarios': results[:10000],  # Limit stored scenarios to 10k for performance
                'statistics': {
                    'best_scenario': summary.best_scenario,
                    'worst_scenario': summary.worst_scenario,
                    'median_metrics': summary.median_metrics,
                    'percentile_95_metrics': summary.percentile_95_metrics,
                    'percentile_5_metrics': summary.percentile_5_metrics,
                    'distribution_stats': summary.distribution_stats
                }
            }

            # Store using GridFS
            storage_result = self.storage.save_permutation_results(
                project_id, user_email, storage_data
            )

            if storage_result['success']:
                print(f"[ENGINE V2] Results stored successfully:")
                print(f"  Size: {storage_result['size_mb']} MB")
                print(f"  Compression: {storage_result['compression_ratio']}%")

            return storage_result

        except Exception as e:
            print(f"[ENGINE V2] Failed to store results: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_summary(self, results: List[Dict[str, Any]],
                          batch_summaries: List[BatchResult]) -> PermutationSummary:
        """
        Calculate comprehensive summary statistics
        """
        if not results:
            return PermutationSummary(
                total_scenarios=0,
                viable_scenarios=0,
                viability_rate=0,
                execution_time=0,
                memory_peak_mb=0,
                best_scenario=None,
                worst_scenario=None,
                median_metrics={},
                percentile_95_metrics={},
                percentile_5_metrics={},
                distribution_stats={}
            )

        # Basic counts
        total_scenarios = len(results)
        viable_scenarios = sum(1 for r in results if r.get('viable', False))
        viability_rate = (viable_scenarios / total_scenarios) * 100

        # Performance metrics
        execution_time = (datetime.now() - self.start_time).total_seconds()
        memory_peak_mb = max(batch.memory_usage for batch in batch_summaries) if batch_summaries else 0

        # Extract metrics for statistical analysis
        viable_results = [r for r in results if r.get('viable', False)]

        if viable_results:
            # Key metrics arrays
            senior_notionals = [r['kpis']['SeniorNotional'] for r in viable_results]
            equity_irrs = [r['kpis']['EquityIRR'] for r in viable_results]
            waccs = [r['kpis']['WACC'] for r in viable_results]
            dscr_mins = [r['kpis']['DSCR_Min'] for r in viable_results]

            # Find best and worst scenarios
            best_idx = np.argmax([r.get('composite_score', 0) for r in viable_results])
            worst_idx = np.argmin([r.get('composite_score', 0) for r in viable_results])

            best_scenario = viable_results[best_idx]
            worst_scenario = viable_results[worst_idx]

            # Statistical measures
            median_metrics = {
                'senior_notional': float(np.median(senior_notionals)),
                'equity_irr': float(np.median(equity_irrs)),
                'wacc': float(np.median(waccs)),
                'dscr_min': float(np.median(dscr_mins))
            }

            percentile_95_metrics = {
                'senior_notional': float(np.percentile(senior_notionals, 95)),
                'equity_irr': float(np.percentile(equity_irrs, 95)),
                'wacc': float(np.percentile(waccs, 5)),  # Lower is better for WACC
                'dscr_min': float(np.percentile(dscr_mins, 95))
            }

            percentile_5_metrics = {
                'senior_notional': float(np.percentile(senior_notionals, 5)),
                'equity_irr': float(np.percentile(equity_irrs, 5)),
                'wacc': float(np.percentile(waccs, 95)),  # Higher is worse for WACC
                'dscr_min': float(np.percentile(dscr_mins, 5))
            }

            # Distribution statistics
            distribution_stats = {
                'senior_notional': {
                    'mean': float(np.mean(senior_notionals)),
                    'std': float(np.std(senior_notionals)),
                    'min': float(np.min(senior_notionals)),
                    'max': float(np.max(senior_notionals))
                },
                'equity_irr': {
                    'mean': float(np.mean(equity_irrs)),
                    'std': float(np.std(equity_irrs)),
                    'min': float(np.min(equity_irrs)),
                    'max': float(np.max(equity_irrs))
                },
                'wacc': {
                    'mean': float(np.mean(waccs)),
                    'std': float(np.std(waccs)),
                    'min': float(np.min(waccs)),
                    'max': float(np.max(waccs))
                },
                'dscr_min': {
                    'mean': float(np.mean(dscr_mins)),
                    'std': float(np.std(dscr_mins)),
                    'min': float(np.min(dscr_mins)),
                    'max': float(np.max(dscr_mins))
                }
            }
        else:
            best_scenario = worst_scenario = None
            median_metrics = percentile_95_metrics = percentile_5_metrics = {}
            distribution_stats = {}

        return PermutationSummary(
            total_scenarios=total_scenarios,
            viable_scenarios=viable_scenarios,
            viability_rate=viability_rate,
            execution_time=execution_time,
            memory_peak_mb=memory_peak_mb,
            best_scenario=best_scenario,
            worst_scenario=worst_scenario,
            median_metrics=median_metrics,
            percentile_95_metrics=percentile_95_metrics,
            percentile_5_metrics=percentile_5_metrics,
            distribution_stats=distribution_stats
        )

    def get_stored_results(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load stored permutation results for a project"""
        return self.storage.load_permutation_results(project_id)

    def list_stored_results(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all stored permutation results"""
        return self.storage.list_results(user_email)

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return self.storage.get_storage_stats()

# ==================== Worker Functions ====================

def process_scenario_chunk(scenarios: List[Dict[str, Any]],
                          config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a chunk of scenarios in a worker process
    This function must be defined at module level for multiprocessing
    """
    # Create engine instance in worker process
    engine = PermutationEngine(config)
    results = []

    for i, scenario_params in enumerate(scenarios):
        try:
            # Create scenario state
            scenario = ScenarioState(**{
                k: v for k, v in scenario_params.items()
                if k in ScenarioState.__dataclass_fields__
            })

            # Calculate KPIs
            kpis = engine.calculate_kpis(scenario)

            # Determine viability
            viable = (
                kpis.DSCR_Min >= 1.0 and
                kpis.EquityIRR >= 10 and
                kpis.SeniorNotional > 0
            )

            # Convert KPI to dict for serialization
            kpi_dict = {
                'SeniorNotional': kpis.SeniorNotional,
                'MezzNotional': kpis.MezzNotional,
                'EquityNotional': kpis.EquityNotional,
                'Day1Cash': kpis.Day1Cash,
                'WACC': kpis.WACC,
                'EquityIRR': kpis.EquityIRR,
                'SeniorRating': kpis.SeniorRating,
                'SeniorWAL': kpis.SeniorWAL,
                'DSCR_Min': kpis.DSCR_Min,
                'DSCR_Avg': kpis.DSCR_Avg,
                'RepoEligible': kpis.RepoEligible
            }

            # Calculate composite score for ranking
            rating_score = {'AAA': 1.0, 'AA': 0.8, 'A': 0.6, 'BBB': 0.4, 'BB': 0.2}.get(kpis.SeniorRating, 0)
            composite_score = (
                0.35 * (kpis.SeniorNotional / 1e8) +  # Normalize to £100M
                0.25 * (20 - kpis.WACC) / 20 +  # Lower is better
                0.20 * (kpis.Day1Cash / 1e8) +
                0.10 * min(kpis.DSCR_Min / 2, 1) +  # Cap at 2.0
                0.10 * rating_score
            )

            result = {
                'id': f"scenario_{i}",
                'inputs': scenario_params,
                'kpis': kpi_dict,
                'viable': viable,
                'composite_score': composite_score
            }

            results.append(result)

        except Exception as e:
            print(f"[WORKER] Error processing scenario {i}: {e}")
            # Add failed scenario with default values
            results.append({
                'id': f"scenario_{i}",
                'inputs': scenario_params,
                'kpis': {
                    'SeniorNotional': 0,
                    'MezzNotional': 0,
                    'EquityNotional': 0,
                    'Day1Cash': 0,
                    'WACC': 999,
                    'EquityIRR': -999,
                    'SeniorRating': 'D',
                    'SeniorWAL': 0,
                    'DSCR_Min': 0,
                    'DSCR_Avg': 0,
                    'RepoEligible': False
                },
                'viable': False,
                'composite_score': 0
            })

    return results

# ==================== API Interface ====================

def run_permutation_engine_v2(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced API entry point for the optimized permutation engine

    Expected config structure:
    {
        'project_id': str,
        'user_email': str,
        'variables': [
            {
                'name': str,
                'type': 'continuous|discrete|categorical',
                'min_value': float,  # for continuous
                'max_value': float,  # for continuous
                'step_size': float,  # for continuous
                'values': [values],  # for discrete/categorical
                'priority': int
            }
        ],
        'base_scenario': dict,
        'ranking_objective': str,
        'batch_size': int,
        'max_workers': int,
        'MaxPermutations_108': int
    }
    """
    try:
        # Extract parameters
        project_id = config.get('project_id', 'unknown')
        user_email = config.get('user_email', 'unknown')
        variables_config = config.get('variables', [])
        base_scenario = config.get('base_scenario', {})
        ranking_objective = config.get('RankingObjective_109', 'Composite')

        # Create variable definitions
        variables = []
        for var_config in variables_config:
            var_type = VariableType(var_config['type'])

            variable = VariableDefinition(
                name=var_config['name'],
                type=var_type,
                min_value=var_config.get('min_value'),
                max_value=var_config.get('max_value'),
                step_size=var_config.get('step_size'),
                values=var_config.get('values'),
                priority=var_config.get('priority', 1)
            )
            variables.append(variable)

        # Create and run engine
        engine = PermutationEngineV2(config)

        result = engine.execute(
            project_id=project_id,
            user_email=user_email,
            variables=variables,
            base_scenario=base_scenario,
            ranking_objective=ranking_objective,
            store_results=config.get('store_results', True)
        )

        return result

    except Exception as e:
        print(f"[API] Permutation engine v2 failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'engine_version': '2.0.0'
        }

# ==================== Example Usage ====================

def create_example_config() -> Dict[str, Any]:
    """Create example configuration for testing"""
    return {
        'project_id': 'test_project_001',
        'user_email': 'test@example.com',
        'variables': [
            {
                'name': 'GrossMonthlyRent_07',
                'type': 'continuous',
                'min_value': 2000000,
                'max_value': 3000000,
                'step_size': 100000,
                'priority': 3
            },
            {
                'name': 'OPEX_08',
                'type': 'continuous',
                'min_value': 20.0,
                'max_value': 35.0,
                'step_size': 2.5,
                'priority': 2
            },
            {
                'name': 'SeniorCoupon_38',
                'type': 'discrete',
                'values': [4.0, 4.5, 5.0, 5.5, 6.0],
                'priority': 1
            },
            {
                'name': 'SeniorAmortType_40',
                'type': 'categorical',
                'values': ['Annuity', 'Bullet', 'Sculpted'],
                'priority': 1
            }
        ],
        'base_scenario': {
            'Currency_01': 'GBP',
            'GrossITLoad_02': 100.0,
            'PUE_03': 1.30,
            'CapexCostPrice_04': 7500000,
            'CapexMarketRate_05': 9000000,
            'LandPurchaseFees_06': 20000000,
            'TargetDSCRSenior_37': 1.30,
            'SeniorTenorY_39': 25,
            'OPEXMode_17': 'PercentOfRevenue',
            'IndexationMode_18': 'Flat',
            'LeaseTermYears_22': 25,
            'BaseCurveShift_bps_28': 0,
            'CreditSpreadAAA_bps_29': 70,
            'InflationSpot_33': 2.0,
            'CPI_FloorPct_63': 1.0,
            'CPI_CapPct_64': 4.0,
            'EscalatorFixedPct_65': 2.0,
            'OPEX_StressPct_84': 10.0,
            'Rent_DownsidePct_85': 10.0
        },
        'RankingObjective_109': 'Composite',
        'MaxPermutations_108': 50000,
        'batch_size': 1000,
        'max_workers': 4,
        'store_results': True
    }

if __name__ == "__main__":
    # Example execution
    print("Atlas Forge - Permutation Engine v2.0.0")
    print("High-performance permutation engine with multiprocessing")

    example_config = create_example_config()
    result = run_permutation_engine_v2(example_config)

    if result['success']:
        print(f"\nExecution completed successfully!")
        print(f"Total scenarios: {result['total_scenarios']}")
        print(f"Execution time: {result['execution_time']:.2f}s")
        if result.get('storage'):
            print(f"Storage: {result['storage']['size_mb']} MB")
    else:
        print(f"\nExecution failed: {result['error']}")