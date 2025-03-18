"""
Insurance specialist functions for the CCS Insurance assistant.
This module contains all AI-callable functions for insurance and warranty operations.
"""
import os
import json
import logging
import datetime
import asyncio
from typing import Annotated, Dict, Any, List, Optional
from pathlib import Path

from livekit.agents import llm
from . import BaseBusinessFnc

# Try to import database libraries, but provide fallbacks if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

logger = logging.getLogger("insurance-assistant")

class InsuranceAssistantFnc(BaseBusinessFnc):
    """
    Insurance specialist functions for the CCS Insurance assistant
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialize_db_connection()
        self._load_warranty_plans()

    def _initialize_db_connection(self):
        """Initialize database connection for storing customer and policy data"""
        self.db_connected = False
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase library not available. DB functions will be simulated.")
            return
        
        try:
            self.supabase_url = os.environ.get("SUPABASE_URL")
            self.supabase_key = os.environ.get("SUPABASE_KEY")
            
            if not self.supabase_url or not self.supabase_key:
                logger.warning("Supabase credentials not found in environment variables")
                return
                
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            self.db_connected = True
            logger.info("Successfully connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.db_connected = False

    def _load_warranty_plans(self):
        """Load warranty plans from configuration"""
        try:
            self.warranty_plans = self.domain_config.get("warranty_plans", [])
            self.eligibility_criteria = self.domain_config.get("eligibility_criteria", {})
            
            if not self.warranty_plans:
                # Try to load from config file directly if not in domain_config
                config_path = Path(__file__).parent.parent.parent / "config" / "insurance_config.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        self.warranty_plans = config.get("warranty_plans", [])
                        self.eligibility_criteria = config.get("domain_config", {}).get("eligibility_criteria", {})
                        
            logger.info(f"Loaded {len(self.warranty_plans)} warranty plans")
        except Exception as e:
            logger.error(f"Error loading warranty plans: {e}")
            self.warranty_plans = []
            self.eligibility_criteria = {}

    @llm.ai_callable()
    async def save_customer_lead(
        self,
        first_name: Annotated[
            str, llm.TypeInfo(description="Customer's first name")
        ],
        last_name: Annotated[
            str, llm.TypeInfo(description="Customer's last name")
        ],
        phone: Annotated[
            str, llm.TypeInfo(description="Customer's phone number")
        ],
        insurance_type: Annotated[
            str, llm.TypeInfo(description="Type of insurance (e.g., auto_warranty, home_warranty)")
        ],
        email: Annotated[
            str, llm.TypeInfo(description="Customer's email address (optional)")
        ] = "",
        zip_code: Annotated[
            str, llm.TypeInfo(description="Customer's ZIP code (optional)")
        ] = "",
        notes: Annotated[
            str, llm.TypeInfo(description="Additional notes about the customer")
        ] = "",
    ) -> Dict[str, Any]:
        """
        Save a new customer lead to the database
        """
        logger.info(f"Saving customer lead: {first_name} {last_name}")
        
        # Prepare lead data
        lead_data = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "insurance_type": insurance_type,
            "lead_source": "phone_call",
            "status": "new",
            "created_at": datetime.datetime.now().isoformat()
        }
        
        if email:
            lead_data["email"] = email
        if zip_code:
            lead_data["zip_code"] = zip_code
        if notes:
            lead_data["notes"] = notes
            
        # If connected to database, save the lead
        if self.db_connected:
            try:
                result = self.supabase.table("customer_leads").insert(lead_data).execute()
                if result.data:
                    lead_id = result.data[0].get("id")
                    return {
                        "status": "success",
                        "message": "Customer lead saved successfully",
                        "lead_id": lead_id
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Failed to save customer lead"
                    }
            except Exception as e:
                logger.error(f"Error saving customer lead: {e}")
                return {
                    "status": "error",
                    "message": f"Database error: {str(e)}"
                }
        else:
            # Simulate successful database operation
            await asyncio.sleep(0.5)  # Simulate processing time
            return {
                "status": "success",
                "message": "Customer lead saved successfully (simulated)",
                "lead_id": "sim_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            }

    @llm.ai_callable()
    async def check_vehicle_eligibility(
        self,
        vehicle_year: Annotated[
            int, llm.TypeInfo(description="Year the vehicle was manufactured")
        ],
        vehicle_make: Annotated[
            str, llm.TypeInfo(description="Make of the vehicle (e.g., Toyota, Honda)")
        ],
        vehicle_model: Annotated[
            str, llm.TypeInfo(description="Model of the vehicle (e.g., Corolla, Civic)")
        ],
        mileage: Annotated[
            int, llm.TypeInfo(description="Current mileage of the vehicle")
        ],
    ) -> Dict[str, Any]:
        """
        Check if a vehicle is eligible for warranty coverage based on age and mileage
        """
        logger.info(f"Checking eligibility for {vehicle_year} {vehicle_make} {vehicle_model} with {mileage} miles")
        
        # Calculate vehicle age
        current_year = datetime.datetime.now().year
        vehicle_age = current_year - int(vehicle_year)
        
        # Get eligibility criteria from config
        max_age = self.eligibility_criteria.get('max_vehicle_age', 10)
        max_mileage = self.eligibility_criteria.get('max_vehicle_mileage', 100000)
        
        # Check basic eligibility
        is_eligible_standard = vehicle_age <= max_age and mileage <= max_mileage
        is_eligible_high_mileage = mileage > max_mileage and mileage <= 150000 and vehicle_age <= 15
        
        # Find suitable warranty plans
        suitable_plans = []
        for plan in self.warranty_plans:
            if mileage <= plan.get('max_vehicle_mileage', 0) and vehicle_age <= plan.get('max_vehicle_age', 0):
                suitable_plans.append({
                    "name": plan.get("name"),
                    "description": plan.get("description"),
                    "monthly_premium_range": plan.get("monthly_premium_range"),
                    "coverage_details": plan.get("coverage_details"),
                    "term_options": plan.get("term_length_options", [12, 24, 36]),
                    "deductible": plan.get("deductible", 100)
                })
        
        # Add high mileage plan if applicable
        if is_eligible_high_mileage and not suitable_plans:
            high_mileage_plan = next((p for p in self.warranty_plans if "High Mileage" in p.get("name", "")), None)
            if high_mileage_plan:
                suitable_plans.append({
                    "name": high_mileage_plan.get("name"),
                    "description": high_mileage_plan.get("description"),
                    "monthly_premium_range": high_mileage_plan.get("monthly_premium_range"),
                    "coverage_details": high_mileage_plan.get("coverage_details"),
                    "term_options": high_mileage_plan.get("term_length_options", [12, 24]),
                    "deductible": high_mileage_plan.get("deductible", 150)
                })
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "vehicle_details": {
                "year": vehicle_year,
                "make": vehicle_make,
                "model": vehicle_model,
                "age": vehicle_age,
                "mileage": mileage
            },
            "is_eligible_standard": is_eligible_standard,
            "is_eligible_high_mileage": is_eligible_high_mileage,
            "is_eligible": is_eligible_standard or is_eligible_high_mileage,
            "suitable_plans": suitable_plans,
            "recommendation": suitable_plans[0].get("name") if suitable_plans else "No suitable plans found"
        }

    @llm.ai_callable()
    async def save_insurance_quote(
        self,
        insurance_type: Annotated[
            str, llm.TypeInfo(description="Type of insurance (e.g., auto_warranty)")
        ],
        coverage_level: Annotated[
            str, llm.TypeInfo(description="Level of coverage (e.g., basic, standard, premium)")
        ],
        vehicle_make: Annotated[
            str, llm.TypeInfo(description="Make of the vehicle")
        ],
        vehicle_model: Annotated[
            str, llm.TypeInfo(description="Model of the vehicle")
        ],
        vehicle_year: Annotated[
            int, llm.TypeInfo(description="Year the vehicle was manufactured")
        ],
        term_length: Annotated[
            int, llm.TypeInfo(description="Term length in months")
        ],
        monthly_premium: Annotated[
            float, llm.TypeInfo(description="Monthly premium amount (optional)")
        ] = 0.0,
        customer_id: Annotated[
            str, llm.TypeInfo(description="Customer ID if available (optional)")
        ] = "",
        notes: Annotated[
            str, llm.TypeInfo(description="Additional notes about the quote")
        ] = "",
    ) -> Dict[str, Any]:
        """
        Save an insurance quote to the database
        """
        logger.info(f"Saving insurance quote for {vehicle_year} {vehicle_make} {vehicle_model}")
        
        # If monthly premium not provided, estimate based on warranty plans
        if monthly_premium <= 0:
            # Find the matching plan in config
            for plan in self.warranty_plans:
                if plan.get("name", "").lower() == coverage_level.lower() or coverage_level.lower() in plan.get("name", "").lower():
                    # Extract min and max from range (format: "$X-$Y")
                    premium_range = plan.get("monthly_premium_range", "$0-$0")
                    try:
                        min_premium = float(premium_range.split("-")[0].replace("$", "").strip())
                        max_premium = float(premium_range.split("-")[1].replace("$", "").strip())
                        monthly_premium = (min_premium + max_premium) / 2
                        break
                    except (ValueError, IndexError):
                        monthly_premium = 149.99  # Default fallback value
        
        # Prepare quote data
        quote_data = {
            "insurance_type": insurance_type,
            "coverage_level": coverage_level,
            "vehicle_make": vehicle_make,
            "vehicle_model": vehicle_model,
            "vehicle_year": vehicle_year,
            "monthly_premium": monthly_premium,
            "term_length": term_length,
            "status": "generated",
            "created_at": datetime.datetime.now().isoformat()
        }
        
        if customer_id:
            quote_data["customer_id"] = customer_id
        if notes:
            quote_data["notes"] = notes
            
        # If connected to database, save the quote
        if self.db_connected:
            try:
                result = self.supabase.table("insurance_quotes").insert(quote_data).execute()
                if result.data:
                    quote_id = result.data[0].get("id")
                    return {
                        "status": "success",
                        "message": "Insurance quote saved successfully",
                        "quote_id": quote_id,
                        "monthly_premium": monthly_premium,
                        "total_cost": monthly_premium * term_length
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Failed to save insurance quote"
                    }
            except Exception as e:
                logger.error(f"Error saving insurance quote: {e}")
                return {
                    "status": "error",
                    "message": f"Database error: {str(e)}"
                }
        else:
            # Simulate successful database operation
            await asyncio.sleep(0.5)  # Simulate processing time
            quote_id = "quote_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            return {
                "status": "success",
                "message": "Insurance quote saved successfully (simulated)",
                "quote_id": quote_id,
                "monthly_premium": monthly_premium,
                "total_cost": monthly_premium * term_length
            }

    @llm.ai_callable()
    async def schedule_callback(
        self,
        first_name: Annotated[
            str, llm.TypeInfo(description="Customer's first name")
        ],
        last_name: Annotated[
            str, llm.TypeInfo(description="Customer's last name")
        ],
        phone: Annotated[
            str, llm.TypeInfo(description="Customer's phone number")
        ],
        preferred_date: Annotated[
            str, llm.TypeInfo(description="Preferred callback date (YYYY-MM-DD format)")
        ],
        preferred_time: Annotated[
            str, llm.TypeInfo(description="Preferred callback time (e.g., '2:00 PM')")
        ],
        insurance_type: Annotated[
            str, llm.TypeInfo(description="Type of insurance (e.g., auto_warranty)")
        ],
        email: Annotated[
            str, llm.TypeInfo(description="Customer's email address (optional)")
        ] = "",
        specific_question: Annotated[
            str, llm.TypeInfo(description="Specific questions or topics to address during callback")
        ] = "",
    ) -> Dict[str, Any]:
        """
        Schedule a callback appointment for a customer
        """
        logger.info(f"Scheduling callback for {first_name} {last_name} on {preferred_date} at {preferred_time}")
        
        # Prepare callback data
        callback_data = {
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "preferred_date": preferred_date,
            "preferred_time": preferred_time,
            "insurance_type": insurance_type,
            "status": "scheduled",
            "source": "phone_call",
            "requested_at": datetime.datetime.now().isoformat()
        }
        
        if email:
            callback_data["email"] = email
        if specific_question:
            callback_data["specific_question"] = specific_question
            
        # If connected to database, save the callback request
        if self.db_connected:
            try:
                result = self.supabase.table("callback_requests").insert(callback_data).execute()
                if result.data:
                    callback_id = result.data[0].get("id")
                    return {
                        "status": "success",
                        "message": "Callback scheduled successfully",
                        "callback_id": callback_id,
                        "callback_details": {
                            "name": f"{first_name} {last_name}",
                            "date": preferred_date,
                            "time": preferred_time
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Failed to schedule callback"
                    }
            except Exception as e:
                logger.error(f"Error scheduling callback: {e}")
                return {
                    "status": "error",
                    "message": f"Database error: {str(e)}"
                }
        else:
            # Simulate successful database operation
            await asyncio.sleep(0.5)  # Simulate processing time
            callback_id = "cb_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            return {
                "status": "success",
                "message": "Callback scheduled successfully (simulated)",
                "callback_id": callback_id,
                "callback_details": {
                    "name": f"{first_name} {last_name}",
                    "date": preferred_date,
                    "time": preferred_time
                }
            }

    @llm.ai_callable()
    async def save_conversation_feedback(
        self,
        conversation_id: Annotated[
            str, llm.TypeInfo(description="Conversation or call identifier")
        ],
        satisfaction_rating: Annotated[
            int, llm.TypeInfo(description="Customer satisfaction rating (1-5)")
        ],
        comments: Annotated[
            str, llm.TypeInfo(description="Customer comments or feedback (optional)")
        ] = "",
        helpful: Annotated[
            bool, llm.TypeInfo(description="Whether the conversation was helpful (optional)")
        ] = True,
        issues: Annotated[
            List[str], llm.TypeInfo(description="List of issues encountered (optional)")
        ] = None,
    ) -> Dict[str, Any]:
        """
        Save customer feedback about the conversation
        """
        logger.info(f"Saving conversation feedback for conversation {conversation_id}: rating {satisfaction_rating}")
        
        if issues is None:
            issues = []
            
        # Prepare feedback data
        feedback_data = {
            "conversation_id": conversation_id,
            "satisfaction_rating": satisfaction_rating,
            "helpful": helpful,
            "submitted_at": datetime.datetime.now().isoformat()
        }
        
        if comments:
            feedback_data["comments"] = comments
        if issues:
            feedback_data["issues"] = issues
            
        # If connected to database, save the feedback
        if self.db_connected:
            try:
                result = self.supabase.table("conversation_feedback").insert(feedback_data).execute()
                if result.data:
                    feedback_id = result.data[0].get("id")
                    return {
                        "status": "success",
                        "message": "Feedback saved successfully",
                        "feedback_id": feedback_id
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Failed to save feedback"
                    }
            except Exception as e:
                logger.error(f"Error saving feedback: {e}")
                return {
                    "status": "error",
                    "message": f"Database error: {str(e)}"
                }
        else:
            # Simulate successful database operation
            await asyncio.sleep(0.5)  # Simulate processing time
            return {
                "status": "success",
                "message": "Feedback saved successfully (simulated)",
                "feedback_id": "fb_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            }

    @llm.ai_callable()
    async def get_warranty_plans(
        self,
        coverage_type: Annotated[
            str, llm.TypeInfo(description="Type of coverage (e.g., standard, premium, high_mileage)")
        ] = "",
        max_vehicle_age: Annotated[
            int, llm.TypeInfo(description="Maximum vehicle age in years")
        ] = 0,
        max_mileage: Annotated[
            int, llm.TypeInfo(description="Maximum vehicle mileage")
        ] = 0,
    ) -> Dict[str, Any]:
        """
        Get available warranty plans matching the specified criteria
        """
        logger.info(f"Getting warranty plans: type={coverage_type}, age={max_vehicle_age}, mileage={max_mileage}")
        
        matching_plans = []
        
        for plan in self.warranty_plans:
            # Check if plan matches the criteria
            matches = True
            
            if coverage_type and coverage_type.lower() not in plan.get("name", "").lower():
                matches = False
                
            if max_vehicle_age > 0 and plan.get("max_vehicle_age", 0) < max_vehicle_age:
                matches = False
                
            if max_mileage > 0 and plan.get("max_vehicle_mileage", 0) < max_mileage:
                matches = False
                
            if matches:
                matching_plans.append({
                    "name": plan.get("name"),
                    "description": plan.get("description"),
                    "monthly_premium_range": plan.get("monthly_premium_range"),
                    "coverage_details": plan.get("coverage_details"),
                    "term_length_options": plan.get("term_length_options", [12, 24, 36]),
                    "max_vehicle_age": plan.get("max_vehicle_age"),
                    "max_vehicle_mileage": plan.get("max_vehicle_mileage"),
                    "deductible": plan.get("deductible")
                })
        
        # If no specific criteria provided, return all plans
        if not coverage_type and max_vehicle_age == 0 and max_mileage == 0:
            matching_plans = [
                {
                    "name": plan.get("name"),
                    "description": plan.get("description"),
                    "monthly_premium_range": plan.get("monthly_premium_range"),
                    "coverage_details": plan.get("coverage_details"),
                    "term_length_options": plan.get("term_length_options", [12, 24, 36]),
                    "max_vehicle_age": plan.get("max_vehicle_age"),
                    "max_vehicle_mileage": plan.get("max_vehicle_mileage"),
                    "deductible": plan.get("deductible")
                }
                for plan in self.warranty_plans
            ]
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "status": "success",
            "total_plans": len(matching_plans),
            "plans": matching_plans,
            "criteria": {
                "coverage_type": coverage_type if coverage_type else "any",
                "max_vehicle_age": max_vehicle_age if max_vehicle_age > 0 else "any",
                "max_mileage": max_mileage if max_mileage > 0 else "any"
            }
        }
    
    @llm.ai_callable()
    async def get_business_info(
        self,
        info_type: Annotated[
            str, llm.TypeInfo(description="Type of business information requested (e.g., services, contact, plans)")
        ]
    ) -> Dict[str, Any]:
        """
        Get insurance business information based on the requested type
        """
        logger.info(f"Getting business info: {info_type}")
        
        info_type = info_type.lower()
        
        # Example business information for CCS Insurance
        business_info = {
            "services": self.domain_config.get("services", [
                "warranty renewal qualification",
                "warranty plan options",
                "claim processing",
                "warranty transfers"
            ]),
            "contact": {
                "phone": "(800) 555-CARS",
                "email": "info@ccsinsurance.com",
                "website": "www.ccsinsurance.com",
                "hours": {
                    "monday": "8:00 AM - 8:00 PM",
                    "tuesday": "8:00 AM - 8:00 PM",
                    "wednesday": "8:00 AM - 8:00 PM",
                    "thursday": "8:00 AM - 8:00 PM",
                    "friday": "8:00 AM - 8:00 PM",
                    "saturday": "9:00 AM - 5:00 PM",
                    "sunday": "Closed"
                }
            },
            "plans": [
                {
                    "name": plan.get("name"),
                    "description": plan.get("description")
                }
                for plan in self.warranty_plans
            ],
            "coverage": {
                "standard_coverage": "Engine, transmission, drivetrain, electrical systems, and air conditioning",
                "premium_coverage": "Full coverage including engine, transmission, drivetrain, electrical, AC, steering, braking systems, and electronics",
                "high_mileage_coverage": "Engine, transmission, and major component coverage for high-mileage vehicles"
            },
            "eligibility": {
                "standard_eligibility": "Vehicles under 10 years old with less than 100,000 miles",
                "high_mileage_eligibility": "Vehicles under 15 years old with up to 150,000 miles"
            }
        }
        
        if info_type in business_info:
            result = business_info[info_type]
        else:
            result = {
                "message": f"Information about '{info_type}' is not available.",
                "available_info_types": list(business_info.keys())
            }
        
        await asyncio.sleep(0.5)  # Simulate processing time
        return result
