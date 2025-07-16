"""
EVM MCP 服务器主程序
"""

import asyncio
import logging
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from .tools import AccountTools, TokenTools
from .config import Config
from .web3_manager import web3_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EVMMCPServer:
    """EVM MCP 服务器"""
    
    def __init__(self):
        self.server = Server("evm-mcp-server")
        self._setup_tools()
        self._setup_resources()
    
    def _setup_tools(self):
        """设置工具"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """返回可用工具列表"""
            return [
                Tool(
                    name="get_balance",
                    description="查询地址的 ETH 余额",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "address": {
                                "type": "string",
                                "description": "以太坊地址"
                            },
                            "network": {
                                "type": "string",
                                "description": "网络名称 (ethereum, polygon, bsc, arbitrum, optimism)",
                                "default": Config.DEFAULT_NETWORK
                            }
                        },
                        "required": ["address"]
                    }
                ),
                Tool(
                    name="get_token_balance",
                    description="查询地址的 ERC20 代币余额",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "address": {
                                "type": "string",
                                "description": "持有者地址"
                            },
                            "token_address": {
                                "type": "string",
                                "description": "代币合约地址"
                            },
                            "network": {
                                "type": "string",
                                "description": "网络名称",
                                "default": Config.DEFAULT_NETWORK
                            }
                        },
                        "required": ["address", "token_address"]
                    }
                ),
                Tool(
                    name="get_account_info",
                    description="获取账户综合信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "address": {
                                "type": "string",
                                "description": "以太坊地址"
                            },
                            "network": {
                                "type": "string",
                                "description": "网络名称",
                                "default": Config.DEFAULT_NETWORK
                            }
                        },
                        "required": ["address"]
                    }
                ),
                Tool(
                    name="get_token_metadata",
                    description="查询代币元数据（名称、符号、精度等）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "token_address": {
                                "type": "string",
                                "description": "代币合约地址"
                            },
                            "network": {
                                "type": "string",
                                "description": "网络名称",
                                "default": Config.DEFAULT_NETWORK
                            }
                        },
                        "required": ["token_address"]
                    }
                ),
                Tool(
                    name="get_token_price",
                    description="查询代币当前价格",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "token_symbol": {
                                "type": "string",
                                "description": "代币符号 (如 BTC, ETH, USDT)"
                            },
                            "vs_currency": {
                                "type": "string",
                                "description": "对比货币",
                                "default": "usd"
                            }
                        },
                        "required": ["token_symbol"]
                    }
                ),
                Tool(
                    name="search_tokens",
                    description="搜索代币信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索关键词"
                            },
                            "network": {
                                "type": "string",
                                "description": "网络名称",
                                "default": "all"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量限制",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_supported_networks",
                    description="获取支持的网络列表",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_network_status",
                    description="获取网络连接状态",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "network": {
                                "type": "string",
                                "description": "网络名称（可选，不提供则检查所有网络）"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """处理工具调用"""
            try:
                if name == "get_balance":
                    result = AccountTools.get_balance(
                        arguments["address"],
                        arguments.get("network")
                    )
                
                elif name == "get_token_balance":
                    result = AccountTools.get_token_balance(
                        arguments["address"],
                        arguments["token_address"],
                        arguments.get("network")
                    )
                
                elif name == "get_account_info":
                    result = AccountTools.get_account_info(
                        arguments["address"],
                        arguments.get("network")
                    )
                
                elif name == "get_token_metadata":
                    result = TokenTools.get_token_metadata(
                        arguments["token_address"],
                        arguments.get("network")
                    )
                
                elif name == "get_token_price":
                    result = TokenTools.get_token_price(
                        arguments["token_symbol"],
                        arguments.get("vs_currency", "usd")
                    )
                
                elif name == "search_tokens":
                    result = TokenTools.search_tokens(
                        arguments["query"],
                        arguments.get("network"),
                        arguments.get("limit", 10)
                    )
                
                elif name == "get_supported_networks":
                    result = {
                        "success": True,
                        "data": {
                            "networks": Config.get_supported_networks(),
                            "default_network": Config.DEFAULT_NETWORK,
                            "network_details": Config.NETWORKS
                        }
                    }
                
                elif name == "get_network_status":
                    network = arguments.get("network")
                    if network:
                        status = {
                            "network": network,
                            "connected": web3_manager.is_connected(network),
                            "chain_id": web3_manager.get_chain_id(network),
                            "latest_block": web3_manager.get_latest_block_number(network)
                        }
                    else:
                        connected_networks = web3_manager.get_connected_networks()
                        status = {
                            "connected_networks": connected_networks,
                            "total_supported": len(Config.NETWORKS),
                            "details": {
                                net: {
                                    "connected": web3_manager.is_connected(net),
                                    "chain_id": web3_manager.get_chain_id(net),
                                    "latest_block": web3_manager.get_latest_block_number(net)
                                }
                                for net in Config.NETWORKS.keys()
                            }
                        }
                    
                    result = {
                        "success": True,
                        "data": status
                    }
                
                else:
                    result = {
                        "success": False,
                        "error": f"未知工具: {name}"
                    }
                
                # 格式化返回结果
                if result["success"]:
                    content = f"✅ 操作成功\\n\\n```json\\n{result}\\n```"
                else:
                    content = f"❌ 操作失败: {result['error']}\\n\\n```json\\n{result}\\n```"
                
                return [TextContent(type="text", text=content)]
                
            except Exception as e:
                logger.error(f"工具调用错误 {name}: {e}")
                error_content = f"❌ 工具调用失败: {str(e)}"
                return [TextContent(type="text", text=error_content)]
    
    def _setup_resources(self):
        """设置资源"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """返回可用资源列表"""
            return [
                Resource(
                    uri="evm://networks",
                    name="支持的网络列表",
                    description="获取所有支持的 EVM 网络信息",
                    mimeType="application/json"
                ),
                Resource(
                    uri="evm://status",
                    name="服务器状态",
                    description="获取 EVM MCP 服务器当前状态",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """读取资源内容"""
            if uri == "evm://networks":
                return {
                    "networks": Config.NETWORKS,
                    "default_network": Config.DEFAULT_NETWORK,
                    "supported_count": len(Config.NETWORKS)
                }
            
            elif uri == "evm://status":
                connected_networks = web3_manager.get_connected_networks()
                return {
                    "server_name": "EVM MCP Server",
                    "version": "1.0.0",
                    "connected_networks": connected_networks,
                    "total_networks": len(Config.NETWORKS),
                    "default_network": Config.DEFAULT_NETWORK,
                    "cache_ttl": Config.CACHE_TTL,
                    "rate_limit": Config.RATE_LIMIT
                }
            
            else:
                raise ValueError(f"未知资源: {uri}")
    
    async def run(self):
        """运行服务器"""
        logger.info("启动 EVM MCP 服务器...")
        
        # 检查网络连接
        connected_networks = web3_manager.get_connected_networks()
        logger.info(f"已连接网络: {connected_networks}")
        
        if not connected_networks:
            logger.warning("警告: 没有成功连接到任何网络")
        
        # 启动服务器
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="evm-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )

def main():
    """主函数"""
    server = EVMMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()