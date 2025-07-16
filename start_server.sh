#!/bin/bash

echo "启动 EVM MCP 服务器..."
echo

# 检查是否安装了依赖
python3 -c "import web3, requests, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
    echo
fi

# 检查是否存在 .env 文件
if [ ! -f .env ]; then
    echo "警告: 未找到 .env 文件，将使用默认配置"
    echo "建议复制 .env.example 为 .env 并配置您的 API 密钥"
    echo
fi

# 启动服务器
echo "启动 EVM MCP 服务器..."
python3 -m src