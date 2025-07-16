"""
工具函数模块
"""

import re
from typing import Union, Optional
from decimal import Decimal
from web3 import Web3
from eth_utils import is_address, to_checksum_address

def validate_ethereum_address(address: str) -> bool:
    """验证以太坊地址格式"""
    if not address:
        return False
    
    try:
        return is_address(address)
    except Exception:
        return False

def to_checksum(address: str) -> Optional[str]:
    """转换为校验和地址"""
    if not validate_ethereum_address(address):
        return None
    
    try:
        return to_checksum_address(address)
    except Exception:
        return None

def wei_to_ether(wei: Union[int, str]) -> Decimal:
    """Wei 转换为 Ether"""
    try:
        return Decimal(str(wei)) / Decimal('1000000000000000000')
    except Exception:
        return Decimal('0')

def ether_to_wei(ether: Union[float, str, Decimal]) -> int:
    """Ether 转换为 Wei"""
    try:
        return int(Decimal(str(ether)) * Decimal('1000000000000000000'))
    except Exception:
        return 0

def gwei_to_wei(gwei: Union[float, str, Decimal]) -> int:
    """Gwei 转换为 Wei"""
    try:
        return int(Decimal(str(gwei)) * Decimal('1000000000'))
    except Exception:
        return 0

def wei_to_gwei(wei: Union[int, str]) -> Decimal:
    """Wei 转换为 Gwei"""
    try:
        return Decimal(str(wei)) / Decimal('1000000000')
    except Exception:
        return Decimal('0')

def format_token_amount(amount: Union[int, str], decimals: int) -> Decimal:
    """格式化代币数量"""
    try:
        return Decimal(str(amount)) / Decimal(10 ** decimals)
    except Exception:
        return Decimal('0')

def parse_token_amount(amount: Union[float, str, Decimal], decimals: int) -> int:
    """解析代币数量为最小单位"""
    try:
        return int(Decimal(str(amount)) * Decimal(10 ** decimals))
    except Exception:
        return 0

def is_contract_address(w3: Web3, address: str) -> bool:
    """检查地址是否为合约地址"""
    if not validate_ethereum_address(address):
        return False
    
    try:
        code = w3.eth.get_code(to_checksum_address(address))
        return len(code) > 0
    except Exception:
        return False

def shorten_address(address: str, start_chars: int = 6, end_chars: int = 4) -> str:
    """缩短地址显示"""
    if not address or len(address) < start_chars + end_chars:
        return address
    
    return f"{address[:start_chars]}...{address[-end_chars:]}"

def validate_transaction_hash(tx_hash: str) -> bool:
    """验证交易哈希格式"""
    if not tx_hash:
        return False
    
    # 检查是否为 64 位十六进制字符串（可选 0x 前缀）
    pattern = r'^(0x)?[a-fA-F0-9]{64}$'
    return bool(re.match(pattern, tx_hash))

def normalize_tx_hash(tx_hash: str) -> Optional[str]:
    """标准化交易哈希"""
    if not validate_transaction_hash(tx_hash):
        return None
    
    if not tx_hash.startswith('0x'):
        tx_hash = '0x' + tx_hash
    
    return tx_hash.lower()

def validate_block_identifier(block_id: Union[str, int]) -> bool:
    """验证区块标识符"""
    if isinstance(block_id, int):
        return block_id >= 0
    
    if isinstance(block_id, str):
        # 检查是否为特殊标识符
        if block_id.lower() in ['latest', 'earliest', 'pending']:
            return True
        
        # 检查是否为区块哈希
        if validate_transaction_hash(block_id):
            return True
        
        # 检查是否为数字字符串
        try:
            return int(block_id) >= 0
        except ValueError:
            return False
    
    return False

def format_gas_price(gas_price_wei: int) -> dict:
    """格式化 Gas 价格"""
    return {
        'wei': str(gas_price_wei),
        'gwei': str(wei_to_gwei(gas_price_wei)),
        'ether': str(wei_to_ether(gas_price_wei))
    }

def calculate_transaction_fee(gas_used: int, gas_price: int) -> dict:
    """计算交易费用"""
    fee_wei = gas_used * gas_price
    return {
        'gas_used': gas_used,
        'gas_price': format_gas_price(gas_price),
        'fee': {
            'wei': str(fee_wei),
            'gwei': str(wei_to_gwei(fee_wei)),
            'ether': str(wei_to_ether(fee_wei))
        }
    }

def safe_int(value: any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        if isinstance(value, str) and value.startswith('0x'):
            return int(value, 16)
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_hex(value: any) -> Optional[str]:
    """安全转换为十六进制字符串"""
    try:
        if isinstance(value, int):
            return hex(value)
        elif isinstance(value, str) and value.startswith('0x'):
            return value
        else:
            return hex(int(value))
    except (ValueError, TypeError):
        return None