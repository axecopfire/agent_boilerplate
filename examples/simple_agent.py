"""
Example of how to use the Agent Boilerplate package.
"""
import os
import sys
import dotenv

# Load environment variables from .env file if available
dotenv.load_dotenv()

# Add the parent directory to the path to import the package
# (only needed when running from the examples directory without installing the package)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Agent class
from agents import Agent


def main():
    # Create a simple agent
    agent = Agent(
        name="example_agent",
        system_message="You are a helpful assistant that provides concise answers."
    )

    # Get a response from the agent
    prompt = "Explain what an AI agent is in one sentence."
    response = agent(prompt)

    print(f"Prompt: {prompt}")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
