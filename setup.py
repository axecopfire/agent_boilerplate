from setuptools import setup, find_packages

setup(
    name="agent_boilerplate",
    version="0.1.0",
    description="Boilerplate for creating and managing AI agents",
    author="SchusterBraun",
    packages=find_packages(),
    install_requires=[
        "openai",  # Azure OpenAI is part of the openai package
    ],
    python_requires=">=3.9",
)
