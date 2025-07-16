"""
ENS (Ethereum Name Service) 工具
提供 ENS 域名解析和反向解析功能
"""

import logging
from typing import Optional, Dict, Any
from ens import ENS
from web3 import Web3
from ..web3_manager import Web3Manager
from ..utils import is_valid_address, to_checksum_address
from ..config import Config

logger = logging.getLogger(__name__)

class ENSTools:
    """ENS 相关工具类"""
    
    def __init__(self, web3_manager: Web3Manager):
        self.web3_manager = web3_manager
        self._ens_instances = {}
    
    def _get_ens_instance(self, network: str = "ethereum") -> Optional[ENS]:
        """获取 ENS 实例"""
        try:
            # 检查网络是否支持 ENS
            network_config = Config.get_network_config(network)
            if not network_config or not network_config.get("supports_ens", False):
                logger.warning(f"Network {network} does not support ENS")
                return None
            
            # 缓存 ENS 实例
            if network not in self._ens_instances:
                w3 = self.web3_manager.get_web3(network)
                if w3 and w3.is_connected():
                    self._ens_instances[network] = ENS.from_web3(w3)
                else:
                    logger.error(f"Web3 connection not available for network: {network}")
                    return None
            
            return self._ens_instances[network]
        except Exception as e:
            logger.error(f"Error getting ENS instance for {network}: {e}")
            return None
    
    async def resolve_name(self, name: str, network: str = "ethereum") -> Dict[str, Any]:
        """
        解析 ENS 域名到地址
        
        Args:
            name: ENS 域名 (例如: vitalik.eth)
            network: 网络名称
            
        Returns:
            包含解析结果的字典
        """
        try:
            ens = self._get_ens_instance(network)
            if not ens:
                return {
                    "success": False,
                    "error": f"ENS not supported on network: {network}"
                }
            
            # 解析域名
            address = ens.address(name)
            
            if address:
                result = {
                    "success": True,
                    "name": name,
                    "address": to_checksum_address(address),
                    "network": network
                }
                
                # 尝试获取其他记录
                try:
                    # 获取文本记录
                    avatar = ens.get_text(name, "avatar")
                    email = ens.get_text(name, "email")
                    url = ens.get_text(name, "url")
                    description = ens.get_text(name, "description")
                    twitter = ens.get_text(name, "com.twitter")
                    github = ens.get_text(name, "com.github")
                    
                    records = {}
                    if avatar:
                        records["avatar"] = avatar
                    if email:
                        records["email"] = email
                    if url:
                        records["url"] = url
                    if description:
                        records["description"] = description
                    if twitter:
                        records["twitter"] = twitter
                    if github:
                        records["github"] = github
                    
                    if records:
                        result["records"] = records
                        
                except Exception as e:
                    logger.debug(f"Could not fetch text records for {name}: {e}")
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"ENS name '{name}' not found or not resolved"
                }
                
        except Exception as e:
            logger.error(f"Error resolving ENS name {name}: {e}")
            return {
                "success": False,
                "error": f"Failed to resolve ENS name: {str(e)}"
            }
    
    async def reverse_resolve(self, address: str, network: str = "ethereum") -> Dict[str, Any]:
        """
        反向解析地址到 ENS 域名
        
        Args:
            address: 以太坊地址
            network: 网络名称
            
        Returns:
            包含反向解析结果的字典
        """
        try:
            # 验证地址
            if not is_valid_address(address):
                return {
                    "success": False,
                    "error": "Invalid Ethereum address"
                }
            
            ens = self._get_ens_instance(network)
            if not ens:
                return {
                    "success": False,
                    "error": f"ENS not supported on network: {network}"
                }
            
            # 反向解析
            checksum_address = to_checksum_address(address)
            name = ens.name(checksum_address)
            
            if name:
                # 验证正向解析是否匹配
                forward_address = ens.address(name)
                if forward_address and to_checksum_address(forward_address) == checksum_address:
                    return {
                        "success": True,
                        "address": checksum_address,
                        "name": name,
                        "network": network,
                        "verified": True
                    }
                else:
                    return {
                        "success": True,
                        "address": checksum_address,
                        "name": name,
                        "network": network,
                        "verified": False,
                        "warning": "Forward resolution does not match"
                    }
            else:
                return {
                    "success": False,
                    "error": f"No ENS name found for address {checksum_address}"
                }
                
        except Exception as e:
            logger.error(f"Error reverse resolving address {address}: {e}")
            return {
                "success": False,
                "error": f"Failed to reverse resolve address: {str(e)}"
            }
    
    async def get_content_hash(self, name: str, network: str = "ethereum") -> Dict[str, Any]:
        """
        获取 ENS 域名的内容哈希
        
        Args:
            name: ENS 域名
            network: 网络名称
            
        Returns:
            包含内容哈希的字典
        """
        try:
            ens = self._get_ens_instance(network)
            if not ens:
                return {
                    "success": False,
                    "error": f"ENS not supported on network: {network}"
                }
            
            # 获取内容哈希
            content_hash = ens.get_text(name, "contenthash")
            
            return {
                "success": True,
                "name": name,
                "content_hash": content_hash,
                "network": network
            }
            
        except Exception as e:
            logger.error(f"Error getting content hash for {name}: {e}")
            return {
                "success": False,
                "error": f"Failed to get content hash: {str(e)}"
            }
    
    async def get_all_records(self, name: str, network: str = "ethereum") -> Dict[str, Any]:
        """
        获取 ENS 域名的所有记录
        
        Args:
            name: ENS 域名
            network: 网络名称
            
        Returns:
            包含所有记录的字典
        """
        try:
            ens = self._get_ens_instance(network)
            if not ens:
                return {
                    "success": False,
                    "error": f"ENS not supported on network: {network}"
                }
            
            # 基本解析
            address = ens.address(name)
            if not address:
                return {
                    "success": False,
                    "error": f"ENS name '{name}' not found"
                }
            
            result = {
                "success": True,
                "name": name,
                "address": to_checksum_address(address),
                "network": network,
                "records": {}
            }
            
            # 常见的文本记录
            text_records = [
                "avatar", "email", "url", "description", "notice",
                "com.twitter", "com.github", "com.discord", "com.reddit",
                "org.telegram", "contenthash"
            ]
            
            for record in text_records:
                try:
                    value = ens.get_text(name, record)
                    if value:
                        result["records"][record] = value
                except Exception as e:
                    logger.debug(f"Could not fetch {record} for {name}: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting all records for {name}: {e}")
            return {
                "success": False,
                "error": f"Failed to get records: {str(e)}"
            }