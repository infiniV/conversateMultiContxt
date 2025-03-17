"""
Insurance-specific functions for Acme Insurance business.
This module contains AI-callable functions specific to insurance services.
"""
import asyncio
import logging
from typing import Annotated, Dict, Any

from livekit.agents import llm
# Import the base class differently
from livekit.agents.llm import FunctionContext
from src.utils.config import get_domain_config, get_business_config

logger = logging.getLogger("insurance-assistant")


class InsuranceAssistantFnc(FunctionContext):
    """
    InsuranceAssistantFnc is a class that extends the FunctionContext class
    and provides additional functionality for the InsuranceAssistant.
    """
