"""
网络和工具相关功能
"""

from typing import Dict, Union
import logging
from decimal import Decimal

from ..web3_manager import web3_manager
from ..utils import (
    validate_ethereum_address,
    wei_to_ether,
    ether_to_wei,
    gwei_to_wei,
    wei_to_gwei,
    format_gas_price
)
from ..config import Config

logger = logging.getLogger(__name__)

class NetworkTools:
    """网络和工具相关功能类"""
    
    @staticmethod
    def get_network_info(network: str = None) -> Dict:
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
                if not Config.validate_network(network):
                    return {
                        "success": False,
                        "error": f"不支持的网络: {network}"
                    }
                
                w3 = web3_manager.get_web3(network)
                network_config = Config.get_network_config(network)
                
                if not w3:
                    return {
                        "success": False,
                        "error": f"无法连接到网络: {network}"
                    }
                
                try:
                    chain_id = w3.eth.chain_id
                    latest_block = w3.eth.block_number
                    gas_price = w3.eth.gas_price
                    
                    return {
                        "success": True,
                        "data": {
                            "network": network,
                            "config": network_config,
                            "status": {
                                "connected": True,
                                "chain_id": chain_id,
                                "latest_block": latest_block,
                                "gas_price": format_gas_price(gas_price)
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
                    w3 = web3_manager.get_web3(net_name)
                    network_config = Config.get_network_config(net_name)
                    
                    if w3 and w3.is_connected():
                        try:
                            chain_id = w3.eth.chain_id
                            latest_block = w3.eth.block_number
                            gas_price = w3.eth.gas_price
                            
                            all_networks[net_name] = {
                                "config": network_config,
                                "status": {
                                    "connected": True,
                                    "chain_id": chain_id,
                                    "latest_block": latest_block,
                                    "gas_price": format_gas_price(gas_price)
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
                            "connected_networks": connected_count,
                            "default_network": Config.DEFAULT_NETWORK
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
    
    @staticmethod
    def get_gas_price(network: str = None) -> Dict:
        """
        获取当前 Gas 价格
        
        Args:
            network: 网络名称
            
        Returns:
            包含 Gas 价格信息的字典
        """
        try:
            w3 = web3_manager.get_web3(network)
            if not w3:
                return {
                    "success": False,
                    "error": f"无法连接到网络: {network or Config.DEFAULT_NETWORK}"
                }
            
            network_config = Config.get_network_config(network or Config.DEFAULT_NETWORK)
            
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
                "network": network or Config.DEFAULT_NETWORK,
                "native_token": network_config["native_token"],
                "legacy_gas_price": format_gas_price(gas_price)
            }
            
            if fee_history:
                # 计算建议的费用
                base_fees = fee_history.get('baseFeePerGas', [])
                if base_fees:
                    latest_base_fee = base_fees[-1]
                    
                    # 建议的优先费用（通常是 1-2 Gwei）
                    priority_fee_suggestions = {
                        "slow": gwei_to_wei(1),
                        "standard": gwei_to_wei(1.5),
                        "fast": gwei_to_wei(2)
                    }
                    
                    result["eip1559"] = {
                        "base_fee": format_gas_price(latest_base_fee),
                        "priority_fee_suggestions": {
                            speed: format_gas_price(fee)
                            for speed, fee in priority_fee_suggestions.items()
                        },
                        "max_fee_suggestions": {
                            speed: format_gas_price(latest_base_fee * 2 + fee)
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
    
    @staticmethod
    def convert_units(amount: Union[str, float, int], from_unit: str, to_unit: str) -> Dict:
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
                wei_amount = int(amount_decimal * Decimal('1000000000'))
            elif from_unit == 'ether':
                wei_amount = int(amount_decimal * Decimal('1000000000000000000'))
            
            # 再从 Wei 转换为目标单位
            if to_unit == 'wei':
                result = str(wei_amount)
            elif to_unit == 'gwei':
                result = str(wei_to_gwei(wei_amount))
            elif to_unit == 'ether':
                result = str(wei_to_ether(wei_amount))
            
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
                        "gwei": str(wei_to_gwei(wei_amount)),
                        "ether": str(wei_to_ether(wei_amount))
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"单位转换时出错: {e}")
            return {
                "success": False,
                "error": f"单位转换失败: {str(e)}"
            }
    
    @staticmethod
    def validate_address(address: str) -> Dict:
        """
        验证以太坊地址格式
        
        Args:
            address: 以太坊地址
            
        Returns:
            包含验证结果的字典
        """
        try:
            is_valid = validate_ethereum_address(address)
            
            result = {
                "address": address,
                "is_valid": is_valid
            }
            
            if is_valid:
                from ..utils import to_checksum
                checksum_address = to_checksum(address)
                
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