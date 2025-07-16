"""
区块查询工具
提供区块信息查询和分析功能
"""

import logging
from typing import Optional, Dict, Any, List, Union
from web3 import Web3
from web3.types import BlockData
from ..web3_manager import Web3Manager
from ..utils import (
    is_valid_block_identifier,
    wei_to_ether,
    format_gas_price,
    to_checksum_address
)
from ..config import Config

logger = logging.getLogger(__name__)

class BlockTools:
    """区块工具类"""
    
    def __init__(self, web3_manager: Web3Manager):
        self.web3_manager = web3_manager
    
    async def get_block(
        self, 
        block_identifier: Union[int, str] = "latest", 
        full_transactions: bool = False,
        network: str = None
    ) -> Dict[str, Any]:
        """
        获取区块信息
        
        Args:
            block_identifier: 区块标识符 (数字、哈希或 'latest', 'pending')
            full_transactions: 是否包含完整交易信息
            network: 网络名称
            
        Returns:
            包含区块信息的字典
        """
        try:
            # 验证区块标识符
            if not is_valid_block_identifier(block_identifier):
                return {
                    "success": False,
                    "error": "Invalid block identifier"
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
            
            # 获取区块数据
            try:
                block: BlockData = w3.eth.get_block(block_identifier, full_transactions=full_transactions)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Block not found: {str(e)}"
                }
            
            # 格式化区块信息
            result = {
                "success": True,
                "number": block["number"],
                "hash": block["hash"].hex(),
                "parent_hash": block["parentHash"].hex(),
                "timestamp": block["timestamp"],
                "miner": to_checksum_address(block["miner"]),
                "difficulty": block["difficulty"],
                "total_difficulty": block["totalDifficulty"],
                "size": block["size"],
                "gas_limit": block["gasLimit"],
                "gas_used": block["gasUsed"],
                "gas_used_percentage": round((block["gasUsed"] / block["gasLimit"]) * 100, 2),
                "transaction_count": len(block["transactions"]),
                "network": network
            }
            
            # 添加 EIP-1559 信息（如果适用）
            if "baseFeePerGas" in block and block["baseFeePerGas"]:
                result["base_fee_per_gas"] = {
                    "wei": str(block["baseFeePerGas"]),
                    "gwei": str(w3.from_wei(block["baseFeePerGas"], "gwei"))
                }
            
            # 添加额外字段
            if "extraData" in block:
                result["extra_data"] = block["extraData"].hex()
            
            if "nonce" in block:
                result["nonce"] = block["nonce"].hex()
            
            if "mixHash" in block:
                result["mix_hash"] = block["mixHash"].hex()
            
            # 处理交易信息
            if full_transactions:
                transactions = []
                for tx in block["transactions"]:
                    tx_info = {
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
                        "nonce": tx["nonce"]
                    }
                    
                    # 添加 EIP-1559 信息
                    if "maxFeePerGas" in tx and tx["maxFeePerGas"]:
                        tx_info["max_fee_per_gas"] = {
                            "wei": str(tx["maxFeePerGas"]),
                            "gwei": str(w3.from_wei(tx["maxFeePerGas"], "gwei"))
                        }
                    
                    if "maxPriorityFeePerGas" in tx and tx["maxPriorityFeePerGas"]:
                        tx_info["max_priority_fee_per_gas"] = {
                            "wei": str(tx["maxPriorityFeePerGas"]),
                            "gwei": str(w3.from_wei(tx["maxPriorityFeePerGas"], "gwei"))
                        }
                    
                    transactions.append(tx_info)
                
                result["transactions"] = transactions
            else:
                # 只包含交易哈希
                result["transaction_hashes"] = [tx.hex() for tx in block["transactions"]]
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting block {block_identifier}: {e}")
            return {
                "success": False,
                "error": f"Failed to get block: {str(e)}"
            }
    
    async def get_latest_blocks(self, count: int = 10, network: str = None) -> Dict[str, Any]:
        """
        获取最新的多个区块
        
        Args:
            count: 获取区块数量
            network: 网络名称
            
        Returns:
            包含最新区块列表的字典
        """
        try:
            if count <= 0 or count > 100:
                return {
                    "success": False,
                    "error": "Count must be between 1 and 100"
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
            
            # 获取最新区块号
            latest_block_number = w3.eth.block_number
            
            blocks = []
            for i in range(count):
                block_number = latest_block_number - i
                if block_number < 0:
                    break
                
                try:
                    block = w3.eth.get_block(block_number)
                    block_info = {
                        "number": block["number"],
                        "hash": block["hash"].hex(),
                        "timestamp": block["timestamp"],
                        "miner": to_checksum_address(block["miner"]),
                        "gas_used": block["gasUsed"],
                        "gas_limit": block["gasLimit"],
                        "gas_used_percentage": round((block["gasUsed"] / block["gasLimit"]) * 100, 2),
                        "transaction_count": len(block["transactions"]),
                        "size": block["size"]
                    }
                    
                    # 添加基础费用（如果适用）
                    if "baseFeePerGas" in block and block["baseFeePerGas"]:
                        block_info["base_fee_per_gas"] = {
                            "wei": str(block["baseFeePerGas"]),
                            "gwei": str(w3.from_wei(block["baseFeePerGas"], "gwei"))
                        }
                    
                    blocks.append(block_info)
                except Exception as e:
                    logger.warning(f"Could not get block {block_number}: {e}")
                    continue
            
            return {
                "success": True,
                "latest_block_number": latest_block_number,
                "blocks": blocks,
                "count": len(blocks),
                "network": network
            }
            
        except Exception as e:
            logger.error(f"Error getting latest blocks: {e}")
            return {
                "success": False,
                "error": f"Failed to get latest blocks: {str(e)}"
            }
    
    async def get_block_transactions(self, block_identifier: Union[int, str], network: str = None) -> Dict[str, Any]:
        """
        获取区块中的所有交易
        
        Args:
            block_identifier: 区块标识符
            network: 网络名称
            
        Returns:
            包含区块交易的字典
        """
        try:
            # 验证区块标识符
            if not is_valid_block_identifier(block_identifier):
                return {
                    "success": False,
                    "error": "Invalid block identifier"
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
            
            # 获取区块（包含完整交易）
            try:
                block = w3.eth.get_block(block_identifier, full_transactions=True)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Block not found: {str(e)}"
                }
            
            # 处理交易
            transactions = []
            total_value = 0
            total_gas_used = 0
            
            for tx in block["transactions"]:
                tx_info = {
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
                    "transaction_index": tx["transactionIndex"]
                }
                
                # 累计统计
                total_value += tx["value"]
                
                # 尝试获取交易收据来计算实际 Gas 使用量
                try:
                    receipt = w3.eth.get_transaction_receipt(tx["hash"])
                    tx_info["gas_used"] = receipt["gasUsed"]
                    tx_info["status"] = receipt["status"]
                    total_gas_used += receipt["gasUsed"]
                except Exception:
                    pass
                
                transactions.append(tx_info)
            
            return {
                "success": True,
                "block_number": block["number"],
                "block_hash": block["hash"].hex(),
                "timestamp": block["timestamp"],
                "transaction_count": len(transactions),
                "transactions": transactions,
                "statistics": {
                    "total_value": {
                        "wei": str(total_value),
                        "ether": str(wei_to_ether(total_value))
                    },
                    "total_gas_used": total_gas_used,
                    "block_gas_limit": block["gasLimit"],
                    "block_gas_used": block["gasUsed"]
                },
                "network": network
            }
            
        except Exception as e:
            logger.error(f"Error getting block transactions: {e}")
            return {
                "success": False,
                "error": f"Failed to get block transactions: {str(e)}"
            }
    
    async def analyze_block_range(
        self, 
        start_block: int, 
        end_block: int, 
        network: str = None
    ) -> Dict[str, Any]:
        """
        分析区块范围的统计信息
        
        Args:
            start_block: 起始区块号
            end_block: 结束区块号
            network: 网络名称
            
        Returns:
            包含区块范围分析的字典
        """
        try:
            if start_block > end_block:
                return {
                    "success": False,
                    "error": "Start block must be less than or equal to end block"
                }
            
            if end_block - start_block > 1000:
                return {
                    "success": False,
                    "error": "Block range too large (maximum 1000 blocks)"
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
            
            # 分析统计
            total_transactions = 0
            total_gas_used = 0
            total_gas_limit = 0
            total_size = 0
            miners = {}
            gas_prices = []
            block_times = []
            
            blocks_analyzed = 0
            
            for block_num in range(start_block, end_block + 1):
                try:
                    block = w3.eth.get_block(block_num, full_transactions=True)
                    
                    # 基本统计
                    total_transactions += len(block["transactions"])
                    total_gas_used += block["gasUsed"]
                    total_gas_limit += block["gasLimit"]
                    total_size += block["size"]
                    
                    # 矿工统计
                    miner = to_checksum_address(block["miner"])
                    miners[miner] = miners.get(miner, 0) + 1
                    
                    # Gas 价格统计
                    for tx in block["transactions"]:
                        gas_prices.append(tx["gasPrice"])
                    
                    # 区块时间
                    if blocks_analyzed > 0:
                        prev_block = w3.eth.get_block(block_num - 1)
                        block_time = block["timestamp"] - prev_block["timestamp"]
                        block_times.append(block_time)
                    
                    blocks_analyzed += 1
                    
                except Exception as e:
                    logger.warning(f"Could not analyze block {block_num}: {e}")
                    continue
            
            if blocks_analyzed == 0:
                return {
                    "success": False,
                    "error": "No blocks could be analyzed"
                }
            
            # 计算统计信息
            avg_gas_usage = (total_gas_used / total_gas_limit) * 100 if total_gas_limit > 0 else 0
            avg_transactions_per_block = total_transactions / blocks_analyzed
            avg_block_size = total_size / blocks_analyzed
            
            # Gas 价格统计
            gas_price_stats = {}
            if gas_prices:
                gas_prices.sort()
                gas_price_stats = {
                    "min": {
                        "wei": str(min(gas_prices)),
                        "gwei": str(w3.from_wei(min(gas_prices), "gwei"))
                    },
                    "max": {
                        "wei": str(max(gas_prices)),
                        "gwei": str(w3.from_wei(max(gas_prices), "gwei"))
                    },
                    "median": {
                        "wei": str(gas_prices[len(gas_prices) // 2]),
                        "gwei": str(w3.from_wei(gas_prices[len(gas_prices) // 2], "gwei"))
                    },
                    "average": {
                        "wei": str(sum(gas_prices) // len(gas_prices)),
                        "gwei": str(w3.from_wei(sum(gas_prices) // len(gas_prices), "gwei"))
                    }
                }
            
            # 区块时间统计
            block_time_stats = {}
            if block_times:
                avg_block_time = sum(block_times) / len(block_times)
                block_time_stats = {
                    "average_seconds": round(avg_block_time, 2),
                    "min_seconds": min(block_times),
                    "max_seconds": max(block_times)
                }
            
            return {
                "success": True,
                "range": {
                    "start_block": start_block,
                    "end_block": end_block,
                    "blocks_analyzed": blocks_analyzed
                },
                "statistics": {
                    "total_transactions": total_transactions,
                    "average_transactions_per_block": round(avg_transactions_per_block, 2),
                    "total_gas_used": total_gas_used,
                    "total_gas_limit": total_gas_limit,
                    "average_gas_usage_percentage": round(avg_gas_usage, 2),
                    "average_block_size_bytes": round(avg_block_size, 2)
                },
                "gas_price_analysis": gas_price_stats,
                "block_time_analysis": block_time_stats,
                "miner_distribution": dict(sorted(miners.items(), key=lambda x: x[1], reverse=True)[:10]),
                "network": network
            }
            
        except Exception as e:
            logger.error(f"Error analyzing block range: {e}")
            return {
                "success": False,
                "error": f"Failed to analyze block range: {str(e)}"
            }