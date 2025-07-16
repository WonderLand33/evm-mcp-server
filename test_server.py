"""
EVM MCP 服务器测试脚本
"""

import asyncio
import json
from evm_mcp_server.tools import AccountTools, TokenTools, NetworkTools

async def test_basic_functions():
    """测试基本功能"""
    print("🧪 开始测试 EVM MCP 服务器基本功能...")
    print("=" * 50)
    
    # 测试网络状态
    print("📡 测试网络连接状态...")
    network_info = NetworkTools.get_network_info()
    print(f"网络状态: {json.dumps(network_info, indent=2, ensure_ascii=False)}")
    print()
    
    # 测试地址验证
    print("🔍 测试地址验证...")
    test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # Vitalik's address
    validation_result = NetworkTools.validate_address(test_address)
    print(f"地址验证结果: {json.dumps(validation_result, indent=2, ensure_ascii=False)}")
    print()
    
    # 测试余额查询
    print("💰 测试余额查询...")
    balance_result = AccountTools.get_balance(test_address, "ethereum")
    print(f"余额查询结果: {json.dumps(balance_result, indent=2, ensure_ascii=False)}")
    print()
    
    # 测试账户信息
    print("📊 测试账户信息查询...")
    account_info = AccountTools.get_account_info(test_address, "ethereum")
    print(f"账户信息: {json.dumps(account_info, indent=2, ensure_ascii=False)}")
    print()
    
    # 测试代币价格查询
    print("💱 测试代币价格查询...")
    price_result = TokenTools.get_token_price("ethereum")
    print(f"ETH 价格: {json.dumps(price_result, indent=2, ensure_ascii=False)}")
    print()
    
    # 测试单位转换
    print("🔄 测试单位转换...")
    conversion_result = NetworkTools.convert_units(1, "ether", "wei")
    print(f"单位转换结果: {json.dumps(conversion_result, indent=2, ensure_ascii=False)}")
    print()
    
    # 测试代币搜索
    print("🔎 测试代币搜索...")
    search_result = TokenTools.search_tokens("ethereum", limit=3)
    print(f"搜索结果: {json.dumps(search_result, indent=2, ensure_ascii=False)}")
    print()
    
    print("✅ 测试完成!")

if __name__ == "__main__":
    asyncio.run(test_basic_functions())