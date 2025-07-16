# EVM MCP Server

一个基于 Model Context Protocol (MCP) 的以太坊虚拟机区块链数据服务器，提供全面的区块链数据查询和交互功能。

## 🌟 特性

- **多网络支持**: 支持 10+ EVM 兼容网络（Ethereum、Polygon、BSC、Arbitrum、Optimism、Base 等）
- **全面的工具集**: 提供 20+ 个专业的区块链查询工具
- **ENS 支持**: 完整的 ENS 域名解析和反向解析功能
- **智能合约交互**: 支持合约读取、事件查询、Gas 估算
- **交易分析**: 详细的交易信息、收据查询、输入数据解码
- **区块数据**: 区块查询、范围分析、统计信息
- **实时数据**: Gas 价格跟踪、网络状态监控
- **MCP 标准**: 完全符合 Model Context Protocol 规范

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/WonderLand33/evm-mcp-server.git
cd evm-mcp-server

# 安装依赖
pip install -r requirements.txt
```

### 配置

创建 `.env` 文件：

```env
# RPC 节点配置
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID
BSC_RPC_URL=https://bsc-dataseed.binance.org/

# API 密钥
ETHERSCAN_API_KEY=your_etherscan_api_key
COINGECKO_API_KEY=your_coingecko_api_key

# 服务配置
DEFAULT_NETWORK=ethereum
CACHE_TTL=300
RATE_LIMIT=100
```

### 使用方法

```bash
python -m src
```

## 📖 文档

- **[连接指南](docs/connection-guide.md)** - 详细的客户端连接说明，包括 Cursor、Claude Desktop 等
- **[API 文档](docs/api.md)** - 完整的工具和 API 参考
- **[安装指南](INSTALL.md)** - 详细的安装和配置说明

## 🔗 连接到客户端

### Cursor

在 Cursor 中配置 MCP 服务器：

```json
{
  "mcpServers": {
    "evm-mcp-server": {
      "command": "python",
      "args": ["-m", "src"],
      "cwd": "/path/to/evm-mcp-server"
    }
  }
}
```

### Claude Desktop

编辑 Claude Desktop 配置文件：

```json
{
  "mcpServers": {
    "evm-mcp-server": {
      "command": "python",
      "args": ["-m", "src"],
      "cwd": "/path/to/evm-mcp-server"
    }
  }
}
```

详细连接说明请参阅 [连接指南](docs/connection-guide.md)。

## 🛠️ 主要工具

### 账户和余额
- `get_balance` - 查询原生代币余额
- `get_token_balance` - 查询 ERC20 代币余额
- `get_account_info` - 获取账户综合信息

### 代币信息
- `get_token_metadata` - 查询代币元数据
- `get_token_price` - 获取代币价格
- `search_tokens` - 搜索代币信息

### 交易分析
- `get_transaction` - 获取交易详情
- `get_transaction_receipt` - 获取交易收据
- `estimate_gas` - 估算 Gas 费用
- `decode_transaction_input` - 解码交易数据

### 区块数据
- `get_block` - 获取区块信息
- `get_latest_blocks` - 获取最新区块
- `analyze_block_range` - 分析区块范围

### 智能合约
- `read_contract` - 读取合约数据
- `get_contract_info` - 获取合约信息
- `estimate_contract_gas` - 估算合约调用 Gas
- `get_contract_events` - 查询合约事件

### ENS 服务
- `resolve_ens_name` - 解析 ENS 域名
- `reverse_resolve_ens` - 反向解析地址
- `get_ens_records` - 获取 ENS 记录

### 网络工具
- `get_supported_networks` - 获取支持的网络
- `get_network_status` - 检查网络状态
- `get_gas_price` - 获取 Gas 价格
- `convert_units` - 单位转换
- `validate_address` - 地址验证

## 🌐 支持的网络

### 主网络
- **Ethereum Mainnet** - 支持 ENS
- **Polygon**
- **Binance Smart Chain**
- **Arbitrum One** - 支持 ENS
- **Optimism** - 支持 ENS
- **Base** - 支持 ENS
- **Avalanche C-Chain**
- **Fantom Opera**

### 测试网络
- **Ethereum Sepolia** - 支持 ENS
- **Ethereum Goerli** - 支持 ENS

## 📊 使用示例

### 查询余额
```
请帮我查询地址 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 在以太坊主网上的余额
```

### 解析 ENS 域名
```
请解析 vitalik.eth 这个 ENS 域名对应的地址
```

### 分析交易
```
请分析交易 0x... 的详细信息，包括 Gas 使用情况
```

### 查询代币信息
```
请查询 USDC 代币的详细信息和当前价格
```

## 🔧 开发

### 项目结构

```
evm-mcp-server/
├── src/                    # 主要代码
│   ├── tools/               # 工具模块
│   ├── config.py           # 配置管理
│   ├── server.py           # MCP 服务器
│   ├── utils.py            # 工具函数
│   └── web3_manager.py     # Web3 连接管理
├── docs/                   # 文档
├── tests/                  # 测试文件
└── requirements.txt        # 依赖列表
```

### 测试

```bash
python test_server.py
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请查看：
1. [连接指南](docs/connection-guide.md)
2. [API 文档](docs/api.md)
3. [安装指南](INSTALL.md)
4. [GitHub Issues](https://github.com/WonderLand33/evm-mcp-server/issues)