# Agent Boilerplate

A Python framework for creating and managing AI agents, primarily using Azure OpenAI.

## Installation

You can install this package directly from GitHub:

```bash
# Install directly from the repository
pip install git+https://github.com/axecopfire/agent_boilerplate.git

# Or clone and install in development mode
git clone https://github.com/axecopfire/agent_boilerplate.git
cd agent_boilerplate
pip install -e .
```

## Environment Setup

This package requires the following environment variables:

```
AOAI_ENDPOINT=your-azure-openai-endpoint
AOAI_KEY=your-azure-openai-key
OPENAI_API_VERSION=your-openai-api-version
DEPLOYMENT_NAME=your-deployment-name
```

## Virtual Environment Setup

It's recommended to use a virtual environment when developing:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# When you're done, deactivate the virtual environment
deactivate
```

## Basic Usage

```python
from agent_boilerplate.agents import Agent

# Create a new agent
agent = Agent(
    name="my_agent",
    system_message="You are a helpful assistant."
)

# Get a response
response = agent("Tell me a joke")
print(response)
```

### Running the Examples

The repository includes example scripts in the `examples` directory. To run these examples:

```bash
# Make sure you've set up your environment variables first
# Either export them in your shell or create a .env file

# Run the simple agent example
python -m examples.simple_agent
```

This will execute the example script which demonstrates creating a basic agent and getting a response.

## Components

- `agents`: Base agent class and specialized agents
- `executor`: Tools for running code in Docker and other environments
- `flows`: Framework for creating agent workflows
- `git`: Git integration utilities
- `utils`: Utility functions for file handling and logging

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
