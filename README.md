# Business Assistant Platform

A customizable voice-enabled business assistant that adapts to different business types and needs using LiveKit's real-time communication platform.

## Overview

This platform creates specialized voice assistants tailored to different business domains. Initially created for agricultural assistance (Farmovation), the platform has been expanded to support any business type. The system:

1. Collects business information through a web application signup process
2. Generates a custom configuration based on business needs
3. Deploys a specialized voice assistant with relevant domain knowledge and functions
4. Provides real-time assistance to customers based on the business requirements

## Features

- **Dynamic Business Configuration**: Automatically adapts to different business types and needs
- **Voice Interaction**: Natural conversation with customers using LiveKit's audio capabilities
- **Function Calling**: Optional business-specific functions based on subscription plan
- **Customizable Knowledge Base**: Domain-specific information tailored to each business
- **Real-time Assistance**: Live answers to customer questions through voice
- **Robust RAG System**: Retrieval-Augmented Generation for accurate domain-specific responses

## Business Onboarding Process

1. **Sign up on web application**:

   - Business provides basic information (name, type, description, etc.)
   - Business selects subscription plan (standard or custom solution)
   - Business answers domain-specific questions to build their configuration

2. **Configuration Generation**:

   - System creates a custom JSON configuration for the business
   - For custom plans, developers implement specialized functions

3. **Assistant Deployment**:

   - Server spins up with the business's custom configuration
   - Voice assistant initializes with appropriate system prompt and functions

4. **Customer Interaction**:
   - Business customers connect to the voice assistant
   - Assistant provides domain-specific information and assistance

## Web Application Integration

The web application collects business-specific information during signup and passes it to the assistant creation system.
Below is the expected JSON structure for the data required from the web application:

```json
{
  "business_type": "restaurant",
  "business_name": "Pizza Palace",
  "tagline": "Authentic Italian pizza made with love",
  "description": "A family-owned pizzeria serving traditional Neapolitan style pizza since 1985",
  "region": "Chicago, IL",
  "language": "en",
  "subscription_plan": "premium",
  "enable_function_calling": true,
  "services": [
    "Dine-in service",
    "Take-out orders",
    "Catering for events",
    "Weekly specials"
  ],
  // Additional fields based on business type
  "menu_categories": ["Pizzas", "Pasta", "Salads", "Desserts"],
  "popular_items": [
    "Margherita Pizza",
    "Pepperoni Pizza",
    "Spaghetti Carbonara"
  ],
  "contact_info": {
    "phone": "(555) 123-4567",
    "email": "info@pizzapalace.com",
    "website": "www.pizzapalace.com"
  },
  "business_hours": {
    "monday": "11:00 AM - 10:00 PM",
    "tuesday": "11:00 AM - 10:00 PM",
    "wednesday": "11:00 AM - 10:00 PM",
    "thursday": "11:00 AM - 10:00 PM",
    "friday": "11:00 AM - 11:00 PM",
    "saturday": "12:00 PM - 11:00 PM",
    "sunday": "12:00 PM - 9:00 PM"
  }
}
```

For agriculture businesses, the required fields would be different:

```json
{
  "business_type": "agriculture",
  "business_name": "Green Fields Farm",
  "tagline": "Sustainable farming for a better tomorrow",
  "description": "An organic farm specializing in seasonal vegetables and fruits",
  "region": "Punjab, Pakistan",
  "language": "en",
  "subscription_plan": "standard",
  "enable_function_calling": true,
  "services": [
    "Crop consulting",
    "Sustainable farming practices",
    "Organic certification assistance",
    "Seasonal planting guides"
  ],
  "crops": ["Wheat", "Rice", "Cotton", "Vegetables"],
  "growing_seasons": ["Rabi (Winter)", "Kharif (Summer)"],
  "irrigation_methods": ["Drip", "Sprinkler"]
}
```

The system adapts dynamically based on the business type and will request appropriate additional information during the signup process.

## Setup

1. **Environment Setup**:

   ```
   # Clone the repository
   cd farmovationbot

   # Create and activate a virtual environment
   python -m venv .venv
   .venv\Scripts\activate  # On Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   The `.env` file should be configured with:
   - `LIVEKIT_URL`: WebSocket URL for your LiveKit server
   - API keys for various services
   - `BUSINESS_TYPE`: The type of business for the assistant
   - `ENABLE_FUNCTION_CALLING`: Set to "true" to enable custom business functions
   - `CONFIG_FILE_PATH`: Optional path to a custom configuration file

## Usage

1. Start the agent:

   ```
   # Using default configuration
   python main.py

   # Using custom configuration
   python main.py --config path/to/custom_config.json
   ```

2. Connect to the LiveKit room using a compatible client (web, mobile, or SIP interface)

3. Start speaking with the agent with domain-specific questions related to the business type

## Document Management for RAG

The platform includes robust tools for managing your knowledge base documents:

1. **Add Documents**:

   ```bash
   python add_documents.py --domain agriculture --sources path/to/docs
   ```

2. **Create Sample Documents**:

   ```bash
   python add_documents.py --create-sample agriculture --sample-type faq
   ```
   
3. **List Available Domains**:

   ```bash
   python add_documents.py --list
   ```

4. **View Domain Information**:
   ```bash
   python add_documents.py --info agriculture
   ```

## RAG System Management

The platform includes a dedicated tool for managing the Retrieval Augmented Generation (RAG) system:

1. **Check All Indexes**:

   ```bash
   python rag_manage.py --check-all
   ```

2. **Rebuild Domain Index**:

   ```bash
   python rag_manage.py --rebuild agriculture
   ```

3. **Validate Documents**:

   ```bash
   python rag_manage.py --validate agriculture
   ```

4. **Clean Problematic Files**:
   ```bash
   python rag_manage.py --clean agriculture --fix
   ```

## Creating a New Business Configuration

For testing and development, you can use the included business configuration creator:

```bash
python create_business_config.py --enable-functions
```

This interactive tool will guide you through creating a configuration for a new business.

## Assistant Architecture

- **Configuration System**: Loads and manages business-specific settings
- **Dynamic Function Loading**: Conditionally loads functions based on business type
- **LiveKit Integration**: Provides real-time communication capabilities
- **Speech Processing**: Using Groq's Whisper model for STT and Deepgram for TTS
- **LLM Backend**: Cerebras Llama 3.3 70B for natural language understanding
- **Retrieval Augmented Generation**: Vector-based document retrieval using LlamaIndex and ChromaDB

## Supported Business Types

The platform currently includes specialized configurations for:

1. **Agriculture**: Crop management, pest control, water management, etc.
2. **Restaurant**: Menu information, reservations, dietary options, etc.
3. **Conversate**: Technology platform information, subscription details, integration options
4. **Custom Businesses**: Any business type can be configured through the platform

## Developer Information

To add support for a new business type:

1. Create a `[business_type]_config.json` file in the config directory
2. Create a `[business_type]_functions.py` file in the src/functions directory
3. Implement a class that inherits from `BaseBusinessFnc` with business-specific functions
4. Add relevant documents to the `data/[business_type]` directory for RAG capabilities

All custom business implementations must follow the standard function format with annotated parameters and return types.

## Future Enhancements

- Expanded library of pre-configured business types
- Integration with business-specific external APIs
- Multi-language support for global businesses
- Image and document processing capabilities
- Advanced RAG capabilities with multi-document reasoning
#   c o n v e r s a t e M u l t i C o n t x t  
 