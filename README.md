# 韭菜罐子 (HODL Box) 

> 韭菜的存钱罐 HODL!
> Save first, HODL smarter

韭菜罐子是一个集智能合约、AI 助手和 Web 应用于一体的智能定投平台，旨在帮助用户建立长期投资习惯，抵御市场波动带来的心理压力。

## 项目结构

```
hodl_box_mono/
├── hodl_agent/     # AI 心理按摩助手
├── hodl_contract/  # 智能合约代码
└── hodl_web/       # Web 前端应用
```

## 核心功能

### 🤖 AI Agent (hodl_agent)
- 情绪分析：识别用户的投资焦虑情绪
- 市场状态判断：基于历史数据提供市场分析
- 心理按摩：生成激励性回应，帮助用户坚持长期投资理念
- 用户配置管理：记录用户偏好和投资目标

### 📝 智能合约 (hodl_contract)
- 安全存款/提款功能
- 自动定投计划创建与执行
- DEX 路由管理
- 基于 OpenZeppelin 的安全实现

### 💻 Web 应用 (hodl_web)
- 用户友好的界面展示资产概览
- 简单直观的定投计划管理
- 实时的 AI 心理按摩聊天功能
- 响应式设计，适配各种设备

## 技术栈

### AI Agent
- **语言**：Python
- **依赖管理**：uv
- **核心依赖**：OpenAI API, Pandas, Matplotlib

### 智能合约
- **语言**：Solidity
- **框架**：Hardhat
- **核心依赖**：OpenZeppelin Contracts

### Web 应用
- **框架**：Next.js 16
- **前端库**：React 19
- **样式**：Tailwind CSS
- **包管理**：pnpm

## 开发指南

### 安装与运行

#### AI Agent
```bash
cd hodl_agent
uv venv
uv sync
python main.py
```

#### 智能合约
```bash
cd hodl_contract
npm install
npx hardhat compile
```

#### Web 应用
```bash
cd hodl_web
pnpm install
pnpm dev
```

## 项目理念

韭菜罐子的核心理念是 "Save first, HODL smarter" - 先储蓄，更聪明地持有。通过自动化定投和 AI 心理支持，我们希望帮助用户建立健康的投资习惯，避免情绪化交易，最终实现长期财富增长。