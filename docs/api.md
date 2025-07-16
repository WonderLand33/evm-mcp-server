# EVM MCP Server API 文档

## 概述

EVM MCP Server 是一个基于 Model Context Protocol (MCP) 的以太坊虚拟机区块链数据服务器，提供全面的区块链数据查询和交互功能。

## 支持的网络

- **Ethereum Mainnet** (ethereum)
- **Polygon** (polygon)  
- **Binance Smart Chain** (bsc)
- **Arbitrum One** (arbitrum)
- **Optimism** (optimism)

## 工具列表

### 1. 账户和余额相关

#### `get_balance`
查询地址的原生代币余额（ETH、MATIC、BNB 等）

**参数:**
- `address` (string, 必需): 以太坊地址
- `network` (string, 可选): 网络名称，默认为 ethereum

**返回示例:**
```json
{
  "success": true,
  "data": {
    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "network": "ethereum",
    "native_token": "ETH",
    "balance": {
      "wei": "1234567890123456789",
      "ether": "1.234567890123456789",
      "formatted": "1.234568 ETH"
    },
    "is_contract": false
  }
}
```

#### `get_token_balance`
查询地址的 ERC20 代币余额

**参数:**
- `address` (string, 必需): 持有者地址
- `token_address` (string, 必需): 代币合约地址
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "holder_address": "0x...",
    "token_address": "0x...",
    "network": "ethereum",
    "token_info": {
      "name": "USD Coin",
      "symbol": "USDC",
      "decimals": 6
    },
    "balance": {
      "raw": "1000000000",
      "formatted": "1000.000000",
      "display": "1000.000000 USDC"
    }
  }
}
```

#### `get_account_info`
获取账户综合信息

**参数:**
- `address` (string, 必需): 以太坊地址
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "address": "0x...",
    "network": "ethereum",
    "account_type": "externally_owned",
    "balance": {
      "wei": "1234567890123456789",
      "ether": "1.234567890123456789",
      "formatted": "1.234568 ETH"
    },
    "nonce": 42,
    "is_contract": false,
    "contract_code": null
  }
}
```

### 2. 代币信息查询

#### `get_token_metadata`
查询代币元数据（名称、符号、精度等）

**参数:**
- `token_address` (string, 必需): 代币合约地址
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "address": "0xA0b86a33E6441b8C4505E2E8E3C3C4C8E6441b8C",
    "network": "ethereum",
    "name": "USD Coin",
    "symbol": "USDC",
    "decimals": 6,
    "total_supply": {
      "raw": "50000000000000000",
      "formatted": "50000000000.000000",
      "display": "50,000,000,000.00 USDC"
    }
  }
}
```

#### `get_token_price`
查询代币当前价格

**参数:**
- `token_symbol` (string, 必需): 代币符号 (如 BTC, ETH, USDT)
- `vs_currency` (string, 可选): 对比货币，默认为 usd

**返回示例:**
```json
{
  "success": true,
  "data": {
    "symbol": "ETH",
    "price": 2500.50,
    "currency": "USD",
    "market_cap": 300000000000,
    "24h_volume": 15000000000,
    "24h_change": 2.5,
    "last_updated": "实时数据"
  }
}
```

#### `search_tokens`
搜索代币信息

**参数:**
- `query` (string, 必需): 搜索关键词
- `network` (string, 可选): 网络名称，默认为 all
- `limit` (integer, 可选): 返回结果数量限制，默认为 10

**返回示例:**
```json
{
  "success": true,
  "data": {
    "query": "ethereum",
    "network": "all",
    "results_count": 3,
    "tokens": [
      {
        "id": "ethereum",
        "name": "Ethereum",
        "symbol": "ETH",
        "market_cap_rank": 2,
        "thumb": "https://...",
        "large": "https://..."
      }
    ]
  }
}
```

### 3. 网络和工具

#### `get_supported_networks`
获取支持的网络列表

**参数:** 无

**返回示例:**
```json
{
  "success": true,
  "data": {
    "networks": ["ethereum", "polygon", "bsc", "arbitrum", "optimism"],
    "default_network": "ethereum",
    "network_details": {
      "ethereum": {
        "name": "Ethereum Mainnet",
        "chain_id": 1,
        "rpc_url": "https://...",
        "explorer": "https://etherscan.io",
        "native_token": "ETH"
      }
    }
  }
}
```

#### `get_network_status`
获取网络连接状态

**参数:**
- `network` (string, 可选): 网络名称（不提供则检查所有网络）

**返回示例:**
```json
{
  "success": true,
  "data": {
    "connected_networks": ["ethereum", "polygon"],
    "total_supported": 5,
    "details": {
      "ethereum": {
        "connected": true,
        "chain_id": 1,
        "latest_block": 18500000
      }
    }
  }
}
```

## 资源列表

### `evm://networks`
获取所有支持的 EVM 网络信息

### `evm://status`
获取 EVM MCP 服务器当前状态

## 错误处理

所有 API 调用都返回统一的响应格式：

**成功响应:**
```json
{
  "success": true,
  "data": { ... }
}
```

**错误响应:**
```json
{
  "success": false,
  "error": "错误描述"
}
```

## 常见错误

- `无效的以太坊地址` - 提供的地址格式不正确
- `无法连接到网络` - 网络连接失败
- `合约调用失败` - 智能合约调用出错
- `未知工具` - 调用了不存在的工具
- `不支持的网络` - 指定的网络不在支持列表中

## 使用示例

### 查询 Vitalik 的 ETH 余额
```json
{
  "tool": "get_balance",
  "arguments": {
    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "network": "ethereum"
  }
}
```

### 查询 USDC 代币信息
```json
{
  "tool": "get_token_metadata",
  "arguments": {
    "token_address": "0xA0b86a33E6441b8C4505E2E8E3C3C4C8E6441b8C",
    "network": "ethereum"
  }
}
```

### 搜索比特币相关代币
```json
{
  "tool": "search_tokens",
  "arguments": {
    "query": "bitcoin",
    "limit": 5
  }
}
```