# HODLBox 智能合约

这是一个基于ZetaChain的HODLBox智能合约项目，实现了USDT到BTC的自动定投功能。

## 项目结构

```
./
├── contracts/           # 智能合约源代码
│   └── HODLBox.sol      # HODLBox主合约
├── scripts/             # 部署和交互脚本
│   ├── deploy.js        # 部署脚本
│   └── interact.js      # 交互演示脚本
├── test/                # 测试脚本
│   └── HODLBox.test.js  # 单元测试
├── hardhat.config.js    # Hardhat配置文件
├── .env                 # 环境变量配置
├── package.json         # 项目依赖
└── README.md            # 项目说明文档
```

## 功能特性

- **存款功能**: 用户可以存入USDT代币
- **定投计划**: 创建、执行和取消USDT到BTC的定投计划
- **余额查询**: 查询用户的USDT和BTC余额
- **安全保障**: 简化版实现了基本的资金安全控制

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

编辑`.env`文件，添加以下配置：

```
# 私钥配置
PRIVATE_KEY=your_private_key_here

# ZetaChain Athens测试网配置
ZETA_CHAIN_ATTHENS_TESTNET_DEX_ROUTER=0x1a0ad011913A150f69f6A19DF447A0CfD9551054
ZETA_CHAIN_ATTHENS_TESTNET_USDT=0x55d398326f99059fF775485246999027B3197955
ZETA_CHAIN_ATTHENS_TESTNET_BTC=0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c
ZETA_CHAIN_ATTHENS_TESTNET_ZETA_CONNECTOR=0x377d55a7928c046e18eebb61977e714d2a764733
ZETA_CHAIN_ATTHENS_TESTNET_ZETA_TOKEN=0x95d4163a36a4241e9e4733a6804a494e3c332e1e
```

### 3. 编译合约

```bash
npx hardhat compile
```

### 4. 运行测试

```bash
npx hardhat test
```

### 5. 部署合约

部署到ZetaChain Athens测试网：

```bash
npx hardhat run scripts/deploy.js --network zeta-athens-testnet
```

注意：部署前请确保账户有足够的ZETA代币支付gas费用。

### 6. 与合约交互

```bash
npx hardhat run scripts/interact.js --network zeta-athens-testnet
```

请先在interact.js中更新合约地址，然后取消注释相应的交互代码块。

## 合约接口说明

### 主要函数

- `deposit(uint256 amount)`: 存款USDT
- `createDCAPlan(uint256 amountPerInterval, uint256 intervalSeconds, uint256 totalIntervals)`: 创建定投计划
- `executeDCAPlan(uint256 planId)`: 执行定投计划
- `cancelDCAPlan(uint256 planId)`: 取消定投计划
- `getUserBalance(address user)`: 查询用户USDT余额
- `getUserBTCBalance(address user)`: 查询用户BTC余额
- `getDCAPlan(uint256 planId)`: 查询定投计划详情

## 注意事项

1. **测试网环境**: 当前配置使用的是ZetaChain Athens测试网
2. **资金安全**: 本项目为演示版本，请谨慎处理实际资金
3. **Gas费用**: 确保账户有足够的代币支付交易费用
4. **版本兼容性**: 使用Solidity 0.8.17版本

## 开发说明

- 合约已简化实现USDT到BTC的兑换逻辑
- 测试脚本涵盖了主要功能的单元测试
- 部署脚本支持多网络配置

## 许可证

MIT
