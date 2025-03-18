import os
import asyncio
import logging
import importlib
import sys
import traceback
from typing import  Optional
from pathlib import Path

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    JobProcess,
    llm,
    metrics,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, silero, openai
from dotenv import load_dotenv
env_file = Path(__file__).parent / ".env"
if (env_file).exists():
    load_dotenv(dotenv_path=env_file)
    logging.info(f"Loaded environment from {env_file}")
# Load environment variables from .env file
else:
    load_dotenv()  # Try to load from default locations
    logging.info("Loaded environment from default locations")
from src.utils.config import (
    get_system_prompt,
    get_welcome_message,
    get_voice_config,
    get_business_config,
    get_domain_config,
    reload_config
)
import pprint

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Get business configuration
business_config = get_business_config()
logger = logging.getLogger(f"{business_config['business_name'].lower()}-assistant")
logger.setLevel(logging.INFO)

 # Log configurations
logger.info("Current configurations:")
logger.info("Business Config:")
logger.info(pprint.pformat(business_config, indent=2))
        
voice_config = get_voice_config()
logger.info("Voice Config:")
logger.info(pprint.pformat(voice_config, indent=2))
        
domain_config = get_domain_config()
logger.info("Domain Config:")
logger.info(pprint.pformat(domain_config, indent=2))


# Ensure data directory exists
data_dir = Path(__file__).parent.parent.parent / "data"
data_dir.mkdir(exist_ok=True)

# Create subdirectories for different business domains
for domain in ["agriculture", "restaurant", "technology", "conversate"]:
    domain_dir = data_dir / domain
    domain_dir.mkdir(exist_ok=True)

# Create indexes directory
indexes_dir = data_dir / "indexes"
indexes_dir.mkdir(exist_ok=True)

def prewarm(proc: JobProcess):
    """
    Preload models to improve startup time
    
    Args:
        proc: JobProcess to store preloaded models
    """
    logger.info("Prewarming models...")
    try:
        proc.userdata["fnc_ctx"] = load_function_context()
        if proc.userdata["fnc_ctx"]:
            logger.info("Function context loaded successfully")
        else:
            logger.info("No function context available") 
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("Voice Activity Detection model loaded")
    except Exception as e:
        logger.error(f"Error loading VAD model: {e}")
        # Create empty placeholder to avoid errors
        proc.userdata["vad"] = None

def load_function_context() -> Optional[llm.FunctionContext]:
    """
    Dynamically load the appropriate function context based on business type
    Only loads if ENABLE_FUNCTION_CALLING is set to true
    
    Returns:
        FunctionContext or None if function calling is disabled or if loading fails
    """
    if os.environ.get("ENABLE_FUNCTION_CALLING", "false").lower() != "true":
        logger.info("Function calling disabled")
        return None

    try:
        business_domain = business_config["domain"]
        function_file = f"{business_domain}_functions.py"
        function_class = f"{business_domain.capitalize()}AssistantFnc"
        
        logger.info(f"Attempting to load function context for domain: {business_domain}")
        
        # Check if specific function module exists, otherwise use default functions
        function_path = Path(__file__).parent.parent / "functions" / function_file
        if not function_path.exists():
            logger.warning(f"Function file {function_file} not found, checking for alternatives")
            
            # Look for any available function files for this domain
            available_function_files = list(function_path.parent.glob(f"{business_domain}*.py"))
            if available_function_files:
                function_file = available_function_files[0].name
                logger.info(f"Found alternative function file: {function_file}")
            else:
                logger.warning("No domain-specific function file found, using default functions")
                if (function_path.parent / "__init__.py").exists():
                    function_file = "__init__.py"
                    function_class = "BaseBusinessFnc"
                else:
                    logger.error("No suitable function file found")
                    return None
        
        # Try to dynamically import the appropriate function module
        module_name = f"src.functions.{function_file[:-3]}"
        logger.info(f"Importing module: {module_name}")
        
        try:
            if module_name not in sys.modules:
                module = importlib.import_module(module_name)
            else:
                module = sys.modules[module_name]
            
            # Get the function class from the module
            if hasattr(module, function_class):
                fnc_class = getattr(module, function_class)
                logger.info(f"Successfully loaded function class: {function_class}")
                return fnc_class()
            else:
                # List available classes in the module
                available_classes = [cls for cls in dir(module) if cls.endswith("AssistantFnc")]
                if available_classes:
                    alternative_class = available_classes[0]
                    logger.info(f"Using alternative function class: {alternative_class}")
                    fnc_class = getattr(module, alternative_class)
                    return fnc_class()
                else:
                    logger.error(f"Could not find suitable function class in {module_name}")
                    return None
                
        except ImportError as e:
            logger.error(f"Error importing module {module_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading function context: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error in load_function_context: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

prox = load_function_context()
if prox:
        logger.info("Function context loaded successfully")
else:
        logger.info("No function context available") 
       

async def entrypoint(ctx: JobContext):
    """
    Main entry point for the assistant
    
    Args:
        ctx: JobContext for the current session
    """
    try:
        logger.info("Starting assistant entrypoint")
        
        # Connect to room and wait for participants
        
        # Get configuration
        voice_config = get_voice_config()
        # domain_config = get_domain_config()
        system_prompt = get_system_prompt()
        initial_ctx = llm.ChatContext().append(
            text=system_prompt,
            role="system",
        )
        
        # Wait for participant to join
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        logger.info("Connected to room, waiting for participants")
        participant = await ctx.wait_for_participant()
        logger.info(f"Participant joined: {participant.identity}")
        
        # Set up VAD from prewarmed models or create a new one if not available
        vad = ctx.proc.userdata.get("vad")
        fnc_ctx=prox
        if vad is None:
            logger.info("VAD not prewarmed, loading now")
            vad = silero.VAD.load()
        
        # Create agent with configured voice models
        agent = VoicePipelineAgent(
            vad=vad,
            stt=openai.STT().with_groq(
                model=voice_config["stt_model"],
                language=business_config["language"],
            ),
            llm=openai.LLM().with_cerebras(
                model=voice_config["llm_model"],
                temperature=voice_config["llm_temperature"],
            ),
            tts=deepgram.TTS(),
            fnc_ctx= fnc_ctx,
            chat_ctx=initial_ctx,
        )
        
        # Setup metrics collection
        usage_collector = metrics.UsageCollector()

        @agent.on("user_speech_committed")
       
            
        @agent.on("metrics_collected")
        def _on_metrics_collected(mtrcs: metrics.AgentMetrics):
            metrics.log_metrics(mtrcs)
            usage_collector.collect(mtrcs)

        @agent.on("error")
        def _on_error(error: Exception):
            logger.error(f"Agent error: {str(error)}")
        
        async def log_usage():
            summary = usage_collector.get_summary()
            logger.info(f"Usage: {summary}")

        # Start the agent with a configurable welcome message
        agent.start(ctx.room, participant)
        welcome_message = get_welcome_message()
        
        logger.info(f"Starting conversation with welcome message: {welcome_message}")
        await agent.say(welcome_message,allow_interruptions=False)
        
        # Stay alive
        while True:
            await asyncio.sleep(60)
            # Periodically log usage
            await log_usage()
            
    except Exception as e:
        logger.error(f"Error in entrypoint: {str(e)}")
        logger.debug(traceback.format_exc())


def parse_args():
    """Parse command line arguments"""
    import argparse
    parser = argparse.ArgumentParser(description="Business Assistant")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--business-type", type=str, help="Business type")
    return parser.parse_args()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        num_idle_processes=1,
        initialize_process_timeout=30  # Increased from default 10 to 30 seconds
    ))