"""
账户和余额相关工具
"""

from typing import Dict, List, Optional, Union
from decimal import Decimal
import logging
from web3 import Web3
from web3.exceptions import Web3Exception

from ..web3_manager import web3_manager
from ..utils import (
    validate_ethereum_address, 
    to_checksum, 
    wei_to_ether, 
    format_token_amount,
    is_contract_address
)
from ..config import Config

logger = logging.getLogger(__name__)

class AccountTools:
    """账户相关工具类"""
    
    # ERC20 标准 ABI（简化版）
    ERC20_ABI = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        }
    ]
    
    @staticmethod
    def get_balance(address: str, network: str = None) -> Dict:
        """
        查询地址的 ETH 余额
        
        Args:
            address: 以太坊地址
            network: 网络名称
            
        Returns:
            包含余额信息的字典
        """
        try:
            # 验证地址
            if not validate_ethereum_address(address):
                return {
                    "success": False,
                    "error": "无效的以太坊地址"
                }
            
            # 获取 Web3 实例
            w3 = web3_manager.get_web3(network)
            if not w3:
                return {
                    "success": False,
                    "error": f"无法连接到网络: {network or Config.DEFAULT_NETWORK}"
                }
            
            # 获取网络配置
            network_config = Config.get_network_config(network or Config.DEFAULT_NETWORK)
            
            # 转换为校验和地址
            checksum_address = to_checksum(address)
            
            # 查询余额
            balance_wei = w3.eth.get_balance(checksum_address)
            balance_ether = wei_to_ether(balance_wei)
            
            return {
                "success": True,
                "data": {
                    "address": checksum_address,
                    "network": network or Config.DEFAULT_NETWORK,
                    "native_token": network_config["native_token"],
                    "balance": {
                        "wei": str(balance_wei),
                        "ether": str(balance_ether),
                        "formatted": f"{balance_ether:.6f} {network_config['native_token']}"
                    },
                    "is_contract": is_contract_address(w3, checksum_address)
                }
            }
            
        except Web3Exception as e:
            logger.error(f"Web3 错误: {e}")
            return {
                "success": False,
                "error": f"区块链查询错误: {str(e)}"
            }
        except Exception as e:
            logger.error(f"查询余额时出错: {e}")
            return {
                "success": False,
                "error": f"查询失败: {str(e)}"
            }
    
    @staticmethod
    def get_token_balance(address: str, token_address: str, network: str = None) -> Dict:
        """
        查询地址的 ERC20 代币余额
        
        Args:
            address: 持有者地址
            token_address: 代币合约地址
            network: 网络名称
            
        Returns:
            包含代币余额信息的字典
        """
        try:
            # 验证地址
            if not validate_ethereum_address(address):
                return {
                    "success": False,
                    "error": "无效的持有者地址"
                }
            
            if not validate_ethereum_address(token_address):
                return {
                    "success": False,
                    "error": "无效的代币合约地址"
                }
            
            # 获取 Web3 实例
            w3 = web3_manager.get_web3(network)
            if not w3:
                return {
                    "success": False,
                    "error": f"无法连接到网络: {network or Config.DEFAULT_NETWORK}"
                }
            
            # 转换为校验和地址
            checksum_address = to_checksum(address)
            checksum_token_address = to_checksum(token_address)
            
            # 创建合约实例
            contract = w3.eth.contract(
                address=checksum_token_address,
                abi=AccountTools.ERC20_ABI
            )
            
            # 查询代币信息
            try:
                name = contract.functions.name().call()
                symbol = contract.functions.symbol().call()
                decimals = contract.functions.decimals().call()
                balance_raw = contract.functions.balanceOf(checksum_address).call()
                
                # 格式化余额
                balance_formatted = format_token_amount(balance_raw, decimals)
                
                return {
                    "success": True,
                    "data": {
                        "holder_address": checksum_address,
                        "token_address": checksum_token_address,
                        "network": network or Config.DEFAULT_NETWORK,
                        "token_info": {
                            "name": name,
                            "symbol": symbol,
                            "decimals": decimals
                        },
                        "balance": {
                            "raw": str(balance_raw),
                            "formatted": str(balance_formatted),
                            "display": f"{balance_formatted:.6f} {symbol}"
                        }
                    }
                }
                
            except Exception as contract_error:
                return {
                    "success": False,
                    "error": f"合约调用失败: {str(contract_error)}"
                }
            
        except Web3Exception as e:
            logger.error(f"Web3 错误: {e}")
            return {
                "success": False,
                "error": f"区块链查询错误: {str(e)}"
            }
        except Exception as e:
            logger.error(f"查询代币余额时出错: {e}")
            return {
                "success": False,
                "error": f"查询失败: {str(e)}"
            }
    
    @staticmethod
    def get_account_info(address: str, network: str = None) -> Dict:
        """
        获取账户综合信息
        
        Args:
            address: 以太坊地址
            network: 网络名称
            
        Returns:
            包含账户综合信息的字典
        """
        try:
            # 验证地址
            if not validate_ethereum_address(address):
                return {
                    "success": False,
                    "error": "无效的以太坊地址"
                }
            
            # 获取 Web3 实例
            w3 = web3_manager.get_web3(network)
            if not w3:
                return {
                    "success": False,
                    "error": f"无法连接到网络: {network or Config.DEFAULT_NETWORK}"
                }
            
            # 获取网络配置
            network_config = Config.get_network_config(network or Config.DEFAULT_NETWORK)
            
            # 转换为校验和地址
            checksum_address = to_checksum(address)
            
            # 获取基本信息
            balance_wei = w3.eth.get_balance(checksum_address)
            balance_ether = wei_to_ether(balance_wei)
            nonce = w3.eth.get_transaction_count(checksum_address)
            is_contract = is_contract_address(w3, checksum_address)
            
            # 获取代码（如果是合约）
            code = None
            if is_contract:
                try:
                    code_bytes = w3.eth.get_code(checksum_address)
                    code = code_bytes.hex() if code_bytes else None
                except Exception:
                    pass
            
            return {
                "success": True,
                "data": {
                    "address": checksum_address,
                    "network": network or Config.DEFAULT_NETWORK,
                    "network_info": network_config,
                    "account_type": "contract" if is_contract else "externally_owned",
                    "balance": {
                        "wei": str(balance_wei),
                        "ether": str(balance_ether),
                        "formatted": f"{balance_ether:.6f} {network_config['native_token']}"
                    },
                    "nonce": nonce,
                    "is_contract": is_contract,
                    "contract_code": code[:100] + "..." if code and len(code) > 100 else code
                }
            }
            
        except Web3Exception as e:
            logger.error(f"Web3 错误: {e}")
            return {
                "success": False,
                "error": f"区块链查询错误: {str(e)}"
            }
        except Exception as e:
            logger.error(f"查询账户信息时出错: {e}")
            return {
                "success": False,
                "error": f"查询失败: {str(e)}"
            }