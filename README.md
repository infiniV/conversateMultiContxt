# Multi-Context Conversate Agent

An enterprise-grade voice assistant platform powered by LiveKit that adapts to multiple business contexts while maintaining contextual awareness and comprehensive information tracking.

## Key Features

- **Adaptive Context Handling**

  - Dynamic business domain adaptation
  - Real-time context switching
  - Comprehensive information validation

- **Voice Processing**

  - Real-time voice interaction
  - High-accuracy speech recognition
  - Natural language processing

- **Information Management**
  - Structured data collection
  - Edge case handling
  - Progressive information gathering

## Installation

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

## Configuration

### Environment Setup

Required environment variables in `.env`:

```ini
LIVEKIT_URL=ws://your-livekit-server
BUSINESS_TYPE=insurance
ENABLE_FUNCTION_CALLING=true
OPENAI_API_KEY=your-key
DEEPGRAM_API_KEY=your-key
```

### Business Configuration

Generate business-specific configuration:

```bash
python create_config.py --type insurance --name "Your Business"
```

## Usage

Launch the agent:

```bash
python src/agent/main.py
```

## Business Domains

Currently supported domains:

| Domain      | Description               | Configuration                    |
| ----------- | ------------------------- | -------------------------------- |
| Insurance   | Vehicle warranty services | `config/insurance_config.json`   |
| Agriculture | Farming assistance        | `config/agriculture_config.json` |
| Restaurant  | Food service management   | `config/restaurant_config.json`  |
| Technology  | Tech support services     | `config/technology_config.json`  |

## Architecture

```
multicontext-conversate-agent/
├── config/                 # Domain configurations
├── src/
│   ├── agent/             # Core agent logic
│   ├── functions/         # Domain-specific functions
│   └── utils/             # Shared utilities
├── data/                  # Domain data storage
└── tests/                 # Test suites
```

## Development

### Function Implementation

Example function usage:

```python
# Check vehicle eligibility
await agent.check_vehicle_eligibility(
    vehicle_year=2020,
    vehicle_make="Toyota",
    vehicle_model="Camry",
    mileage=50000
)

# Save customer information
await agent.save_customer_lead(
    first_name="John",
    last_name="Doe",
    phone="1234567890"
)
```

### Testing

Run the test suite:

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push branch (`git push origin feature/name`)
5. Open Pull Request

## Documentation

- [API Reference](docs/api.md)
- [Domain Configuration Guide](docs/domain-config.md)
- [Function Development Guide](docs/function-dev.md)

## Support

- GitHub Issues: [Open Issue](https://github.com/yourusername/multicontext-conversate-agent/issues)
- Email: support@conversate.ai
- Documentation: [Wiki](https://github.com/yourusername/multicontext-conversate-agent/wiki)

## License

MIT License - See [LICENSE](LICENSE) file
