"""
智能合约交互工具
提供合约读取、写入和部署功能
"""

import logging
import json
from typing import Optional, Dict, Any, List, Union
from web3 import Web3
from web3.contract import Contract
from eth_utils import to_checksum_address
from ..web3_manager import Web3Manager
from ..utils import is_valid_address, is_contract_address
from ..config import Config

logger = logging.getLogger(__name__)

class ContractTools:
    """智能合约工具类"""
    
    def __init__(self, web3_manager: Web3Manager):
        self.web3_manager = web3_manager
        self._contract_cache = {}
    
    def _get_contract(self, address: str, abi: List[Dict], network: str) -> Optional[Contract]:
        """获取合约实例"""
        try:
            cache_key = f"{network}:{address}"
            if cache_key not in self._contract_cache:
                w3 = self.web3_manager.get_web3(network)
                if not w3 or not w3.is_connected():
                    return None
                
                checksum_address = to_checksum_address(address)
                contract = w3.eth.contract(address=checksum_address, abi=abi)
                self._contract_cache[cache_key] = contract
            
            return self._contract_cache[cache_key]
        except Exception as e:
            logger.error(f"Error creating contract instance: {e}")
            return None
    
    async def read_contract(
        self, 
        address: str, 
        abi: Union[str, List[Dict]], 
        function_name: str, 
        args: List[Any] = None,
        network: str = None
    ) -> Dict[str, Any]:
        """
        读取智能合约函数
        
        Args:
            address: 合约地址
            abi: 合约 ABI (JSON 字符串或字典列表)
            function_name: 函数名称
            args: 函数参数列表
            network: 网络名称
            
        Returns:
            包含函数调用结果的字典
        """
        try:
            # 验证地址
            if not is_valid_address(address):
                return {
                    "success": False,
                    "error": "Invalid contract address"
                }
            
            # 解析 ABI
            if isinstance(abi, str):
                try:
                    abi = json.loads(abi)
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Invalid ABI format"
                    }
            
            # 使用默认网络
            if not network:
                network = Config.DEFAULT_NETWORK
            
            # 检查是否为合约地址
            w3 = self.web3_manager.get_web3(network)
            if not w3:
                return {
                    "success": False,
                    "error": f"Network {network} not available"
                }
            
            if not is_contract_address(address, w3):
                return {
                    "success": False,
                    "error": "Address is not a contract"
                }
            
            # 获取合约实例
            contract = self._get_contract(address, abi, network)
            if not contract:
                return {
                    "success": False,
                    "error": "Failed to create contract instance"
                }
            
            # 检查函数是否存在
            if not hasattr(contract.functions, function_name):
                return {
                    "success": False,
                    "error": f"Function '{function_name}' not found in contract"
                }
            
            # 调用函数
            if args is None:
                args = []
            
            function = getattr(contract.functions, function_name)
            result = function(*args).call()
            
            return {
                "success": True,
                "contract_address": to_checksum_address(address),
                "function_name": function_name,
                "args": args,
                "result": result,
                "network": network
            }
            
        except Exception as e:
            logger.error(f"Error reading contract function: {e}")
            return {
                "success": False,
                "error": f"Failed to read contract: {str(e)}"
            }
    
    async def get_contract_info(self, address: str, network: str = None) -> Dict[str, Any]:
        """
        获取合约基本信息
        
        Args:
            address: 合约地址
            network: 网络名称
            
        Returns:
            包含合约信息的字典
        """
        try:
            # 验证地址
            if not is_valid_address(address):
                return {
                    "success": False,
                    "error": "Invalid contract address"
                }
            
            # 使用默认网络
            if not network:
                network = Config.DEFAULT_NETWORK
            
            w3 = self.web3_manager.get_web3(network)
            if not w3:
                return {
                    "success": False,
                    "error": f"Network {network} not available"
                }
            
            checksum_address = to_checksum_address(address)
            
            # 检查是否为合约
            code = w3.eth.get_code(checksum_address)
            if code == b'':
                return {
                    "success": False,
                    "error": "Address is not a contract"
                }
            
            # 获取合约信息
            result = {
                "success": True,
                "address": checksum_address,
                "network": network,
                "is_contract": True,
                "code_size": len(code),
                "code_hash": w3.keccak(code).hex()
            }
            
            # 尝试获取余额
            try:
                balance = w3.eth.get_balance(checksum_address)
                result["balance"] = {
                    "wei": str(balance),
                    "ether": str(w3.from_wei(balance, 'ether'))
                }
            except Exception as e:
                logger.debug(f"Could not get balance for contract {address}: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting contract info: {e}")
            return {
                "success": False,
                "error": f"Failed to get contract info: {str(e)}"
            }
    
    async def estimate_gas(
        self,
        address: str,
        abi: Union[str, List[Dict]],
        function_name: str,
        args: List[Any] = None,
        from_address: str = None,
        value: int = 0,
        network: str = None
    ) -> Dict[str, Any]:
        """
        估算合约函数调用的 Gas 费用
        
        Args:
            address: 合约地址
            abi: 合约 ABI
            function_name: 函数名称
            args: 函数参数
            from_address: 调用者地址
            value: 发送的 ETH 数量 (wei)
            network: 网络名称
            
        Returns:
            包含 Gas 估算的字典
        """
        try:
            # 验证地址
            if not is_valid_address(address):
                return {
                    "success": False,
                    "error": "Invalid contract address"
                }
            
            # 解析 ABI
            if isinstance(abi, str):
                try:
                    abi = json.loads(abi)
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Invalid ABI format"
                    }
            
            # 使用默认网络
            if not network:
                network = Config.DEFAULT_NETWORK
            
            # 获取合约实例
            contract = self._get_contract(address, abi, network)
            if not contract:
                return {
                    "success": False,
                    "error": "Failed to create contract instance"
                }
            
            # 检查函数是否存在
            if not hasattr(contract.functions, function_name):
                return {
                    "success": False,
                    "error": f"Function '{function_name}' not found in contract"
                }
            
            # 准备交易参数
            if args is None:
                args = []
            
            function = getattr(contract.functions, function_name)
            
            # 构建交易
            tx_params = {"value": value}
            if from_address and is_valid_address(from_address):
                tx_params["from"] = to_checksum_address(from_address)
            
            # 估算 Gas
            gas_estimate = function(*args).estimate_gas(tx_params)
            
            # 获取当前 Gas 价格
            w3 = self.web3_manager.get_web3(network)
            gas_price = w3.eth.gas_price
            
            # 计算费用
            estimated_cost = gas_estimate * gas_price
            
            return {
                "success": True,
                "contract_address": to_checksum_address(address),
                "function_name": function_name,
                "args": args,
                "gas_estimate": gas_estimate,
                "gas_price": gas_price,
                "estimated_cost": {
                    "wei": str(estimated_cost),
                    "ether": str(w3.from_wei(estimated_cost, 'ether'))
                },
                "network": network
            }
            
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return {
                "success": False,
                "error": f"Failed to estimate gas: {str(e)}"
            }
    
    async def get_events(
        self,
        address: str,
        abi: Union[str, List[Dict]],
        event_name: str,
        from_block: Union[int, str] = "latest",
        to_block: Union[int, str] = "latest",
        argument_filters: Dict[str, Any] = None,
        network: str = None
    ) -> Dict[str, Any]:
        """
        获取合约事件日志
        
        Args:
            address: 合约地址
            abi: 合约 ABI
            event_name: 事件名称
            from_block: 起始区块
            to_block: 结束区块
            argument_filters: 事件参数过滤器
            network: 网络名称
            
        Returns:
            包含事件日志的字典
        """
        try:
            # 验证地址
            if not is_valid_address(address):
                return {
                    "success": False,
                    "error": "Invalid contract address"
                }
            
            # 解析 ABI
            if isinstance(abi, str):
                try:
                    abi = json.loads(abi)
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Invalid ABI format"
                    }
            
            # 使用默认网络
            if not network:
                network = Config.DEFAULT_NETWORK
            
            # 获取合约实例
            contract = self._get_contract(address, abi, network)
            if not contract:
                return {
                    "success": False,
                    "error": "Failed to create contract instance"
                }
            
            # 检查事件是否存在
            if not hasattr(contract.events, event_name):
                return {
                    "success": False,
                    "error": f"Event '{event_name}' not found in contract"
                }
            
            # 获取事件
            event = getattr(contract.events, event_name)
            
            # 构建过滤器参数
            filter_params = {
                "fromBlock": from_block,
                "toBlock": to_block
            }
            
            if argument_filters:
                filter_params["argument_filters"] = argument_filters
            
            # 获取事件日志
            event_filter = event.create_filter(**filter_params)
            logs = event_filter.get_all_entries()
            
            # 格式化日志
            formatted_logs = []
            for log in logs:
                formatted_log = {
                    "block_number": log["blockNumber"],
                    "transaction_hash": log["transactionHash"].hex(),
                    "log_index": log["logIndex"],
                    "args": dict(log["args"])
                }
                formatted_logs.append(formatted_log)
            
            return {
                "success": True,
                "contract_address": to_checksum_address(address),
                "event_name": event_name,
                "from_block": from_block,
                "to_block": to_block,
                "logs": formatted_logs,
                "count": len(formatted_logs),
                "network": network
            }
            
        except Exception as e:
            logger.error(f"Error getting contract events: {e}")
            return {
                "success": False,
                "error": f"Failed to get events: {str(e)}"
            }