"""AgentHub CLI - The official CLI for A2A agent discovery and testing."""
from setuptools import setup, find_packages

setup(
    name="agenthub",
    version="0.2.0",
    description="The official CLI for A2A agent discovery, testing, and registration.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="WorkspaceLab",
    author_email="185436620@qq.com",
    url="https://github.com/snowflying117-ship-it/agenthub",
    project_urls={
        "Homepage": "https://eco.xiangma.ren/agents/",
        "Documentation": "https://github.com/snowflying117-ship-it/agenthub",
    },
    py_modules=["agenthub_cli"],
    entry_points={
        "console_scripts": [
            "agenthub=agenthub_cli:main",
        ],
    },
    install_requires=["httpx>=0.24.0"],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    license="MIT",
)
