"""
API v2 Blueprint for 3-Gate Workflow System
==========================================
Clean REST API endpoints for the three-gate workflow system with proper error handling
and JSON responses.

Gate 1: Project Management (Basic CRUD)
Gate 2: Securitization Engine
Gate 3: Permutation Engine
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime
import uuid
import json

# Import existing utilities and database functions
from auth_helpers import get_real_ip, check_auth_status
from utils import load_json_db, save_json_db, sanitize_input, log_event

# Try to import cloud database functions
try:
    from cloud_database import load_projects as db_load_projects, save_project_data as db_save_project_data
    CLOUD_DB_AVAILABLE = True
except ImportError:
    CLOUD_DB_AVAILABLE = False
    db_load_projects = None
    db_save_project_data = None

# Create Blueprint
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api')

# ====================
# Authentication Decorator
# ====================

def require_authentication(f):
    """Decorator to require user authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')

        if not session.get(f'site_authenticated_{ip_address}'):
            return jsonify({
                'status': 'error',
                'message': 'Site authentication required',
                'code': 'SITE_AUTH_REQUIRED'
            }), 401

        if not session.get(f'user_authenticated_{ip_address}') or not user_email:
            return jsonify({
                'status': 'error',
                'message': 'User authentication required',
                'code': 'USER_AUTH_REQUIRED'
            }), 401

        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator to require admin access for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip_address = get_real_ip()
        is_admin = session.get(f'is_admin_{ip_address}', False)
        user_email = session.get(f'user_email_{ip_address}')

        if not is_admin and user_email != 'spikemaz8@aol.com':
            return jsonify({
                'status': 'error',
                'message': 'Admin access required',
                'code': 'ADMIN_REQUIRED'
            }), 403

        return f(*args, **kwargs)
    return decorated_function

# ====================
# Utility Functions
# ====================

def load_projects_data():
    """Load projects from database"""
    if CLOUD_DB_AVAILABLE and db_load_projects:
        return db_load_projects()
    return load_json_db('data/projects.json')

def save_projects_data(user_email, project_data):
    """Save projects to database"""
    if CLOUD_DB_AVAILABLE and db_save_project_data:
        return db_save_project_data(user_email, project_data)

    # Fallback to local storage
    projects = load_json_db('data/projects.json')
    projects[user_email] = project_data
    return save_json_db('data/projects.json', projects)

def get_user_projects(user_email):
    """Get projects for a specific user"""
    projects = load_projects_data()
    if user_email not in projects:
        projects[user_email] = {'projects': [], 'order': []}
    return projects[user_email]

def generate_project_id():
    """Generate a unique project ID"""
    return f"project_{uuid.uuid4().hex[:8]}"

def validate_project_data(data):
    """Validate project data"""
    errors = []

    if not data.get('title'):
        errors.append('Title is required')

    # Validate numeric fields
    numeric_fields = ['value', 'progress', 'grossITLoad', 'pue', 'capexCost',
                     'capexRate', 'landPurchaseFees', 'grossMonthlyRent', 'opex']

    for field in numeric_fields:
        if field in data and data[field] is not None:
            try:
                float(data[field])
            except (ValueError, TypeError):
                errors.append(f'{field} must be a valid number')

    return errors

# ====================
# Gate 1: Project Management Endpoints
# ====================

@api_v2.route('/gate1/projects', methods=['POST'])
@require_authentication
def create_project():
    """Create a new project (Gate 1)"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided',
                'code': 'NO_DATA'
            }), 400

        # Validate project data
        validation_errors = validate_project_data(data)
        if validation_errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation failed',
                'errors': validation_errors,
                'code': 'VALIDATION_ERROR'
            }), 400

        # Create new project
        project = {
            'id': data.get('id', generate_project_id()),
            'title': sanitize_input(data.get('title', 'New Project'), 200),
            'description': sanitize_input(data.get('description', ''), 1000),
            'value': data.get('value', 0),
            'progress': data.get('progress', 0),
            'status': data.get('status', 'draft'),
            'details': sanitize_input(data.get('details', ''), 2000),

            # Permutation Engine Fields
            'currency': data.get('currency', 'GBP'),
            'grossITLoad': data.get('grossITLoad'),
            'pue': data.get('pue'),
            'capexCost': data.get('capexCost'),
            'capexRate': data.get('capexRate'),
            'landPurchaseFees': data.get('landPurchaseFees'),
            'grossMonthlyRent': data.get('grossMonthlyRent'),
            'opex': data.get('opex'),
            'seriesId': data.get('seriesId'),

            # Metadata
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'created_by': user_email,
            'gate1_completed': False,
            'gate2_completed': False,
            'gate3_completed': False
        }

        # Load user's projects
        user_projects = get_user_projects(user_email)
        user_projects['projects'].append(project)
        user_projects['order'].append(project['id'])

        # Save to database
        success = save_projects_data(user_email, user_projects)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save project',
                'code': 'SAVE_ERROR'
            }), 500

        log_event('project_created', {
            'project_id': project['id'],
            'user_email': user_email,
            'title': project['title']
        })

        return jsonify({
            'status': 'success',
            'message': 'Project created successfully',
            'project': project
        }), 201

    except Exception as e:
        log_event('project_creation_error', {'error': str(e)}, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@api_v2.route('/gate1/projects', methods=['GET'])
@require_authentication
def get_projects():
    """Get all projects for current user (Gate 1)"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')
        is_admin = session.get(f'is_admin_{ip_address}', False)

        # Check if admin is requesting another user's projects
        requested_user = request.args.get('user')

        if requested_user and is_admin:
            target_email = requested_user
        else:
            target_email = user_email

        user_projects = get_user_projects(target_email)
        projects = user_projects['projects']
        order = user_projects.get('order', [])

        # Sort projects by saved order
        ordered_projects = []
        for project_id in order:
            for project in projects:
                if project['id'] == project_id:
                    ordered_projects.append(project)
                    break

        # Add any new projects not in order
        for project in projects:
            if project['id'] not in order:
                ordered_projects.append(project)

        return jsonify({
            'status': 'success',
            'projects': ordered_projects,
            'total': len(ordered_projects),
            'user': target_email
        })

    except Exception as e:
        log_event('projects_retrieval_error', {'error': str(e)}, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve projects',
            'code': 'RETRIEVAL_ERROR'
        }), 500

@api_v2.route('/gate1/projects/<project_id>/autosave', methods=['PUT'])
@require_authentication
def autosave_project(project_id):
    """Auto-save project data (Gate 1)"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided',
                'code': 'NO_DATA'
            }), 400

        # Validate project data
        validation_errors = validate_project_data(data)
        if validation_errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation failed',
                'errors': validation_errors,
                'code': 'VALIDATION_ERROR'
            }), 400

        # Load user's projects
        user_projects = get_user_projects(user_email)
        projects = user_projects['projects']

        # Find and update the project
        project_found = False
        for i, project in enumerate(projects):
            if project['id'] == project_id:
                # Update project fields
                for key, value in data.items():
                    if key != 'id':  # Don't allow ID changes
                        if key in ['title', 'description', 'details']:
                            projects[i][key] = sanitize_input(value, 2000)
                        else:
                            projects[i][key] = value

                projects[i]['updated_at'] = datetime.now().isoformat()
                project_found = True
                break

        if not project_found:
            return jsonify({
                'status': 'error',
                'message': 'Project not found',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Save to database
        success = save_projects_data(user_email, user_projects)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save project',
                'code': 'SAVE_ERROR'
            }), 500

        return jsonify({
            'status': 'success',
            'message': 'Project auto-saved successfully',
            'project_id': project_id,
            'saved_at': datetime.now().isoformat()
        })

    except Exception as e:
        log_event('project_autosave_error', {
            'project_id': project_id,
            'error': str(e)
        }, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Auto-save failed',
            'code': 'AUTOSAVE_ERROR'
        }), 500

@api_v2.route('/gate1/projects/<project_id>/validate', methods=['GET'])
@require_authentication
def validate_project(project_id):
    """Validate project for Gate 1 completion"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')

        # Load user's projects
        user_projects = get_user_projects(user_email)
        projects = user_projects['projects']

        # Find the project
        project = None
        for p in projects:
            if p['id'] == project_id:
                project = p
                break

        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Validation rules for Gate 1
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'required_fields': ['title', 'description', 'value'],
            'optional_fields': ['grossITLoad', 'pue', 'capexCost']
        }

        # Check required fields
        for field in validation_results['required_fields']:
            if not project.get(field):
                validation_results['errors'].append(f'{field} is required')
                validation_results['valid'] = False

        # Check numeric fields
        if project.get('value') is not None:
            try:
                value = float(project['value'])
                if value < 0:
                    validation_results['warnings'].append('Project value should be positive')
            except (ValueError, TypeError):
                validation_results['errors'].append('Project value must be a valid number')
                validation_results['valid'] = False

        # Check progress
        if project.get('progress') is not None:
            try:
                progress = float(project['progress'])
                if progress < 0 or progress > 100:
                    validation_results['warnings'].append('Progress should be between 0 and 100')
            except (ValueError, TypeError):
                validation_results['warnings'].append('Progress should be a valid number')

        validation_results['gate1_ready'] = validation_results['valid']

        return jsonify({
            'status': 'success',
            'project_id': project_id,
            'validation': validation_results
        })

    except Exception as e:
        log_event('project_validation_error', {
            'project_id': project_id,
            'error': str(e)
        }, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'code': 'VALIDATION_ERROR'
        }), 500

# ====================
# Gate 2: Securitization Engine Endpoints
# ====================

@api_v2.route('/gate2/initialize/<project_id>', methods=['POST'])
@require_authentication
def initialize_gate2(project_id):
    """Initialize Gate 2 (Securitization Engine)"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')

        # Load user's projects
        user_projects = get_user_projects(user_email)
        projects = user_projects['projects']

        # Find and update the project
        project_found = False
        for i, project in enumerate(projects):
            if project['id'] == project_id:
                # Initialize Gate 2 data structure
                projects[i]['gate2_data'] = {
                    'initialized_at': datetime.now().isoformat(),
                    'status': 'initialized',
                    'securitization_parameters': {},
                    'calculation_results': None
                }
                projects[i]['gate1_completed'] = True
                projects[i]['updated_at'] = datetime.now().isoformat()
                project_found = True
                break

        if not project_found:
            return jsonify({
                'status': 'error',
                'message': 'Project not found',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Save to database
        success = save_projects_data(user_email, user_projects)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize Gate 2',
                'code': 'SAVE_ERROR'
            }), 500

        log_event('gate2_initialized', {
            'project_id': project_id,
            'user_email': user_email
        })

        return jsonify({
            'status': 'success',
            'message': 'Gate 2 initialized successfully',
            'project_id': project_id,
            'gate2_data': projects[i]['gate2_data']
        })

    except Exception as e:
        log_event('gate2_initialization_error', {
            'project_id': project_id,
            'error': str(e)
        }, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Failed to initialize Gate 2',
            'code': 'INITIALIZATION_ERROR'
        }), 500

@api_v2.route('/gate2/calculate/<project_id>', methods=['POST'])
@require_authentication
def calculate_gate2(project_id):
    """Run securitization calculations (Gate 2)"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')
        data = request.get_json() or {}

        # Load user's projects
        user_projects = get_user_projects(user_email)
        projects = user_projects['projects']

        # Find the project
        project = None
        project_index = -1
        for i, p in enumerate(projects):
            if p['id'] == project_id:
                project = p
                project_index = i
                break

        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Check if Gate 2 is initialized
        if 'gate2_data' not in project:
            return jsonify({
                'status': 'error',
                'message': 'Gate 2 not initialized',
                'code': 'GATE2_NOT_INITIALIZED'
            }), 400

        # Perform securitization calculations (simplified example)
        parameters = data.get('parameters', {})

        # Sample calculation results
        calculation_results = {
            'irr': 12.5,  # Internal Rate of Return
            'npv': 5000000,  # Net Present Value
            'dscr': 1.35,  # Debt Service Coverage Ratio
            'ltv': 75.0,  # Loan to Value
            'yield': 8.2,  # Expected Yield
            'duration': 120,  # Months
            'calculated_at': datetime.now().isoformat(),
            'parameters_used': parameters
        }

        # Update project with calculation results
        projects[project_index]['gate2_data']['calculation_results'] = calculation_results
        projects[project_index]['gate2_data']['status'] = 'calculated'
        projects[project_index]['gate2_completed'] = True
        projects[project_index]['updated_at'] = datetime.now().isoformat()

        # Save to database
        success = save_projects_data(user_email, user_projects)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save calculation results',
                'code': 'SAVE_ERROR'
            }), 500

        log_event('gate2_calculated', {
            'project_id': project_id,
            'user_email': user_email,
            'irr': calculation_results['irr'],
            'npv': calculation_results['npv']
        })

        return jsonify({
            'status': 'success',
            'message': 'Securitization calculations completed',
            'project_id': project_id,
            'results': calculation_results
        })

    except Exception as e:
        log_event('gate2_calculation_error', {
            'project_id': project_id,
            'error': str(e)
        }, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Calculation failed',
            'code': 'CALCULATION_ERROR'
        }), 500

# ====================
# Gate 3: Permutation Engine Endpoints
# ====================

@api_v2.route('/gate3/initialize/<project_id>', methods=['POST'])
@require_authentication
def initialize_gate3(project_id):
    """Initialize Gate 3 (Permutation Engine)"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')

        # Load user's projects
        user_projects = get_user_projects(user_email)
        projects = user_projects['projects']

        # Find and update the project
        project_found = False
        for i, project in enumerate(projects):
            if project['id'] == project_id:
                # Check if Gate 2 is completed
                if not project.get('gate2_completed'):
                    return jsonify({
                        'status': 'error',
                        'message': 'Gate 2 must be completed before initializing Gate 3',
                        'code': 'GATE2_NOT_COMPLETED'
                    }), 400

                # Initialize Gate 3 data structure
                projects[i]['gate3_data'] = {
                    'initialized_at': datetime.now().isoformat(),
                    'status': 'initialized',
                    'variables': {},
                    'permutation_results': None
                }
                projects[i]['updated_at'] = datetime.now().isoformat()
                project_found = True
                break

        if not project_found:
            return jsonify({
                'status': 'error',
                'message': 'Project not found',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Save to database
        success = save_projects_data(user_email, user_projects)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize Gate 3',
                'code': 'SAVE_ERROR'
            }), 500

        log_event('gate3_initialized', {
            'project_id': project_id,
            'user_email': user_email
        })

        return jsonify({
            'status': 'success',
            'message': 'Gate 3 initialized successfully',
            'project_id': project_id,
            'gate3_data': projects[i]['gate3_data']
        })

    except Exception as e:
        log_event('gate3_initialization_error', {
            'project_id': project_id,
            'error': str(e)
        }, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Failed to initialize Gate 3',
            'code': 'INITIALIZATION_ERROR'
        }), 500

@api_v2.route('/gate3/<project_id>/variables', methods=['POST'])
@require_authentication
def update_gate3_variables(project_id):
    """Update permutation variables (Gate 3)"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')
        data = request.get_json()

        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No variables provided',
                'code': 'NO_DATA'
            }), 400

        # Load user's projects
        user_projects = get_user_projects(user_email)
        projects = user_projects['projects']

        # Find and update the project
        project_found = False
        for i, project in enumerate(projects):
            if project['id'] == project_id:
                # Check if Gate 3 is initialized
                if 'gate3_data' not in project:
                    return jsonify({
                        'status': 'error',
                        'message': 'Gate 3 not initialized',
                        'code': 'GATE3_NOT_INITIALIZED'
                    }), 400

                # Update variables
                projects[i]['gate3_data']['variables'] = data.get('variables', {})
                projects[i]['gate3_data']['status'] = 'variables_set'
                projects[i]['updated_at'] = datetime.now().isoformat()
                project_found = True
                break

        if not project_found:
            return jsonify({
                'status': 'error',
                'message': 'Project not found',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Save to database
        success = save_projects_data(user_email, user_projects)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save variables',
                'code': 'SAVE_ERROR'
            }), 500

        return jsonify({
            'status': 'success',
            'message': 'Permutation variables updated successfully',
            'project_id': project_id,
            'variables': data.get('variables', {})
        })

    except Exception as e:
        log_event('gate3_variables_error', {
            'project_id': project_id,
            'error': str(e)
        }, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Failed to update variables',
            'code': 'VARIABLES_ERROR'
        }), 500

# ====================
# Permutation Execution Endpoint
# ====================

@api_v2.route('/permutation/execute/<project_id>', methods=['POST'])
@require_admin
def execute_permutation_v2(project_id):
    """Execute permutation engine (Admin only)"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')
        data = request.get_json() or {}

        # Load user's projects (admin can access any user's projects)
        projects_data = load_projects_data()

        # Find the project across all users
        project = None
        project_owner = None
        for email, user_data in projects_data.items():
            for p in user_data.get('projects', []):
                if p['id'] == project_id:
                    project = p
                    project_owner = email
                    break
            if project:
                break

        if not project:
            return jsonify({
                'status': 'error',
                'message': 'Project not found',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Check if Gate 3 is ready
        if not project.get('gate3_data') or not project.get('gate2_completed'):
            return jsonify({
                'status': 'error',
                'message': 'Project must complete Gates 2 and 3 before permutation execution',
                'code': 'GATES_NOT_READY'
            }), 400

        # Generate permutation results (simplified example)
        variables = project['gate3_data'].get('variables', {})
        base_results = project.get('gate2_data', {}).get('calculation_results', {})

        permutations = []
        for i in range(data.get('count', 100)):  # Generate specified number of permutations
            permutation = {
                'id': f'perm_{i+1}',
                'irr': base_results.get('irr', 12.5) + (i * 0.1) - 5,
                'npv': base_results.get('npv', 5000000) + (i * 10000) - 500000,
                'dscr': base_results.get('dscr', 1.35) + (i * 0.01) - 0.15,
                'yield': base_results.get('yield', 8.2) + (i * 0.05) - 2,
                'ltv': base_results.get('ltv', 75.0) + (i * 0.2) - 10,
                'scenario': i + 1,
                'variables_used': variables
            }
            permutations.append(permutation)

        # Create permutation results
        permutation_results = {
            'project_id': project_id,
            'project_owner': project_owner,
            'executed_by': user_email,
            'executed_at': datetime.now().isoformat(),
            'total_permutations': len(permutations),
            'permutations': permutations,
            'summary': {
                'avg_irr': sum(p['irr'] for p in permutations) / len(permutations),
                'max_npv': max(p['npv'] for p in permutations),
                'min_dscr': min(p['dscr'] for p in permutations),
                'best_scenario': max(permutations, key=lambda x: x['irr'])['scenario'],
                'worst_scenario': min(permutations, key=lambda x: x['irr'])['scenario']
            }
        }

        # Update project with permutation results
        for email, user_data in projects_data.items():
            for i, p in enumerate(user_data.get('projects', [])):
                if p['id'] == project_id:
                    projects_data[email]['projects'][i]['gate3_data']['permutation_results'] = permutation_results
                    projects_data[email]['projects'][i]['gate3_data']['status'] = 'completed'
                    projects_data[email]['projects'][i]['gate3_completed'] = True
                    projects_data[email]['projects'][i]['updated_at'] = datetime.now().isoformat()

                    # Save updated data
                    save_projects_data(email, projects_data[email])
                    break

        log_event('permutation_executed', {
            'project_id': project_id,
            'project_owner': project_owner,
            'executed_by': user_email,
            'total_permutations': len(permutations)
        })

        return jsonify({
            'status': 'success',
            'message': f'Permutation execution completed: {len(permutations)} scenarios generated',
            'project_id': project_id,
            'results': permutation_results
        })

    except Exception as e:
        log_event('permutation_execution_error', {
            'project_id': project_id,
            'error': str(e)
        }, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Permutation execution failed',
            'code': 'EXECUTION_ERROR'
        }), 500

# ====================
# Trash Management Endpoints
# ====================

@api_v2.route('/trash/move', methods=['POST'])
@require_authentication
def move_to_trash():
    """Move a project to trash"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')
        data = request.get_json()

        if not data or not data.get('project_id'):
            return jsonify({
                'status': 'error',
                'message': 'Project ID required',
                'code': 'PROJECT_ID_REQUIRED'
            }), 400

        project_id = data['project_id']

        # Load user's projects
        user_projects = get_user_projects(user_email)
        projects = user_projects['projects']

        # Find and remove the project
        project_to_trash = None
        for i, project in enumerate(projects):
            if project['id'] == project_id:
                project_to_trash = projects.pop(i)
                # Remove from order as well
                if project_id in user_projects['order']:
                    user_projects['order'].remove(project_id)
                break

        if not project_to_trash:
            return jsonify({
                'status': 'error',
                'message': 'Project not found',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Initialize trash if not exists
        if 'trash' not in user_projects:
            user_projects['trash'] = []

        # Add to trash with metadata
        project_to_trash['deleted_at'] = datetime.now().isoformat()
        project_to_trash['deleted_by'] = user_email
        user_projects['trash'].append(project_to_trash)

        # Save to database
        success = save_projects_data(user_email, user_projects)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to move project to trash',
                'code': 'SAVE_ERROR'
            }), 500

        log_event('project_moved_to_trash', {
            'project_id': project_id,
            'user_email': user_email,
            'project_title': project_to_trash.get('title')
        })

        return jsonify({
            'status': 'success',
            'message': 'Project moved to trash successfully',
            'project_id': project_id
        })

    except Exception as e:
        log_event('trash_move_error', {'error': str(e)}, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Failed to move project to trash',
            'code': 'TRASH_ERROR'
        }), 500

@api_v2.route('/trash/restore/<project_id>', methods=['POST'])
@require_authentication
def restore_from_trash(project_id):
    """Restore a project from trash"""
    try:
        ip_address = get_real_ip()
        user_email = session.get(f'user_email_{ip_address}')

        # Load user's projects
        user_projects = get_user_projects(user_email)

        if 'trash' not in user_projects:
            user_projects['trash'] = []

        # Find and restore the project
        project_to_restore = None
        for i, project in enumerate(user_projects['trash']):
            if project['id'] == project_id:
                project_to_restore = user_projects['trash'].pop(i)
                break

        if not project_to_restore:
            return jsonify({
                'status': 'error',
                'message': 'Project not found in trash',
                'code': 'PROJECT_NOT_FOUND'
            }), 404

        # Clean up trash metadata
        project_to_restore.pop('deleted_at', None)
        project_to_restore.pop('deleted_by', None)
        project_to_restore['updated_at'] = datetime.now().isoformat()

        # Add back to projects
        user_projects['projects'].append(project_to_restore)
        user_projects['order'].append(project_id)

        # Save to database
        success = save_projects_data(user_email, user_projects)
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Failed to restore project',
                'code': 'SAVE_ERROR'
            }), 500

        log_event('project_restored_from_trash', {
            'project_id': project_id,
            'user_email': user_email,
            'project_title': project_to_restore.get('title')
        })

        return jsonify({
            'status': 'success',
            'message': 'Project restored successfully',
            'project': project_to_restore
        })

    except Exception as e:
        log_event('trash_restore_error', {
            'project_id': project_id,
            'error': str(e)
        }, 'ERROR')
        return jsonify({
            'status': 'error',
            'message': 'Failed to restore project',
            'code': 'RESTORE_ERROR'
        }), 500

# ====================
# Error Handlers
# ====================

@api_v2.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'code': 'NOT_FOUND'
    }), 404

@api_v2.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': 'Method not allowed',
        'code': 'METHOD_NOT_ALLOWED'
    }), 405

@api_v2.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500

# ====================
# Health Check Endpoint
# ====================

@api_v2.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API v2 is healthy',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'cloud_db_available': CLOUD_DB_AVAILABLE
    })