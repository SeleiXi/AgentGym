"""
TravelPlanner Environment for AgentGym Setup Script
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "TravelPlanner Environment for AgentGym"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="agentenv-travelplanner",
    version="0.1.0",
    description="TravelPlanner Environment for AgentGym - A benchmark for evaluating language agents in travel planning scenarios",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="AgentGym Contributors",
    author_email="agentgym@example.com",
    url="https://github.com/BytedanceLab/AgentGym",
    packages=find_packages(),
    package_data={
        "agentenv_travelplanner": ["*.yaml", "*.yml"],
    },
    include_package_data=True,
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "ui": [
            "streamlit>=1.28.0",
            "gradio>=3.50.2",
        ],
        "full": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "streamlit>=1.28.0",
            "gradio>=3.50.2",
        ]
    },
    entry_points={
        "console_scripts": [
            "travelplanner-env=agentenv_travelplanner.launch:launch",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Researchers",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    keywords="agent gym travel planning benchmark language models llm",
    project_urls={
        "Bug Reports": "https://github.com/BytedanceLab/AgentGym/issues",
        "Source": "https://github.com/BytedanceLab/AgentGym",
        "Documentation": "https://github.com/BytedanceLab/AgentGym/tree/main/docs",
    },
) 