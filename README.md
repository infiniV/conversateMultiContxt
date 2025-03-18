# Multi-Context Conversate Agent

An enterprise-grade voice assistant platform powered by LiveKit that adapts to multiple business contexts.

## Configuration Structure

All business configurations must follow this structure:

```json
{
  "business_config": {
    "business_name": "String (required)",
    "business_tagline": "String (required)",
    "business_description": "String (required)",
    "specialist_name": "String (required)",
    "domain": "String (required) - One of: insurance, agriculture, restaurant, technology",
    "region": "String (required)",
    "language": "String (required) - ISO code",
    "assistant_personality": "String (comma-separated traits)"
  },
  "voice_config": {
    "welcome_message": "String (required)",
    "stt_model": "String (required)",
    "llm_model": "String (required)",
    "llm_temperature": "Number (0.0-1.0)",
    "tts_voice": "String (required)"
  },
  "required_information": {
    "customer_details": {
      "basic": ["Array of required fields"],
      "additional": ["Array of optional fields"],
      "validation_rules": {
        "field_name": "Regex validation pattern"
      }
    },
    "domain_specific_details": {
      "basic": ["Array of required fields"],
      "additional": ["Array of optional fields"],
      "validation_rules": {
        "field_name": "Regex validation pattern"
      }
    }
  },
  "edge_cases": {
    "case_category": {
      "case_name": {
        "property": "value",
        "conditions": ["Array of conditions"],
        "actions": ["Array of actions"]
      }
    }
  },
  "information_collection_flow": {
    "sequence": [
      {
        "step": "String (step identifier)",
        "required_fields": ["Array of fields"],
        "next_step": "String (next step identifier)"
      }
    ],
    "fallback_actions": {
      "action_type": {
        "action": "String (action to take)",
        "max_attempts": "Number",
        "timeout_minutes": "Number"
      }
    }
  },
  "domain_config": {
    "services": ["Array of services"]
    // Domain-specific configuration items
  },
  "conversation_flows": {
    "flow_name": [
      {
        "id": "String (step identifier)",
        "assistant_message": "String (message to speak)",
        "expected_responses": [
          {
            "type": "String (response type)",
            "next": "String (next step)"
          }
        ],
        "save_to_db": {
          "table": "String (table name)",
          "fields": ["Array of fields to save"]
        }
      }
    ]
  }
}
```

## Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/multicontext-conversate-agent.git
cd multicontext-conversate-agent

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

Generate test config:

```bash
python src/utils/config_generator.py -t insurance -n "Test Insurance Co"
```

Launch the agent:

```bash
python src/agent/main.py --config config/insurance_config.json
```

## Business Domains

| Domain      | Description               | Configuration             |
| ----------- | ------------------------- | ------------------------- |
| Insurance   | Vehicle warranty services | `insurance_config.json`   |
| Agriculture | Farming assistance        | `agriculture_config.json` |
| Restaurant  | Food service management   | `restaurant_config.json`  |
| Technology  | Tech support services     | `technology_config.json`  |

## Example Function Call

```python
# Check vehicle eligibility
await agent.check_vehicle_eligibility(
    vehicle_year=2020,
    vehicle_make="Toyota",
    vehicle_model="Camry",
    mileage=50000
)
```

## License

MIT License - See [LICENSE](LICENSE) file
