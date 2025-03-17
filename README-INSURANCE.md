# Acme Insurance - AI Voice Assistant Setup

This README provides instructions for setting up and running the Acme Insurance AI voice assistant using the Conversate platform.

## Overview

The Acme Insurance AI assistant is designed to:

- Provide friendly, proactive customer interactions
- Collect customer information for insurance quotes
- Answer questions about insurance options and coverage
- Schedule callbacks with human agents
- Process basic claim information
- Build trust through knowledgeable responses about Acme Insurance offerings

## Files Structure

- `config/insurance_config.json` - Main configuration file for the insurance assistant
- `data/insurance/sample_faq.md` - FAQ knowledge base for insurance questions
- `data/insurance/sample_guide.md` - Detailed insurance guides and educational content
- `src/functions/insurance_functions.py` - Custom functions for processing insurance data
- `setup_supabase.py` - Script to set up required database tables in Supabase

## Setup Instructions

### 1. Environment Setup

1. Make sure you have Python 3.9+ installed
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

### 2. Supabase Configuration

1. Create a Supabase account and project at https://supabase.com/
2. Get your project URL and anon key from the Supabase project settings
3. Update the `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL="https://your-project-id.supabase.co"
   SUPABASE_KEY="your-anon-key"
   ```

### 3. Set Up Database Tables

Run the Supabase setup script to create all necessary tables and sample data:

```
python setup_supabase.py
```

This script will create the following tables:

- `customer_leads` - For storing potential customer information
- `customers` - For storing verified customer data
- `policies` - For storing insurance policy information
- `insurance_quotes` - For storing quote requests and estimates
- `insurance_claims` - For storing claim reports
- `conversation_feedback` - For storing customer feedback about the assistant
- `callback_requests` - For storing callback scheduling requests
- `insurance_plans` - For storing available insurance plan details

### 4. Create Vector Index for RAG

To enable the AI to retrieve information from the insurance FAQs and guides:

```
python add_documents.py --business_type insurance
```

This will process the documents in `data/insurance/` and create searchable vector embeddings.

### 5. Run the Assistant

Run the insurance bot with:

```
python run.bat
```

Or directly with:

```
python src/agent/main.py
```

## Key Features

### Proactive Conversation

The assistant is configured to ask questions and guide customers through the insurance process rather than waiting for them to ask questions.

### Insurance Quote Collection

The assistant can collect all necessary information to generate insurance quotes for different types of coverage:

- Auto insurance
- Home insurance
- Life insurance
- Health insurance

### Data Storage

All customer information is securely stored in your Supabase database for later retrieval by agents.

### Agent Callback Scheduling

When customers need to speak with a human agent, the assistant can schedule callbacks at the customer's preferred time.

### Insurance Education

The assistant can provide educational content about different types of insurance, coverage options, and help customers understand their insurance needs.

## Customization

### Modifying Insurance Plans

Edit the `insurance_plans` section in `config/insurance_config.json` to update available insurance plans and their details.

### Adding New FAQ Content

Add new questions and answers to `data/insurance/sample_faq.md` and rebuild the vector index to make the information available to the assistant.

### Updating Functions

If you need to modify how the assistant handles data, edit functions in `src/functions/insurance_functions.py`.

## Troubleshooting

### Database Connection Issues

- Verify your Supabase URL and key in the `.env` file
- Check if the Supabase service is operational
- Try running `python setup_supabase.py` again with `--debug` flag

### RAG Not Working Properly

- Make sure you've run `add_documents.py` for the insurance business type
- Check that your document files are properly formatted markdown
- Verify that the paths in `insurance_config.json` point to the correct document locations

## Support

For additional assistance with the Acme Insurance assistant configuration, please contact Conversate support at support@acmeinsurance.com.
