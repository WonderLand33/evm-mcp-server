"""
配置管理模块
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # RPC 节点配置
    ETHEREUM_RPC_URL = os.getenv("ETHEREUM_RPC_URL", "https://eth.llamarpc.com")
    POLYGON_RPC_URL = os.getenv("POLYGON_RPC_URL", "https://polygon.llamarpc.com")
    BSC_RPC_URL = os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org/")
    ARBITRUM_RPC_URL = os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc")
    OPTIMISM_RPC_URL = os.getenv("OPTIMISM_RPC_URL", "https://mainnet.optimism.io")
    
    # API 密钥
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")
    
    # 服务配置
    DEFAULT_NETWORK = os.getenv("DEFAULT_NETWORK", "ethereum")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
    
    # 网络配置映射
    NETWORKS = {
        "ethereum": {
            "name": "Ethereum Mainnet",
            "chain_id": 1,
            "rpc_url": ETHEREUM_RPC_URL,
            "explorer": "https://etherscan.io",
            "explorer_api": "https://api.etherscan.io/api",
            "native_token": "ETH"
        },
        "polygon": {
            "name": "Polygon",
            "chain_id": 137,
            "rpc_url": POLYGON_RPC_URL,
            "explorer": "https://polygonscan.com",
            "explorer_api": "https://api.polygonscan.com/api",
            "native_token": "MATIC"
        },
        "bsc": {
            "name": "Binance Smart Chain",
            "chain_id": 56,
            "rpc_url": BSC_RPC_URL,
            "explorer": "https://bscscan.com",
            "explorer_api": "https://api.bscscan.com/api",
            "native_token": "BNB"
        },
        "arbitrum": {
            "name": "Arbitrum One",
            "chain_id": 42161,
            "rpc_url": ARBITRUM_RPC_URL,
            "explorer": "https://arbiscan.io",
            "explorer_api": "https://api.arbiscan.io/api",
            "native_token": "ETH"
        },
        "optimism": {
            "name": "Optimism",
            "chain_id": 10,
            "rpc_url": OPTIMISM_RPC_URL,
            "explorer": "https://optimistic.etherscan.io",
            "explorer_api": "https://api-optimistic.etherscan.io/api",
            "native_token": "ETH"
        }
    }
    
    @classmethod
    def get_network_config(cls, network: str) -> Optional[Dict]:
        """获取网络配置"""
        return cls.NETWORKS.get(network.lower())
    
    @classmethod
    def get_supported_networks(cls) -> list:
        """获取支持的网络列表"""
        return list(cls.NETWORKS.keys())
    
    @classmethod
    def validate_network(cls, network: str) -> bool:
        """验证网络是否支持"""
        return network.lower() in cls.NETWORKS