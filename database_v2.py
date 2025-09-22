import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson import ObjectId
import certifi

# Import existing cloud database module
from cloud_database import CloudDatabase, get_mongodb_uri

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecuritizationDatabase:
    """
    Complete database implementation for securitization platform with MongoDB Atlas.
    Handles 3-gate workflow, trash operations, and audit logging.
    """

    def __init__(self):
        """Initialize database connection and collections."""
        try:
            # Try to use existing CloudDatabase infrastructure first
            mongodb_uri = get_mongodb_uri()

            if mongodb_uri:
                # Connect to MongoDB Atlas with SSL certificate verification
                self.client = MongoClient(
                    mongodb_uri,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000
                )

                # Test connection
                self.client.admin.command('ping')
                logger.info("Successfully connected to MongoDB Atlas")

                # Get database
                self.db = self.client.securitization_platform
            else:
                # Fallback to CloudDatabase instance
                cloud_db = CloudDatabase()
                if hasattr(cloud_db, 'db') and cloud_db.db:
                    self.client = cloud_db.client
                    self.db = cloud_db.db
                    logger.info("Using existing CloudDatabase connection")
                else:
                    raise ValueError("No MongoDB connection available")

            # Initialize collections
            self._initialize_collections()

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _initialize_collections(self):
        """Initialize all collections with proper indexes and TTL."""
        try:
            # Define collections
            self.gate1_projects = self.db.gate1_projects
            self.gate2_derived = self.db.gate2_derived
            self.gate3_variables = self.db.gate3_variables
            self.permutation_results = self.db.permutation_results
            self.trash = self.db.trash
            self.audit_log = self.db.audit_log

            # Create indexes for gate1_projects
            self.gate1_projects.create_index([("project_id", ASCENDING)], unique=True)
            self.gate1_projects.create_index([("user_id", ASCENDING)])
            self.gate1_projects.create_index([("created_at", DESCENDING)])
            self.gate1_projects.create_index([("last_modified", DESCENDING)])

            # Create indexes for gate2_derived
            self.gate2_derived.create_index([("project_id", ASCENDING)], unique=True)
            self.gate2_derived.create_index([("user_id", ASCENDING)])

            # Create indexes for gate3_variables
            self.gate3_variables.create_index([("project_id", ASCENDING)], unique=True)
            self.gate3_variables.create_index([("user_id", ASCENDING)])

            # Create indexes for permutation_results
            self.permutation_results.create_index([("project_id", ASCENDING)])
            self.permutation_results.create_index([("user_id", ASCENDING)])
            self.permutation_results.create_index([("created_at", DESCENDING)])

            # Create TTL index for trash collection (30 days)
            self.trash.create_index([("deleted_at", ASCENDING)], expireAfterSeconds=30*24*3600)
            self.trash.create_index([("original_project_id", ASCENDING)])
            self.trash.create_index([("user_id", ASCENDING)])

            # Create indexes for audit_log
            self.audit_log.create_index([("timestamp", DESCENDING)])
            self.audit_log.create_index([("user_id", ASCENDING)])
            self.audit_log.create_index([("action", ASCENDING)])
            self.audit_log.create_index([("project_id", ASCENDING)])

            logger.info("Collections and indexes initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
            raise

    def _audit_log(self, user_id: str, action: str, details: Dict[str, Any], project_id: str = None):
        """Log user actions for audit trail."""
        try:
            audit_entry = {
                "user_id": user_id,
                "action": action,
                "project_id": project_id,
                "details": details,
                "timestamp": datetime.utcnow(),
                "ip_address": details.get("ip_address"),
                "user_agent": details.get("user_agent")
            }

            self.audit_log.insert_one(audit_entry)

        except Exception as e:
            logger.error(f"Failed to log audit entry: {e}")
            # Don't raise exception as audit logging shouldn't break main functionality

    # ===============================
    # GATE 1 OPERATIONS
    # ===============================

    def create_project(self, user_id: str, project_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Create a new Gate 1 project."""
        try:
            # Generate project ID
            project_id = str(ObjectId())

            # Validate required fields
            validation_result = self.validate_gate1(project_data)
            if not validation_result[0]:
                return False, validation_result[1], {}

            # Prepare project document
            project_doc = {
                "project_id": project_id,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "last_modified": datetime.utcnow(),
                "gate1_status": "active",
                "gate2_status": "not_started",
                "gate3_status": "not_started",
                **project_data
            }

            # Insert project
            result = self.gate1_projects.insert_one(project_doc)

            # Log action
            self._audit_log(
                user_id=user_id,
                action="create_project",
                details={"project_name": project_data.get("project_name", "Unknown")},
                project_id=project_id
            )

            return True, "Project created successfully", {
                "project_id": project_id,
                "created_at": project_doc["created_at"]
            }

        except DuplicateKeyError:
            return False, "Project ID already exists", {}
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            return False, f"Database error: {str(e)}", {}

    def auto_save_project(self, user_id: str, project_id: str, project_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Auto-save project data (no validation required)."""
        try:
            update_data = {
                **project_data,
                "last_modified": datetime.utcnow(),
                "auto_saved": True
            }

            result = self.gate1_projects.update_one(
                {"project_id": project_id, "user_id": user_id},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return False, "Project not found"

            return True, "Project auto-saved successfully"

        except Exception as e:
            logger.error(f"Failed to auto-save project: {e}")
            return False, f"Database error: {str(e)}"

    def validate_gate1(self, project_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate Gate 1 project data."""
        required_fields = [
            "project_name",
            "asset_type",
            "total_asset_value",
            "target_rating",
            "structure_type"
        ]

        # Check required fields
        for field in required_fields:
            if field not in project_data or not project_data[field]:
                return False, f"Missing required field: {field}"

        # Validate data types and ranges
        try:
            total_value = float(project_data["total_asset_value"])
            if total_value <= 0:
                return False, "Total asset value must be positive"
        except (ValueError, TypeError):
            return False, "Invalid total asset value format"

        # Validate target rating
        valid_ratings = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-"]
        if project_data["target_rating"] not in valid_ratings:
            return False, "Invalid target rating"

        return True, "Validation successful"

    def get_gate1_project(self, user_id: str, project_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Retrieve a Gate 1 project."""
        try:
            project = self.gate1_projects.find_one(
                {"project_id": project_id, "user_id": user_id},
                {"_id": 0}
            )

            if not project:
                return False, "Project not found", {}

            return True, "Project retrieved successfully", project

        except Exception as e:
            logger.error(f"Failed to retrieve project: {e}")
            return False, f"Database error: {str(e)}", {}

    def update_gate1_project(self, user_id: str, project_id: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """Update a Gate 1 project."""
        try:
            # Validate updates if they contain core fields
            core_fields = ["project_name", "asset_type", "total_asset_value", "target_rating", "structure_type"]
            if any(field in updates for field in core_fields):
                validation_result = self.validate_gate1(updates)
                if not validation_result[0]:
                    return False, validation_result[1]

            updates["last_modified"] = datetime.utcnow()

            result = self.gate1_projects.update_one(
                {"project_id": project_id, "user_id": user_id},
                {"$set": updates}
            )

            if result.matched_count == 0:
                return False, "Project not found"

            # Log action
            self._audit_log(
                user_id=user_id,
                action="update_gate1_project",
                details={"updated_fields": list(updates.keys())},
                project_id=project_id
            )

            return True, "Project updated successfully"

        except Exception as e:
            logger.error(f"Failed to update project: {e}")
            return False, f"Database error: {str(e)}"

    def list_user_projects(self, user_id: str, limit: int = 50, skip: int = 0) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """List all projects for a user."""
        try:
            projects = list(self.gate1_projects.find(
                {"user_id": user_id},
                {"_id": 0}
            ).sort("last_modified", DESCENDING).skip(skip).limit(limit))

            return True, "Projects retrieved successfully", projects

        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return False, f"Database error: {str(e)}", []

    # ===============================
    # GATE 2 OPERATIONS
    # ===============================

    def initialize_gate2(self, user_id: str, project_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Initialize Gate 2 for a project."""
        try:
            # Check if Gate 1 exists and is valid
            gate1_result = self.get_gate1_project(user_id, project_id)
            if not gate1_result[0]:
                return False, "Gate 1 project not found", {}

            gate1_data = gate1_result[2]

            # Check if Gate 2 already exists
            existing_gate2 = self.gate2_derived.find_one({"project_id": project_id})
            if existing_gate2:
                return True, "Gate 2 already initialized", existing_gate2

            # Calculate derived fields
            derived_data = self.calculate_derived_fields(gate1_data)

            # Prepare Gate 2 document
            gate2_doc = {
                "project_id": project_id,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "last_modified": datetime.utcnow(),
                "gate2_status": "active",
                **derived_data
            }

            # Insert Gate 2 data
            self.gate2_derived.insert_one(gate2_doc)

            # Update Gate 1 status
            self.gate1_projects.update_one(
                {"project_id": project_id},
                {"$set": {"gate2_status": "active"}}
            )

            # Log action
            self._audit_log(
                user_id=user_id,
                action="initialize_gate2",
                details={"derived_fields_count": len(derived_data)},
                project_id=project_id
            )

            return True, "Gate 2 initialized successfully", gate2_doc

        except Exception as e:
            logger.error(f"Failed to initialize Gate 2: {e}")
            return False, f"Database error: {str(e)}", {}

    def calculate_derived_fields(self, gate1_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived fields for Gate 2."""
        derived = {}

        try:
            total_value = float(gate1_data.get("total_asset_value", 0))
            target_rating = gate1_data.get("target_rating", "BBB")
            asset_type = gate1_data.get("asset_type", "")

            # Calculate credit enhancement based on target rating
            credit_enhancement_map = {
                "AAA": 0.20, "AA+": 0.18, "AA": 0.16, "AA-": 0.14,
                "A+": 0.12, "A": 0.10, "A-": 0.08,
                "BBB+": 0.06, "BBB": 0.04, "BBB-": 0.02
            }

            credit_enhancement = credit_enhancement_map.get(target_rating, 0.04)
            derived["credit_enhancement_pct"] = credit_enhancement
            derived["credit_enhancement_amount"] = total_value * credit_enhancement

            # Calculate tranching structure
            senior_pct = 1 - credit_enhancement
            derived["senior_tranche_pct"] = senior_pct
            derived["senior_tranche_amount"] = total_value * senior_pct

            # Calculate expected losses based on asset type
            expected_loss_map = {
                "residential_mortgage": 0.02,
                "commercial_mortgage": 0.03,
                "auto_loan": 0.015,
                "credit_card": 0.05,
                "corporate_bond": 0.01
            }

            expected_loss = expected_loss_map.get(asset_type.lower(), 0.025)
            derived["expected_loss_rate"] = expected_loss
            derived["expected_loss_amount"] = total_value * expected_loss

            # Calculate required capital
            derived["required_capital"] = max(
                derived["credit_enhancement_amount"],
                derived["expected_loss_amount"] * 2
            )

            # Calculate yield and spread estimates
            base_yield_map = {
                "AAA": 0.025, "AA+": 0.028, "AA": 0.030, "AA-": 0.032,
                "A+": 0.035, "A": 0.038, "A-": 0.041,
                "BBB+": 0.045, "BBB": 0.050, "BBB-": 0.055
            }

            derived["estimated_yield"] = base_yield_map.get(target_rating, 0.050)
            derived["estimated_spread"] = derived["estimated_yield"] - 0.020  # Assuming 2% risk-free rate

            # Add calculation timestamp
            derived["calculations_performed_at"] = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error calculating derived fields: {e}")
            # Return basic structure even if calculations fail
            derived = {
                "credit_enhancement_pct": 0.04,
                "error": f"Calculation error: {str(e)}",
                "calculations_performed_at": datetime.utcnow()
            }

        return derived

    def get_gate2_data(self, user_id: str, project_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Retrieve Gate 2 data for a project."""
        try:
            gate2_data = self.gate2_derived.find_one(
                {"project_id": project_id, "user_id": user_id},
                {"_id": 0}
            )

            if not gate2_data:
                return False, "Gate 2 data not found", {}

            return True, "Gate 2 data retrieved successfully", gate2_data

        except Exception as e:
            logger.error(f"Failed to retrieve Gate 2 data: {e}")
            return False, f"Database error: {str(e)}", {}

    def update_gate2_data(self, user_id: str, project_id: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """Update Gate 2 derived data."""
        try:
            updates["last_modified"] = datetime.utcnow()

            result = self.gate2_derived.update_one(
                {"project_id": project_id, "user_id": user_id},
                {"$set": updates}
            )

            if result.matched_count == 0:
                return False, "Gate 2 data not found"

            # Log action
            self._audit_log(
                user_id=user_id,
                action="update_gate2_data",
                details={"updated_fields": list(updates.keys())},
                project_id=project_id
            )

            return True, "Gate 2 data updated successfully"

        except Exception as e:
            logger.error(f"Failed to update Gate 2 data: {e}")
            return False, f"Database error: {str(e)}"

    # ===============================
    # GATE 3 OPERATIONS
    # ===============================

    def initialize_gate3(self, user_id: str, project_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Initialize Gate 3 for a project."""
        try:
            # Check if Gate 2 exists and is valid
            gate2_result = self.get_gate2_data(user_id, project_id)
            if not gate2_result[0]:
                return False, "Gate 2 not found or not completed", {}

            # Check if Gate 3 already exists
            existing_gate3 = self.gate3_variables.find_one({"project_id": project_id})
            if existing_gate3:
                return True, "Gate 3 already initialized", existing_gate3

            # Initialize Gate 3 with default variable structure
            gate3_doc = {
                "project_id": project_id,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "last_modified": datetime.utcnow(),
                "gate3_status": "active",
                "permutation_variables": {},
                "variable_count": 0,
                "max_permutations": 1000000,  # Default limit
                "current_permutations": 0
            }

            # Insert Gate 3 data
            self.gate3_variables.insert_one(gate3_doc)

            # Update Gate 1 status
            self.gate1_projects.update_one(
                {"project_id": project_id},
                {"$set": {"gate3_status": "active"}}
            )

            # Log action
            self._audit_log(
                user_id=user_id,
                action="initialize_gate3",
                details={},
                project_id=project_id
            )

            return True, "Gate 3 initialized successfully", gate3_doc

        except Exception as e:
            logger.error(f"Failed to initialize Gate 3: {e}")
            return False, f"Database error: {str(e)}", {}

    def add_permutation_variable(self, user_id: str, project_id: str, variable_name: str,
                               variable_config: Dict[str, Any]) -> Tuple[bool, str]:
        """Add a variable for permutation analysis."""
        try:
            # Validate variable configuration
            required_fields = ["type", "min_value", "max_value", "step_size"]
            for field in required_fields:
                if field not in variable_config:
                    return False, f"Missing required field in variable config: {field}"

            # Calculate number of steps for this variable
            try:
                min_val = float(variable_config["min_value"])
                max_val = float(variable_config["max_value"])
                step_size = float(variable_config["step_size"])

                if min_val >= max_val:
                    return False, "Min value must be less than max value"

                if step_size <= 0:
                    return False, "Step size must be positive"

                steps = int((max_val - min_val) / step_size) + 1
                variable_config["calculated_steps"] = steps

            except (ValueError, TypeError):
                return False, "Invalid numeric values in variable configuration"

            # Update the variable in Gate 3
            update_result = self.gate3_variables.update_one(
                {"project_id": project_id, "user_id": user_id},
                {
                    "$set": {
                        f"permutation_variables.{variable_name}": variable_config,
                        "last_modified": datetime.utcnow()
                    },
                    "$inc": {"variable_count": 1}
                }
            )

            if update_result.matched_count == 0:
                return False, "Gate 3 not found"

            # Log action
            self._audit_log(
                user_id=user_id,
                action="add_permutation_variable",
                details={
                    "variable_name": variable_name,
                    "steps": steps
                },
                project_id=project_id
            )

            return True, f"Variable '{variable_name}' added successfully with {steps} steps"

        except Exception as e:
            logger.error(f"Failed to add permutation variable: {e}")
            return False, f"Database error: {str(e)}"

    def get_gate3_data(self, user_id: str, project_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Retrieve Gate 3 data for a project."""
        try:
            gate3_data = self.gate3_variables.find_one(
                {"project_id": project_id, "user_id": user_id},
                {"_id": 0}
            )

            if not gate3_data:
                return False, "Gate 3 data not found", {}

            return True, "Gate 3 data retrieved successfully", gate3_data

        except Exception as e:
            logger.error(f"Failed to retrieve Gate 3 data: {e}")
            return False, f"Database error: {str(e)}", {}

    def update_gate3_data(self, user_id: str, project_id: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """Update Gate 3 data."""
        try:
            updates["last_modified"] = datetime.utcnow()

            result = self.gate3_variables.update_one(
                {"project_id": project_id, "user_id": user_id},
                {"$set": updates}
            )

            if result.matched_count == 0:
                return False, "Gate 3 data not found"

            # Log action
            self._audit_log(
                user_id=user_id,
                action="update_gate3_data",
                details={"updated_fields": list(updates.keys())},
                project_id=project_id
            )

            return True, "Gate 3 data updated successfully"

        except Exception as e:
            logger.error(f"Failed to update Gate 3 data: {e}")
            return False, f"Database error: {str(e)}"

    def remove_permutation_variable(self, user_id: str, project_id: str, variable_name: str) -> Tuple[bool, str]:
        """Remove a permutation variable."""
        try:
            result = self.gate3_variables.update_one(
                {"project_id": project_id, "user_id": user_id},
                {
                    "$unset": {f"permutation_variables.{variable_name}": ""},
                    "$inc": {"variable_count": -1},
                    "$set": {"last_modified": datetime.utcnow()}
                }
            )

            if result.matched_count == 0:
                return False, "Gate 3 data not found"

            # Log action
            self._audit_log(
                user_id=user_id,
                action="remove_permutation_variable",
                details={"variable_name": variable_name},
                project_id=project_id
            )

            return True, f"Variable '{variable_name}' removed successfully"

        except Exception as e:
            logger.error(f"Failed to remove permutation variable: {e}")
            return False, f"Database error: {str(e)}"

    # ===============================
    # PERMUTATION RESULTS OPERATIONS
    # ===============================

    def save_permutation_results(self, user_id: str, project_id: str, results_data: Dict[str, Any]) -> Tuple[bool, str, str]:
        """Save permutation analysis results."""
        try:
            result_doc = {
                "result_id": str(ObjectId()),
                "project_id": project_id,
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "result_type": results_data.get("result_type", "permutation_analysis"),
                "total_permutations": results_data.get("total_permutations", 0),
                "execution_time_seconds": results_data.get("execution_time_seconds", 0),
                "results": results_data
            }

            insert_result = self.permutation_results.insert_one(result_doc)
            result_id = result_doc["result_id"]

            # Update Gate 3 with latest results info
            self.gate3_variables.update_one(
                {"project_id": project_id, "user_id": user_id},
                {
                    "$set": {
                        "last_results_id": result_id,
                        "last_results_created": datetime.utcnow(),
                        "current_permutations": results_data.get("total_permutations", 0)
                    }
                }
            )

            # Log action
            self._audit_log(
                user_id=user_id,
                action="save_permutation_results",
                details={
                    "result_id": result_id,
                    "total_permutations": results_data.get("total_permutations", 0)
                },
                project_id=project_id
            )

            return True, "Permutation results saved successfully", result_id

        except Exception as e:
            logger.error(f"Failed to save permutation results: {e}")
            return False, f"Database error: {str(e)}", ""

    def get_permutation_results(self, user_id: str, project_id: str, result_id: str = None) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """Retrieve permutation results."""
        try:
            query = {"project_id": project_id, "user_id": user_id}
            if result_id:
                query["result_id"] = result_id

            results = list(self.permutation_results.find(
                query,
                {"_id": 0}
            ).sort("created_at", DESCENDING))

            return True, "Results retrieved successfully", results

        except Exception as e:
            logger.error(f"Failed to retrieve permutation results: {e}")
            return False, f"Database error: {str(e)}", []

    # ===============================
    # TRASH OPERATIONS
    # ===============================

    def move_to_trash(self, user_id: str, project_id: str, deletion_reason: str = "") -> Tuple[bool, str]:
        """Move a project to trash with 30-day TTL."""
        try:
            # Get all project data from all gates
            gate1_data = self.gate1_projects.find_one({"project_id": project_id, "user_id": user_id})
            if not gate1_data:
                return False, "Project not found"

            gate2_data = self.gate2_derived.find_one({"project_id": project_id})
            gate3_data = self.gate3_variables.find_one({"project_id": project_id})
            permutation_data = list(self.permutation_results.find({"project_id": project_id}))

            # Create trash document
            trash_doc = {
                "trash_id": str(ObjectId()),
                "original_project_id": project_id,
                "user_id": user_id,
                "deleted_at": datetime.utcnow(),
                "deletion_reason": deletion_reason,
                "gate1_data": gate1_data,
                "gate2_data": gate2_data,
                "gate3_data": gate3_data,
                "permutation_data": permutation_data,
                "project_name": gate1_data.get("project_name", "Unknown")
            }

            # Insert into trash
            self.trash.insert_one(trash_doc)

            # Remove from all active collections
            self.gate1_projects.delete_one({"project_id": project_id, "user_id": user_id})
            self.gate2_derived.delete_one({"project_id": project_id})
            self.gate3_variables.delete_one({"project_id": project_id})
            self.permutation_results.delete_many({"project_id": project_id})

            # Log action
            self._audit_log(
                user_id=user_id,
                action="move_to_trash",
                details={
                    "project_name": gate1_data.get("project_name", "Unknown"),
                    "deletion_reason": deletion_reason,
                    "trash_id": trash_doc["trash_id"]
                },
                project_id=project_id
            )

            return True, f"Project moved to trash successfully. Will be permanently deleted in 30 days."

        except Exception as e:
            logger.error(f"Failed to move project to trash: {e}")
            return False, f"Database error: {str(e)}"

    def restore_from_trash(self, user_id: str, trash_id: str) -> Tuple[bool, str, str]:
        """Restore a project from trash."""
        try:
            # Find trash document
            trash_doc = self.trash.find_one({"trash_id": trash_id, "user_id": user_id})
            if not trash_doc:
                return False, "Trash item not found", ""

            original_project_id = trash_doc["original_project_id"]

            # Check if project with same ID already exists
            existing = self.gate1_projects.find_one({"project_id": original_project_id})
            if existing:
                # Generate new project ID
                new_project_id = str(ObjectId())
            else:
                new_project_id = original_project_id

            # Restore Gate 1 data
            if trash_doc.get("gate1_data"):
                gate1_data = trash_doc["gate1_data"].copy()
                gate1_data["project_id"] = new_project_id
                gate1_data["restored_at"] = datetime.utcnow()
                gate1_data["restored_from_trash_id"] = trash_id
                self.gate1_projects.insert_one(gate1_data)

            # Restore Gate 2 data
            if trash_doc.get("gate2_data"):
                gate2_data = trash_doc["gate2_data"].copy()
                gate2_data["project_id"] = new_project_id
                gate2_data["restored_at"] = datetime.utcnow()
                self.gate2_derived.insert_one(gate2_data)

            # Restore Gate 3 data
            if trash_doc.get("gate3_data"):
                gate3_data = trash_doc["gate3_data"].copy()
                gate3_data["project_id"] = new_project_id
                gate3_data["restored_at"] = datetime.utcnow()
                self.gate3_variables.insert_one(gate3_data)

            # Restore permutation data
            if trash_doc.get("permutation_data"):
                for perm_doc in trash_doc["permutation_data"]:
                    perm_doc = perm_doc.copy()
                    perm_doc["project_id"] = new_project_id
                    perm_doc["restored_at"] = datetime.utcnow()
                    self.permutation_results.insert_one(perm_doc)

            # Remove from trash
            self.trash.delete_one({"trash_id": trash_id})

            # Log action
            self._audit_log(
                user_id=user_id,
                action="restore_from_trash",
                details={
                    "trash_id": trash_id,
                    "new_project_id": new_project_id,
                    "original_project_id": original_project_id
                },
                project_id=new_project_id
            )

            return True, "Project restored successfully", new_project_id

        except Exception as e:
            logger.error(f"Failed to restore project from trash: {e}")
            return False, f"Database error: {str(e)}", ""

    def list_trash_items(self, user_id: str, limit: int = 50) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """List items in trash for a user."""
        try:
            trash_items = list(self.trash.find(
                {"user_id": user_id},
                {
                    "_id": 0,
                    "trash_id": 1,
                    "original_project_id": 1,
                    "project_name": 1,
                    "deleted_at": 1,
                    "deletion_reason": 1
                }
            ).sort("deleted_at", DESCENDING).limit(limit))

            # Add days remaining before permanent deletion
            for item in trash_items:
                deleted_at = item["deleted_at"]
                expires_at = deleted_at + timedelta(days=30)
                days_remaining = (expires_at - datetime.utcnow()).days
                item["days_remaining"] = max(0, days_remaining)
                item["expires_at"] = expires_at

            return True, "Trash items retrieved successfully", trash_items

        except Exception as e:
            logger.error(f"Failed to list trash items: {e}")
            return False, f"Database error: {str(e)}", []

    def permanently_delete_trash_item(self, user_id: str, trash_id: str) -> Tuple[bool, str]:
        """Permanently delete an item from trash."""
        try:
            result = self.trash.delete_one({"trash_id": trash_id, "user_id": user_id})

            if result.deleted_count == 0:
                return False, "Trash item not found"

            # Log action
            self._audit_log(
                user_id=user_id,
                action="permanently_delete_trash_item",
                details={"trash_id": trash_id}
            )

            return True, "Item permanently deleted from trash"

        except Exception as e:
            logger.error(f"Failed to permanently delete trash item: {e}")
            return False, f"Database error: {str(e)}"

    # ===============================
    # UTILITY METHODS
    # ===============================

    def get_project_summary(self, user_id: str, project_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Get a complete summary of a project across all gates."""
        try:
            summary = {}

            # Get Gate 1 data
            gate1_result = self.get_gate1_project(user_id, project_id)
            if gate1_result[0]:
                summary["gate1"] = gate1_result[2]

            # Get Gate 2 data
            gate2_result = self.get_gate2_data(user_id, project_id)
            if gate2_result[0]:
                summary["gate2"] = gate2_result[2]

            # Get Gate 3 data
            gate3_result = self.get_gate3_data(user_id, project_id)
            if gate3_result[0]:
                summary["gate3"] = gate3_result[2]

            # Get latest permutation results
            results = self.get_permutation_results(user_id, project_id)
            if results[0] and results[2]:
                summary["latest_permutation_results"] = results[2][0]  # Most recent

            if not summary:
                return False, "No project data found", {}

            return True, "Project summary retrieved successfully", summary

        except Exception as e:
            logger.error(f"Failed to get project summary: {e}")
            return False, f"Database error: {str(e)}", {}

    def get_user_statistics(self, user_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Get user statistics across all projects."""
        try:
            stats = {}

            # Count projects by status
            stats["total_projects"] = self.gate1_projects.count_documents({"user_id": user_id})
            stats["gate2_completed"] = self.gate2_derived.count_documents({"user_id": user_id})
            stats["gate3_completed"] = self.gate3_variables.count_documents({"user_id": user_id})

            # Count trash items
            stats["trash_items"] = self.trash.count_documents({"user_id": user_id})

            # Count permutation results
            stats["total_permutation_runs"] = self.permutation_results.count_documents({"user_id": user_id})

            # Get recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            stats["recent_projects"] = self.gate1_projects.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": thirty_days_ago}
            })

            # Get most recent project
            recent_project = self.gate1_projects.find_one(
                {"user_id": user_id},
                {"project_name": 1, "last_modified": 1},
                sort=[("last_modified", DESCENDING)]
            )

            if recent_project:
                stats["most_recent_project"] = {
                    "name": recent_project.get("project_name"),
                    "last_modified": recent_project.get("last_modified")
                }

            return True, "User statistics retrieved successfully", stats

        except Exception as e:
            logger.error(f"Failed to get user statistics: {e}")
            return False, f"Database error: {str(e)}", {}

    def health_check(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Check database health and connectivity."""
        try:
            # Test connection
            self.client.admin.command('ping')

            # Test each collection
            collections_status = {}
            test_collections = [
                ("gate1_projects", self.gate1_projects),
                ("gate2_derived", self.gate2_derived),
                ("gate3_variables", self.gate3_variables),
                ("permutation_results", self.permutation_results),
                ("trash", self.trash),
                ("audit_log", self.audit_log)
            ]

            for name, collection in test_collections:
                try:
                    count = collection.count_documents({}, limit=1)
                    collections_status[name] = "healthy"
                except Exception as e:
                    collections_status[name] = f"error: {str(e)}"

            health_info = {
                "database_connected": True,
                "collections": collections_status,
                "timestamp": datetime.utcnow()
            }

            return True, "Database health check passed", health_info

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False, f"Health check failed: {str(e)}", {}

    def close_connection(self):
        """Close database connection."""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")


# Example usage and testing
if __name__ == "__main__":
    # This section can be used for testing the database class
    import os

    # Make sure to set your MongoDB URI environment variable
    # os.environ['MONGODB_URI'] = 'your_mongodb_atlas_connection_string'

    try:
        # Initialize database
        db = SecuritizationDatabase()

        # Test health check
        health_result = db.health_check()
        print(f"Health check: {health_result}")

        # Test user creation and project workflow
        test_user_id = "test_user_123"

        # Test Gate 1 creation
        test_project_data = {
            "project_name": "Test Securitization Project",
            "asset_type": "residential_mortgage",
            "total_asset_value": 100000000,  # $100M
            "target_rating": "AA",
            "structure_type": "pass_through",
            "description": "Test project for system validation"
        }

        create_result = db.create_project(test_user_id, test_project_data)
        print(f"Create project result: {create_result}")

        if create_result[0]:
            project_id = create_result[2]["project_id"]

            # Test Gate 2 initialization
            gate2_result = db.initialize_gate2(test_user_id, project_id)
            print(f"Gate 2 initialization: {gate2_result}")

            # Test Gate 3 initialization
            gate3_result = db.initialize_gate3(test_user_id, project_id)
            print(f"Gate 3 initialization: {gate3_result}")

            # Test adding permutation variable
            variable_config = {
                "type": "numeric",
                "min_value": 0.01,
                "max_value": 0.05,
                "step_size": 0.005,
                "description": "Interest rate variation"
            }

            var_result = db.add_permutation_variable(test_user_id, project_id, "interest_rate", variable_config)
            print(f"Add variable result: {var_result}")

            # Test project summary
            summary_result = db.get_project_summary(test_user_id, project_id)
            print(f"Project summary: {summary_result[0]}")

            # Test moving to trash
            trash_result = db.move_to_trash(test_user_id, project_id, "Test cleanup")
            print(f"Move to trash result: {trash_result}")

        # Close connection
        db.close_connection()

    except Exception as e:
        print(f"Test error: {e}")