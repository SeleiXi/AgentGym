# TravelPlanner Environment for AgentGym

This package provides a TravelPlanner environment implementation for AgentGym, offering an interactive travel planning environment where agents can use various tools to create comprehensive travel plans.

## Overview

TravelPlanner is a complex travel planning environment that includes:
- 8 different tools for travel information gathering
- Interactive planning process
- Comprehensive constraint evaluation
- Real-world travel database integration

## Features

- **Multi-tool Support**: 8 travel-related tools including FlightSearch, AccommodationSearch, RestaurantSearch, etc.
- **Interactive Planning**: Step-by-step travel plan creation with notebook functionality
- **Flexible Configuration**: Comprehensive YAML configuration system
- **Mock Mode**: Built-in mock data for testing without external dependencies
- **RESTful API**: Standard AgentGym-compatible HTTP interface

## Installation

### Quick Start

```bash
# Install core dependencies
pip install -r requirements.txt

# Install package for development
pip install -e .
```

### Docker Installation (Recommended)

```bash
# Build Docker image
docker build -t travelplanner-env .

# Run container
docker run -p 8000:8000 travelplanner-env
```

## Usage

### Command Line Launch

```bash
# Basic usage
travelplanner-launch

# Custom configuration
travelplanner-launch --host 0.0.0.0 --port 8000 --log-level info

# Development mode
travelplanner-launch --reload --log-level debug
```

### Python API

```python
from agentenv_travelplanner import TravelPlannerEnvironment

# Create environment
env = TravelPlannerEnvironment()

# Reset with specific query
result = env.reset(query_id=0)
print(result['state'])

# Execute action
state, reward, done, info = env.step(
    'Action: FlightSearch with Action Input: {"departure_city": "New York", "destination_city": "Paris"}'
)

print(f"Reward: {reward}, Done: {done}")
print(f"New State: {state}")
```

### HTTP Client Usage

```python
import httpx
import asyncio

async def test_environment():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Create environment
        response = await client.post(f"{base_url}/create")
        env_id = response.json()["id"]
        
        # Reset environment
        reset_data = {"env_idx": env_id, "query_id": 0}
        response = await client.post(f"{base_url}/reset", json=reset_data)
        state = response.json()["state"]
        print("Initial State:", state)
        
        # Execute step
        step_data = {
            "env_idx": env_id,
            "action": 'Action: FlightSearch with Action Input: {"departure_city": "New York", "destination_city": "Paris"}'
        }
        response = await client.post(f"{base_url}/step", json=step_data)
        result = response.json()
        print("Step Result:", result)

# Run test
asyncio.run(test_environment())
```

## API Endpoints

- `POST /create` - Create new environment instance
- `POST /reset` - Reset environment with specific query
- `POST /step` - Execute action step
- `GET /info` - Get environment information
- `GET /observation` - Get current observation
- `GET /health` - Health check
- `GET /list_envs` - List all environment instances

## Configuration

The environment can be configured via `config.yaml`:

```yaml
# Server settings
server:
  host: "0.0.0.0"
  port: 8000
  workers: 1

# Environment settings
environment:
  max_steps: 30
  max_environments: 100

# Tool configuration
tools:
  available:
    - "FlightSearch"
    - "AccommodationSearch"
    # ... more tools
```

## Available Tools

1. **FlightSearch**: Search for flight options
2. **AccommodationSearch**: Find hotels and accommodations
3. **RestaurantSearch**: Discover dining options
4. **AttractionSearch**: Find tourist attractions
5. **GoogleDistanceMatrix**: Calculate distances between locations
6. **CitySearch**: Search for cities in specific regions
7. **NotebookWrite**: Save information to planning notebook
8. **Planner**: Generate final travel plan

## Development

### Testing

```bash
# Run all tests
python -m pytest test_environment.py -v

# Quick test without pytest
python quick_test.py
```

### Project Structure

```
agentenv_travelplanner/
├── __init__.py          # Package initialization
├── environment.py       # Core environment implementation
├── server.py           # FastAPI server
├── model.py            # Pydantic data models
├── utils.py            # Utility functions
├── config.yaml         # Configuration file
└── launch.py           # Command line launcher
```

## Dependencies

Core dependencies:
- fastapi: Web framework
- uvicorn: ASGI server
- pydantic: Data validation
- datasets: Hugging Face datasets
- httpx: HTTP client for testing

## Troubleshooting

### Common Issues

1. **Port Already in Use**: Change port in config or use `--port` argument
2. **Dataset Loading Failed**: Ensure internet connection or enable mock mode
3. **Memory Issues**: Reduce `max_environments` in configuration

### Debug Mode

Enable debug logging for detailed information:

```bash
travelplanner-launch --log-level debug
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

This project is part of AgentGym and follows the same license terms.

## Support

For issues and questions:
- Check the documentation
- Review configuration options
- Enable debug logging
- Submit GitHub issues with detailed information 