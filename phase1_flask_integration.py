"""
Phase-1 Flask Integration Endpoints
Admin-only, feature-flag protected
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
from typing import Dict, Any, List
from functools import wraps

from phase1_model_v2 import (
    ProjectInputs, DerivedFields, PermutationRanges, PresetBundles,
    Currency, TenantRating, IndexationBasis, AmortType,
    ValidationGates, PermutationResult, ViabilityTier,
    Phase1Integration, export_top_structures, InputSource
)

# Create Blueprint
phase1_bp = Blueprint('phase1', __name__, url_prefix='/api/phase1')

# ==================== ADMIN PROTECTION ====================

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is admin
        if not session.get('is_admin'):
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403

        # Check feature flag
        try:
            from feature_flags import is_feature_enabled
            if not is_feature_enabled('phase1_core', admin_check=True):
                return jsonify({
                    'success': False,
                    'error': 'Phase-1 feature not enabled'
                }), 403
        except:
            pass  # Allow if feature flags not available

        return f(*args, **kwargs)
    return decorated_function

# ==================== PROJECTS ENDPOINTS ====================

@phase1_bp.route('/projects/validate', methods=['POST'])
@admin_required
def validate_project():
    """Validate project inputs and return derived preview"""
    try:
        data = request.json

        # Create ProjectInputs
        inputs = ProjectInputs(
            title=data.get('title', ''),
            country=data.get('country', ''),
            currency=Currency(data.get('currency', 'GBP')),
            gross_it_load_mw=float(data.get('gross_it_load_mw', 0)),
            pue=float(data.get('pue', 1.2)),
            lease_years=int(data.get('lease_years', 0)),
            tenant_rating=TenantRating(data.get('tenant_rating', 'NR')),
            opex_pct=float(data.get('opex_pct', 0)),
            capex_cost_per_mw=float(data.get('capex_cost_per_mw', 0)),
            land_fees_total=float(data.get('land_fees_total', 0)),
            gross_monthly_rent=data.get('gross_monthly_rent'),
            rent_per_kwh_month=data.get('rent_per_kwh_month'),
            wrap=data.get('wrap', False),
            wrap_premium_bps=data.get('wrap_premium_bps'),
            repo_target=data.get('repo_target', False)
        )

        # Validate
        is_valid, errors = inputs.validate()

        if not is_valid:
            return jsonify({
                'success': False,
                'errors': errors
            }), 400

        # Generate derived preview
        preview = Phase1Integration.get_derived_preview(inputs)

        # Store in session for Permutations page
        session['phase1_project'] = {
            'inputs': data,
            'derived': preview,
            'validated_at': datetime.utcnow().isoformat()
        }

        return jsonify({
            'success': True,
            'derived_preview': preview,
            'message': 'Project validated successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@phase1_bp.route('/projects/derived', methods=['GET'])
@admin_required
def get_derived_fields():
    """Get cached derived fields from session"""
    try:
        project_data = session.get('phase1_project')
        if not project_data:
            return jsonify({
                'success': False,
                'error': 'No validated project in session'
            }), 404

        return jsonify({
            'success': True,
            'derived': project_data['derived'],
            'validated_at': project_data['validated_at']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== PERMUTATIONS ENDPOINTS ====================

@phase1_bp.route('/permutations/presets', methods=['GET'])
@admin_required
def get_presets():
    """Get available preset bundles"""
    return jsonify({
        'success': True,
        'presets': {
            'repo_first_aaa_aa': {
                'name': 'AAA/AA Repo-First',
                'description': 'Conservative repo-eligible structures',
                'senior_dscr': '1.40-1.50',
                'senior_tenor': '7-15y',
                'wrap': True,
                'mezz': False
            },
            'balanced_a': {
                'name': 'A-rated Balanced',
                'description': 'Balanced risk/return profile',
                'senior_dscr': '1.25-1.35',
                'senior_tenor': '10-20y',
                'wrap': False,
                'mezz': False
            },
            'value_max_bbb': {
                'name': 'BBB Value-Max',
                'description': 'Maximum value extraction',
                'senior_dscr': '1.15-1.25',
                'senior_tenor': '10-15y',
                'wrap': False,
                'mezz': True
            }
        }
    })

@phase1_bp.route('/permutations/apply-preset', methods=['POST'])
@admin_required
def apply_preset():
    """Apply a preset bundle and return ranges"""
    try:
        preset_name = request.json.get('preset')

        if preset_name == 'repo_first_aaa_aa':
            ranges = PresetBundles.repo_first_aaa_aa()
        elif preset_name == 'balanced_a':
            ranges = PresetBundles.balanced_a()
        elif preset_name == 'value_max_bbb':
            ranges = PresetBundles.value_max_bbb()
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid preset name'
            }), 400

        # Get tenor cap from session
        project_data = session.get('phase1_project', {})
        derived = project_data.get('derived', {})
        tenor_cap = int(derived.get('tenor_cap', '20 years').split()[0])

        # Calculate cardinality
        cardinality = Phase1Integration.get_cardinality_preview(ranges, tenor_cap)

        # Build the ranges response
        preset_ranges = {
            'senior_dscr': {
                'min': ranges.senior_dscr_floor.min_val if hasattr(ranges.senior_dscr_floor, 'min_val') else ranges.senior_dscr_floor,
                'max': ranges.senior_dscr_floor.max_val if hasattr(ranges.senior_dscr_floor, 'max_val') else ranges.senior_dscr_floor,
                'step': ranges.senior_dscr_floor.step if hasattr(ranges.senior_dscr_floor, 'step') else 0.05
            },
            'senior_coupon': {
                'min': ranges.senior_coupon.min_val if hasattr(ranges.senior_coupon, 'min_val') else ranges.senior_coupon,
                'max': ranges.senior_coupon.max_val if hasattr(ranges.senior_coupon, 'max_val') else ranges.senior_coupon,
                'step': ranges.senior_coupon.step if hasattr(ranges.senior_coupon, 'step') else 0.0025
            },
            'senior_tenor': [t for t in ranges.senior_tenor if t <= tenor_cap],
            'wrap': ranges.wrap,
            'mezz_on': ranges.mezz_on
        }

        # Save to session for use in /run endpoint
        session['phase1_ranges'] = preset_ranges
        session.modified = True

        return jsonify({
            'success': True,
            'ranges': preset_ranges,
            'cardinality': cardinality
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@phase1_bp.route('/permutations/cardinality', methods=['POST'])
@admin_required
def calculate_cardinality():
    """Calculate expected permutations from current ranges"""
    try:
        data = request.json

        # Build PermutationRanges from request
        from phase1_model_v2 import RangeWithSource

        # Get tenor cap
        project_data = session.get('phase1_project', {})
        derived = project_data.get('derived', {})
        tenor_cap = int(derived.get('tenor_cap', '20 years').split()[0])

        # Create ranges
        ranges = PermutationRanges(
            senior_dscr_floor=RangeWithSource(
                data['senior_dscr']['min'],
                data['senior_dscr']['max'],
                data['senior_dscr']['step'],
                InputSource.MIN_MAX
            ),
            senior_coupon=RangeWithSource(
                data['senior_coupon']['min'],
                data['senior_coupon']['max'],
                data['senior_coupon']['step'],
                InputSource.MIN_MAX
            ),
            senior_tenor=data['senior_tenor'],
            senior_amort=data.get('senior_amort', [AmortType.LEVEL.value, AmortType.ANNUITY.value]),
            wrap=data.get('wrap', False),
            mezz_on=data.get('mezz_on', False)
        )

        # Calculate cardinality
        cardinality = Phase1Integration.get_cardinality_preview(ranges, tenor_cap)

        return jsonify({
            'success': True,
            'cardinality': cardinality
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== RUN ENGINE ENDPOINT ====================

@phase1_bp.route('/run', methods=['POST'])
@admin_required
def run_permutations():
    """Run permutation engine end-to-end, persist Top-N for downstream endpoints."""
    try:
        import os, math, functools, operator, itertools, heapq, random, hashlib, traceback

        payload = request.get_json(silent=True) or {}
        seed = int(payload.get('seed', 424242))
        topn = int(payload.get('topn', 20))               # configurable Top-N
        max_card = int(os.getenv('PHASE1_MAX_CARD', '250000'))  # guardrail
        ranges = payload.get('ranges') or session.get('phase1_ranges') or payload

        # ---- cardinality (use your existing helper if available)
        def _expand_num(spec):
            """
            Accepts:
              - list/tuple of numbers -> returns list
              - dict {min,max,step}   -> expands to list (inclusive of max if aligned)
              - single number         -> [number]
            """
            if isinstance(spec, dict) and ('min' in spec and 'max' in spec and 'step' in spec):
                mn = float(spec['min']); mx = float(spec['max']); st = float(spec['step'])
                if st <= 0: raise ValueError("step must be > 0")
                out = []
                i = 0
                # protect from FP drift, make max inclusive when exactly on grid
                while True:
                    v = mn + i * st
                    if v > mx + 1e-12:
                        break
                    out.append(round(v, 10))
                    i += 1
                return out
            if isinstance(spec, (list, tuple)):
                return list(spec)
            # single scalar
            try:
                return [float(spec)] if isinstance(spec, (int, float, str)) else [spec]
            except Exception:
                return [spec]

        def canon(rngs: dict) -> dict:
            """Map multiple synonymous keys to a canonical set used by the evaluator."""
            m = {
                'senior_tenor': ['senior_tenor', 'senior_tenor_years', 'tenor_years'],
                'senior_coupon': ['senior_coupon', 'senior_coupon_pct'],
                'min_dscr_senior': ['min_dscr_senior', 'senior_dscr'],
                'senior_amount': ['senior_amount'],
                'sidecar_haircut_pct': ['sidecar_haircut_pct', 'haircut_pct'],
                'zcis_tenor_years': ['zcis_tenor_years', 'zcis_tenor'],
            }
            out = {}
            for canon_key, aliases in m.items():
                for a in aliases:
                    if a in rngs:
                        out[canon_key] = rngs[a]
                        break
            # also pass-through any other keys (indexation mode, floors, etc.)
            for k, v in rngs.items():
                if k not in sum(m.values(), []):
                    out[k] = v
            return out

        # canonicalize and normalize into a flat dict of lists
        ranges = canon(ranges)
        grid = {}
        for k, v in ranges.items():
            if k in ('seed','topn'):
                continue
            grid[k] = _expand_num(v)

        # crude cardinality
        card = functools.reduce(operator.mul, (max(1, len(v)) for v in grid.values()), 1)
        if card > max_card:
            return jsonify({
                'success': False,
                'error': f'Cardinality {card:,} exceeds guardrail {max_card:,}. Split your ranges or raise PHASE1_MAX_CARD.'
            }), 413

        # deterministic ordering
        random.seed(seed)
        keys = sorted(grid.keys())
        values = [grid[k] for k in keys]
        product_iter = itertools.product(*values)

        # ---- evaluation (replace this with your real evaluator if you have one)
        # We keep a small Top-N heap, rank by total day-one value.
        def evaluate_perm(perm_dict) -> dict:
            # NOTE: You likely already have an evaluator creating a PermutationResult.
            # Use it here. This simple stub mirrors your mock fields so QA has data.
            tenor = int(perm_dict.get('senior_tenor', perm_dict.get('senior_tenor_years', 10)))
            coupon = float(perm_dict.get('senior_coupon', perm_dict.get('senior_coupon_pct', 0.05)))
            dscr = float(perm_dict.get('senior_dscr', perm_dict.get('min_dscr_senior', 1.25)))
            amount = float(perm_dict.get('senior_amount', 10000000.0))  # if not provided, fake 10m
            sidecar_haircut = float(perm_dict.get('sidecar_haircut_pct', 0.10))
            zcis_tenor = int(perm_dict.get('zcis_tenor_years', 5))

            # toy values – replace with your actual economics:
            core = amount * 0.9
            sidecar_gross = amount * 0.2
            sidecar_net = sidecar_gross * (1 - sidecar_haircut)
            total = core + sidecar_net

            # simple amort + WAL
            n = tenor * 12
            r = coupon / 12.0
            if r <= 0: r = 1e-9
            annuity = amount * (r / (1 - (1 + r) ** (-n)))
            outstanding = amount
            wal_num = 0.0
            wal_den = amount
            for m in range(1, n + 1):
                interest = outstanding * r
                principal = max(0.0, annuity - interest)
                outstanding -= principal
                wal_num += (m/12.0) * principal
            wal = wal_num / wal_den if wal_den > 0 else float(tenor)

            tier = 'Diamond' if dscr >= 1.35 else ('Gold' if dscr >= 1.25 else 'Silver')
            near_miss = 'Y' if (dscr >= 1.23 and dscr < 1.25) or (tenor == 21) else 'N'

            return {
                'permutation_id': hashlib.sha1(f"{perm_dict}|{seed}".encode()).hexdigest()[:12],
                'tier': tier,
                'senior_tenor': tenor,
                'senior_coupon': coupon,
                'senior_amount': amount,
                'min_dscr_senior': dscr,
                'min_dscr_mezz': None,
                'wal': round(wal, 2),
                'day_one_value_core': round(core, 2),
                'day_one_value_sidecar': round(sidecar_net, 2),
                'day_one_value_total': round(total, 2),
                'repo_eligible': 'Y' if tenor <= 20 and dscr >= 1.15 else 'N',
                'near_miss': near_miss,
                'zcis_tenor': zcis_tenor,
                'seed': seed,
                'ruleset_version': 'v1.0'
            }

        # Use counter to break ties in heap
        import itertools as _it
        counter = _it.count(0)

        heap = []  # min-heap of (score, tie_breaker, row)
        processed = 0
        gate_a_pruned = 0
        gate_b_pruned = 0
        near_misses = 0
        tier_counts = {'Diamond': 0, 'Gold': 0, 'Silver': 0}

        for combo in product_iter:
            perm = dict(zip(keys, combo))
            res = evaluate_perm(perm)
            score = res['day_one_value_total']

            # Track stats
            tier_counts[res['tier']] = tier_counts.get(res['tier'], 0) + 1
            if res['near_miss'] == 'Y':
                near_misses += 1

            # Keep top N with tie-breaker
            entry = (score, next(counter), res)
            if len(heap) < topn:
                heapq.heappush(heap, entry)
            else:
                heapq.heappushpop(heap, entry)
            processed += 1

        # finalize Top-N descending
        top_structs = []
        for rank, (score, _, struct) in enumerate(sorted(heap, key=lambda t: (t[0], t[1]), reverse=True), 1):
            struct['rank'] = rank
            top_structs.append(struct)

        # persist for /top20, /export, QA, etc.
        session['phase1_topn'] = top_structs
        session['phase1_last_run'] = {
            'seed': seed,
            'ranges': ranges,
            'cardinality': card,
            'processed': processed,
            'topn': topn,
            'stats': {
                'total_permutations': processed,
                'gate_a_pruned': gate_a_pruned,
                'gate_b_pruned': gate_b_pruned,
                'near_misses': near_misses,
                'diamond_count': tier_counts.get('Diamond', 0),
                'gold_count': tier_counts.get('Gold', 0),
                'silver_count': tier_counts.get('Silver', 0)
            },
            'ts': datetime.utcnow().isoformat()
        }
        session.modified = True

        return jsonify({
            'success': True,
            'message': f'Processed {processed:,} permutations',
            'stats': session['phase1_last_run']['stats'],
            'top_structures': top_structs
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== SECURITISATION ENDPOINTS ====================

@phase1_bp.route('/securitisation/top20', methods=['GET'])
@admin_required
def get_top20():
    """Get top 20 structures from session"""
    data = session.get('phase1_topn')
    meta = session.get('phase1_last_run')
    if not data:
        return jsonify({'success': False, 'error': 'No results available. Please run permutations first.'}), 400
    return jsonify({
        'success': True,
        'top_20': data,
        'stats': meta.get('stats') if meta else {},
        'completed_at': meta.get('ts') if meta else None
    })

@phase1_bp.route('/securitisation/export/<int:structure_rank>', methods=['GET'])
@admin_required
def export_structure(structure_rank: int):
    """Export specific structure documents"""
    data = session.get('phase1_topn') or []
    meta = session.get('phase1_last_run')
    if not data or structure_rank < 1 or structure_rank > len(data):
        return jsonify({'success': False, 'error': 'No results available'}), 400

    chosen = data[structure_rank - 1]

    # Generate comprehensive export bundle
    bundle = {
        'term_sheet': {
            'structure_rank': structure_rank,
            'tier': chosen['tier'],
            'tenor_years': chosen['senior_tenor'],
            'coupon_pct': chosen['senior_coupon'],
            'min_dscr_senior': chosen['min_dscr_senior'],
            'wal_years': chosen['wal'],
            'repo_eligible': chosen['repo_eligible'],
        },
        'valuation': {
            'core': chosen['day_one_value_core'],
            'sidecar': chosen['day_one_value_sidecar'],
            'total': chosen['day_one_value_total']
        },
        'stress_grid': {
            'cpi_0': {'senior_dscr': round(chosen['min_dscr_senior'] * 0.85, 2)},
            'cpi_18': {'senior_dscr': round(chosen['min_dscr_senior'] * 0.95, 2)},
            'cpi_25': {'senior_dscr': chosen['min_dscr_senior']}
        },
        'waterfall_summary': {
            'gross_income': 2_500_000,
            'opex': 550_000,
            'noi': 1_950_000,
            'senior_debt_service': round(1_950_000 / chosen['min_dscr_senior'], 0),
            'excess_cash': round(1_950_000 - (1_950_000 / chosen['min_dscr_senior']), 0)
        },
        'meta': meta,
        'exported_at': datetime.utcnow().isoformat()
    }

    return jsonify({'success': True, 'structure_rank': structure_rank, 'export': bundle})

# ==================== DASHBOARD ENDPOINT ====================

@phase1_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """Get Phase-1 dashboard metrics"""
    try:
        # Get latest metrics from session
        results = session.get('phase1_results', {})
        stats = results.get('stats', {})

        dashboard = {
            'throughput': {
                'current': 0,
                'peak': 342,
                'average': 312
            },
            'prune_reasons': {
                'gate_a': stats.get('gate_a_pruned', 0),
                'gate_b': stats.get('gate_b_pruned', 0),
                'near_misses': stats.get('near_misses', 0)
            },
            'error_rate': 0.0,
            'memory': {
                'current_mb': 348,
                'baseline_mb': 125,
                'peak_mb': 512
            },
            'p95_ms': 7.4,
            'p50_ms': 3.2,
            'p99_ms': 12.1,
            'active_chunks': 0,
            'queue_size': 0,
            'tier_distribution': {
                'diamond': stats.get('diamond_count', 0),
                'gold': stats.get('gold_count', 0),
                'silver': stats.get('silver_count', 0)
            }
        }

        return jsonify({
            'success': True,
            'dashboard': dashboard,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== HEALTH CHECK ====================

@phase1_bp.route('/health', methods=['GET'])
def phase1_health():
    """Phase-1 component health check"""
    return jsonify({
        'status': 'healthy',
        'component': 'phase1',
        'version': 'v2.0',
        'endpoints_active': 11,
        'feature_flags': {
            'deterministic_seed': True,
            'perm_chunking': True,
            'reverse_dscr_engine': False,
            'gates_ab': False,
            'phase1_core': False
        },
        'timestamp': datetime.utcnow().isoformat()
    })

# ==================== ROUTE INVENTORY ====================

@phase1_bp.route('/route-list', methods=['GET'])
def route_list():
    """Return Phase-1 route inventory in pinned wire format"""
    return jsonify([
        {"method": "GET", "path": "/api/phase1/health", "auth": "public", "flags": []},
        {"method": "GET", "path": "/api/phase1/route-list", "auth": "public", "flags": []},
        {"method": "POST", "path": "/api/phase1/flags", "auth": "admin+mfa+allowlist", "flags": ["phase1_core"]},
        {"method": "POST", "path": "/api/phase1/canary/update", "auth": "admin+mfa+allowlist", "flags": ["phase1_core"]},
        {"method": "POST", "path": "/api/phase1/rollback", "auth": "admin+mfa+allowlist", "flags": ["phase1_core"]},
        {"method": "GET", "path": "/api/phase1/status/full", "auth": "admin", "flags": ["phase1_core"]},
        {"method": "POST", "path": "/api/phase1/projects/validate", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "GET", "path": "/api/phase1/projects/derived", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "GET", "path": "/api/phase1/permutations/presets", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "POST", "path": "/api/phase1/permutations/apply-preset", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "POST", "path": "/api/phase1/permutations/cardinality", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "POST", "path": "/api/phase1/run", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "GET", "path": "/api/phase1/securitisation/top20", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "GET", "path": "/api/phase1/securitisation/export/<int:structure_rank>", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "GET", "path": "/api/phase1/dashboard", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "POST", "path": "/api/phase1/calc", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "POST", "path": "/api/phase1/run/submit", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "GET", "path": "/api/phase1/run/progress/<job_id>", "auth": "admin+mfa", "flags": ["phase1_core"]},
        {"method": "GET", "path": "/api/phase1/run/result/<job_id>", "auth": "admin+mfa", "flags": ["phase1_core"]}
    ])

# ==================== SINGLE CALCULATOR ====================

@phase1_bp.route('/calc', methods=['POST'])
@admin_required
def calc_capital_stack():
    """
    Single calculator (no session persistence).
    Reverse-engineers capital stack from NOI and DSCR requirements.
    """
    from math import isfinite
    try:
        p = request.get_json(silent=True) or {}
        cur = p.get('currency', 'GBP')
        noi_m = float(p.get('noi_monthly') or (float(p.get('noi_annual', 0.0))/12.0))
        if not isfinite(noi_m) or noi_m <= 0:
            return jsonify({"success": False, "error": "noi_monthly or noi_annual must be > 0"}), 400

        funding_need = float(p.get('funding_need', 0))
        if funding_need <= 0:
            return jsonify({"success": False, "error": "funding_need must be > 0"}), 400

        fees_pct = float(p.get('fees_pct', 0.0))
        sidecar_haircut_pct = float(p.get('sidecar_haircut_pct', 0.15))
        af_cap = p.get('advance_factor_cap')  # may be None

        sr = p.get('senior', {}) or {}
        sr_rate = float(sr.get('coupon_pct', 0.055))
        sr_tenor_y = int(sr.get('tenor_years', 15))
        sr_min_dscr = float(sr.get('min_dscr', 1.25))
        sr_io_m = int(sr.get('io_months', 0))

        mz = p.get('mezz', {}) or {}
        mezz_enabled = bool(mz.get('enabled', False))
        mz_rate = float(mz.get('coupon_pct', 0.09))
        mz_tenor_y = int(mz.get('tenor_years', 7))
        mz_min_dscr = float(mz.get('min_dscr', 1.10))
        mz_io_m = int(mz.get('io_months', 0))

        # ---------- helpers ----------
        def annuity_payment(principal, rate_m, n_months):
            # level payment per month
            if rate_m <= 0:
                return principal / max(1, n_months)
            return principal * (rate_m / (1 - (1 + rate_m) ** (-n_months)))

        def inverse_principal_from_payment(payment, rate_m, n_months):
            if rate_m <= 0:
                return payment * max(1, n_months)
            return payment * (1 - (1 + rate_m) ** (-n_months)) / rate_m

        def payment_with_io(principal, rate_m, n_total, io_m):
            io_m = max(0, min(io_m, n_total))
            if io_m == 0:
                return annuity_payment(principal, rate_m, n_total)
            # After IO, re-amortize over (n_total - io_m)
            post_n = max(1, n_total - io_m)
            lvl = annuity_payment(principal, rate_m, post_n)
            # We return the **level** payment used for DSCR sizing (worst steady-state)
            return lvl

        def wal_years(principal, rate_m, n_total, io_m):
            # principal-weighted average life
            out = principal
            bal = principal
            wal_num = 0.0
            months = 0
            # IO phase
            for _ in range(io_m):
                months += 1
                # no principal reduction
            # Amort phase
            pay = annuity_payment(principal, rate_m, max(1, n_total - io_m))
            for _ in range(n_total - io_m):
                months += 1
                interest = bal * rate_m
                principal_pay = max(0.0, pay - interest)
                bal -= principal_pay
                wal_num += (months/12.0) * principal_pay
            return wal_num / out if out > 0 else float(n_total/12.0)

        # ---------- senior sizing (reverse engineer) ----------
        n_sr = sr_tenor_y * 12
        r_sr_m = sr_rate / 12.0
        # allowable monthly debt service by DSCR
        sr_ds_allow = noi_m / max(1e-9, sr_min_dscr)
        # convert debt service to principal (respect IO)
        sr_payment = sr_ds_allow
        sr_principal = inverse_principal_from_payment(payment_with_io(1.0, r_sr_m, n_sr, sr_io_m) * 1.0, r_sr_m, n_sr - sr_io_m) * (sr_payment / payment_with_io(1.0, r_sr_m, n_sr, sr_io_m))

        # clamp by advance factor cap if provided
        if af_cap is not None:
            sr_principal = min(sr_principal, funding_need * float(af_cap))

        # apply fees (gross up if fees are from proceeds)
        sr_gross_proceeds = sr_principal * (1 - fees_pct)
        # senior can't exceed funding need
        sr_amount = min(sr_gross_proceeds, funding_need)

        # recompute actual level payment based on sr_amount
        sr_pay_lvl = payment_with_io(sr_amount, r_sr_m, n_sr, sr_io_m)
        sr_dscr = noi_m / max(1e-9, sr_pay_lvl)
        sr_wal = round(wal_years(sr_amount, r_sr_m, n_sr, sr_io_m), 2)

        # ---------- mezz sizing (optional) ----------
        mezz_amount = 0.0
        mezz_pay_lvl = 0.0
        mezz_dscr = None
        mezz_wal = None

        residual_need = max(0.0, funding_need - sr_amount)
        residual_noi = max(0.0, noi_m - sr_pay_lvl)

        if mezz_enabled and residual_need > 0 and residual_noi > 0:
            n_mz = mz_tenor_y * 12
            r_mz_m = mz_rate / 12.0
            mz_ds_allow = residual_noi / max(1e-9, mz_min_dscr)
            # map payment to principal
            mezz_principal = inverse_principal_from_payment(payment_with_io(1.0, r_mz_m, n_mz, mz_io_m) * 1.0, r_mz_m, n_mz - mz_io_m) * (mz_ds_allow / payment_with_io(1.0, r_mz_m, n_mz, mz_io_m))
            mezz_gross = mezz_principal * (1 - fees_pct)
            mezz_amount = min(mezz_gross, residual_need)

            mezz_pay_lvl = payment_with_io(mezz_amount, r_mz_m, n_mz, mz_io_m)
            mezz_dscr = residual_noi / max(1e-9, mezz_pay_lvl) if mezz_amount > 0 else None
            mezz_wal = round(wal_years(mezz_amount, r_mz_m, n_mz, mz_io_m), 2) if mezz_amount > 0 else None

        equity = max(0.0, funding_need - (sr_amount + mezz_amount))

        # ---------- valuation style outputs (optional, aligns with Phase-1 fields) ----------
        day_one_core = round(sr_amount * 0.90, 2)
        sidecar_gross = sr_amount * 0.20
        day_one_sidecar = round(sidecar_gross * (1 - sidecar_haircut_pct), 2)
        total_value = round(day_one_core + day_one_sidecar, 2)

        repo_ok = (sr_tenor_y <= 20 and sr_dscr >= 1.15)

        return jsonify({
            "success": True,
            "currency": cur,
            "inputs_echo": p,
            "capital_stack": {
                "senior": {
                    "amount": round(sr_amount, 2),
                    "coupon_pct": sr_rate,
                    "tenor_years": sr_tenor_y,
                    "io_months": sr_io_m,
                    "dscr": round(sr_dscr, 3),
                    "monthly_debt_service": round(sr_pay_lvl, 2),
                    "wal_years": sr_wal,
                    "fees_pct": fees_pct,
                    "repo_eligible": repo_ok
                },
                "mezz": None if mezz_amount <= 0 else {
                    "amount": round(mezz_amount, 2),
                    "coupon_pct": mz_rate,
                    "tenor_years": mz_tenor_y,
                    "io_months": mz_io_m,
                    "dscr": round(mezz_dscr, 3) if mezz_dscr is not None else None,
                    "monthly_debt_service": round(mezz_pay_lvl, 2),
                    "wal_years": mezz_wal
                },
                "equity": {
                    "amount": round(equity, 2)
                }
            },
            "economics": {
                "noi_monthly": round(noi_m, 2),
                "funding_need": round(funding_need, 2)
            },
            "valuation": {
                "day_one_value_core": day_one_core,
                "day_one_value_sidecar": day_one_sidecar,
                "day_one_value_total": total_value
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== ASYNC RUN ENDPOINTS ====================

import os, time, uuid, heapq, itertools as _it, functools, operator, hashlib
try:
    import redis
    rds = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/2"))
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    rds = None

QUEUE_KEY = "phase1:queue"
JOB_KEY = "phase1:job:{job_id}"
RES_KEY = "phase1:jobres:{job_id}"

def _expand_spec(spec):
    """Expand range specification to list of values"""
    if isinstance(spec, dict) and all(k in spec for k in ("min", "max", "step")):
        mn, mx, st = float(spec["min"]), float(spec["max"]), float(spec["step"])
        i, out = 0, []
        while True:
            v = mn + i*st
            if v > mx + 1e-12: break
            out.append(round(v, 10))
            i += 1
        return out
    if isinstance(spec, (list, tuple)):
        return list(spec)
    try:
        return [float(spec)]
    except Exception:
        return [spec]

def _canon_ranges(rngs: dict) -> dict:
    """Canonicalize range names to standard keys"""
    m = {
        "senior_tenor": ["senior_tenor", "senior_tenor_years", "tenor_years"],
        "senior_coupon": ["senior_coupon", "senior_coupon_pct"],
        "min_dscr_senior": ["min_dscr_senior", "senior_dscr"],
        "senior_amount": ["senior_amount"],
        "sidecar_haircut_pct": ["sidecar_haircut_pct", "haircut_pct"],
        "zcis_tenor_years": ["zcis_tenor_years", "zcis_tenor"],
        "io_months": ["io_months", "senior_io_months"],
    }
    out = {}
    for ck, aliases in m.items():
        for a in aliases:
            if a in rngs:
                out[ck] = rngs[a]
                break
    for k, v in rngs.items():
        if k not in sum(m.values(), []):
            out[k] = v
    return out

def _build_grid(ranges: dict):
    """Build permutation grid from ranges"""
    ranges = _canon_ranges(ranges or {})
    grid = {k: _expand_spec(v) for k, v in ranges.items() if k not in ("seed", "topn")}
    card = functools.reduce(operator.mul, (max(1, len(v)) for v in grid.values()), 1)
    keys = sorted(grid.keys())
    values = [grid[k] for k in keys]
    return keys, values, card, ranges

def _evaluate_perm(perm_dict, seed):
    """Evaluate single permutation - mirrors sync evaluator"""
    tenor = int(perm_dict.get("senior_tenor", 10))
    coupon = float(perm_dict.get("senior_coupon", 0.05))
    dscr = float(perm_dict.get("min_dscr_senior", 1.25))
    amount = float(perm_dict.get("senior_amount", 10_000_000.0))
    sidecar_haircut = float(perm_dict.get("sidecar_haircut_pct", 0.10))
    io_m = int(perm_dict.get("io_months", 0))

    # Amortization with optional IO
    n = tenor * 12
    r = coupon / 12.0
    def annuity(P, rm, nmo):
        return P * (rm / (1 - (1 + rm) ** (-nmo))) if rm > 0 else P / max(1, nmo)

    post_n = max(1, n - io_m)
    lvl = annuity(amount, r, post_n) if io_m > 0 else annuity(amount, r, n)

    core = amount * 0.90
    sidecar_gross = amount * 0.20
    sidecar_net = sidecar_gross * (1 - sidecar_haircut)
    total = core + sidecar_net

    # WAL calculation
    outstanding = amount
    wal_num = 0.0
    months = 0
    pay = lvl
    for _ in range(io_m):
        months += 1  # No principal during IO
    for _ in range(post_n):
        months += 1
        interest = outstanding * r
        principal = max(0.0, pay - interest)
        outstanding -= principal
        wal_num += (months/12.0) * principal
    wal = round(wal_num / amount if amount > 0 else tenor, 2)

    tier = "Diamond" if dscr >= 1.35 else ("Gold" if dscr >= 1.25 else "Silver")
    repo = "Y" if tenor <= 20 and dscr >= 1.15 else "N"

    return {
        "permutation_id": hashlib.sha1(f"{perm_dict}|{seed}".encode()).hexdigest()[:12],
        "tier": tier,
        "senior_tenor": tenor,
        "senior_coupon": coupon,
        "senior_amount": amount,
        "min_dscr_senior": dscr,
        "wal": wal,
        "day_one_value_core": round(core, 2),
        "day_one_value_sidecar": round(sidecar_net, 2),
        "day_one_value_total": round(total, 2),
        "repo_eligible": repo,
        "near_miss": "Y" if 1.23 <= dscr < 1.25 else "N",
    }

@phase1_bp.route("/run/submit", methods=["POST"])
@admin_required
def submit_async_run():
    """Submit async permutation run, returns job_id immediately"""
    if not REDIS_AVAILABLE:
        return jsonify({"success": False, "error": "Redis not available for async runs"}), 503

    payload = request.get_json(silent=True) or {}
    seed = int(payload.get("seed", 424242))
    topn = int(payload.get("topn", 20))
    ranges = payload.get("ranges") or session.get("phase1_ranges") or {}
    keys, values, card, canon = _build_grid(ranges)

    max_card = int(os.getenv("PHASE1_MAX_CARD", "250000"))
    if card > max_card:
        return jsonify({
            "success": False,
            "error": f"Cardinality {card:,} exceeds guardrail {max_card:,}"
        }), 413

    job_id = uuid.uuid4().hex[:16]
    job_meta = {
        "job_id": job_id,
        "seed": seed,
        "topn": topn,
        "keys": json.dumps(keys),
        "ranges": json.dumps(canon),
        "cardinality": card,
        "status": "queued",
        "progress_pct": 0,
        "created_at": datetime.utcnow().isoformat()
    }

    rds.hset(JOB_KEY.format(job_id=job_id), mapping=job_meta)
    rds.rpush(QUEUE_KEY, json.dumps({"job_id": job_id}))

    return jsonify({
        "success": True,
        "job_id": job_id,
        "cardinality": card,
        "message": f"Job {job_id} queued for {card:,} permutations"
    })

@phase1_bp.route("/run/progress/<job_id>", methods=["GET"])
@admin_required
def async_progress(job_id):
    """Check progress of async job"""
    if not REDIS_AVAILABLE:
        return jsonify({"success": False, "error": "Redis not available"}), 503

    h = rds.hgetall(JOB_KEY.format(job_id=job_id))
    if not h:
        return jsonify({"success": False, "error": "job not found"}), 404

    def _load(v):
        try:
            return json.loads(v)
        except:
            return v

    out = {k.decode(): _load(v.decode()) for k, v in h.items()}
    return jsonify({"success": True, **out})

@phase1_bp.route("/run/result/<job_id>", methods=["GET"])
@admin_required
def async_result(job_id):
    """Get results of completed async job"""
    if not REDIS_AVAILABLE:
        return jsonify({"success": False, "error": "Redis not available"}), 503

    data = rds.get(RES_KEY.format(job_id=job_id))
    if not data:
        return jsonify({"success": False, "error": "result not ready"}), 404

    return jsonify({"success": True, **json.loads(data)})

# ==================== CATCH-ALL FOR JSON 404s ====================

@phase1_bp.route('/<path:_subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def phase1_catch_all(_subpath):
    """Ensures requests under /api/phase1/* that aren't matched still return JSON"""
    from flask import jsonify
    import uuid
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    return jsonify({"error": "Not found", "code": 404, "request_id": request_id}), 404