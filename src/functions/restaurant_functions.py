"""
Restaurant-specific functions for restaurant business types.
This module contains AI-callable functions for restaurant services.
"""
import asyncio
import logging
from typing import Annotated, Dict, Any, List

from livekit.agents import llm
from . import BaseBusinessFnc

logger = logging.getLogger("restaurant-assistant")


class RestaurantAssistantFnc(BaseBusinessFnc):
    """
    Restaurant specialist functions for restaurant businesses
    """

    @llm.ai_callable()
    async def get_menu_items(
        self,
        category: Annotated[
            str, llm.TypeInfo(description="The category of menu items to retrieve (e.g., appetizers, main course, desserts)")
        ] = "",
        dietary_restriction: Annotated[
            str, llm.TypeInfo(description="Optional dietary restriction filter (e.g., vegetarian, gluten-free, halal)")
        ] = ""
    ) -> Dict[str, Any]:
        """
        Get menu items, optionally filtered by category and dietary restrictions
        """
        logger.info(f"Getting menu items for category: {category}, dietary restriction: {dietary_restriction}")
        
        # Example menu data - would typically come from a database
        menu = {
            "appetizers": [
                {"name": "Hummus", "price": 6.99, "description": "Creamy chickpea dip with olive oil and pita", "dietary": ["vegetarian", "vegan"]},
                {"name": "Falafel", "price": 7.99, "description": "Crispy chickpea fritters with tahini sauce", "dietary": ["vegetarian", "vegan"]},
                {"name": "Stuffed Grape Leaves", "price": 8.99, "description": "Rice and herb stuffed grape leaves", "dietary": ["vegetarian"]},
            ],
            "main course": [
                {"name": "Chicken Shawarma", "price": 13.99, "description": "Marinated chicken with garlic sauce and pickles", "dietary": ["halal"]},
                {"name": "Beef Kebab", "price": 15.99, "description": "Grilled seasoned beef with rice and vegetables", "dietary": ["halal"]},
                {"name": "Vegetable Tagine", "price": 12.99, "description": "Moroccan vegetable stew with couscous", "dietary": ["vegetarian", "vegan", "gluten-free"]},
            ],
            "desserts": [
                {"name": "Baklava", "price": 5.99, "description": "Layered phyllo pastry with honey and nuts", "dietary": ["vegetarian"]},
                {"name": "Rice Pudding", "price": 4.99, "description": "Creamy rice pudding with cinnamon and rose water", "dietary": ["vegetarian", "gluten-free"]},
            ],
            "drinks": [
                {"name": "Turkish Coffee", "price": 3.99, "description": "Strong coffee with cardamom", "dietary": ["vegetarian", "vegan", "gluten-free"]},
                {"name": "Mint Tea", "price": 2.99, "description": "Fresh mint leaves steeped with green tea", "dietary": ["vegetarian", "vegan", "gluten-free"]},
            ]
        }
        
        result = {"items": []}
        
        # Filter by category if provided
        if category:
            category = category.lower()
            if category in menu:
                items = menu[category]
                # Further filter by dietary restriction if provided
                if dietary_restriction:
                    dietary_restriction = dietary_restriction.lower()
                    items = [item for item in items if dietary_restriction in item["dietary"]]
                result["items"] = items
            else:
                result["message"] = f"Category '{category}' not found. Available categories: " + ", ".join(menu.keys())
        else:
            # If no category provided, return all items
            for cat, items in menu.items():
                # Filter by dietary restriction if provided
                if dietary_restriction:
                    dietary_restriction = dietary_restriction.lower()
                    filtered_items = [item for item in items if dietary_restriction in item["dietary"]]
                    if filtered_items:
                        result["items"].extend(filtered_items)
                else:
                    result["items"].extend(items)
        
        # Add a message if no items found after filtering
        if not result["items"] and dietary_restriction:
            result["message"] = f"No menu items found with dietary restriction: {dietary_restriction}"
        
        await asyncio.sleep(1)  # Simulate processing time
        return result

    @llm.ai_callable()
    async def check_reservation_availability(
        self,
        date: Annotated[
            str, llm.TypeInfo(description="The date for the reservation (YYYY-MM-DD)")
        ],
        time: Annotated[
            str, llm.TypeInfo(description="The time for the reservation (HH:MM)")
        ],
        party_size: Annotated[
            int, llm.TypeInfo(description="Number of people in the party")
        ]
    ) -> Dict[str, Any]:
        """
        Check if a reservation is available for the given date, time, and party size
        """
        logger.info(f"Checking reservation availability for {party_size} people on {date} at {time}")
        
        # In a real implementation, this would check a database of reservations
        # This is a simple simulation for demonstration purposes
        
        # Simulate some busy times
        busy_times = {
            "2023-12-31": ["18:00", "19:00", "20:00"],  # New Year's Eve
            "2023-12-25": ["12:00", "13:00", "14:00"],  # Christmas
        }
        
        # Check if the requested date and time is in the busy times
        date_busy = date in busy_times and time in busy_times[date]
        party_too_large = party_size > 8
        
        result = {}
        
        if date_busy and party_too_large:
            result["available"] = False
            result["message"] = "Sorry, we're fully booked at that time and cannot accommodate a party of that size."
            result["alternative_times"] = ["17:00", "21:00"]
        elif date_busy:
            result["available"] = False
            result["message"] = "Sorry, we're fully booked at that time."
            result["alternative_times"] = ["17:00", "21:00"]
        elif party_too_large:
            result["available"] = False
            result["message"] = "Sorry, we cannot accommodate a party larger than 8 people without advance notice."
            result["message"] += " Please call us directly to make arrangements for larger parties."
        else:
            result["available"] = True
            result["message"] = "Great news! We have availability at that time."
            result["reservation_instructions"] = "To confirm your reservation, please provide your name and contact information."
        
        await asyncio.sleep(1)  # Simulate processing time
        return result

    @llm.ai_callable()
    async def get_dietary_options(
        self,
        dietary_need: Annotated[
            str, llm.TypeInfo(description="The dietary need (e.g., vegetarian, vegan, gluten-free, halal)")
        ]
    ) -> Dict[str, List[str]]:
        """
        Get a list of menu items suitable for specific dietary needs
        """
        logger.info(f"Getting dietary options for: {dietary_need}")
        
        dietary_need = dietary_need.lower()
        
        # Example data - would typically come from a database
        dietary_options = {
            "vegetarian": [
                "Falafel Wrap",
                "Hummus Plate",
                "Greek Salad",
                "Vegetable Tagine",
                "Stuffed Grape Leaves",
                "Rice Pudding",
                "Baklava"
            ],
            "vegan": [
                "Falafel Wrap (no tzatziki)",
                "Hummus Plate",
                "Stuffed Grape Leaves",
                "Vegetable Tagine",
                "Mediterranean Salad (no feta)"
            ],
            "gluten-free": [
                "Greek Salad",
                "Vegetable Tagine",
                "Grilled Chicken Plate (with rice instead of pita)",
                "Rice Pudding"
            ],
            "halal": [
                "All meat dishes on our menu are certified Halal",
                "Chicken Shawarma",
                "Beef Kebab",
                "Lamb Gyro",
                "Falafel Plate"
            ]
        }
        
        result = {}
        
        if dietary_need in dietary_options:
            result["items"] = dietary_options[dietary_need]
        else:
            result["message"] = f"We don't have specific information for '{dietary_need}' dietary needs."
            result["available_options"] = list(dietary_options.keys())
        
        await asyncio.sleep(1)  # Simulate processing time
        return result

    @llm.ai_callable()
    async def get_business_info(
        self,
        info_type: Annotated[
            str, llm.TypeInfo(description="Type of business information requested (e.g., hours, location, services, contact)")
        ]
    ) -> Dict[str, Any]:
        """
        Get restaurant business information based on the requested type
        """
        logger.info(f"Getting business info: {info_type}")
        
        info_type = info_type.lower()
        result = {}
        
        # Example business information
        business_info = {
            "hours": {
                "monday": "11:00 AM - 10:00 PM",
                "tuesday": "11:00 AM - 10:00 PM",
                "wednesday": "11:00 AM - 10:00 PM",
                "thursday": "11:00 AM - 10:00 PM",
                "friday": "11:00 AM - 11:00 PM",
                "saturday": "11:00 AM - 11:00 PM",
                "sunday": "12:00 PM - 9:00 PM"
            },
            "location": {
                "address": "123 Mediterranean Ave",
                "city": "Athens",
                "state": "GA",
                "zip": "30601",
                "parking": "Free parking available in the rear lot"
            },
            "services": [
                "Dine-in",
                "Takeout",
                "Delivery (via third-party apps)",
                "Catering",
                "Private events"
            ],
            "contact": {
                "phone": "(555) 123-4567",
                "email": "info@shawarma-delight.com",
                "website": "www.shawarma-delight.com",
                "social_media": {
                    "facebook": "@ShawarmaDelight",
                    "instagram": "@ShawarmaDelight",
                    "twitter": "@ShawarmaDelight"
                }
            }
        }
        
        if info_type in business_info:
            result = business_info[info_type]
        else:
            result["message"] = f"Information about '{info_type}' is not available."
            result["available_info_types"] = list(business_info.keys())
        
        await asyncio.sleep(0.5)  # Simulate processing time
        return result