# EVM MCP Server API 文档

## 概述

EVM MCP Server 是一个基于 Model Context Protocol (MCP) 的以太坊虚拟机区块链数据服务器，提供全面的区块链数据查询和交互功能。

## 支持的网络

### 主网络
- **Ethereum Mainnet** (ethereum) - 支持 ENS
- **Polygon** (polygon)
- **Binance Smart Chain** (bsc)
- **Arbitrum One** (arbitrum) - 支持 ENS
- **Optimism** (optimism) - 支持 ENS
- **Base** (base) - 支持 ENS
- **Avalanche C-Chain** (avalanche)
- **Fantom Opera** (fantom)

### 测试网络
- **Ethereum Sepolia** (sepolia) - 支持 ENS
- **Ethereum Goerli** (goerli) - 支持 ENS

## 工具分类

### 1. 账户和余额工具

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
      "gwei": "1234567890.123456789",
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
      "gwei": "1234567890.123456789",
      "ether": "1.234567890123456789",
      "formatted": "1.234568 ETH"
    },
    "nonce": 42,
    "is_contract": false,
    "contract_code": null,
    "code_hash": "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
  }
}
```

### 2. 代币信息工具

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
    "last_updated": "2024-01-01T12:00:00Z"
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

### 3. 交易工具

#### `get_transaction`
获取交易详细信息

**参数:**
- `tx_hash` (string, 必需): 交易哈希
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "hash": "0x...",
    "network": "ethereum",
    "status": "success",
    "block_number": 18500000,
    "block_hash": "0x...",
    "transaction_index": 42,
    "from": "0x...",
    "to": "0x...",
    "value": {
      "wei": "1000000000000000000",
      "ether": "1.0"
    },
    "gas": 21000,
    "gas_price": {
      "wei": "20000000000",
      "gwei": "20"
    },
    "gas_used": 21000,
    "nonce": 123,
    "input": "0x",
    "logs": [],
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### `get_transaction_receipt`
获取交易收据

**参数:**
- `tx_hash` (string, 必需): 交易哈希
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "transaction_hash": "0x...",
    "network": "ethereum",
    "status": 1,
    "block_number": 18500000,
    "block_hash": "0x...",
    "transaction_index": 42,
    "from": "0x...",
    "to": "0x...",
    "gas_used": 21000,
    "cumulative_gas_used": 1500000,
    "effective_gas_price": "20000000000",
    "logs": [],
    "logs_bloom": "0x...",
    "contract_address": null
  }
}
```

#### `estimate_gas`
估算交易 Gas 费用

**参数:**
- `from` (string, 必需): 发送方地址
- `to` (string, 可选): 接收方地址
- `value` (string, 可选): 转账金额（Wei）
- `data` (string, 可选): 交易数据
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "network": "ethereum",
    "gas_estimate": 21000,
    "gas_price": {
      "wei": "20000000000",
      "gwei": "20"
    },
    "estimated_cost": {
      "wei": "420000000000000",
      "ether": "0.00042"
    },
    "eip1559": {
      "base_fee": "15000000000",
      "max_priority_fee": "2000000000",
      "max_fee": "32000000000"
    }
  }
}
```

#### `decode_transaction_input`
解码交易输入数据

**参数:**
- `tx_hash` (string, 必需): 交易哈希
- `abi` (array, 可选): 合约 ABI（用于详细解码）
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "transaction_hash": "0x...",
    "input_data": "0xa9059cbb...",
    "method_id": "0xa9059cbb",
    "method_name": "transfer",
    "decoded_input": {
      "function": "transfer(address,uint256)",
      "parameters": {
        "to": "0x...",
        "value": "1000000000000000000"
      }
    }
  }
}
```

### 4. 区块工具

#### `get_block`
获取区块信息

**参数:**
- `block_identifier` (string/number, 必需): 区块号、哈希或 "latest"/"pending"
- `include_transactions` (boolean, 可选): 是否包含完整交易信息，默认 false
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "number": 18500000,
    "hash": "0x...",
    "parent_hash": "0x...",
    "nonce": "0x...",
    "sha3_uncles": "0x...",
    "logs_bloom": "0x...",
    "transactions_root": "0x...",
    "state_root": "0x...",
    "receipts_root": "0x...",
    "miner": "0x...",
    "difficulty": 0,
    "total_difficulty": 0,
    "extra_data": "0x...",
    "size": 12345,
    "gas_limit": 30000000,
    "gas_used": 15000000,
    "timestamp": 1704110400,
    "transactions": ["0x...", "0x..."],
    "uncles": [],
    "base_fee_per_gas": "15000000000"
  }
}
```

#### `get_latest_blocks`
获取最新的多个区块

**参数:**
- `count` (integer, 可选): 获取区块数量，默认 5，最大 20
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "network": "ethereum",
    "latest_block_number": 18500000,
    "count": 5,
    "blocks": [
      {
        "number": 18500000,
        "hash": "0x...",
        "timestamp": 1704110400,
        "miner": "0x...",
        "gas_used": 15000000,
        "gas_limit": 30000000,
        "transaction_count": 150,
        "size": 12345
      }
    ]
  }
}
```

#### `analyze_block_range`
分析区块范围统计信息

**参数:**
- `start_block` (integer, 必需): 起始区块号
- `end_block` (integer, 必需): 结束区块号
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "network": "ethereum",
    "start_block": 18500000,
    "end_block": 18500010,
    "block_count": 11,
    "statistics": {
      "total_transactions": 1650,
      "total_gas_used": 165000000,
      "average_gas_used": 15000000,
      "total_block_size": 135795,
      "average_block_size": 12345,
      "unique_miners": 8,
      "gas_price_stats": {
        "min": "10000000000",
        "max": "25000000000",
        "average": "17500000000"
      },
      "block_time_stats": {
        "min": 11,
        "max": 15,
        "average": 12.5
      }
    }
  }
}
```

### 5. 智能合约工具

#### `read_contract`
读取智能合约数据

**参数:**
- `contract_address` (string, 必需): 合约地址
- `function_name` (string, 必需): 函数名称
- `function_args` (array, 可选): 函数参数
- `abi` (array, 可选): 合约 ABI
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "contract_address": "0x...",
    "function_name": "balanceOf",
    "function_args": ["0x..."],
    "result": "1000000000000000000",
    "decoded_result": {
      "type": "uint256",
      "value": "1000000000000000000"
    }
  }
}
```

#### `get_contract_info`
获取合约基本信息

**参数:**
- `contract_address` (string, 必需): 合约地址
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "address": "0x...",
    "network": "ethereum",
    "is_contract": true,
    "code_size": 12345,
    "code_hash": "0x...",
    "balance": {
      "wei": "0",
      "ether": "0"
    },
    "creation_info": {
      "creator": "0x...",
      "transaction_hash": "0x...",
      "block_number": 12345678
    }
  }
}
```

#### `estimate_contract_gas`
估算合约函数调用 Gas

**参数:**
- `contract_address` (string, 必需): 合约地址
- `function_name` (string, 必需): 函数名称
- `function_args` (array, 可选): 函数参数
- `from_address` (string, 必需): 调用者地址
- `abi` (array, 可选): 合约 ABI
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "contract_address": "0x...",
    "function_name": "transfer",
    "gas_estimate": 65000,
    "gas_price": {
      "wei": "20000000000",
      "gwei": "20"
    },
    "estimated_cost": {
      "wei": "1300000000000000",
      "ether": "0.0013"
    }
  }
}
```

#### `get_contract_events`
获取合约事件日志

**参数:**
- `contract_address` (string, 必需): 合约地址
- `event_name` (string, 可选): 事件名称
- `from_block` (integer, 可选): 起始区块
- `to_block` (integer, 可选): 结束区块
- `abi` (array, 可选): 合约 ABI
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "contract_address": "0x...",
    "event_name": "Transfer",
    "from_block": 18500000,
    "to_block": 18500100,
    "events": [
      {
        "address": "0x...",
        "topics": ["0x...", "0x...", "0x..."],
        "data": "0x...",
        "block_number": 18500050,
        "transaction_hash": "0x...",
        "log_index": 5,
        "decoded_event": {
          "event": "Transfer",
          "args": {
            "from": "0x...",
            "to": "0x...",
            "value": "1000000000000000000"
          }
        }
      }
    ]
  }
}
```

### 6. ENS 工具

#### `resolve_ens_name`
解析 ENS 域名到地址

**参数:**
- `ens_name` (string, 必需): ENS 域名（如 vitalik.eth）
- `network` (string, 可选): 网络名称（必须支持 ENS）

**返回示例:**
```json
{
  "success": true,
  "data": {
    "ens_name": "vitalik.eth",
    "resolved_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "network": "ethereum",
    "text_records": {
      "avatar": "https://...",
      "email": "vitalik@ethereum.org",
      "url": "https://vitalik.ca",
      "twitter": "VitalikButerin",
      "github": "vbuterin"
    }
  }
}
```

#### `reverse_resolve_ens`
反向解析地址到 ENS 域名

**参数:**
- `address` (string, 必需): 以太坊地址
- `network` (string, 可选): 网络名称（必须支持 ENS）

**返回示例:**
```json
{
  "success": true,
  "data": {
    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "ens_name": "vitalik.eth",
    "network": "ethereum",
    "verified": true
  }
}
```

#### `get_ens_records`
获取 ENS 域名的所有记录

**参数:**
- `ens_name` (string, 必需): ENS 域名
- `network` (string, 可选): 网络名称（必须支持 ENS）

**返回示例:**
```json
{
  "success": true,
  "data": {
    "ens_name": "vitalik.eth",
    "network": "ethereum",
    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "content_hash": "0x...",
    "text_records": {
      "avatar": "https://...",
      "description": "Ethereum co-founder",
      "display": "Vitalik Buterin",
      "email": "vitalik@ethereum.org",
      "keywords": "ethereum,blockchain",
      "mail": "vitalik@ethereum.org",
      "notice": "Public figure",
      "location": "Global",
      "phone": "",
      "url": "https://vitalik.ca",
      "com.github": "vbuterin",
      "com.twitter": "VitalikButerin",
      "com.discord": "",
      "com.reddit": "",
      "com.telegram": ""
    }
  }
}
```

### 7. 网络和工具

#### `get_supported_networks`
获取支持的网络列表

**参数:** 无

**返回示例:**
```json
{
  "success": true,
  "data": {
    "networks": ["ethereum", "polygon", "bsc", "arbitrum", "optimism", "base", "avalanche", "fantom", "sepolia", "goerli"],
    "default_network": "ethereum",
    "network_details": {
      "ethereum": {
        "name": "Ethereum Mainnet",
        "chain_id": 1,
        "rpc_url": "https://...",
        "explorer": "https://etherscan.io",
        "native_token": "ETH",
        "supports_ens": true
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
    "network": "ethereum",
    "connected": true,
    "chain_id": 1,
    "latest_block": {
      "number": 18500000,
      "hash": "0x...",
      "timestamp": 1704110400
    },
    "gas_price": {
      "wei": "20000000000",
      "gwei": "20",
      "ether": "0.00000002"
    }
  }
}
```

#### `get_gas_price`
获取当前 Gas 价格

**参数:**
- `network` (string, 可选): 网络名称

**返回示例:**
```json
{
  "success": true,
  "data": {
    "network": "ethereum",
    "gas_price": {
      "wei": "20000000000",
      "gwei": "20",
      "ether": "0.00000002"
    },
    "eip1559": {
      "base_fee": {
        "wei": "15000000000",
        "gwei": "15",
        "ether": "0.000000015"
      },
      "priority_fee": {
        "wei": "2000000000",
        "gwei": "2",
        "ether": "0.000000002"
      },
      "max_fee": {
        "wei": "32000000000",
        "gwei": "32",
        "ether": "0.000000032"
      }
    }
  }
}
```

#### `convert_units`
单位转换工具

**参数:**
- `amount` (string/number, 必需): 数量
- `from_unit` (string, 必需): 源单位（wei, gwei, ether）
- `to_unit` (string, 必需): 目标单位（wei, gwei, ether）

**返回示例:**
```json
{
  "success": true,
  "data": {
    "original": {
      "amount": "1",
      "unit": "ether"
    },
    "converted": {
      "amount": "1000000000000000000",
      "unit": "wei"
    },
    "all_units": {
      "wei": "1000000000000000000",
      "gwei": "1000000000",
      "ether": "1"
    }
  }
}
```

#### `validate_address`
验证以太坊地址格式

**参数:**
- `address` (string, 必需): 以太坊地址

**返回示例:**
```json
{
  "success": true,
  "data": {
    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "is_valid": true,
    "checksum_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "is_checksum": true,
    "format_info": {
      "length": 42,
      "has_0x_prefix": true,
      "is_lowercase": false,
      "is_uppercase": false
    }
  }
}
```

## 资源列表

### `evm://networks`
获取所有支持的 EVM 网络信息和配置

### `evm://status`
获取 EVM MCP 服务器当前状态和连接信息

### `evm://gas-tracker`
实时 Gas 价格跟踪器，显示所有网络的当前 Gas 价格

### `evm://latest-blocks`
最新区块信息，显示所有连接网络的最新区块

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
- `ENS 不支持` - 在不支持 ENS 的网络上调用 ENS 功能
- `交易未找到` - 指定的交易哈希不存在
- `区块未找到` - 指定的区块不存在
- `Gas 估算失败` - 无法估算交易 Gas 费用

## 使用示例

### 基础查询示例

#### 查询 Vitalik 的 ETH 余额
```json
{
  "tool": "get_balance",
  "arguments": {
    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "network": "ethereum"
  }
}
```

#### 查询 USDC 代币信息
```json
{
  "tool": "get_token_metadata",
  "arguments": {
    "token_address": "0xA0b86a33E6441b8C4505E2E8E3C3C4C8E6441b8C",
    "network": "ethereum"
  }
}
```

#### 解析 ENS 域名
```json
{
  "tool": "resolve_ens_name",
  "arguments": {
    "ens_name": "vitalik.eth",
    "network": "ethereum"
  }
}
```

### 高级查询示例

#### 分析最近 100 个区块
```json
{
  "tool": "analyze_block_range",
  "arguments": {
    "start_block": 18500000,
    "end_block": 18500100,
    "network": "ethereum"
  }
}
```

#### 查询合约事件
```json
{
  "tool": "get_contract_events",
  "arguments": {
    "contract_address": "0xA0b86a33E6441b8C4505E2E8E3C3C4C8E6441b8C",
    "event_name": "Transfer",
    "from_block": 18500000,
    "to_block": 18500100,
    "network": "ethereum"
  }
}
```

#### 估算合约调用 Gas
```json
{
  "tool": "estimate_contract_gas",
  "arguments": {
    "contract_address": "0xA0b86a33E6441b8C4505E2E8E3C3C4C8E6441b8C",
    "function_name": "transfer",
    "function_args": ["0x...", "1000000000000000000"],
    "from_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "network": "ethereum"
  }
}
```

## 最佳实践

1. **网络选择**: 根据您的需求选择合适的网络，主网用于生产环境，测试网用于开发测试
2. **错误处理**: 始终检查返回的 `success` 字段，并适当处理错误情况
3. **地址验证**: 在进行任何操作前，使用 `validate_address` 工具验证地址格式
4. **Gas 估算**: 在发送交易前，使用 Gas 估算工具预估费用
5. **ENS 支持**: 只在支持 ENS 的网络上使用 ENS 相关功能
6. **缓存**: 对于不经常变化的数据（如代币元数据），考虑在客户端进行缓存
7. **批量查询**: 对于需要查询多个数据的场景，考虑使用批量查询减少请求次数

## 版本信息

- **当前版本**: 2.0.0
- **MCP 协议版本**: 1.0.0
- **支持的 Web3 版本**: 6.0.0+
- **最后更新**: 2024-01-01