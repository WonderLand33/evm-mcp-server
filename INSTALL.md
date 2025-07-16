# 安装和使用指南

## 前置要求

### 1. 安装 Python
请确保您的系统已安装 Python 3.8 或更高版本：

**Windows:**
- 从 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python
- 或者从 Microsoft Store 安装 Python

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS (使用 Homebrew)
brew install python3
```

### 2. 验证安装
```bash
python --version
# 或
python3 --version
```

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/WonderLand33/evm-mcp-server.git
cd evm-mcp-server
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量（可选）
```bash
cp .env.example .env
# 编辑 .env 文件，添加您的 API 密钥
```

### 4. 运行测试
```bash
python test_server.py
```

### 5. 启动服务器
```bash
# Windows
start_server.bat

# Linux/Mac
chmod +x start_server.sh
./start_server.sh

# 或直接使用 Python
python -m evm_mcp_server
```

## 配置说明

### API 密钥配置
为了获得更好的服务质量，建议配置以下 API 密钥：

1. **Infura/Alchemy** - 用于区块链 RPC 连接
2. **Etherscan** - 用于获取详细的区块链数据
3. **CoinGecko** - 用于获取代币价格信息

### 网络配置
默认支持以下网络：
- Ethereum Mainnet
- Polygon
- Binance Smart Chain
- Arbitrum One
- Optimism

## 故障排除

### 常见问题

1. **Python 未找到**
   - 确保已正确安装 Python
   - 检查 PATH 环境变量

2. **依赖安装失败**
   - 尝试升级 pip: `pip install --upgrade pip`
   - 使用虚拟环境: `python -m venv venv && source venv/bin/activate`

3. **网络连接失败**
   - 检查网络连接
   - 验证 RPC URL 是否正确
   - 确认 API 密钥是否有效

4. **权限错误**
   - Linux/Mac: 使用 `chmod +x start_server.sh`
   - Windows: 以管理员身份运行

## 开发指南

### 项目结构
```
evm-mcp-server/
├── evm_mcp_server/          # 主要代码
│   ├── tools/               # 工具模块
│   ├── config.py           # 配置管理
│   ├── server.py           # MCP 服务器
│   ├── utils.py            # 工具函数
│   └── web3_manager.py     # Web3 连接管理
├── docs/                   # 文档
├── tests/                  # 测试文件
└── requirements.txt        # 依赖列表
```

### 添加新功能
1. 在 `tools/` 目录下创建新的工具模块
2. 在 `server.py` 中注册新工具
3. 更新 API 文档
4. 添加测试用例

## 许可证

MIT License - 详见 LICENSE 文件