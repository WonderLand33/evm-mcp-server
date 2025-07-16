"""
交易相关工具
提供交易查询、发送和状态跟踪功能
"""

import logging
from typing import Optional, Dict, Any, List, Union
from web3 import Web3
from web3.types import TxReceipt, TxData
from eth_account import Account
from eth_utils import to_checksum_address
from ..web3_manager import Web3Manager
from ..utils import (
    is_valid_address, 
    is_valid_tx_hash, 
    normalize_tx_hash,
    format_gas_price,
    calculate_tx_fee,
    wei_to_ether,
    ether_to_wei
)
from ..config import Config

logger = logging.getLogger(__name__)

class TransactionTools:
    """交易工具类"""
    
    def __init__(self, web3_manager: Web3Manager):
        self.web3_manager = web3_manager
    
    async def get_transaction(self, tx_hash: str, network: str = None) -> Dict[str, Any]:
        """
        获取交易详情
        
        Args:
            tx_hash: 交易哈希
            network: 网络名称
            
        Returns:
            包含交易详情的字典
        """
        try:
            # 验证交易哈希
            if not is_valid_tx_hash(tx_hash):
                return {
                    "success": False,
                    "error": "Invalid transaction hash"
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
            
            # 标准化交易哈希
            normalized_hash = normalize_tx_hash(tx_hash)
            
            # 获取交易数据
            try:
                tx: TxData = w3.eth.get_transaction(normalized_hash)
            except Exception:
                return {
                    "success": False,
                    "error": "Transaction not found"
                }
            
            # 尝试获取交易收据
            receipt = None
            try:
                receipt: TxReceipt = w3.eth.get_transaction_receipt(normalized_hash)
            except Exception:
                pass  # 交易可能还未被确认
            
            # 格式化交易信息
            result = {
                "success": True,
                "hash": tx["hash"].hex(),
                "from": to_checksum_address(tx["from"]),
                "to": to_checksum_address(tx["to"]) if tx["to"] else None,
                "value": {
                    "wei": str(tx["value"]),
                    "ether": str(wei_to_ether(tx["value"]))
                },
                "gas": tx["gas"],
                "gas_price": {
                    "wei": str(tx["gasPrice"]),
                    "gwei": str(w3.from_wei(tx["gasPrice"], "gwei"))
                },
                "nonce": tx["nonce"],
                "block_number": tx["blockNumber"],
                "transaction_index": tx["transactionIndex"],
                "input": tx["input"].hex() if tx["input"] else "0x",
                "network": network
            }
            
            # 添加 EIP-1559 信息（如果适用）
            if "maxFeePerGas" in tx and tx["maxFeePerGas"]:
                result["max_fee_per_gas"] = {
                    "wei": str(tx["maxFeePerGas"]),
                    "gwei": str(w3.from_wei(tx["maxFeePerGas"], "gwei"))
                }
            
            if "maxPriorityFeePerGas" in tx and tx["maxPriorityFeePerGas"]:
                result["max_priority_fee_per_gas"] = {
                    "wei": str(tx["maxPriorityFeePerGas"]),
                    "gwei": str(w3.from_wei(tx["maxPriorityFeePerGas"], "gwei"))
                }
            
            # 添加收据信息（如果可用）
            if receipt:
                result["receipt"] = {
                    "status": receipt["status"],
                    "gas_used": receipt["gasUsed"],
                    "cumulative_gas_used": receipt["cumulativeGasUsed"],
                    "effective_gas_price": {
                        "wei": str(receipt.get("effectiveGasPrice", tx["gasPrice"])),
                        "gwei": str(w3.from_wei(receipt.get("effectiveGasPrice", tx["gasPrice"]), "gwei"))
                    },
                    "logs_count": len(receipt["logs"]),
                    "confirmed": True
                }
                
                # 计算实际交易费用
                actual_fee = calculate_tx_fee(receipt["gasUsed"], receipt.get("effectiveGasPrice", tx["gasPrice"]))
                result["receipt"]["transaction_fee"] = {
                    "wei": str(actual_fee),
                    "ether": str(wei_to_ether(actual_fee))
                }
            else:
                result["receipt"] = {
                    "confirmed": False
                }
                
                # 估算交易费用
                estimated_fee = calculate_tx_fee(tx["gas"], tx["gasPrice"])
                result["estimated_fee"] = {
                    "wei": str(estimated_fee),
                    "ether": str(wei_to_ether(estimated_fee))
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting transaction {tx_hash}: {e}")
            return {
                "success": False,
                "error": f"Failed to get transaction: {str(e)}"
            }
    
    async def get_transaction_receipt(self, tx_hash: str, network: str = None) -> Dict[str, Any]:
        """
        获取交易收据
        
        Args:
            tx_hash: 交易哈希
            network: 网络名称
            
        Returns:
            包含交易收据的字典
        """
        try:
            # 验证交易哈希
            if not is_valid_tx_hash(tx_hash):
                return {
                    "success": False,
                    "error": "Invalid transaction hash"
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
            
            # 标准化交易哈希
            normalized_hash = normalize_tx_hash(tx_hash)
            
            # 获取交易收据
            try:
                receipt: TxReceipt = w3.eth.get_transaction_receipt(normalized_hash)
            except Exception:
                return {
                    "success": False,
                    "error": "Transaction receipt not found (transaction may not be confirmed yet)"
                }
            
            # 格式化收据信息
            result = {
                "success": True,
                "transaction_hash": receipt["transactionHash"].hex(),
                "block_number": receipt["blockNumber"],
                "block_hash": receipt["blockHash"].hex(),
                "transaction_index": receipt["transactionIndex"],
                "from": to_checksum_address(receipt["from"]),
                "to": to_checksum_address(receipt["to"]) if receipt["to"] else None,
                "status": receipt["status"],
                "gas_used": receipt["gasUsed"],
                "cumulative_gas_used": receipt["cumulativeGasUsed"],
                "logs_count": len(receipt["logs"]),
                "network": network
            }
            
            # 添加有效 Gas 价格（EIP-1559）
            if "effectiveGasPrice" in receipt:
                result["effective_gas_price"] = {
                    "wei": str(receipt["effectiveGasPrice"]),
                    "gwei": str(w3.from_wei(receipt["effectiveGasPrice"], "gwei"))
                }
                
                # 计算交易费用
                tx_fee = calculate_tx_fee(receipt["gasUsed"], receipt["effectiveGasPrice"])
                result["transaction_fee"] = {
                    "wei": str(tx_fee),
                    "ether": str(wei_to_ether(tx_fee))
                }
            
            # 添加合约地址（如果是合约创建交易）
            if receipt.get("contractAddress"):
                result["contract_address"] = to_checksum_address(receipt["contractAddress"])
            
            # 添加日志信息
            if receipt["logs"]:
                logs = []
                for log in receipt["logs"]:
                    log_info = {
                        "address": to_checksum_address(log["address"]),
                        "topics": [topic.hex() for topic in log["topics"]],
                        "data": log["data"].hex(),
                        "log_index": log["logIndex"]
                    }
                    logs.append(log_info)
                result["logs"] = logs
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting transaction receipt {tx_hash}: {e}")
            return {
                "success": False,
                "error": f"Failed to get transaction receipt: {str(e)}"
            }
    
    async def estimate_gas(
        self,
        from_address: str,
        to_address: str = None,
        value: Union[int, str] = 0,
        data: str = None,
        network: str = None
    ) -> Dict[str, Any]:
        """
        估算交易 Gas 费用
        
        Args:
            from_address: 发送者地址
            to_address: 接收者地址
            value: 发送金额 (wei 或 ether 字符串)
            data: 交易数据
            network: 网络名称
            
        Returns:
            包含 Gas 估算的字典
        """
        try:
            # 验证地址
            if not is_valid_address(from_address):
                return {
                    "success": False,
                    "error": "Invalid from address"
                }
            
            if to_address and not is_valid_address(to_address):
                return {
                    "success": False,
                    "error": "Invalid to address"
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
            
            # 处理 value 参数
            if isinstance(value, str):
                try:
                    # 尝试解析为 ether
                    value = int(ether_to_wei(float(value)))
                except ValueError:
                    # 尝试解析为 wei
                    value = int(value)
            
            # 构建交易参数
            tx_params = {
                "from": to_checksum_address(from_address),
                "value": value
            }
            
            if to_address:
                tx_params["to"] = to_checksum_address(to_address)
            
            if data:
                tx_params["data"] = data
            
            # 估算 Gas
            gas_estimate = w3.eth.estimate_gas(tx_params)
            
            # 获取当前 Gas 价格
            gas_price = w3.eth.gas_price
            
            # 计算费用
            estimated_cost = calculate_tx_fee(gas_estimate, gas_price)
            
            result = {
                "success": True,
                "from": to_checksum_address(from_address),
                "gas_estimate": gas_estimate,
                "gas_price": {
                    "wei": str(gas_price),
                    "gwei": str(w3.from_wei(gas_price, "gwei"))
                },
                "estimated_cost": {
                    "wei": str(estimated_cost),
                    "ether": str(wei_to_ether(estimated_cost))
                },
                "network": network
            }
            
            if to_address:
                result["to"] = to_checksum_address(to_address)
            
            if value > 0:
                result["value"] = {
                    "wei": str(value),
                    "ether": str(wei_to_ether(value))
                }
            
            # 尝试获取 EIP-1559 费用建议
            try:
                latest_block = w3.eth.get_block("latest")
                if "baseFeePerGas" in latest_block:
                    base_fee = latest_block["baseFeePerGas"]
                    max_priority_fee = w3.eth.max_priority_fee
                    max_fee = base_fee * 2 + max_priority_fee
                    
                    result["eip1559_fees"] = {
                        "base_fee": {
                            "wei": str(base_fee),
                            "gwei": str(w3.from_wei(base_fee, "gwei"))
                        },
                        "max_priority_fee": {
                            "wei": str(max_priority_fee),
                            "gwei": str(w3.from_wei(max_priority_fee, "gwei"))
                        },
                        "max_fee": {
                            "wei": str(max_fee),
                            "gwei": str(w3.from_wei(max_fee, "gwei"))
                        }
                    }
            except Exception as e:
                logger.debug(f"Could not get EIP-1559 fees: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return {
                "success": False,
                "error": f"Failed to estimate gas: {str(e)}"
            }
    
    async def get_pending_transactions(self, address: str, network: str = None) -> Dict[str, Any]:
        """
        获取地址的待处理交易
        
        Args:
            address: 地址
            network: 网络名称
            
        Returns:
            包含待处理交易的字典
        """
        try:
            # 验证地址
            if not is_valid_address(address):
                return {
                    "success": False,
                    "error": "Invalid address"
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
            
            # 获取当前 nonce 和待处理 nonce
            current_nonce = w3.eth.get_transaction_count(checksum_address, "latest")
            pending_nonce = w3.eth.get_transaction_count(checksum_address, "pending")
            
            result = {
                "success": True,
                "address": checksum_address,
                "current_nonce": current_nonce,
                "pending_nonce": pending_nonce,
                "pending_count": pending_nonce - current_nonce,
                "network": network
            }
            
            # 如果有待处理交易，尝试获取详情
            if pending_nonce > current_nonce:
                try:
                    # 获取内存池中的交易（这个功能可能不是所有节点都支持）
                    pending_txs = []
                    # 注意：这里只是示例，实际实现可能需要使用特定的 RPC 方法
                    result["pending_transactions"] = pending_txs
                except Exception as e:
                    logger.debug(f"Could not get pending transaction details: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting pending transactions for {address}: {e}")
            return {
                "success": False,
                "error": f"Failed to get pending transactions: {str(e)}"
            }
    
    async def decode_transaction_input(self, tx_hash: str, abi: List[Dict] = None, network: str = None) -> Dict[str, Any]:
        """
        解码交易输入数据
        
        Args:
            tx_hash: 交易哈希
            abi: 合约 ABI（可选）
            network: 网络名称
            
        Returns:
            包含解码结果的字典
        """
        try:
            # 验证交易哈希
            if not is_valid_tx_hash(tx_hash):
                return {
                    "success": False,
                    "error": "Invalid transaction hash"
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
            
            # 获取交易
            normalized_hash = normalize_tx_hash(tx_hash)
            tx = w3.eth.get_transaction(normalized_hash)
            
            result = {
                "success": True,
                "transaction_hash": tx["hash"].hex(),
                "input_data": tx["input"].hex(),
                "network": network
            }
            
            # 如果没有输入数据
            if not tx["input"] or tx["input"] == b'':
                result["decoded"] = {
                    "type": "simple_transfer",
                    "description": "Simple ETH transfer with no data"
                }
                return result
            
            # 提取函数选择器
            if len(tx["input"]) >= 4:
                function_selector = tx["input"][:4].hex()
                result["function_selector"] = function_selector
                
                # 常见函数选择器
                common_selectors = {
                    "0xa9059cbb": "transfer(address,uint256)",
                    "0x23b872dd": "transferFrom(address,address,uint256)",
                    "0x095ea7b3": "approve(address,uint256)",
                    "0x40c10f19": "mint(address,uint256)",
                    "0x42966c68": "burn(uint256)",
                    "0x70a08231": "balanceOf(address)"
                }
                
                if function_selector in common_selectors:
                    result["decoded"] = {
                        "type": "contract_call",
                        "function": common_selectors[function_selector],
                        "description": f"Call to {common_selectors[function_selector]}"
                    }
                else:
                    result["decoded"] = {
                        "type": "contract_call",
                        "function": "unknown",
                        "description": f"Contract call with selector {function_selector}"
                    }
            
            # 如果提供了 ABI，尝试详细解码
            if abi and tx["to"]:
                try:
                    contract = w3.eth.contract(address=tx["to"], abi=abi)
                    decoded = contract.decode_function_input(tx["input"])
                    
                    result["decoded"]["function_object"] = str(decoded[0])
                    result["decoded"]["inputs"] = dict(decoded[1])
                except Exception as e:
                    logger.debug(f"Could not decode with provided ABI: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error decoding transaction input: {e}")
            return {
                "success": False,
                "error": f"Failed to decode transaction input: {str(e)}"
            }