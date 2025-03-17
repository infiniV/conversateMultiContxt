"""
Technology-specific functions for Conversate business.
This module contains AI-callable functions specific to voice assistant technology providers.
"""
import asyncio
import logging
from typing import Annotated, Dict, Any, List
from llama_index.core import Settings
from livekit.agents import llm
from . import BaseBusinessFnc
from llama_index.llms.groq import Groq
Settings.llm = Groq(model="llama-3.1-8b-instant")
logger = logging.getLogger("conversate-assistant")


class ConversateAssistantFnc(BaseBusinessFnc):
    """
    Technology specialist functions for Conversate's AI assistant platform
    """

    @llm.ai_callable()
    async def get_subscription_details(
        self,
        tier: Annotated[
            str, llm.TypeInfo(description="The subscription tier to get information about (e.g., starter, professional, enterprise, custom)")
        ]
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific subscription tier
        """
        logger.info(f"Getting subscription details for tier: {tier}")
        
        tier = tier.lower()
        
        # Subscription tier details
        subscription_info = {
            "starter": {
                "name": "Starter Plan",
                "price": "$299/month",
                "description": "Perfect for small businesses looking to introduce voice AI",
                "features": [
                    "Single voice assistant deployment",
                    "Basic configuration options",
                    "Standard business templates",
                    "Email support (response within 24 hours)",
                    "Up to 1,000 minutes of voice interaction per month",
                    "Basic analytics dashboard"
                ],
                "limitations": [
                    "Limited customization options",
                    "No custom function development",
                    "Standard voice options only"
                ],
                "ideal_for": "Small businesses, startups, single-location retail"
            },
            "professional": {
                "name": "Professional Plan",
                "price": "$999/month",
                "description": "Comprehensive solution for growing businesses with multiple locations or departments",
                "features": [
                    "Up to 5 voice assistants",
                    "Advanced configuration options",
                    "Industry-specific templates and knowledge bases",
                    "Priority support (response within 4 hours)",
                    "Up to 5,000 minutes of voice interaction per month",
                    "Advanced analytics and reporting",
                    "Custom welcome messages and voice personalities",
                    "Basic CRM integration"
                ],
                "limitations": [
                    "Limited function customization",
                    "Standard deployment options only"
                ],
                "ideal_for": "Medium businesses, multi-location retail, professional services firms"
            },
            "enterprise": {
                "name": "Enterprise Plan",
                "price": "Starting at $2,999/month",
                "description": "Full-featured solution for large organizations with complex needs",
                "features": [
                    "Unlimited voice assistants",
                    "Full customization capabilities",
                    "Custom domain expertise development",
                    "Dedicated account manager",
                    "Advanced analytics and reporting",
                    "Service Level Agreement guarantees",
                    "24/7 priority support",
                    "Up to 20,000 minutes of voice interaction per month",
                    "Enterprise CRM and ERP integrations",
                    "Custom voice selection"
                ],
                "limitations": [
                    "Custom development may require additional time",
                    "Complex integrations may incur additional costs"
                ],
                "ideal_for": "Large enterprises, healthcare networks, financial institutions, hospitality chains"
            },
            "custom": {
                "name": "Custom Solutions",
                "price": "Custom pricing based on requirements",
                "description": "Tailored solutions for organizations with unique requirements",
                "features": [
                    "Custom function development",
                    "Specialized AI models",
                    "Integration with proprietary systems",
                    "White-label solutions",
                    "On-premises deployment options",
                    "Custom security protocols",
                    "Dedicated development team",
                    "Custom training and onboarding",
                    "Unlimited voice interaction minutes"
                ],
                "process": [
                    "Initial consultation and requirements gathering",
                    "Solution design and proposal",
                    "Development and customization",
                    "Testing and validation",
                    "Deployment and integration",
                    "Ongoing support and optimization"
                ],
                "ideal_for": "Organizations with specific compliance requirements, unique business processes, or specialized industry needs"
            }
        }
        
        # Match the requested tier with available options
        if tier in ["starter", "start", "basic"]:
            result = subscription_info["starter"]
        elif tier in ["professional", "pro", "standard"]:
            result = subscription_info["professional"]
        elif tier in ["enterprise", "business", "advanced"]:
            result = subscription_info["enterprise"]
        elif tier in ["custom", "custom solutions", "tailored"]:
            result = subscription_info["custom"]
        else:
            # If tier not recognized, return general information
            result = {
                "message": f"Subscription tier '{tier}' not recognized. Available tiers are: Starter, Professional, Enterprise, and Custom Solutions.",
                "available_tiers": list(subscription_info.keys())
            }
        
        await asyncio.sleep(0.5)  # Simulate processing time
        return result

    @llm.ai_callable()
    async def get_integration_options(
        self,
        integration_type: Annotated[
            str, llm.TypeInfo(description="The type of integration (e.g., web, phone, mobile, api, crm)")
        ] = ""
    ) -> Dict[str, Any]:
        """
        Get information about integration options for voice assistants
        """
        logger.info(f"Getting integration information for: {integration_type}")
        
        # Integration options
        integrations = {
            "web": {
                "description": "Integrate voice assistants into websites and web applications",
                "options": [
                    "Embedded chat widget",
                    "Full-page voice assistant",
                    "Pop-up assistant"
                ],
                "requirements": [
                    "JavaScript integration",
                    "HTTPS website",
                    "WebRTC support"
                ],
                "setup_time": "1-3 days",
                "documentation": "https://docs.conversate.ai/web-integration"
            },
            "phone": {
                "description": "Connect voice assistants to phone systems",
                "options": [
                    "Direct SIP integration",
                    "PSTN connection",
                    "IVR replacement",
                    "Call center augmentation"
                ],
                "requirements": [
                    "SIP trunk or compatible phone system",
                    "Phone number allocation",
                    "Call routing configuration"
                ],
                "setup_time": "3-7 days",
                "documentation": "https://docs.conversate.ai/phone-integration"
            },
            "mobile": {
                "description": "Implement voice assistants in mobile applications",
                "options": [
                    "SDK for iOS",
                    "SDK for Android",
                    "React Native component",
                    "Flutter plugin"
                ],
                "requirements": [
                    "Mobile app development capabilities",
                    "Microphone permissions",
                    "Background audio handling"
                ],
                "setup_time": "5-10 days",
                "documentation": "https://docs.conversate.ai/mobile-integration"
            },
            "api": {
                "description": "Direct API integration for custom implementations",
                "options": [
                    "REST API",
                    "WebSocket API",
                    "Streaming API"
                ],
                "requirements": [
                    "API key management",
                    "Development resources",
                    "Audio handling capabilities"
                ],
                "features": [
                    "Real-time transcription",
                    "Audio streaming",
                    "Function calling",
                    "Session management"
                ],
                "setup_time": "Varies based on implementation",
                "documentation": "https://docs.conversate.ai/api-reference"
            },
            "crm": {
                "description": "Integration with popular CRM systems",
                "supported_systems": [
                    "Salesforce",
                    "HubSpot",
                    "Microsoft Dynamics",
                    "Zoho CRM",
                    "Custom CRM (via API)"
                ],
                "features": [
                    "Customer record lookup",
                    "Interaction history",
                    "Lead creation",
                    "Case management",
                    "Activity logging"
                ],
                "requirements": [
                    "CRM API credentials",
                    "Data mapping configuration",
                    "User permission setup"
                ],
                "setup_time": "7-14 days",
                "documentation": "https://docs.conversate.ai/crm-integration"
            }
        }
        
        if not integration_type:
            # If no specific type requested, return overview of all types
            return {
                "available_integration_types": list(integrations.keys()),
                "message": "Please specify an integration type for detailed information.",
                "general_info": "Conversate supports various integration methods including web, phone systems, mobile apps, direct API access, and CRM systems."
            }
        
        integration_type = integration_type.lower()
        
        # Try to match the requested integration type
        for key, value in integrations.items():
            if integration_type in key or key in integration_type:
                result = value
                result["type"] = key  # Add the type for clarity
                await asyncio.sleep(0.5)  # Simulate processing time
                return result
        
        # If no match found
        return {
            "message": f"Integration type '{integration_type}' not recognized.",
            "available_types": list(integrations.keys()),
            "suggestion": "For customized integration solutions, consider our Professional or Enterprise plans."
        }

    @llm.ai_callable()
    async def estimate_implementation_time(
        self,
        business_type: Annotated[
            str, llm.TypeInfo(description="The type of business (e.g., restaurant, retail, healthcare)")
        ],
        integration_complexity: Annotated[
            str, llm.TypeInfo(description="The complexity of integration (simple, moderate, complex)")
        ],
        custom_functions: Annotated[
            bool, llm.TypeInfo(description="Whether custom functions are required")
        ] = False
    ) -> Dict[str, Any]:
        """
        Estimate implementation time and resources for a voice assistant deployment
        """
        logger.info(f"Estimating implementation time for {business_type} business with {integration_complexity} integration complexity")
        
        # Base implementation times (in days)
        base_times = {
            "simple": 5,
            "moderate": 10,
            "complex": 20
        }
        
        # Business type complexity factors
        business_factors = {
            "restaurant": 1.0,
            "retail": 1.0,
            "healthcare": 1.5,
            "finance": 1.5,
            "education": 1.2,
            "real estate": 1.1,
            "technology": 1.2,
            "manufacturing": 1.3,
            "hospitality": 1.1,
            "legal": 1.4
        }
        
        # Default factor for unlisted business types
        default_factor = 1.2
        
        # Adjust for business complexity
        business_type = business_type.lower()
        business_factor = business_factors.get(business_type, default_factor)
        
        # Adjust for integration complexity
        integration_complexity = integration_complexity.lower()
        if integration_complexity not in base_times:
            return {
                "message": f"Integration complexity '{integration_complexity}' not recognized. Please use 'simple', 'moderate', or 'complex'.",
                "available_complexity_levels": list(base_times.keys())
            }
        
        base_time = base_times[integration_complexity]
        
        # Calculate implementation time
        implementation_time = base_time * business_factor
        
        # Adjust for custom functions
        if custom_functions:
            implementation_time += 7  # Add days for custom function development
        
        # Round to the nearest integer
        implementation_time = round(implementation_time)
        
        # Prepare response
        result = {
            "estimated_days": implementation_time,
            "estimated_range": f"{implementation_time - 2} to {implementation_time + 3} business days",
            "business_type": business_type,
            "integration_complexity": integration_complexity,
            "custom_functions_required": custom_functions
        }
        
        # Add phase breakdown
        result["implementation_phases"] = {
            "consultation_and_requirements": f"{max(1, round(implementation_time * 0.2))} days",
            "configuration_and_customization": f"{max(2, round(implementation_time * 0.4))} days",
            "integration_and_testing": f"{max(2, round(implementation_time * 0.3))} days",
            "deployment_and_training": f"{max(1, round(implementation_time * 0.1))} days"
        }
        
        # Add recommendation
        if implementation_time <= 7:
            result["recommended_plan"] = "Starter or Professional Plan"
        elif implementation_time <= 14:
            result["recommended_plan"] = "Professional Plan"
        else:
            result["recommended_plan"] = "Enterprise Plan or Custom Solution"
        
        await asyncio.sleep(0.5)  # Simulate processing time
        return result
        
    @llm.ai_callable()
    async def check_domain_compatibility(
        self,
        business_domain: Annotated[
            str, llm.TypeInfo(description="The business domain to check for compatibility (e.g., healthcare, retail)")
        ],
        special_requirements: Annotated[
            str, llm.TypeInfo(description="Any special requirements or constraints")
        ] = ""
    ) -> Dict[str, Any]:
        """
        Check if a specific business domain is compatible with the platform and identify any special considerations
        """
        logger.info(f"Checking domain compatibility for {business_domain} with requirements: {special_requirements}")
        
        business_domain = business_domain.lower()
        
        # Domain compatibility information
        domains = {
            "restaurant": {
                "compatibility": "High",
                "prebuilt_templates": True,
                "special_considerations": [
                    "Menu integration",
                    "Reservation systems",
                    "Peak hour handling"
                ],
                "recommended_plan": "Professional",
                "case_study": "https://conversate.ai/cases/restaurant-chain"
            },
            "agriculture": {
                "compatibility": "High",
                "prebuilt_templates": True,
                "special_considerations": [
                    "Seasonal advice customization",
                    "Weather data integration",
                    "Technical terminology handling"
                ],
                "recommended_plan": "Professional",
                "case_study": "https://conversate.ai/cases/farm-advisory"
            },
            "healthcare": {
                "compatibility": "Medium",
                "prebuilt_templates": True,
                "special_considerations": [
                    "HIPAA compliance required",
                    "Medical terminology accuracy",
                    "Emergency situation handling",
                    "Patient data security"
                ],
                "recommended_plan": "Enterprise or Custom",
                "compliance_features": [
                    "Encrypted data storage",
                    "Audit logging",
                    "Role-based access control"
                ],
                "case_study": "https://conversate.ai/cases/healthcare-provider"
            },
            "finance": {
                "compatibility": "Medium",
                "prebuilt_templates": True,
                "special_considerations": [
                    "Financial regulations compliance",
                    "Transaction security",
                    "Customer verification",
                    "Data encryption requirements"
                ],
                "recommended_plan": "Enterprise",
                "compliance_features": [
                    "PCI DSS compliance",
                    "Multi-factor authentication",
                    "Secure data handling"
                ],
                "case_study": "https://conversate.ai/cases/community-bank"
            },
            "retail": {
                "compatibility": "High",
                "prebuilt_templates": True,
                "special_considerations": [
                    "Product catalog integration",
                    "Inventory checking",
                    "Order status queries"
                ],
                "recommended_plan": "Professional",
                "case_study": "https://conversate.ai/cases/retail-chain"
            },
            "education": {
                "compatibility": "High",
                "prebuilt_templates": True,
                "special_considerations": [
                    "Student information privacy",
                    "Course information integration",
                    "Schedule management"
                ],
                "recommended_plan": "Professional",
                "case_study": "https://conversate.ai/cases/university-assistance"
            },
            "real estate": {
                "compatibility": "High",
                "prebuilt_templates": True,
                "special_considerations": [
                    "Property listing integration",
                    "Appointment scheduling",
                    "Location-based information"
                ],
                "recommended_plan": "Professional",
                "case_study": "https://conversate.ai/cases/realty-group"
            },
            "legal": {
                "compatibility": "Medium",
                "prebuilt_templates": False,
                "special_considerations": [
                    "Client confidentiality",
                    "Legal terminology accuracy",
                    "Jurisdiction-specific information",
                    "Disclaimer requirements"
                ],
                "recommended_plan": "Enterprise or Custom",
                "case_study": "https://conversate.ai/cases/legal-firm"
            }
        }
        
        # Check for the requested domain
        if business_domain not in domains:
            similar_domains = [d for d in domains.keys() if any(x in d or d in x for x in business_domain.split())]
            
            return {
                "message": f"No specific information available for '{business_domain}' domain.",
                "customizable": True,
                "general_compatibility": "Our platform can be customized for virtually any business domain.",
                "recommended_approach": "Schedule a consultation to discuss your specific requirements.",
                "similar_domains": similar_domains if similar_domains else list(domains.keys())[:3]
            }
        
        # Get domain information
        result = domains[business_domain].copy()
        
        # Process special requirements if provided
        if special_requirements:
            requirements_lower = special_requirements.lower()
            
            # Check for compliance-related keywords
            if any(word in requirements_lower for word in ["hipaa", "compliance", "secure", "privacy", "regulation"]):
                result["compliance_note"] = "Your compliance requirements may necessitate our Enterprise plan with additional security features."
            
            # Check for integration-related keywords
            if any(word in requirements_lower for word in ["integration", "connect", "api", "system"]):
                result["integration_note"] = "Your integration requirements may require custom development work."
            
            # Check for customization-related keywords
            if any(word in requirements_lower for word in ["custom", "specific", "unique", "tailor"]):
                result["customization_note"] = "Your customization needs suggest our Custom Solutions approach would be appropriate."
                
            result["provided_requirements"] = special_requirements
        
        await asyncio.sleep(0.7)  # Simulate processing time
        return result

    @llm.ai_callable()
    async def get_business_info(
        self,
        info_type: Annotated[
            str, llm.TypeInfo(description="Type of business information requested (e.g., hours, location, services, contact)")
        ]
    ) -> Dict[str, Any]:
        """
        Get information about Conversate based on the requested type
        """
        logger.info(f"Getting business info: {info_type}")
        
        info_type = info_type.lower()
        result = {}
        
        # Business information
        business_info = {
            "hours": {
                "monday": "8:00 AM - 8:00 PM EST",
                "tuesday": "8:00 AM - 8:00 PM EST",
                "wednesday": "8:00 AM - 8:00 PM EST",
                "thursday": "8:00 AM - 8:00 PM EST",
                "friday": "8:00 AM - 8:00 PM EST",
                "saturday": "9:00 AM - 5:00 PM EST",
                "sunday": "Closed",
                "note": "Technical support is available 24/7 for Enterprise customers"
            },
            "contact": {
                "sales": "sales@conversate.ai",
                "support": "support@conversate.ai",
                "phone": "+1 (800) TALK-BOT",
                "website": "www.conversate.ai",
                "headquarters": "101 Innovation Drive, Boston, MA 02210"
            },
            "services": [
                {
                    "name": "Voice Assistant Platform",
                    "description": "Customizable AI voice assistants for business applications"
                },
                {
                    "name": "Business Integration",
                    "description": "Solutions to integrate voice AI with existing business systems"
                },
                {
                    "name": "Custom Development",
                    "description": "Specialized function development for unique business needs"
                },
                {
                    "name": "Implementation Services",
                    "description": "End-to-end deployment and configuration services"
                },
                {
                    "name": "Training and Support",
                    "description": "Comprehensive training and ongoing technical support"
                }
            ],
            "company": {
                "founded": 2021,
                "mission": "To revolutionize business communications through accessible and intelligent voice AI technology",
                "employees": "50-100",
                "investors": ["Tech Ventures Capital", "AI Innovation Fund", "Growth Partners LLC"],
                "leadership": [
                    {
                        "name": "Alex Thompson",
                        "position": "CEO and Co-founder",
                        "background": "Former VP of Product at VoiceTech Inc."
                    },
                    {
                        "name": "Dr. Mei Zhang",
                        "position": "CTO and Co-founder",
                        "background": "PhD in Computational Linguistics, former Research Scientist at OpenAI"
                    }
                ]
            },
            "locations": [
                {
                    "type": "Headquarters",
                    "address": "101 Innovation Drive, Boston, MA 02210",
                    "phone": "+1 (800) TALK-BOT"
                },
                {
                    "type": "Development Center",
                    "address": "3300 Technology Way, Mountain View, CA 94043",
                    "phone": "+1 (800) TALK-BOT ext. 2"
                }
            ],
            "technologies": [
                "Speech-to-Text (STT) processing",
                "Natural Language Understanding (NLU)",
                "Large Language Models (LLMs)",
                "Text-to-Speech (TTS) synthesis",
                "Voice Activity Detection (VAD)",
                "Custom function development",
                "API integration frameworks",
                "Analytics and reporting systems"
            ]
        }
        
        if info_type in business_info:
            result = business_info[info_type]
        else:
            result["message"] = f"Information about '{info_type}' is not available."
            result["available_info_types"] = list(business_info.keys())
        
        await asyncio.sleep(0.5)  # Simulate processing time
        return result