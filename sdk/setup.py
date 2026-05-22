from setuptools import setup, find_packages

setup(
    name="agenthub",
    version="0.1.0",
    description="One-line registration for A2A agents. Auto-register with AgentHub on startup.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="WorkspaceLab",
    author_email="185436620@qq.com",
    url="https://github.com/snowflying117-ship-it/agenthub",
    project_urls={
        "Homepage": "https://eco.xiangma.ren/agents/",
        "Documentation": "https://github.com/snowflying117-ship-it/agenthub",
        "Bug Tracker": "https://github.com/snowflying117-ship-it/agenthub/issues",
    },
    packages=find_packages(),
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
