"""
代币信息查询工具
"""

from typing import Dict, List, Optional
import logging
import requests
from web3.exceptions import Web3Exception

from ..web3_manager import web3_manager
from ..utils import validate_ethereum_address, to_checksum, format_token_amount
from ..config import Config

logger = logging.getLogger(__name__)

class TokenTools:
    """代币相关工具类"""
    
    # ERC20 标准 ABI
    ERC20_ABI = [
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
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
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
    def get_token_metadata(token_address: str, network: str = None) -> Dict:
        """
        查询代币元数据
        
        Args:
            token_address: 代币合约地址
            network: 网络名称
            
        Returns:
            包含代币元数据的字典
        """
        try:
            # 验证地址
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
            checksum_address = to_checksum(token_address)
            
            # 创建合约实例
            contract = w3.eth.contract(
                address=checksum_address,
                abi=TokenTools.ERC20_ABI
            )
            
            # 查询代币信息
            try:
                name = contract.functions.name().call()
                symbol = contract.functions.symbol().call()
                decimals = contract.functions.decimals().call()
                total_supply_raw = contract.functions.totalSupply().call()
                
                # 格式化总供应量
                total_supply_formatted = format_token_amount(total_supply_raw, decimals)
                
                return {
                    "success": True,
                    "data": {
                        "address": checksum_address,
                        "network": network or Config.DEFAULT_NETWORK,
                        "name": name,
                        "symbol": symbol,
                        "decimals": decimals,
                        "total_supply": {
                            "raw": str(total_supply_raw),
                            "formatted": str(total_supply_formatted),
                            "display": f"{total_supply_formatted:,.2f} {symbol}"
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
            logger.error(f"查询代币元数据时出错: {e}")
            return {
                "success": False,
                "error": f"查询失败: {str(e)}"
            }
    
    @staticmethod
    def get_token_price(token_symbol: str, vs_currency: str = "usd") -> Dict:
        """
        查询代币价格（使用 CoinGecko API）
        
        Args:
            token_symbol: 代币符号
            vs_currency: 对比货币
            
        Returns:
            包含价格信息的字典
        """
        try:
            # CoinGecko API URL
            url = "https://api.coingecko.com/api/v3/simple/price"
            
            params = {
                "ids": token_symbol.lower(),
                "vs_currencies": vs_currency.lower(),
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true"
            }
            
            # 如果有 API 密钥，添加到请求头
            headers = {}
            if Config.COINGECKO_API_KEY:
                headers["x-cg-demo-api-key"] = Config.COINGECKO_API_KEY
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return {
                    "success": False,
                    "error": f"未找到代币 {token_symbol} 的价格信息"
                }
            
            token_data = data.get(token_symbol.lower(), {})
            
            return {
                "success": True,
                "data": {
                    "symbol": token_symbol.upper(),
                    "price": token_data.get(vs_currency.lower()),
                    "currency": vs_currency.upper(),
                    "market_cap": token_data.get(f"{vs_currency.lower()}_market_cap"),
                    "24h_volume": token_data.get(f"{vs_currency.lower()}_24h_vol"),
                    "24h_change": token_data.get(f"{vs_currency.lower()}_24h_change"),
                    "last_updated": "实时数据"
                }
            }
            
        except requests.RequestException as e:
            logger.error(f"API 请求错误: {e}")
            return {
                "success": False,
                "error": f"价格查询失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"查询代币价格时出错: {e}")
            return {
                "success": False,
                "error": f"查询失败: {str(e)}"
            }
    
    @staticmethod
    def get_token_supply(token_address: str, network: str = None) -> Dict:
        """
        查询代币供应量信息
        
        Args:
            token_address: 代币合约地址
            network: 网络名称
            
        Returns:
            包含供应量信息的字典
        """
        try:
            # 首先获取基本元数据
            metadata_result = TokenTools.get_token_metadata(token_address, network)
            
            if not metadata_result["success"]:
                return metadata_result
            
            metadata = metadata_result["data"]
            
            return {
                "success": True,
                "data": {
                    "address": metadata["address"],
                    "network": metadata["network"],
                    "symbol": metadata["symbol"],
                    "decimals": metadata["decimals"],
                    "total_supply": metadata["total_supply"],
                    "supply_info": {
                        "is_mintable": "未知",  # 需要检查合约是否有 mint 函数
                        "is_burnable": "未知",  # 需要检查合约是否有 burn 函数
                        "max_supply": "未知"    # 大多数 ERC20 没有最大供应量限制
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"查询代币供应量时出错: {e}")
            return {
                "success": False,
                "error": f"查询失败: {str(e)}"
            }
    
    @staticmethod
    def search_tokens(query: str, network: str = None, limit: int = 10) -> Dict:
        """
        搜索代币（基于符号或名称）
        
        Args:
            query: 搜索关键词
            network: 网络名称
            limit: 返回结果数量限制
            
        Returns:
            包含搜索结果的字典
        """
        try:
            # 这里可以集成多个数据源进行搜索
            # 目前使用 CoinGecko 的搜索 API
            
            url = "https://api.coingecko.com/api/v3/search"
            params = {"query": query}
            
            headers = {}
            if Config.COINGECKO_API_KEY:
                headers["x-cg-demo-api-key"] = Config.COINGECKO_API_KEY
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            coins = data.get("coins", [])[:limit]
            
            results = []
            for coin in coins:
                results.append({
                    "id": coin.get("id"),
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol", "").upper(),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "thumb": coin.get("thumb"),
                    "large": coin.get("large")
                })
            
            return {
                "success": True,
                "data": {
                    "query": query,
                    "network": network or "all",
                    "results_count": len(results),
                    "tokens": results
                }
            }
            
        except requests.RequestException as e:
            logger.error(f"搜索 API 请求错误: {e}")
            return {
                "success": False,
                "error": f"搜索失败: {str(e)}"
            }
        except Exception as e:
            logger.error(f"搜索代币时出错: {e}")
            return {
                "success": False,
                "error": f"搜索失败: {str(e)}"
            }