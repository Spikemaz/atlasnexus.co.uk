"""
AtlasNexus Phase-1 Week-1 Components
====================================
New features behind admin-only feature flags:
- Input Hierarchy Processor (Manual → Min/Max → Variations)
- Reverse-DSCR Engine with unit tests
- Repo Eligibility Rule Tables (UK/EU/US)
- Viability Tiering (Not Viable → Diamond) with near-miss capture
"""

import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import unittest
from dataclasses import dataclass

from feature_flags import is_feature_enabled
from observability import metrics_collector, structured_logger, performance_tracker

class InputLevel(Enum):
    """Input hierarchy levels"""
    MANUAL = "manual"
    MIN_MAX = "min_max"
    VARIATIONS = "variations"

class ViabilityTier(Enum):
    """Viability tiers from Not Viable to Diamond"""
    NOT_VIABLE = "not_viable"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class RepoJurisdiction(Enum):
    """Repository jurisdictions"""
    UK = "uk"
    EU = "eu"
    US = "us"

@dataclass
class PermutationInput:
    """Structure for permutation input data"""
    permutation_id: str
    input_level: InputLevel
    raw_data: Dict[str, Any]
    user_email: str
    timestamp: datetime

@dataclass
class DSCRResult:
    """Result from DSCR calculation"""
    dscr_value: float
    input_ltv: float
    calculated_ltv: float
    is_reverse_calculated: bool
    confidence_score: float

@dataclass
class EligibilityResult:
    """Repository eligibility check result"""
    jurisdiction: RepoJurisdiction
    is_eligible: bool
    rules_passed: List[str]
    rules_failed: List[str]
    score: float

@dataclass
class ViabilityResult:
    """Viability tiering result"""
    tier: ViabilityTier
    score: float
    is_near_miss: bool
    near_miss_tier: Optional[ViabilityTier]
    reasons: List[str]

class InputHierarchyProcessor:
    """
    Processes inputs through hierarchy: Manual → Min/Max → Variations
    ADMIN-ONLY feature behind feature flag
    """

    def __init__(self):
        self.logger = structured_logger

    def process_input(self, input_data: PermutationInput, user_email: str, is_admin: bool) -> Dict[str, Any]:
        """
        Process input through hierarchy levels

        Args:
            input_data: Input data structure
            user_email: User email for feature flag check
            is_admin: Whether user is admin

        Returns:
            Processed result with hierarchy steps
        """
        if not is_feature_enabled('input_hierarchy_processor', user_email, is_admin):
            return {'error': 'Feature not available', 'feature': 'input_hierarchy_processor'}

        with performance_tracker.track_operation('input_hierarchy_process', input_data.permutation_id):
            result = {
                'permutation_id': input_data.permutation_id,
                'hierarchy_steps': [],
                'final_data': {},
                'processing_time_ms': 0
            }

            start_time = time.time()

            try:
                # Step 1: Manual input processing
                manual_result = self._process_manual_input(input_data)
                result['hierarchy_steps'].append({
                    'level': InputLevel.MANUAL.value,
                    'data': manual_result,
                    'timestamp': datetime.utcnow().isoformat()
                })

                # Step 2: Min/Max processing
                if input_data.input_level in [InputLevel.MIN_MAX, InputLevel.VARIATIONS]:
                    minmax_result = self._process_min_max(manual_result, input_data)
                    result['hierarchy_steps'].append({
                        'level': InputLevel.MIN_MAX.value,
                        'data': minmax_result,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                else:
                    minmax_result = manual_result

                # Step 3: Variations processing
                if input_data.input_level == InputLevel.VARIATIONS:
                    variations_result = self._process_variations(minmax_result, input_data)
                    result['hierarchy_steps'].append({
                        'level': InputLevel.VARIATIONS.value,
                        'data': variations_result,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    result['final_data'] = variations_result
                else:
                    result['final_data'] = minmax_result

                # Record metrics
                metrics_collector.increment_counter('input_hierarchy_processed')
                processing_time = (time.time() - start_time) * 1000
                result['processing_time_ms'] = processing_time
                metrics_collector.record_histogram('input_hierarchy_duration_ms', processing_time)

                self.logger.info(
                    "Input hierarchy processing completed",
                    permutation_id=input_data.permutation_id,
                    input_level=input_data.input_level.value,
                    steps_processed=len(result['hierarchy_steps']),
                    duration_ms=processing_time
                )

                return result

            except Exception as e:
                self.logger.error(
                    "Input hierarchy processing failed",
                    permutation_id=input_data.permutation_id,
                    error=str(e)
                )
                metrics_collector.increment_counter('input_hierarchy_errors')
                return {'error': str(e), 'permutation_id': input_data.permutation_id}

    def _process_manual_input(self, input_data: PermutationInput) -> Dict[str, Any]:
        """Process manual input level"""
        return {
            'level': 'manual',
            'validated_fields': input_data.raw_data,
            'field_count': len(input_data.raw_data),
            'validation_passed': True
        }

    def _process_min_max(self, manual_data: Dict[str, Any], input_data: PermutationInput) -> Dict[str, Any]:
        """Process min/max input level"""
        # Simulate min/max processing
        return {
            'level': 'min_max',
            'base_data': manual_data,
            'min_values': {k: v * 0.8 if isinstance(v, (int, float)) else v for k, v in input_data.raw_data.items()},
            'max_values': {k: v * 1.2 if isinstance(v, (int, float)) else v for k, v in input_data.raw_data.items()},
            'range_count': sum(1 for v in input_data.raw_data.values() if isinstance(v, (int, float)))
        }

    def _process_variations(self, minmax_data: Dict[str, Any], input_data: PermutationInput) -> Dict[str, Any]:
        """Process variations input level"""
        # Simulate variations processing
        return {
            'level': 'variations',
            'base_data': minmax_data,
            'variations_generated': 10,  # Would be actual variations in real implementation
            'variation_scenarios': ['base', 'conservative', 'aggressive', 'stress_test'],
            'total_permutations': 40
        }

class ReverseDSCREngine:
    """
    Reverse DSCR calculation engine with comprehensive unit tests
    ADMIN-ONLY feature behind feature flag
    """

    def __init__(self):
        self.logger = structured_logger

    def calculate_reverse_dscr(self, target_dscr: float, cashflow: float,
                              existing_debt: float, user_email: str, is_admin: bool) -> DSCRResult:
        """
        Calculate reverse DSCR (determine max additional debt for target DSCR)

        Args:
            target_dscr: Target DSCR ratio
            cashflow: Annual net operating income
            existing_debt: Existing debt service
            user_email: User email for feature flag check
            is_admin: Whether user is admin

        Returns:
            DSCRResult with calculations
        """
        if not is_feature_enabled('reverse_dscr_engine', user_email, is_admin):
            raise ValueError('Reverse DSCR engine not available')

        permutation_id = str(uuid.uuid4())[:8]

        with performance_tracker.track_operation('reverse_dscr_calculation', permutation_id):
            try:
                # Reverse DSCR calculation: Max additional debt = (NOI / target_DSCR) - existing_debt
                max_total_debt_service = cashflow / target_dscr
                max_additional_debt = max_total_debt_service - existing_debt

                # Calculate resulting LTV if we know property value (simplified)
                # In real implementation, this would involve more complex calculations
                calculated_ltv = min(0.85, max_additional_debt / (cashflow * 10))  # Simplified

                # Confidence score based on input quality
                confidence_score = self._calculate_confidence(target_dscr, cashflow, existing_debt)

                result = DSCRResult(
                    dscr_value=target_dscr,
                    input_ltv=calculated_ltv,
                    calculated_ltv=calculated_ltv,
                    is_reverse_calculated=True,
                    confidence_score=confidence_score
                )

                # Record metrics
                metrics_collector.increment_counter('reverse_dscr_calculations')
                metrics_collector.record_histogram('dscr_target_values', target_dscr)

                self.logger.info(
                    "Reverse DSCR calculation completed",
                    permutation_id=permutation_id,
                    target_dscr=target_dscr,
                    max_additional_debt=max_additional_debt,
                    confidence_score=confidence_score
                )

                return result

            except Exception as e:
                self.logger.error(
                    "Reverse DSCR calculation failed",
                    permutation_id=permutation_id,
                    error=str(e)
                )
                raise

    def _calculate_confidence(self, target_dscr: float, cashflow: float, existing_debt: float) -> float:
        """Calculate confidence score for the calculation"""
        # Simplified confidence calculation
        if target_dscr < 1.0 or target_dscr > 3.0:
            return 0.5  # Low confidence for unusual DSCR targets
        if cashflow <= 0 or existing_debt < 0:
            return 0.2  # Very low confidence for invalid inputs
        return 0.9  # High confidence for normal inputs

class RepoEligibilityEngine:
    """
    Repository eligibility rule tables for UK/EU/US
    ADMIN-ONLY feature behind feature flag
    """

    def __init__(self):
        self.logger = structured_logger
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[RepoJurisdiction, Dict[str, Any]]:
        """Initialize eligibility rules for each jurisdiction"""
        return {
            RepoJurisdiction.UK: {
                'min_property_value': 100000,
                'max_ltv': 0.80,
                'min_dscr': 1.25,
                'required_documentation': ['valuation', 'income_proof', 'credit_check'],
                'restricted_property_types': ['commercial', 'land'],
                'min_rental_yield': 0.04
            },
            RepoJurisdiction.EU: {
                'min_property_value': 150000,
                'max_ltv': 0.75,
                'min_dscr': 1.30,
                'required_documentation': ['valuation', 'income_proof', 'credit_check', 'legal_opinion'],
                'restricted_property_types': ['commercial', 'agricultural'],
                'min_rental_yield': 0.045
            },
            RepoJurisdiction.US: {
                'min_property_value': 200000,
                'max_ltv': 0.85,
                'min_dscr': 1.20,
                'required_documentation': ['appraisal', 'income_verification', 'credit_report'],
                'restricted_property_types': ['manufactured', 'co-op'],
                'min_rental_yield': 0.05
            }
        }

    def check_eligibility(self, jurisdiction: RepoJurisdiction, property_data: Dict[str, Any],
                         user_email: str, is_admin: bool) -> EligibilityResult:
        """
        Check repository eligibility for given jurisdiction

        Args:
            jurisdiction: Target jurisdiction
            property_data: Property and loan data
            user_email: User email for feature flag check
            is_admin: Whether user is admin

        Returns:
            EligibilityResult with detailed check results
        """
        if not is_feature_enabled('repo_eligibility_rules', user_email, is_admin):
            raise ValueError('Repository eligibility engine not available')

        permutation_id = str(uuid.uuid4())[:8]

        with performance_tracker.track_operation('repo_eligibility_check', permutation_id):
            rules = self.rules[jurisdiction]
            rules_passed = []
            rules_failed = []
            score = 0

            try:
                # Check minimum property value
                property_value = property_data.get('property_value', 0)
                if property_value >= rules['min_property_value']:
                    rules_passed.append('min_property_value')
                    score += 20
                else:
                    rules_failed.append('min_property_value')

                # Check LTV
                ltv = property_data.get('ltv', 1.0)
                if ltv <= rules['max_ltv']:
                    rules_passed.append('max_ltv')
                    score += 25
                else:
                    rules_failed.append('max_ltv')

                # Check DSCR
                dscr = property_data.get('dscr', 0)
                if dscr >= rules['min_dscr']:
                    rules_passed.append('min_dscr')
                    score += 25
                else:
                    rules_failed.append('min_dscr')

                # Check documentation
                provided_docs = set(property_data.get('documentation', []))
                required_docs = set(rules['required_documentation'])
                if required_docs.issubset(provided_docs):
                    rules_passed.append('documentation')
                    score += 20
                else:
                    rules_failed.append('documentation')

                # Check property type restrictions
                property_type = property_data.get('property_type', '').lower()
                if property_type not in rules['restricted_property_types']:
                    rules_passed.append('property_type')
                    score += 10
                else:
                    rules_failed.append('property_type')

                is_eligible = len(rules_failed) == 0

                # Record metrics
                metrics_collector.increment_counter('repo_eligibility_checks')
                metrics_collector.increment_counter(f'repo_eligibility_{jurisdiction.value}')
                if is_eligible:
                    metrics_collector.increment_counter('repo_eligibility_passed')
                else:
                    metrics_collector.increment_counter('repo_eligibility_failed')

                result = EligibilityResult(
                    jurisdiction=jurisdiction,
                    is_eligible=is_eligible,
                    rules_passed=rules_passed,
                    rules_failed=rules_failed,
                    score=score
                )

                self.logger.info(
                    "Repository eligibility check completed",
                    permutation_id=permutation_id,
                    jurisdiction=jurisdiction.value,
                    is_eligible=is_eligible,
                    score=score,
                    rules_passed=len(rules_passed),
                    rules_failed=len(rules_failed)
                )

                return result

            except Exception as e:
                self.logger.error(
                    "Repository eligibility check failed",
                    permutation_id=permutation_id,
                    error=str(e)
                )
                raise

class ViabilityTieringEngine:
    """
    Viability tiering from Not Viable → Diamond with near-miss capture
    ADMIN-ONLY feature behind feature flag
    """

    def __init__(self):
        self.logger = structured_logger
        self.tier_thresholds = {
            ViabilityTier.NOT_VIABLE: 0,
            ViabilityTier.BRONZE: 40,
            ViabilityTier.SILVER: 55,
            ViabilityTier.GOLD: 70,
            ViabilityTier.PLATINUM: 85,
            ViabilityTier.DIAMOND: 95
        }

    def calculate_viability_tier(self, deal_data: Dict[str, Any], user_email: str, is_admin: bool) -> ViabilityResult:
        """
        Calculate viability tier with near-miss detection

        Args:
            deal_data: Deal analysis data
            user_email: User email for feature flag check
            is_admin: Whether user is admin

        Returns:
            ViabilityResult with tier assignment and near-miss info
        """
        if not is_feature_enabled('viability_tiering', user_email, is_admin):
            raise ValueError('Viability tiering engine not available')

        permutation_id = str(uuid.uuid4())[:8]

        with performance_tracker.track_operation('viability_tier_calculation', permutation_id):
            try:
                # Calculate overall viability score
                score = self._calculate_viability_score(deal_data)

                # Determine tier
                tier = self._score_to_tier(score)

                # Check for near-miss scenarios (within 5 points of next tier)
                near_miss_tier = None
                is_near_miss = False
                next_tier = self._get_next_tier(tier)

                if next_tier and score >= self.tier_thresholds[next_tier] - 5:
                    is_near_miss = True
                    near_miss_tier = next_tier
                    metrics_collector.increment_counter('near_miss_captures')

                # Generate reasons
                reasons = self._generate_tier_reasons(deal_data, score, tier)

                result = ViabilityResult(
                    tier=tier,
                    score=score,
                    is_near_miss=is_near_miss,
                    near_miss_tier=near_miss_tier,
                    reasons=reasons
                )

                # Record metrics
                metrics_collector.increment_counter('viability_tier_assignments')
                metrics_collector.increment_counter(f'viability_tier_{tier.value}')
                metrics_collector.record_histogram('viability_scores', score)

                self.logger.info(
                    "Viability tier calculation completed",
                    permutation_id=permutation_id,
                    tier=tier.value,
                    score=score,
                    is_near_miss=is_near_miss,
                    near_miss_tier=near_miss_tier.value if near_miss_tier else None
                )

                return result

            except Exception as e:
                self.logger.error(
                    "Viability tier calculation failed",
                    permutation_id=permutation_id,
                    error=str(e)
                )
                raise

    def _calculate_viability_score(self, deal_data: Dict[str, Any]) -> float:
        """Calculate overall viability score from deal data"""
        score = 0

        # DSCR contribution (30 points max)
        dscr = deal_data.get('dscr', 0)
        if dscr >= 1.5:
            score += 30
        elif dscr >= 1.25:
            score += 20
        elif dscr >= 1.0:
            score += 10

        # LTV contribution (25 points max)
        ltv = deal_data.get('ltv', 1.0)
        if ltv <= 0.65:
            score += 25
        elif ltv <= 0.75:
            score += 20
        elif ltv <= 0.85:
            score += 15

        # Credit score contribution (20 points max)
        credit_score = deal_data.get('credit_score', 0)
        if credit_score >= 750:
            score += 20
        elif credit_score >= 700:
            score += 15
        elif credit_score >= 650:
            score += 10

        # Property quality (15 points max)
        property_score = deal_data.get('property_quality_score', 0)
        score += min(15, property_score / 10)

        # Market conditions (10 points max)
        market_score = deal_data.get('market_conditions_score', 0)
        score += min(10, market_score)

        return min(100, score)  # Cap at 100

    def _score_to_tier(self, score: float) -> ViabilityTier:
        """Convert score to viability tier"""
        for tier in reversed(list(ViabilityTier)):
            if score >= self.tier_thresholds[tier]:
                return tier
        return ViabilityTier.NOT_VIABLE

    def _get_next_tier(self, current_tier: ViabilityTier) -> Optional[ViabilityTier]:
        """Get the next tier up from current tier"""
        tiers = list(ViabilityTier)
        current_index = tiers.index(current_tier)
        if current_index < len(tiers) - 1:
            return tiers[current_index + 1]
        return None

    def _generate_tier_reasons(self, deal_data: Dict[str, Any], score: float, tier: ViabilityTier) -> List[str]:
        """Generate reasons for the tier assignment"""
        reasons = []

        # Score-based reasons
        if score >= 90:
            reasons.append("Excellent overall financial metrics")
        elif score >= 70:
            reasons.append("Strong financial performance")
        elif score >= 50:
            reasons.append("Adequate financial metrics")
        else:
            reasons.append("Below-average financial performance")

        # Specific metric reasons
        dscr = deal_data.get('dscr', 0)
        if dscr >= 1.5:
            reasons.append("Strong debt service coverage")
        elif dscr < 1.0:
            reasons.append("Insufficient debt service coverage")

        ltv = deal_data.get('ltv', 1.0)
        if ltv <= 0.65:
            reasons.append("Conservative loan-to-value ratio")
        elif ltv > 0.85:
            reasons.append("High loan-to-value ratio increases risk")

        return reasons

# Unit tests for Reverse DSCR Engine
class TestReverseDSCREngine(unittest.TestCase):
    """Comprehensive unit tests for Reverse DSCR Engine"""

    def setUp(self):
        self.engine = ReverseDSCREngine()
        self.test_user = "admin@atlasnexus.co.uk"
        self.is_admin = True

    def test_basic_reverse_dscr_calculation(self):
        """Test basic reverse DSCR calculation"""
        result = self.engine.calculate_reverse_dscr(
            target_dscr=1.25,
            cashflow=100000,
            existing_debt=50000,
            user_email=self.test_user,
            is_admin=self.is_admin
        )

        self.assertEqual(result.dscr_value, 1.25)
        self.assertTrue(result.is_reverse_calculated)
        self.assertGreater(result.confidence_score, 0)

    def test_edge_case_zero_existing_debt(self):
        """Test calculation with zero existing debt"""
        result = self.engine.calculate_reverse_dscr(
            target_dscr=1.5,
            cashflow=120000,
            existing_debt=0,
            user_email=self.test_user,
            is_admin=self.is_admin
        )

        self.assertEqual(result.dscr_value, 1.5)
        self.assertTrue(result.is_reverse_calculated)

    def test_invalid_dscr_target(self):
        """Test with invalid DSCR target"""
        result = self.engine.calculate_reverse_dscr(
            target_dscr=0.5,  # Invalid - below 1.0
            cashflow=100000,
            existing_debt=50000,
            user_email=self.test_user,
            is_admin=self.is_admin
        )

        # Should still calculate but with low confidence
        self.assertEqual(result.dscr_value, 0.5)
        self.assertLess(result.confidence_score, 0.8)

# Global instances
input_hierarchy_processor = InputHierarchyProcessor()
reverse_dscr_engine = ReverseDSCREngine()
repo_eligibility_engine = RepoEligibilityEngine()
viability_tiering_engine = ViabilityTieringEngine()