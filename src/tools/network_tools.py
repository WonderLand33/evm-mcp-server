"""
网络和工具相关功能
"""

from typing import Dict, Union, Optional, Any
import logging
from decimal import Decimal
from web3 import Web3

from ..config import Config

logger = logging.getLogger(__name__)

class NetworkTools:
    """网络和工具相关功能类"""
    
    def __init__(self, web3_manager):
        self.web3_manager = web3_manager
    
    async def get_network_info(self, network: Optional[str] = None) -> Dict[str, Any]:
        """
        获取网络状态信息
        
        Args:
            network: 网络名称
            
        Returns:
            包含网络信息的字典
        """
        try:
            if network:
                # 获取指定网络信息
                if network not in Config.NETWORKS:
                    return {
                        "success": False,
                        "error": f"不支持的网络: {network}"
                    }
                
                w3 = await self.web3_manager.get_web3(network)
                network_config = Config.NETWORKS[network]
                
                if not w3:
                    return {
                        "success": False,
                        "error": f"无法连接到网络: {network}"
                    }
                
                try:
                    chain_id = w3.eth.chain_id
                    latest_block = w3.eth.get_block('latest')
                    gas_price = w3.eth.gas_price
                    
                    return {
                        "success": True,
                        "data": {
                            "network": network,
                            "config": network_config,
                            "status": {
                                "connected": True,
                                "chain_id": chain_id,
                                "latest_block": latest_block.number,
                                "gas_price": {
                                    "wei": gas_price,
                                    "gwei": float(Web3.from_wei(gas_price, 'gwei')),
                                    "ether": float(Web3.from_wei(gas_price, 'ether'))
                                }
                            }
                        }
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"获取网络状态失败: {str(e)}"
                    }
            
            else:
                # 获取所有网络信息
                all_networks = {}
                connected_count = 0
                
                for net_name in Config.NETWORKS.keys():
                    w3 = await self.web3_manager.get_web3(net_name)
                    network_config = Config.NETWORKS[net_name]
                    
                    if w3:
                        try:
                            chain_id = w3.eth.chain_id
                            latest_block = w3.eth.get_block('latest')
                            gas_price = w3.eth.gas_price
                            
                            all_networks[net_name] = {
                                "config": network_config,
                                "status": {
                                    "connected": True,
                                    "chain_id": chain_id,
                                    "latest_block": latest_block.number,
                                    "gas_price": {
                                        "wei": gas_price,
                                        "gwei": float(Web3.from_wei(gas_price, 'gwei')),
                                        "ether": float(Web3.from_wei(gas_price, 'ether'))
                                    }
                                }
                            }
                            connected_count += 1
                            
                        except Exception as e:
                            all_networks[net_name] = {
                                "config": network_config,
                                "status": {
                                    "connected": False,
                                    "error": str(e)
                                }
                            }
                    else:
                        all_networks[net_name] = {
                            "config": network_config,
                            "status": {
                                "connected": False,
                                "error": "连接失败"
                            }
                        }
                
                return {
                    "success": True,
                    "data": {
                        "summary": {
                            "total_networks": len(Config.NETWORKS),
                            "connected_networks": connected_count
                        },
                        "networks": all_networks
                    }
                }
                
        except Exception as e:
            logger.error(f"获取网络信息时出错: {e}")
            return {
                "success": False,
                "error": f"获取网络信息失败: {str(e)}"
            }
    
    async def get_gas_price(self, network: str = "ethereum") -> Dict[str, Any]:
        """
        获取当前 Gas 价格
        
        Args:
            network: 网络名称
            
        Returns:
            包含 Gas 价格信息的字典
        """
        try:
            w3 = await self.web3_manager.get_web3(network)
            if not w3:
                return {
                    "success": False,
                    "error": f"无法连接到网络: {network}"
                }
            
            network_config = Config.NETWORKS.get(network, {})
            
            # 获取当前 Gas 价格
            gas_price = w3.eth.gas_price
            
            # 尝试获取 EIP-1559 费用信息（如果支持）
            fee_history = None
            try:
                # 获取最近 4 个区块的费用历史
                fee_history = w3.eth.fee_history(4, 'latest', [25, 50, 75])
            except Exception:
                pass  # 不是所有网络都支持 EIP-1559
            
            result = {
                "network": network,
                "native_token": network_config.get("native_token", "ETH"),
                "legacy_gas_price": {
                    "wei": gas_price,
                    "gwei": float(Web3.from_wei(gas_price, 'gwei')),
                    "ether": float(Web3.from_wei(gas_price, 'ether'))
                }
            }
            
            if fee_history:
                # 计算建议的费用
                base_fees = fee_history.get('baseFeePerGas', [])
                if base_fees:
                    latest_base_fee = base_fees[-1]
                    
                    # 建议的优先费用（通常是 1-2 Gwei）
                    priority_fee_suggestions = {
                        "slow": Web3.to_wei(1, 'gwei'),
                        "standard": Web3.to_wei(1.5, 'gwei'),
                        "fast": Web3.to_wei(2, 'gwei')
                    }
                    
                    result["eip1559"] = {
                        "base_fee": {
                            "wei": latest_base_fee,
                            "gwei": float(Web3.from_wei(latest_base_fee, 'gwei')),
                            "ether": float(Web3.from_wei(latest_base_fee, 'ether'))
                        },
                        "priority_fee_suggestions": {
                            speed: {
                                "wei": fee,
                                "gwei": float(Web3.from_wei(fee, 'gwei')),
                                "ether": float(Web3.from_wei(fee, 'ether'))
                            }
                            for speed, fee in priority_fee_suggestions.items()
                        },
                        "max_fee_suggestions": {
                            speed: {
                                "wei": latest_base_fee * 2 + fee,
                                "gwei": float(Web3.from_wei(latest_base_fee * 2 + fee, 'gwei')),
                                "ether": float(Web3.from_wei(latest_base_fee * 2 + fee, 'ether'))
                            }
                            for speed, fee in priority_fee_suggestions.items()
                        }
                    }
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            logger.error(f"获取 Gas 价格时出错: {e}")
            return {
                "success": False,
                "error": f"获取 Gas 价格失败: {str(e)}"
            }
    
    async def convert_units(self, amount: Union[str, float, int], from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        单位转换（Wei, Gwei, Ether）
        
        Args:
            amount: 数量
            from_unit: 源单位 (wei, gwei, ether)
            to_unit: 目标单位 (wei, gwei, ether)
            
        Returns:
            包含转换结果的字典
        """
        try:
            from_unit = from_unit.lower()
            to_unit = to_unit.lower()
            
            # 支持的单位
            supported_units = ['wei', 'gwei', 'ether']
            
            if from_unit not in supported_units:
                return {
                    "success": False,
                    "error": f"不支持的源单位: {from_unit}。支持的单位: {supported_units}"
                }
            
            if to_unit not in supported_units:
                return {
                    "success": False,
                    "error": f"不支持的目标单位: {to_unit}。支持的单位: {supported_units}"
                }
            
            # 转换为 Decimal 以保持精度
            amount_decimal = Decimal(str(amount))
            
            # 先转换为 Wei（基础单位）
            if from_unit == 'wei':
                wei_amount = int(amount_decimal)
            elif from_unit == 'gwei':
                wei_amount = Web3.to_wei(amount_decimal, 'gwei')
            elif from_unit == 'ether':
                wei_amount = Web3.to_wei(amount_decimal, 'ether')
            
            # 再从 Wei 转换为目标单位
            if to_unit == 'wei':
                result = str(wei_amount)
            elif to_unit == 'gwei':
                result = str(Web3.from_wei(wei_amount, 'gwei'))
            elif to_unit == 'ether':
                result = str(Web3.from_wei(wei_amount, 'ether'))
            
            return {
                "success": True,
                "data": {
                    "original": {
                        "amount": str(amount),
                        "unit": from_unit
                    },
                    "converted": {
                        "amount": result,
                        "unit": to_unit
                    },
                    "all_units": {
                        "wei": str(wei_amount),
                        "gwei": str(Web3.from_wei(wei_amount, 'gwei')),
                        "ether": str(Web3.from_wei(wei_amount, 'ether'))
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"单位转换时出错: {e}")
            return {
                "success": False,
                "error": f"单位转换失败: {str(e)}"
            }
    
    async def validate_address(self, address: str) -> Dict[str, Any]:
        """
        验证以太坊地址格式
        
        Args:
            address: 以太坊地址
            
        Returns:
            包含验证结果的字典
        """
        try:
            is_valid = Web3.is_address(address)
            
            result = {
                "address": address,
                "is_valid": is_valid
            }
            
            if is_valid:
                checksum_address = Web3.to_checksum_address(address)
                
                result.update({
                    "checksum_address": checksum_address,
                    "is_checksum": address == checksum_address,
                    "format_info": {
                        "length": len(address),
                        "has_0x_prefix": address.startswith('0x'),
                        "is_lowercase": address.islower(),
                        "is_uppercase": address.isupper()
                    }
                })
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            logger.error(f"验证地址时出错: {e}")
            return {
                "success": False,
                "error": f"地址验证失败: {str(e)}"
            }