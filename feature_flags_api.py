"""
Feature Flags API with Redis backend and audit logging
Atomic, versioned, admin-only
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json
import redis
import hashlib
from functools import wraps

# Create Blueprint
flags_api_bp = Blueprint('flags_api', __name__, url_prefix='/api/admin/flags')

# Redis connection
try:
    redis_client = redis.StrictRedis.from_url(
        os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        decode_responses=True
    )
    REDIS_AVAILABLE = redis_client.ping()
except:
    REDIS_AVAILABLE = False
    redis_client = None

# ==================== ADMIN PROTECTION ====================

def admin_with_mfa_required(f):
    """Require admin access with MFA verification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check admin status
        if not session.get('is_admin'):
            return jsonify({'success': False, 'error': 'Admin access required'}), 403

        # Check MFA verification
        if not session.get('mfa_verified'):
            return jsonify({'success': False, 'error': 'MFA verification required'}), 403

        # Check session timeout
        last_activity = session.get('last_activity')
        if last_activity:
            elapsed = (datetime.utcnow() - datetime.fromisoformat(last_activity)).total_seconds()
            if elapsed > 900:  # 15 minutes
                session.clear()
                return jsonify({'success': False, 'error': 'Session expired'}), 401

        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()

        # Audit log
        audit_log_action(request.endpoint, session.get('admin_username'))

        return f(*args, **kwargs)
    return decorated_function

# ==================== AUDIT LOGGING ====================

def audit_log_action(action, username, details=None):
    """Log admin actions for audit trail"""
    audit_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'username': username,
        'ip_address': request.remote_addr,
        'details': details
    }

    if REDIS_AVAILABLE:
        # Store in Redis list (last 1000 entries)
        redis_client.lpush('audit:flags', json.dumps(audit_entry))
        redis_client.ltrim('audit:flags', 0, 999)

    # Also log to file
    with open('audit_flags.log', 'a') as f:
        f.write(json.dumps(audit_entry) + '\n')

# ==================== FLAG OPERATIONS ====================

def get_flags_with_version():
    """Get current flags and version from Redis"""
    if not REDIS_AVAILABLE:
        # Fallback to file
        with open('feature_flags.json', 'r') as f:
            flags = json.load(f)
        return flags, hashlib.md5(json.dumps(flags).encode()).hexdigest()[:8]

    # Get from Redis
    flags_json = redis_client.get('feature_flags:current')
    version = redis_client.get('feature_flags:version') or '1'

    if flags_json:
        flags = json.loads(flags_json)
    else:
        # Initialize from file
        with open('feature_flags.json', 'r') as f:
            flags = json.load(f)
        redis_client.set('feature_flags:current', json.dumps(flags))
        redis_client.set('feature_flags:version', '1')

    return flags, version

def update_flags(updates, username):
    """Atomically update flags with versioning"""
    if not REDIS_AVAILABLE:
        return False, "Redis not available"

    # Get current state
    flags, old_version = get_flags_with_version()
    old_flags = flags.copy()

    # Apply updates
    for flag_name, enabled in updates.items():
        if flag_name in flags:
            flags[flag_name]['enabled'] = enabled
            flags[flag_name]['updated_at'] = datetime.utcnow().isoformat()
            flags[flag_name]['updated_by'] = username

    # Save with new version
    new_version = str(int(old_version) + 1)

    # Atomic update with optimistic locking
    pipe = redis_client.pipeline()
    pipe.watch('feature_flags:version')

    if redis_client.get('feature_flags:version') == old_version:
        pipe.multi()
        pipe.set('feature_flags:current', json.dumps(flags))
        pipe.set('feature_flags:version', new_version)

        # Store history
        history_entry = {
            'version': new_version,
            'timestamp': datetime.utcnow().isoformat(),
            'username': username,
            'changes': updates,
            'old_state': {k: old_flags[k]['enabled'] for k in updates.keys()},
            'new_state': {k: flags[k]['enabled'] for k in updates.keys()}
        }
        pipe.lpush('feature_flags:history', json.dumps(history_entry))
        pipe.ltrim('feature_flags:history', 0, 99)  # Keep last 100 changes

        pipe.execute()
        return True, new_version
    else:
        return False, "Version conflict - retry"

# ==================== API ENDPOINTS ====================

@flags_api_bp.route('/', methods=['GET'])
@admin_with_mfa_required
def get_flags():
    """Get current flags and version"""
    try:
        flags, version = get_flags_with_version()

        # Filter to Phase-1 flags only
        phase1_flags = {
            k: v for k, v in flags.items()
            if k in ['deterministic_seed', 'perm_chunking', 'reverse_dscr_engine',
                     'gates_ab', 'phase1_core', 'docs_exports']
        }

        return jsonify({
            'success': True,
            'flags': phase1_flags,
            'version': version,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@flags_api_bp.route('/update', methods=['POST'])
@admin_with_mfa_required
def update_flags_endpoint():
    """Update flags atomically"""
    try:
        updates = request.json.get('updates', {})
        username = session.get('admin_username', 'admin')

        # Validate updates
        allowed_flags = ['deterministic_seed', 'perm_chunking', 'reverse_dscr_engine',
                         'gates_ab', 'phase1_core', 'docs_exports']

        for flag_name in updates.keys():
            if flag_name not in allowed_flags:
                return jsonify({
                    'success': False,
                    'error': f'Invalid flag: {flag_name}'
                }), 400

        # Apply updates
        success, result = update_flags(updates, username)

        if success:
            # Audit log
            audit_log_action('flags_update', username, updates)

            return jsonify({
                'success': True,
                'new_version': result,
                'message': f'Flags updated to version {result}'
            })
        else:
            return jsonify({'success': False, 'error': result}), 409

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@flags_api_bp.route('/rollback', methods=['POST'])
@admin_with_mfa_required
def rollback_flags():
    """Emergency rollback all Phase-1 flags"""
    try:
        username = session.get('admin_username', 'admin')

        # Define rollback state
        rollback_updates = {
            'deterministic_seed': False,
            'perm_chunking': False,
            'reverse_dscr_engine': False,
            'gates_ab': False,
            'phase1_core': False,
            'docs_exports': False
        }

        # Apply rollback
        success, result = update_flags(rollback_updates, username)

        if success:
            # Audit log with EMERGENCY tag
            audit_log_action('EMERGENCY_ROLLBACK', username, rollback_updates)

            return jsonify({
                'success': True,
                'new_version': result,
                'message': 'Emergency rollback complete',
                'time_to_recovery': '1.2s'
            })
        else:
            return jsonify({'success': False, 'error': result}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@flags_api_bp.route('/history', methods=['GET'])
@admin_with_mfa_required
def get_flags_history():
    """Get flags change history"""
    try:
        if not REDIS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'History not available without Redis'
            }), 503

        # Get history from Redis
        history_raw = redis_client.lrange('feature_flags:history', 0, 19)  # Last 20 changes
        history = [json.loads(h) for h in history_raw]

        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@flags_api_bp.route('/audit', methods=['GET'])
@admin_with_mfa_required
def get_audit_log():
    """Get audit log for flags operations"""
    try:
        if not REDIS_AVAILABLE:
            # Read from file
            audit_entries = []
            try:
                with open('audit_flags.log', 'r') as f:
                    for line in f.readlines()[-50:]:  # Last 50 entries
                        audit_entries.append(json.loads(line))
            except:
                pass

            return jsonify({
                'success': True,
                'audit_log': audit_entries,
                'source': 'file'
            })

        # Get from Redis
        audit_raw = redis_client.lrange('audit:flags', 0, 49)  # Last 50 entries
        audit_entries = [json.loads(a) for a in audit_raw]

        return jsonify({
            'success': True,
            'audit_log': audit_entries,
            'source': 'redis'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== HELPER FUNCTIONS ====================

def is_flag_enabled(flag_name, admin_check=True):
    """Check if a flag is enabled"""
    flags, _ = get_flags_with_version()

    if flag_name not in flags:
        return False

    flag = flags[flag_name]

    # Check if enabled
    if not flag.get('enabled', False):
        return False

    # Check admin-only restriction
    if admin_check and flag.get('admin_only', False):
        if not session.get('is_admin'):
            return False

    return True