# HODL Box Agent

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

HODL Box Agent 是一个基于Python的AI助手系统，专为加密货币投资者设计，提供交易意图识别、智能合约操作和投资心理支持等功能。

## 项目简介

HODL Box Agent 集成了先进的大语言模型(LLM)能力和区块链交互功能，旨在为加密货币投资者提供全方位的智能助手服务。系统通过RESTful API提供服务，可以与各种前端应用集成。

## 主要功能

- **交易意图识别**: 解析用户的交易请求，提取代币交换所需的关键信息
- **智能合约操作**: 支持与区块链智能合约的交互，如代币交换、授权等
- **市场数据分析**: 提供加密货币市场数据和趋势分析
- **投资心理支持**: 在市场波动期间为投资者提供情绪支持和鼓励
- **统一聊天接口**: 自动识别用户意图并路由到相应的功能模块

## 技术栈

- **Python 3.9+**: 主要开发语言
- **FastAPI**: 高性能Web框架，用于构建API端点
- **Qwen Agent**: 基于通义千问大模型的AI Agent框架
- **Web3.py**: 与以太坊及兼容区块链交互的Python库
- **Uvicorn**: ASGI服务器，用于运行FastAPI应用
- **dotenv**: 环境变量管理

## 安装与配置

### 系统要求

- Python 3.9 或更高版本
- pip 或 uv 包管理器

### 安装步骤

1. 克隆项目仓库

```bash
git clone <repository-url>
cd hodl_box_mono/hodl_agent
```

2. 使用 uv 安装依赖

```bash
uv sync
```

或使用 pip

```bash
pip install -e .
```

### 环境变量配置

复制环境变量示例文件并根据需要修改

```bash
cp .env.example .env
```

配置文件中需要设置以下关键参数:

- `BASE_URL`: 自定义API服务的基础URL
- `API_KEY`: API访问密钥
- `ETH_RPC_URL`: 以太坊RPC节点URL
- `PRIVATE_KEY`: （可选）用于区块链交易的私钥
- `APP_PORT`: API服务端口，默认为8000
- `DEBUG`: 是否启用调试模式，默认为False

## 项目结构

```
hodl_agent/
├── agents/              # AI Agent 实现
│   ├── __init__.py
│   ├── base_agent.py    # Agent基类
│   ├── swap_agent.py    # 交易Agent
│   ├── mental_support_agent.py  # 心理支持Agent
│   └── tools/           # Agent工具集
│       ├── __init__.py
│       ├── swap_tools.py      # 交易工具
│       ├── market_tools.py    # 市场数据工具
│       └── contract_tools.py  # 智能合约工具
├── api.py               # FastAPI接口实现
├── pyproject.toml       # 项目配置和依赖管理
├── .env.example         # 环境变量示例
├── .gitignore           # Git忽略文件
└── README.md            # 项目文档
```

## API文档

启动服务后，可以通过以下URL访问自动生成的交互式API文档:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

#### 健康检查

```
GET /health
```

检查API服务是否正常运行

#### 代币交换处理

```
POST /api/swap
```

解析用户的代币交换请求

请求体:
```json
{
  "message": "把100U换成BTC",
  "chain": "Ethereum"
}
```

#### 心理支持

```
POST /api/mental-support
```

为用户提供投资心理支持

请求体:
```json
{
  "message": "市场大跌，我很担心我的投资",
  "market_state": "bear_market"
}
```

#### 市场数据查询

```
POST /api/market-data
```

获取加密货币市场数据

请求体:
```json
{
  "symbol": "BTC",
  "vs_currency": "USD",
  "include_market_state": true
}
```

#### 智能合约调用

```
POST /api/contract-call
```

执行智能合约调用

请求体:
```json
{
  "contract_address": "0xContractAddress",
  "function_name": "balanceOf",
  "function_args": ["0xWalletAddress"],
  "is_write_operation": false
}
```

#### 通用聊天接口

```
POST /api/chat
```

自动识别用户意图并路由到相应功能

请求体:
```json
{
  "message": "BTC现在价格多少？"
}
```

## 使用示例

### 启动API服务

```bash
# 使用脚本启动
python -m api

# 或使用uv命令
uv run api:run_server
```

### 调用API示例

#### Python示例

```python
import requests
import json

# 代币交换请求
url = "http://localhost:8000/api/swap"
data = {
    "message": "我想把50个ETH换成USDT",
    "chain": "Ethereum"
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

#### 市场数据查询

```python
import requests
import json

url = "http://localhost:8000/api/market-data"
data = {
    "symbol": "BTC",
    "vs_currency": "USD"
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

## 开发指南

### 添加新Agent

1. 在 `agents/` 目录下创建新的Agent类，继承自 `HODLBoxAgent`
2. 实现必要的处理方法和逻辑
3. 在 `api.py` 中注册新的API端点

### 添加新工具

1. 在 `agents/tools/` 目录下创建新的工具类，继承自 `BaseTool`
2. 使用 `@register_tool` 装饰器注册工具
3. 在Agent初始化时将工具添加到工具列表中

## 测试

在开发过程中，可以使用FastAPI内置的交互式文档进行API测试。

```bash
# 运行服务
python -m api
```

然后访问 http://localhost:8000/docs 进行测试。

## 安全注意事项

- 私钥应妥善保管，避免硬编码在代码中或提交到版本控制系统
- 在生产环境中，应限制API访问来源，设置合适的认证和授权机制
- 对于区块链交易，建议实施交易金额限制和多重确认机制

## 许可证

MIT
