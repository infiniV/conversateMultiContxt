"""
Farming specialist functions for the Farmovation assistant.
This module contains all AI-callable functions for agricultural advice.
"""
import asyncio
import logging
from typing import Annotated, Dict, Any

from livekit.agents import llm
from . import BaseBusinessFnc

logger = logging.getLogger("farmovation-assistant")


class AgricultureAssistantFnc(BaseBusinessFnc):
    """
    Farming specialist functions for the Farmovation assistant
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @llm.ai_callable()
    async def get_crop_recommendations(
        self,
        soil_type: Annotated[
            str, llm.TypeInfo(description="The type of soil (e.g., sandy loam, clay, silty)")
        ],
        season: Annotated[
            str, llm.TypeInfo(description="The growing season (e.g., Rabi/Winter or Kharif/Summer)")
        ],
    ) -> Dict[str, Any]:
        """
        Get crop recommendations based on soil type and growing season
        """
        logger.info(f"Getting crop recommendations for {soil_type} soil in {season} season")
        
        recommendations = {}
        
        # Process soil type
        if soil_type.lower() in ["sandy loam", "sandy"]:
            recommendations["soil_info"] = {
                "type": "sandy loam",
                "characteristics": ["Good drainage", "Low water retention", "Quick warming in spring"],
                "suitable_crops": ["carrots", "potatoes", "corn", "lettuce", "strawberries"]
            }
        elif soil_type.lower() in ["clay", "clay soil"]:
            recommendations["soil_info"] = {
                "type": "clay",
                "characteristics": ["High water retention", "Rich in nutrients", "Slow drainage"],
                "suitable_crops": ["wheat", "rice", "cabbage", "broccoli"]
            }
        elif soil_type.lower() in ["silty", "silt", "silty soil"]:
            recommendations["soil_info"] = {
                "type": "silty",
                "characteristics": ["Medium drainage", "Good fertility", "Holds moisture well"],
                "suitable_crops": ["wheat", "soybeans", "vegetables", "fruit trees"]
            }
        else:
            recommendations["message"] = f"Soil type '{soil_type}' not recognized. Please specify sandy loam, clay, or silty soil."
            return recommendations

        # Process season
        recommendations["season_info"] = {}
        if season.lower() in ["rabi", "winter", "rabi/winter"]:
            recommendations["season_info"] = {
                "name": "Rabi (Winter)",
                "planting_months": "October to December",
                "harvesting_months": "April to May",
                "recommended_crops": ["wheat", "barley", "chickpeas", "mustard", "potatoes"]
            }
        elif season.lower() in ["kharif", "summer", "kharif/summer"]:
            recommendations["season_info"] = {
                "name": "Kharif (Summer)",
                "planting_months": "June to July",
                "harvesting_months": "September to October",
                "recommended_crops": ["rice", "corn", "cotton", "sugarcane", "soybeans"]
            }
        else:
            recommendations["message"] = "Season not recognized. Please specify Rabi/Winter or Kharif/Summer."
            return recommendations
        
        # Filter the list of suitable crops based on both soil type and season
        soil_suitable_crops = recommendations["soil_info"]["suitable_crops"]
        season_suitable_crops = recommendations["season_info"]["recommended_crops"]
        
        # Find intersection of suitable crops for both soil and season
        suitable_crops = [crop for crop in soil_suitable_crops if crop in season_suitable_crops]
        
        if suitable_crops:
            recommendations["recommended_crops"] = suitable_crops
        else:
            recommendations["recommended_crops"] = []
            recommendations["message"] = "No perfect crop matches for this combination. Consider crop rotation or soil amendments."
        
        await asyncio.sleep(1)  # Simulate processing time
        return recommendations

    @llm.ai_callable()
    async def get_crop_details(
        self,
        crop_name: Annotated[
            str, llm.TypeInfo(description="The name of the crop (e.g., wheat, rice, cotton)")
        ],
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific crop including planting times, irrigation needs, and common problems
        """
        logger.info(f"Getting crop details for {crop_name}")
        
        crop_details = {}
        
        if crop_name.lower() == "wheat":
            crop_details = {
                "planting_time": "Late October to mid-November",
                "seed_rate": "50-55 kg/acre",
                "irrigation": "4-5 times during growing season",
                "fertilizer": "NPK (120-60-60 kg/acre)",
                "harvest_time": "March-April",
                "common_problems": ["Yellow rust", "aphids"],
                "solutions": ["Fungicides", "crop rotation"]
            }
        elif crop_name.lower() == "rice":
            crop_details = {
                "planting_time": "June-July",
                "seedling_age": "25-30 days",
                "plant_spacing": "20x20 cm",
                "water_depth": "5-7 cm",
                "fertilizer": "NPK (90-60-60 kg/acre)",
                "harvest_time": "October-November",
                "common_problems": ["Bacterial leaf blight", "stem borers"],
                "solutions": ["Resistant varieties", "balanced fertilization"]
            }
        elif crop_name.lower() == "cotton":
            crop_details = {
                "planting_time": "March-May",
                "seed_rate": "8-10 kg/acre",
                "row_spacing": "75 cm",
                "fertilizer": "NPK (120-60-60 kg/acre)",
                "irrigation": "6-8 times",
                "common_problems": ["Bollworms", "leaf curl virus"],
                "solutions": ["Bt varieties", "proper spacing"]
            }
        elif crop_name.lower() in ["sugarcane"]:
            crop_details = {
                "planting_time": "February-March",
                "seed_rate": "75-80 quintals/acre",
                "row_spacing": "90 cm",
                "fertilizer": "NPK (150-60-60 kg/acre)",
                "irrigation": "8-10 times",
                "harvest_time": "December-March",
                "common_problems": ["Red rot", "smut"],
                "solutions": ["Disease-free setts", "hot water treatment"]
            }
        else:
            crop_details["message"] = f"Details for {crop_name} are not available. Please ask about wheat, rice, cotton, or sugarcane."
        
        await asyncio.sleep(1)  # Simulate processing time
        return crop_details

    @llm.ai_callable()
    async def get_pest_management_advice(
        self,
        pest_name: Annotated[
            str, llm.TypeInfo(description="The name of the pest (e.g., aphids, bollworms, stem borers)")
        ],
        crop_name: Annotated[
            str, llm.TypeInfo(description="The crop affected by the pest")
        ] = "",
    ) -> Dict[str, Any]:
        """
        Get advice for managing a specific pest, optionally for a particular crop
        """
        logger.info(f"Getting pest management advice for {pest_name} on {crop_name}")
        
        pest_advice = {}
        
        if pest_name.lower() == "aphids":
            pest_advice = {
                "description": "Small sap-sucking insects that cluster on stems and new growth",
                "damage": "Stunted growth, yellowing leaves, sticky honeydew that leads to sooty mold",
                "control_organic": ["Neem oil spray", "Ladybugs and parasitic wasps", "Strong water spray to dislodge"],
                "control_chemical": ["Imidacloprid", "Acetamiprid"],
                "prevention": ["Maintain beneficial insects", "Avoid excessive nitrogen", "Monitor regularly"]
            }
        elif pest_name.lower() in ["bollworms", "bollworm"]:
            pest_advice = {
                "description": "Caterpillars that bore into cotton bolls and other fruit structures",
                "damage": "Holes in bolls/fruits, yield loss, quality reduction",
                "control_organic": ["Bt sprays", "Pheromone traps", "Trichogramma wasps"],
                "control_chemical": ["Spinosad", "Chlorantraniliprole"],
                "prevention": ["Bt cotton varieties", "Early sowing", "Destroy crop residue"]
            }
        elif pest_name.lower() in ["stem borers", "stem borer"]:
            pest_advice = {
                "description": "Larvae that tunnel into plant stems, especially in rice and maize",
                "damage": "Dead heart in vegetative stage, white heads in reproductive stage",
                "control_organic": ["Release Trichogramma", "Destroy stubble after harvest"],
                "control_chemical": ["Cartap hydrochloride", "Chlorantraniliprole"],
                "prevention": ["Early planting", "Resistant varieties", "Balanced fertilization"]
            }
        elif pest_name.lower() in ["whiteflies", "whitefly"]:
            pest_advice = {
                "description": "Small white flying insects that cluster under leaves",
                "damage": "Suck plant sap, vector for viruses, cause leaf curl",
                "control_organic": ["Yellow sticky traps", "Neem oil spray", "Reflective mulches"],
                "control_chemical": ["Diafenthiuron", "Flonicamid"],
                "prevention": ["Clean cultivation", "Resistant varieties", "Avoid water stress"]
            }
        else:
            pest_advice["message"] = f"Information about {pest_name} is not available. Please ask about aphids, bollworms, stem borers, or whiteflies."
            return pest_advice
        
        if crop_name:
            pest_advice["crop_specific_note"] = f"For {crop_name}, adjust application timing to coincide with early pest detection for maximum effectiveness."
        
        await asyncio.sleep(1)  # Simulate processing time
        return pest_advice

    @llm.ai_callable()
    async def get_water_management_advice(
        self,
        irrigation_method: Annotated[
            str, llm.TypeInfo(description="The irrigation method (e.g., flood, drip, sprinkler, furrow)")
        ],
        crop_type: Annotated[
            str, llm.TypeInfo(description="The type of crop being irrigated")
        ] = "",
    ) -> Dict[str, Any]:
        """
        Get water management advice based on irrigation method and optionally crop type
        """
        logger.info(f"Getting water management advice for {irrigation_method} irrigation on {crop_type}")
        
        water_advice = {}
        
        if irrigation_method.lower() in ["flood", "flood irrigation"]:
            water_advice = {
                "description": "Traditional method that covers the entire field with water",
                "efficiency": "40-50% water use efficiency",
                "suitable_crops": ["Rice", "Wheat (in specific conditions)"],
                "advantages": ["Low technical requirement", "Low initial investment"],
                "disadvantages": ["High water consumption", "Uneven distribution", "Runoff issues"],
                "best_practices": ["Proper land leveling", "Flow rate control", "Timing irrigation during cooler parts of day"]
            }
        elif irrigation_method.lower() in ["drip", "drip irrigation"]:
            water_advice = {
                "description": "Water delivered directly to the root zone through emitters",
                "efficiency": "90% water use efficiency, 60% water saving compared to flood",
                "suitable_crops": ["Vegetables", "Fruits", "Cotton"],
                "advantages": ["Highest water efficiency", "Reduced weed growth", "Can be used with fertigation"],
                "disadvantages": ["High initial cost", "Requires filtration", "Clogging issues"],
                "best_practices": ["Regular maintenance", "Good filtration", "Mulching"]
            }
        elif irrigation_method.lower() in ["sprinkler", "sprinkler irrigation"]:
            water_advice = {
                "description": "Water sprayed through nozzles over the crop in a controlled pattern",
                "efficiency": "70-80% water use efficiency",
                "suitable_crops": ["Wheat", "Pulses", "Vegetables"],
                "advantages": ["Good for uneven terrain", "Good for germination", "Medium cost"],
                "disadvantages": ["Wind drift", "Evaporation losses", "Not ideal for tall crops"],
                "best_practices": ["Irrigate during low-wind periods", "Proper spacing", "Maintain operating pressure"]
            }
        elif irrigation_method.lower() in ["furrow", "furrow irrigation"]:
            water_advice = {
                "description": "Water delivered through small parallel channels along crop rows",
                "efficiency": "60-70% water use efficiency",
                "suitable_crops": ["Row crops", "Cotton", "Maize"],
                "advantages": ["Lower cost than sprinkler/drip", "Reduced evaporation compared to flood"],
                "disadvantages": ["Requires precise land grading", "Less efficient than drip"],
                "best_practices": ["Proper furrow length", "Laser leveling", "Surge flow techniques"]
            }
        else:
            water_advice["message"] = f"Information about {irrigation_method} irrigation is not available. Please ask about flood, drip, sprinkler, or furrow irrigation."
            return water_advice
        
        if crop_type:
            if crop_type.lower() == "rice" and irrigation_method.lower() not in ["flood", "flood irrigation"]:
                water_advice["crop_specific_note"] = f"Note: {crop_type} traditionally uses flood irrigation, but water-saving techniques like AWD (Alternate Wetting and Drying) can be used."
            elif crop_type.lower() == "vegetables" and irrigation_method.lower() not in ["drip", "drip irrigation"]:
                water_advice["crop_specific_note"] = f"Note: For {crop_type}, drip irrigation is highly recommended for water efficiency and quality."
            else:
                water_advice["crop_specific_note"] = f"For {crop_type}, adjust irrigation frequency based on growth stage and weather conditions."
        
        await asyncio.sleep(1)  # Simulate processing time
        return water_advice

    @llm.ai_callable()
    async def get_business_info(
        self,
        info_type: Annotated[
            str, llm.TypeInfo(description="Type of business information requested (e.g., hours, services, contact, region)")
        ]
    ) -> Dict[str, Any]:
        """
        Get farming business information based on the requested type
        """
        logger.info(f"Getting business info: {info_type}")
        
        info_type = info_type.lower()
        result = {}
        
        # Example business information for Farmovation
        business_info = {
            "hours": {
                "monday": "9:00 AM - 5:00 PM",
                "tuesday": "9:00 AM - 5:00 PM",
                "wednesday": "9:00 AM - 5:00 PM",
                "thursday": "9:00 AM - 5:00 PM",
                "friday": "9:00 AM - 5:00 PM",
                "saturday": "10:00 AM - 2:00 PM",
                "sunday": "Closed"
            },
            "services": [
                "Crop consultation",
                "Soil analysis",
                "Water conservation advice",
                "Pest management strategies",
                "Weather monitoring",
                "Technology integration"
            ],
            "contact": {
                "phone": "(+92) 555-FARM",
                "email": "info@farmovation.pk",
                "website": "www.farmovation.pk"
            },
            "region": {
                "country": "Pakistan",
                "main_agricultural_areas": [
                    "Punjab",
                    "Sindh",
                    "Khyber Pakhtunkhwa"
                ],
                "climate": "Varies from arid to temperate",
                "major_challenges": [
                    "Water scarcity",
                    "Climate change",
                    "Access to technology"
                ]
            }
        }
        
        if info_type in business_info:
            result = business_info[info_type]
        else:
            result["message"] = f"Information about '{info_type}' is not available."
            result["available_info_types"] = list(business_info.keys())
        
        await asyncio.sleep(0.5)  # Simulate processing time
        return result

