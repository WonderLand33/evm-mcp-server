@echo off
echo 启动 EVM MCP 服务器...
echo.

REM 检查是否安装了依赖
python -c "import web3, requests, dotenv" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    echo.
)

REM 检查是否存在 .env 文件
if not exist .env (
    echo 警告: 未找到 .env 文件，将使用默认配置
    echo 建议复制 .env.example 为 .env 并配置您的 API 密钥
    echo.
)

REM 启动服务器
echo 启动 EVM MCP 服务器...
python -m src

pause