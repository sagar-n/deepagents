"""Setup configuration for DeepAgents Stock Research Assistant."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "readme.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="deepagents-stock-research",
    version="1.0.0",
    author="Sagar",
    author_email="sagarreddyn95@gmail.com",
    description="AI-powered stock research assistant using LangChain DeepAgents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MindXpansion/deepagents",
    packages=find_packages(where="."),
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "deepagents",
        "langchain-ollama",
        "langchain-core",
        "yfinance",
        "gradio",
        "pandas",
        "numpy",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "deepagents-research=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
