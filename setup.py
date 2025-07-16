"""
EVM MCP Server 安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="evm-mcp-server",
    version="1.0.0",
    author="EVM MCP Server Team",
    author_email="",
    description="基于 MCP 的 EVM 区块链数据服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WonderLand33/evm-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "evm-mcp-server=src.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.md", "*.txt"],
    },
    keywords="ethereum, blockchain, mcp, web3, defi, crypto",
    project_urls={
        "Bug Reports": "https://github.com/WonderLand33/evm-mcp-server/issues",
        "Source": "https://github.com/WonderLand33/evm-mcp-server",
        "Documentation": "https://github.com/WonderLand33/evm-mcp-server/blob/main/docs/api.md",
    },
)