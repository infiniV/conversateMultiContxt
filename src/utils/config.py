"""
Configuration module for business-specific assistants.
Allows customization of the assistant for different businesses and use cases.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("config-manager")

def load_config_from_file(business_type: str = None, config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from a JSON file based on business type or direct path
    
    Args:
        business_type: Type of business to load config for (e.g., 'agriculture', 'restaurant')
        config_path: Optional direct path to a config file (overrides business_type if provided)
    
    Returns:
        Dict containing the configuration
    """
    config_type = os.environ.get("CONFIG_TYPE")
    config_file_path = os.environ.get("CONFIG_FILE_PATH")
    
    if config_type and config_file_path:
        logger.info(f"Loading {config_type} configuration from {config_file_path}")
        try:
            full_path = Path(__file__).parent.parent.parent / config_file_path
            if full_path.exists():
                with open(full_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading specified config: {e}")
    
    # Fallback to business type loading
    business_type = business_type or os.environ.get("BUSINESS_TYPE")
    if not business_type:
        raise ValueError("Neither CONFIG_TYPE nor BUSINESS_TYPE environment variables are set")

    # Use direct config path if provided (from web app deployment)
    if config_path and os.path.exists(config_path):
        try:
            logger.info(f"Loading configuration from specified path: {config_path}")
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config from path {config_path}: {e}")
    
    # Otherwise use business_type to find config
    if not business_type:
        business_type = os.environ.get("BUSINESS_TYPE")
        if not business_type:
            raise ValueError("BUSINESS_TYPE environment variable is not set")
        logger.info(f"Using business type from environment: {business_type}")
    
    # Config file path
    config_dir = Path(__file__).parent.parent.parent / "config"
    config_file = config_dir / f"{business_type}_config.json"
    
    # Check for business-specific config in businesses subdirectory
    business_id = os.environ.get("BUSINESS_ID")
    if business_id:
        business_config = config_dir / "businesses" / f"{business_id}_{business_type}_config.json"
        if business_config.exists():
            config_file = business_config
            logger.info(f"Using business-specific config: {config_file}")
    
    # If config file doesn't exist, fallback to default
    if not config_file.exists():
        default_file = config_dir / "agriculture_config.json"
        logger.info(f"Config file {config_file} not found, falling back to {default_file}")
        config_file = default_file
    
    # Ensure config directory exists
    config_dir.mkdir(exist_ok=True)
    
    # If the config file doesn't exist, create default configs
    if not config_file.exists():
        logger.info("Creating default configuration files")
        
        # Create directory for configs if it doesn't exist
        config_dir.mkdir(exist_ok=True)
        
        # Create agriculture config (default)
        create_default_configs(config_dir)
        
        # If a specific non-agriculture config was requested but doesn't exist
        if business_type != "agriculture" and not config_file.exists():
            # Create the requested config
            logger.info(f"Creating new business config for {business_type}")
            create_business_config(business_type, config_dir)
    
    # Load the config file
    try:
        logger.info(f"Loading configuration from: {config_file}")
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        # If loading fails, return hardcoded default
        logger.info("Falling back to hardcoded default configuration")
        return get_default_config("agriculture")

def create_config_from_web_inputs(business_data: Dict[str, Any], output_path: str) -> str:
    """
    Create a configuration file from web application signup data
    
    Args:
        business_data: Dictionary containing business information from web signup
        output_path: Path to save the generated config file
        
    Returns:
        Path to the created config file
    """
    # Extract basic business information
    business_type = business_data.get("business_type", "generic")
    business_name = business_data.get("business_name", f"New {business_type.capitalize()} Business")
    
    logger.info(f"Creating config from web inputs for {business_name} ({business_type})")
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Start with a template based on the business type
    if business_type in ["agriculture", "restaurant", "technology"]:
        config = get_default_config(business_type)
    else:
        config = get_default_config("generic")
    
    # Update with provided business data
    config["business_config"]["business_name"] = business_name
    config["business_config"]["business_tagline"] = business_data.get("tagline", config["business_config"]["business_tagline"])
    config["business_config"]["business_description"] = business_data.get("description", config["business_config"]["business_description"])
    config["business_config"]["domain"] = business_type
    config["business_config"]["region"] = business_data.get("region", "Local")
    config["business_config"]["language"] = business_data.get("language", "en")
    
    # Add subscription info if provided
    if "subscription_plan" in business_data:
        config["business_config"]["subscription_plan"] = business_data["subscription_plan"]
    
    # Update services if provided
    if "services" in business_data:
        config["domain_config"]["services"] = business_data["services"]
    
    # Update domain-specific fields
    if business_type == "agriculture":
        if "crops" in business_data:
            config["domain_config"]["key_crops"] = business_data["crops"]
        if "growing_seasons" in business_data:
            config["domain_config"]["growing_seasons"] = business_data["growing_seasons"]
        if "irrigation_methods" in business_data:
            config["domain_config"]["irrigation_methods"] = business_data["irrigation_methods"]
    
    elif business_type == "restaurant":
        if "menu_categories" in business_data:
            config["domain_config"]["menu_categories"] = business_data["menu_categories"]
        if "popular_items" in business_data:
            config["domain_config"]["popular_items"] = business_data["popular_items"]
        if "special_dietary_options" in business_data:
            config["domain_config"]["special_dietary_options"] = business_data["special_dietary_options"]
    
    # Save the config to the specified path
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Created configuration file at: {output_path}")
    return output_path

def create_default_configs(config_dir: Path) -> None:
    """Create default configuration files if they don't exist"""
    # Create agriculture config
    agriculture_file = config_dir / "agriculture_config.json"
    if not agriculture_file.exists():
        with open(agriculture_file, 'w') as f:
            json.dump(get_default_config("agriculture"), f, indent=4)
    
    # Create restaurant config
    restaurant_file = config_dir / "restaurant_config.json"
    if not restaurant_file.exists():
        with open(restaurant_file, 'w') as f:
            json.dump(get_default_config("restaurant"), f, indent=4)

def create_business_config(business_type: str, config_dir: Path) -> None:
    """Create a new business configuration file"""
    config_file = config_dir / f"{business_type}_config.json"
    
    # Create a basic template config for the new business type
    config = {
        "business_config": {
            "business_name": f"New {business_type.capitalize()} Business",
            "business_tagline": f"A new {business_type} business",
            "business_description": f"A business in the {business_type} industry",
            "specialist_name": f"{business_type.capitalize()} Assistant",
            "domain": business_type,
            "region": "Local",
            "language": "en",
            "assistant_personality": "professional, friendly, helpful"
        },
        "voice_config": {
            "welcome_message": (
                "Welcome to {business_name}! I'm your {domain} specialist assistant. "
                "I can help you with {services}. "
                "How can I assist with your {domain} needs today?"
            ),
            "stt_model": "whisper-large-v3-turbo",
            "llm_model": "llama-3.3-70b",
            "llm_temperature": 0.7,
            "tts_voice": "nova"
        },
        "domain_config": {
            "services": [
                f"{business_type} service 1",
                f"{business_type} service 2",
                f"{business_type} service 3"
            ]
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

def get_default_config(business_type: str) -> Dict[str, Any]:
    """Get default configuration based on business type"""
    if business_type == "agriculture":
        return {
            "business_config": {
                "business_name": "Farmovation",
                "business_tagline": "Empowering Pakistani farmers with modern agricultural knowledge",
                "business_description": "A company helping Pakistani farmers improve yields through data-driven agriculture",
                "specialist_name": "Farmovation Assistant",
                "domain": "agriculture",
                "region": "Pakistan",
                "language": "en",
                "assistant_personality": "professional, friendly, helpful, knowledgeable"
            },
            "voice_config": {
                "welcome_message": (
                    "Welcome to {business_name}! I'm your {domain} specialist assistant. "
                    "I can help you with {services}. "
                    "How can I assist with your {domain} needs today?"
                ),
                "stt_model": "whisper-large-v3-turbo",
                "llm_model": "llama-3.3-70b",
                "llm_temperature": 0.7,
                "tts_voice": "nova"
            },
            "domain_config": {
                "services": [
                    "crop recommendations",
                    "pest management",
                    "water conservation",
                    "farming best practices"
                ],
                "growing_seasons": ["Rabi (winter)", "Kharif (summer)"],
                "soil_types": ["sandy loam", "clay", "silty"],
                "key_crops": ["wheat", "rice", "cotton", "sugarcane", "maize"],
                "irrigation_methods": ["flood", "drip", "sprinkler", "furrow"],
                "knowledge_sources": ["Pakistani agricultural research institutes", "international best practices"]
            }
        }
    elif business_type == "restaurant":
        return {
            "business_config": {
                "business_name": "Shawarma Delight",
                "business_tagline": "Authentic Mediterranean flavors in every bite",
                "business_description": "A local restaurant specializing in fresh, authentic shawarma and Mediterranean cuisine",
                "specialist_name": "Shawarma Delight Assistant",
                "domain": "restaurant",
                "region": "Local",
                "language": "en",
                "assistant_personality": "friendly, helpful, enthusiastic, knowledgeable"
            },
            "voice_config": {
                "welcome_message": (
                    "Welcome to {business_name}! I'm your virtual assistant. "
                    "I can help you with {services}. "
                    "How can I assist you today?"
                ),
                "stt_model": "whisper-large-v3-turbo",
                "llm_model": "llama-3.3-70b",
                "llm_temperature": 0.7,
                "tts_voice": "nova"
            },
            "domain_config": {
                "services": [
                    "menu information",
                    "placing orders",
                    "special dietary requirements",
                    "restaurant hours and location"
                ],
                "menu_categories": ["shawarma", "kebab", "sides", "desserts", "drinks"],
                "popular_items": ["chicken shawarma", "beef shawarma", "mixed grill", "falafel wrap"],
                "special_dietary_options": ["vegetarian", "halal", "gluten-free"],
                "business_hours": {
                    "monday": "11:00 AM - 10:00 PM",
                    "tuesday": "11:00 AM - 10:00 PM",
                    "wednesday": "11:00 AM - 10:00 PM",
                    "thursday": "11:00 AM - 10:00 PM",
                    "friday": "11:00 AM - 11:00 PM",
                    "saturday": "11:00 AM - 11:00 PM",
                    "sunday": "12:00 PM - 9:00 PM"
                }
            }
        }
    elif business_type == "technology":
        return {
            "business_config": {
                "business_name": "Conversate",
                "business_tagline": "AI voice assistants tailored to your business needs",
                "business_description": "A platform that enables businesses to deploy customized voice assistants for customer support, lead generation, and operational workflows",
                "specialist_name": "Conversate Assistant",
                "domain": "technology",
                "region": "Global",
                "language": "en",
                "assistant_personality": "professional, knowledgeable, helpful, adaptable"
            },
            "voice_config": {
                "welcome_message": (
                    "Welcome to {business_name}! I'm your {domain} specialist assistant. "
                    "I can help you with {services}. "
                    "How can I assist you today?"
                ),
                "stt_model": "whisper-large-v3-turbo",
                "llm_model": "llama-3.3-70b",
                "llm_temperature": 0.6,
                "tts_voice": "nova"
            },
            "domain_config": {
                "services": [
                    "voice agent customization",
                    "business integration solutions",
                    "agent deployment workflows",
                    "subscription plan information",
                    "technical support"
                ],
                "product_tiers": [
                    "Starter",
                    "Professional",
                    "Enterprise",
                    "Custom Solutions"
                ],
                "integration_options": [
                    "Web interface",
                    "Phone system",
                    "Mobile app",
                    "Custom API"
                ]
            }
        }
    else:
        # Generic config for any other business type
        return {
            "business_config": {
                "business_name": f"{business_type.capitalize()} Business",
                "business_tagline": f"Your local {business_type} business",
                "business_description": f"A business specializing in {business_type} services",
                "specialist_name": f"{business_type.capitalize()} Assistant",
                "domain": business_type,
                "region": "Local",
                "language": "en",
                "assistant_personality": "professional, friendly, helpful"
            },
            "voice_config": {
                "welcome_message": (
                    "Welcome to {business_name}! I'm your {domain} specialist assistant. "
                    "I can help you with {services}. "
                    "How can I assist with your {domain} needs today?"
                ),
                "stt_model": "whisper-large-v3-turbo",
                "llm_model": "llama-3.3-70b",
                "llm_temperature": 0.7,
                "tts_voice": "nova"
            },
            "domain_config": {
                "services": [
                    f"{business_type} service 1",
                    f"{business_type} service 2",
                    f"{business_type} service 3"
                ]
            }
        }

def get_function_module(business_type: str = None) -> Optional[str]:
    """Get the appropriate function module based on configuration"""
    config_type = os.environ.get("CONFIG_TYPE", business_type)
    if not config_type:
        return None
        
    function_file = f"{config_type.lower()}_functions.py"
    function_path = Path(__file__).parent.parent / "functions" / function_file
    
    if function_path.exists():
        return f"src.functions.{config_type.lower()}_functions"
    return None

# Try loading from environment variables first
config_path = os.environ.get("CONFIG_FILE_PATH")
business_type = os.environ.get("BUSINESS_TYPE")

# Ensure BUSINESS_TYPE is set
if not business_type:
    raise ValueError("BUSINESS_TYPE environment variable is not set")

# Load the configuration
try:
    _config = load_config_from_file(business_type=business_type, config_path=config_path)
except Exception as e:
    logger.error(f"Failed to load configuration for {business_type}: {e}")
    raise

# System prompt template for the assistant
SYSTEM_PROMPT_TEMPLATE = """
You are a {specialist_name} providing expert {domain} assistance. Focus on {services_list} for {region}.
Use available functions to:
- Check warranty eligibility and coverage options
- Handle customer inquiries and information
- Process applications and save records
- Schedule callbacks and follow-ups
Maintain a {personality_traits} approach.
"""

def get_system_prompt() -> str:
    """Generate the system prompt from the configuration"""
    business_config = _config["business_config"]
    domain_config = _config["domain_config"]
    
    services_list = ", ".join(domain_config["services"])
    
    # Handle different domain types
    if business_config["domain"] == "agriculture":
        growing_seasons = domain_config.get("growing_seasons", ["Rabi", "Kharif"])
        domain_knowledge = f"both {' and '.join(growing_seasons)} growing seasons in {business_config['region']}"
    elif business_config["domain"] == "restaurant":
        popular_items = domain_config.get("popular_items", [])
        menu_categories = domain_config.get("menu_categories", [])
        domain_knowledge = f"our menu featuring {', '.join(popular_items[:3])} and {len(menu_categories)} different categories"
    elif business_config["domain"] == "technology":
        product_tiers = domain_config.get("product_tiers", ["Starter", "Professional", "Enterprise"])
        domain_knowledge = f"our {', '.join(product_tiers)} service tiers and integration options"
    else:
        domain_knowledge = f"various {business_config['domain']} topics"
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        domain=business_config["domain"],
        business_name=business_config["business_name"],
        business_description=business_config["business_description"],
        specialist_name=business_config["specialist_name"],
        services_list=services_list,
        region=business_config["region"],
        domain_specific_knowledge=domain_knowledge,
        personality_traits=business_config["assistant_personality"]
    )

def get_welcome_message() -> str:
    """Generate the welcome message from the configuration"""
    business_config = _config["business_config"]
    domain_config = _config["domain_config"]
    voice_config = _config["voice_config"]
    
    services = ", ".join(domain_config["services"][:3])  # Limit to first 3 services for brevity
    
    return voice_config["welcome_message"].format(
        business_name=business_config["business_name"],
        domain=business_config["domain"],
        services=services
    )

def get_voice_config() -> Dict[str, Any]:
    """Get the voice configuration settings"""
    return _config["voice_config"]

def get_business_config() -> Dict[str, Any]:
    """Get the business configuration settings"""
    return _config["business_config"]

def get_domain_config() -> Dict[str, Any]:
    """Get the domain-specific configuration settings"""
    return _config["domain_config"]

def set_business_type(business_type: str) -> None:
    """
    Change the current business type configuration
    This reloads the configuration from the appropriate file
    """
    global _config
    _config = load_config_from_file(business_type)
    
def reload_config(config_path: str = None) -> None:
    """
    Reload configuration from a specific path or environment
    Used when configuration file is updated externally
    """
    global _config
    path = config_path or os.environ.get("CONFIG_FILE_PATH")
    business_type = os.environ.get("BUSINESS_TYPE")
    _config = load_config_from_file(business_type=business_type, config_path=path)