"""
Web3 连接管理器
"""

from typing import Dict, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
import logging
from .config import Config

logger = logging.getLogger(__name__)

class Web3Manager:
    """Web3 连接管理器"""
    
    def __init__(self):
        self._connections: Dict[str, Web3] = {}
        self._initialize_connections()
    
    def _initialize_connections(self):
        """初始化所有网络连接"""
        for network, config in Config.NETWORKS.items():
            try:
                w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
                
                # 为 BSC 和 Polygon 添加 POA 中间件
                if network in ["bsc", "polygon"]:
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                if w3.is_connected():
                    self._connections[network] = w3
                    logger.info(f"成功连接到 {config['name']} 网络")
                else:
                    logger.warning(f"无法连接到 {config['name']} 网络")
                    
            except Exception as e:
                logger.error(f"连接 {config['name']} 网络时出错: {e}")
    
    def get_web3(self, network: str = None) -> Optional[Web3]:
        """获取指定网络的 Web3 实例"""
        if network is None:
            network = Config.DEFAULT_NETWORK
        
        network = network.lower()
        return self._connections.get(network)
    
    def is_connected(self, network: str = None) -> bool:
        """检查网络连接状态"""
        w3 = self.get_web3(network)
        return w3 is not None and w3.is_connected()
    
    def get_chain_id(self, network: str = None) -> Optional[int]:
        """获取链 ID"""
        w3 = self.get_web3(network)
        if w3:
            try:
                return w3.eth.chain_id
            except Exception as e:
                logger.error(f"获取链 ID 失败: {e}")
        return None
    
    def get_latest_block_number(self, network: str = None) -> Optional[int]:
        """获取最新区块号"""
        w3 = self.get_web3(network)
        if w3:
            try:
                return w3.eth.block_number
            except Exception as e:
                logger.error(f"获取最新区块号失败: {e}")
        return None
    
    def get_connected_networks(self) -> list:
        """获取已连接的网络列表"""
        return list(self._connections.keys())
    
    def reconnect(self, network: str = None):
        """重新连接指定网络"""
        if network is None:
            # 重新连接所有网络
            self._connections.clear()
            self._initialize_connections()
        else:
            network = network.lower()
            if network in Config.NETWORKS:
                config = Config.NETWORKS[network]
                try:
                    w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
                    
                    if network in ["bsc", "polygon"]:
                        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    
                    if w3.is_connected():
                        self._connections[network] = w3
                        logger.info(f"重新连接到 {config['name']} 网络成功")
                    else:
                        logger.warning(f"重新连接到 {config['name']} 网络失败")
                        
                except Exception as e:
                    logger.error(f"重新连接 {config['name']} 网络时出错: {e}")

# 全局 Web3 管理器实例
web3_manager = Web3Manager()