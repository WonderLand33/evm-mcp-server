"""
EVM MCP Server - 主服务器文件
提供符合 MCP 标准的 EVM 区块链交互服务
"""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel, CallToolRequest, GetResourceRequest, ListResourcesRequest,
    ListToolsRequest
)
from pydantic import AnyUrl
import mcp.types as types

from .web3_manager import Web3Manager
from .tools import (
    AccountTools, TokenTools, TransactionTools, 
    BlockTools, ContractTools, NetworkTools, ENSTools
)
from .config import Config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建服务器实例
server = Server("evm-mcp-server")

# 初始化组件
web3_manager = Web3Manager()
account_tools = AccountTools(web3_manager)
token_tools = TokenTools(web3_manager)
transaction_tools = TransactionTools(web3_manager)
block_tools = BlockTools(web3_manager)
contract_tools = ContractTools(web3_manager)
network_tools = NetworkTools(web3_manager)
ens_tools = ENSTools(web3_manager)

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """列出可用资源"""
    return [
        Resource(
            uri=AnyUrl("evm://networks"),
            name="Supported Networks",
            description="List of supported EVM networks and their configurations",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("evm://status"),
            name="Server Status",
            description="Current server status and network connections",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("evm://gas-tracker"),
            name="Gas Price Tracker",
            description="Real-time gas prices across supported networks",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("evm://latest-blocks"),
            name="Latest Blocks",
            description="Latest blocks from all connected networks",
            mimeType="application/json",
        )
    ]

@server.get_resource()
async def handle_get_resource(request: GetResourceRequest) -> str:
    """获取资源内容"""
    uri = str(request.uri)
    
    if uri == "evm://networks":
        networks = Config.get_supported_networks()
        return f"# Supported EVM Networks\n\n{networks}"
    
    elif uri == "evm://status":
        status = await network_tools.get_network_info()
        return f"# Server Status\n\n```json\n{status}\n```"
    
    elif uri == "evm://gas-tracker":
        gas_data = {}
        for network in Config.NETWORKS.keys():
            gas_info = await network_tools.get_gas_price(network)
            if gas_info.get("success"):
                gas_data[network] = gas_info
        return f"# Gas Price Tracker\n\n```json\n{gas_data}\n```"
    
    elif uri == "evm://latest-blocks":
        blocks_data = {}
        for network in Config.NETWORKS.keys():
            try:
                latest_blocks = await block_tools.get_latest_blocks(5, network)
                if latest_blocks.get("success"):
                    blocks_data[network] = latest_blocks
            except Exception as e:
                logger.debug(f"Could not get latest blocks for {network}: {e}")
        return f"# Latest Blocks\n\n```json\n{blocks_data}\n```"
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出可用工具"""
    return [
        # 账户和余额工具
        Tool(
            name="get_balance",
            description="Get native token balance for an address",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Ethereum address to check balance for"
                    },
                    "network": {
                        "type": "string", 
                        "description": "Network name (ethereum, polygon, bsc, etc.)",
                        "default": "ethereum"
                    }
                },
                "required": ["address"]
            },
        ),
        Tool(
            name="get_token_balance",
            description="Get ERC20 token balance for an address",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Address to check token balance for"
                    },
                    "token_address": {
                        "type": "string",
                        "description": "ERC20 token contract address"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["address", "token_address"]
            },
        ),
        Tool(
            name="get_account_info",
            description="Get comprehensive account information including balance, nonce, and contract status",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Ethereum address to get info for"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["address"]
            },
        ),
        
        # 代币信息工具
        Tool(
            name="get_token_metadata",
            description="Get ERC20 token metadata (name, symbol, decimals, total supply)",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_address": {
                        "type": "string",
                        "description": "ERC20 token contract address"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["token_address"]
            },
        ),
        Tool(
            name="get_token_price",
            description="Get current token price from CoinGecko",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "CoinGecko token ID (e.g., 'ethereum', 'bitcoin')"
                    },
                    "vs_currency": {
                        "type": "string",
                        "description": "Currency to get price in",
                        "default": "usd"
                    }
                },
                "required": ["token_id"]
            },
        ),
        Tool(
            name="search_tokens",
            description="Search for tokens by name or symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (token name or symbol)"
                    }
                },
                "required": ["query"]
            },
        ),
        
        # 交易工具
        Tool(
            name="get_transaction",
            description="Get detailed transaction information",
            inputSchema={
                "type": "object",
                "properties": {
                    "tx_hash": {
                        "type": "string",
                        "description": "Transaction hash"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["tx_hash"]
            },
        ),
        Tool(
            name="get_transaction_receipt",
            description="Get transaction receipt with execution details",
            inputSchema={
                "type": "object",
                "properties": {
                    "tx_hash": {
                        "type": "string",
                        "description": "Transaction hash"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["tx_hash"]
            },
        ),
        Tool(
            name="estimate_gas",
            description="Estimate gas cost for a transaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_address": {
                        "type": "string",
                        "description": "Sender address"
                    },
                    "to_address": {
                        "type": "string",
                        "description": "Recipient address (optional for contract creation)"
                    },
                    "value": {
                        "type": ["string", "number"],
                        "description": "Amount to send (in wei or ether string)",
                        "default": "0"
                    },
                    "data": {
                        "type": "string",
                        "description": "Transaction data (optional)"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["from_address"]
            },
        ),
        Tool(
            name="decode_transaction_input",
            description="Decode transaction input data",
            inputSchema={
                "type": "object",
                "properties": {
                    "tx_hash": {
                        "type": "string",
                        "description": "Transaction hash"
                    },
                    "abi": {
                        "type": "array",
                        "description": "Contract ABI for detailed decoding (optional)"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["tx_hash"]
            },
        ),
        
        # 区块工具
        Tool(
            name="get_block",
            description="Get block information",
            inputSchema={
                "type": "object",
                "properties": {
                    "block_identifier": {
                        "type": ["string", "number"],
                        "description": "Block number, hash, or 'latest'",
                        "default": "latest"
                    },
                    "full_transactions": {
                        "type": "boolean",
                        "description": "Include full transaction details",
                        "default": False
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                }
            },
        ),
        Tool(
            name="get_latest_blocks",
            description="Get latest blocks from a network",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "number",
                        "description": "Number of blocks to retrieve (1-100)",
                        "default": 10
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                }
            },
        ),
        Tool(
            name="analyze_block_range",
            description="Analyze statistics for a range of blocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_block": {
                        "type": "number",
                        "description": "Starting block number"
                    },
                    "end_block": {
                        "type": "number",
                        "description": "Ending block number"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["start_block", "end_block"]
            },
        ),
        
        # 智能合约工具
        Tool(
            name="read_contract",
            description="Read data from a smart contract",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Contract address"
                    },
                    "abi": {
                        "type": ["string", "array"],
                        "description": "Contract ABI (JSON string or array)"
                    },
                    "function_name": {
                        "type": "string",
                        "description": "Function name to call"
                    },
                    "args": {
                        "type": "array",
                        "description": "Function arguments",
                        "default": []
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["address", "abi", "function_name"]
            },
        ),
        Tool(
            name="get_contract_info",
            description="Get basic contract information",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Contract address"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["address"]
            },
        ),
        Tool(
            name="estimate_contract_gas",
            description="Estimate gas for contract function call",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Contract address"
                    },
                    "abi": {
                        "type": ["string", "array"],
                        "description": "Contract ABI"
                    },
                    "function_name": {
                        "type": "string",
                        "description": "Function name"
                    },
                    "args": {
                        "type": "array",
                        "description": "Function arguments",
                        "default": []
                    },
                    "from_address": {
                        "type": "string",
                        "description": "Caller address (optional)"
                    },
                    "value": {
                        "type": "number",
                        "description": "ETH value to send (wei)",
                        "default": 0
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["address", "abi", "function_name"]
            },
        ),
        Tool(
            name="get_contract_events",
            description="Get contract event logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Contract address"
                    },
                    "abi": {
                        "type": ["string", "array"],
                        "description": "Contract ABI"
                    },
                    "event_name": {
                        "type": "string",
                        "description": "Event name"
                    },
                    "from_block": {
                        "type": ["string", "number"],
                        "description": "Starting block",
                        "default": "latest"
                    },
                    "to_block": {
                        "type": ["string", "number"],
                        "description": "Ending block",
                        "default": "latest"
                    },
                    "argument_filters": {
                        "type": "object",
                        "description": "Event argument filters"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                },
                "required": ["address", "abi", "event_name"]
            },
        ),
        
        # ENS 工具
        Tool(
            name="resolve_ens_name",
            description="Resolve ENS domain name to address",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "ENS domain name (e.g., vitalik.eth)"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name (must support ENS)",
                        "default": "ethereum"
                    }
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="reverse_resolve_ens",
            description="Reverse resolve address to ENS name",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Ethereum address"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name (must support ENS)",
                        "default": "ethereum"
                    }
                },
                "required": ["address"]
            },
        ),
        Tool(
            name="get_ens_records",
            description="Get all ENS records for a domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "ENS domain name"
                    },
                    "network": {
                        "type": "string",
                        "description": "Network name (must support ENS)",
                        "default": "ethereum"
                    }
                },
                "required": ["name"]
            },
        ),
        
        # 网络和实用工具
        Tool(
            name="get_supported_networks",
            description="Get list of supported networks",
            inputSchema={
                "type": "object",
                "properties": {}
            },
        ),
        Tool(
            name="get_network_status",
            description="Get network connection status and information",
            inputSchema={
                "type": "object",
                "properties": {
                    "network": {
                        "type": "string",
                        "description": "Specific network to check (optional)"
                    }
                }
            },
        ),
        Tool(
            name="get_gas_price",
            description="Get current gas prices for a network",
            inputSchema={
                "type": "object",
                "properties": {
                    "network": {
                        "type": "string",
                        "description": "Network name",
                        "default": "ethereum"
                    }
                }
            },
        ),
        Tool(
            name="convert_units",
            description="Convert between Wei, Gwei, and Ether",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {
                        "type": ["string", "number"],
                        "description": "Amount to convert"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "Source unit (wei, gwei, ether)",
                        "enum": ["wei", "gwei", "ether"]
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "Target unit (wei, gwei, ether)",
                        "enum": ["wei", "gwei", "ether"]
                    }
                },
                "required": ["amount", "from_unit", "to_unit"]
            },
        ),
        Tool(
            name="validate_address",
            description="Validate Ethereum address format",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Address to validate"
                    }
                },
                "required": ["address"]
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> list[types.TextContent]:
    """处理工具调用"""
    try:
        tool_name = request.params.name
        args = request.params.arguments or {}
        
        # 账户和余额工具
        if tool_name == "get_balance":
            result = await account_tools.get_balance(
                args["address"], 
                args.get("network")
            )
        elif tool_name == "get_token_balance":
            result = await account_tools.get_token_balance(
                args["address"], 
                args["token_address"], 
                args.get("network")
            )
        elif tool_name == "get_account_info":
            result = await account_tools.get_account_info(
                args["address"], 
                args.get("network")
            )
        
        # 代币信息工具
        elif tool_name == "get_token_metadata":
            result = await token_tools.get_token_metadata(
                args["token_address"], 
                args.get("network")
            )
        elif tool_name == "get_token_price":
            result = await token_tools.get_token_price(
                args["token_id"], 
                args.get("vs_currency", "usd")
            )
        elif tool_name == "search_tokens":
            result = await token_tools.search_tokens(args["query"])
        
        # 交易工具
        elif tool_name == "get_transaction":
            result = await transaction_tools.get_transaction(
                args["tx_hash"], 
                args.get("network")
            )
        elif tool_name == "get_transaction_receipt":
            result = await transaction_tools.get_transaction_receipt(
                args["tx_hash"], 
                args.get("network")
            )
        elif tool_name == "estimate_gas":
            result = await transaction_tools.estimate_gas(
                args["from_address"],
                args.get("to_address"),
                args.get("value", 0),
                args.get("data"),
                args.get("network")
            )
        elif tool_name == "decode_transaction_input":
            result = await transaction_tools.decode_transaction_input(
                args["tx_hash"],
                args.get("abi"),
                args.get("network")
            )
        
        # 区块工具
        elif tool_name == "get_block":
            result = await block_tools.get_block(
                args.get("block_identifier", "latest"),
                args.get("full_transactions", False),
                args.get("network")
            )
        elif tool_name == "get_latest_blocks":
            result = await block_tools.get_latest_blocks(
                args.get("count", 10),
                args.get("network")
            )
        elif tool_name == "analyze_block_range":
            result = await block_tools.analyze_block_range(
                args["start_block"],
                args["end_block"],
                args.get("network")
            )
        
        # 智能合约工具
        elif tool_name == "read_contract":
            result = await contract_tools.read_contract(
                args["address"],
                args["abi"],
                args["function_name"],
                args.get("args", []),
                args.get("network")
            )
        elif tool_name == "get_contract_info":
            result = await contract_tools.get_contract_info(
                args["address"],
                args.get("network")
            )
        elif tool_name == "estimate_contract_gas":
            result = await contract_tools.estimate_gas(
                args["address"],
                args["abi"],
                args["function_name"],
                args.get("args", []),
                args.get("from_address"),
                args.get("value", 0),
                args.get("network")
            )
        elif tool_name == "get_contract_events":
            result = await contract_tools.get_events(
                args["address"],
                args["abi"],
                args["event_name"],
                args.get("from_block", "latest"),
                args.get("to_block", "latest"),
                args.get("argument_filters"),
                args.get("network")
            )
        
        # ENS 工具
        elif tool_name == "resolve_ens_name":
            result = await ens_tools.resolve_name(
                args["name"],
                args.get("network", "ethereum")
            )
        elif tool_name == "reverse_resolve_ens":
            result = await ens_tools.reverse_resolve(
                args["address"],
                args.get("network", "ethereum")
            )
        elif tool_name == "get_ens_records":
            result = await ens_tools.get_all_records(
                args["name"],
                args.get("network", "ethereum")
            )
        
        # 网络和实用工具
        elif tool_name == "get_supported_networks":
            result = {
                "success": True,
                "networks": Config.get_supported_networks()
            }
        elif tool_name == "get_network_status":
            result = await network_tools.get_network_info(args.get("network"))
        elif tool_name == "get_gas_price":
            result = await network_tools.get_gas_price(args.get("network"))
        elif tool_name == "convert_units":
            result = await network_tools.convert_units(
                args["amount"],
                args["from_unit"],
                args["to_unit"]
            )
        elif tool_name == "validate_address":
            result = await network_tools.validate_address(args["address"])
        
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        return [types.TextContent(type="text", text=str(result))]
        
    except Exception as e:
        logger.error(f"Error calling tool {request.params.name}: {e}")
        error_result = {
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        }
        return [types.TextContent(type="text", text=str(error_result))]

async def main():
    """主函数"""
    # 初始化 Web3 连接
    logger.info("Initializing EVM MCP Server...")
    
    # 连接到配置的网络
    for network_name in Config.NETWORKS.keys():
        try:
            await web3_manager.connect_to_network(network_name)
            logger.info(f"Connected to {network_name}")
        except Exception as e:
            logger.warning(f"Failed to connect to {network_name}: {e}")
    
    # 启动服务器
    logger.info("Starting MCP server...")
    
    # 运行服务器
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="evm-mcp-server",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())