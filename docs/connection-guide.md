# EVM MCP Server 连接指南

本指南将帮助您将 EVM MCP Server 连接到各种 MCP 客户端，包括 Cursor、Claude Desktop 等。

## 目录
- [连接到 Cursor](#连接到-cursor)
- [连接到 Claude Desktop](#连接到-claude-desktop)
- [连接到其他 MCP 客户端](#连接到其他-mcp-客户端)
- [故障排除](#故障排除)

## 连接到 Cursor

Cursor 是一个 AI 驱动的代码编辑器，支持 MCP 协议。以下是连接步骤：

### 1. 安装和配置 EVM MCP Server

首先确保您已经正确安装了 EVM MCP Server：

```bash
# 克隆项目
git clone https://github.com/WonderLand33/evm-mcp-server.git
cd evm-mcp-server

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，添加您的 API 密钥
```

### 2. 配置 Cursor

在 Cursor 中配置 MCP 服务器：

#### 方法一：通过 Cursor 设置界面

1. 打开 Cursor
2. 进入 `Settings` > `Extensions` > `MCP Servers`
3. 添加新的 MCP 服务器配置：
   - **Name**: `EVM MCP Server`
   - **Command**: `python`
   - **Args**: `["-m", "src"]`
   - **Working Directory**: `/path/to/evm-mcp-server`

#### 方法二：通过配置文件

创建或编辑 Cursor 的 MCP 配置文件（通常位于 `~/.cursor/mcp-servers.json`）：

```json
{
  "mcpServers": {
    "evm-mcp-server": {
      "command": "python",
      "args": ["-m", "src"],
      "cwd": "/path/to/evm-mcp-server",
      "env": {
        "PYTHONPATH": "/path/to/evm-mcp-server"
      }
    }
  }
}
```

### 3. 启动和验证连接

1. 重启 Cursor
2. 在 Cursor 中打开一个项目
3. 使用 AI 助手时，您应该能够看到 EVM MCP Server 提供的工具
4. 测试连接：询问 AI 助手关于以太坊地址余额或网络状态

### 4. 使用示例

在 Cursor 中，您可以这样使用 EVM MCP Server：

```
请帮我查询地址 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 在以太坊主网上的余额
```

AI 助手将使用 EVM MCP Server 的 `get_balance` 工具来获取信息。

## 连接到 Claude Desktop

### 1. 配置 Claude Desktop

编辑 Claude Desktop 的配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

### 2. 重启 Claude Desktop

配置完成后，重启 Claude Desktop 应用程序。

## 连接到其他 MCP 客户端

### 通用 MCP 客户端配置

对于支持 MCP 协议的其他客户端，通常需要提供以下信息：

- **服务器类型**: stdio
- **命令**: `python -m src`
- **工作目录**: EVM MCP Server 项目根目录
- **环境变量**: 可选的 API 密钥等

### 命令行测试

您也可以通过命令行直接测试 MCP 服务器：

```bash
# 启动服务器
python -m src

# 或使用提供的脚本
./start_server.sh  # Linux/Mac
start_server.bat   # Windows
```

## 高级配置

### 环境变量配置

创建 `.env` 文件来配置 API 密钥和 RPC 节点：

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

### 网络配置

EVM MCP Server 支持多个 EVM 兼容网络：

- **主网**: Ethereum, Polygon, BSC, Arbitrum, Optimism, Base, Avalanche, Fantom
- **测试网**: Sepolia, Goerli

您可以在配置中指定默认网络或在工具调用时指定特定网络。

## 故障排除

### 常见问题

1. **连接失败**
   - 检查 Python 环境和依赖是否正确安装
   - 确认工作目录路径正确
   - 查看服务器日志输出

2. **工具不可用**
   - 验证 MCP 客户端是否正确识别服务器
   - 检查服务器是否成功启动
   - 确认网络连接正常

3. **API 调用失败**
   - 检查 RPC 节点 URL 是否有效
   - 验证 API 密钥是否正确配置
   - 确认网络连接和防火墙设置

### 调试模式

启用详细日志记录：

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG
python -m src
```

### 测试连接

使用提供的测试脚本验证功能：

```bash
python test_server.py
```

## 支持的功能

EVM MCP Server 提供以下主要功能类别：

- **账户管理**: 余额查询、账户信息、地址验证
- **代币操作**: ERC20 代币信息、价格查询、代币搜索
- **交易分析**: 交易详情、收据查询、Gas 估算
- **区块数据**: 区块信息、区块范围分析
- **智能合约**: 合约交互、事件查询
- **ENS 服务**: 域名解析、反向解析
- **网络工具**: 网络状态、单位转换

有关完整的工具列表和使用方法，请参阅 [API 文档](api.md)。