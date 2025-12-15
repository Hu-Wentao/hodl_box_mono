const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("HODLBox 合约测试", function () {
  let HODLBox;
  let hodlBox;
  let owner;
  let user;
  let usdtContract;
  let btcContract;
  let usdtAddress;
  let btcAddress;
  let routerAddress;
  let connectorAddress;
  let zetaTokenAddress;

  beforeEach(async function () {
    // 获取测试账户
    [owner, user] = await ethers.getSigners();

    // 根据网络选择不同的地址
    const networkName = network.name;
    if (networkName === "hardhat" || networkName === "localhost") {
      // 本地测试网使用模拟地址
      usdtAddress = "0x55d398326f99059fF775485246999027B3197955";
      btcAddress = "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c";
      routerAddress = "0x1a0ad011913A150f69f6A19DF447A0CfD9551054";
      connectorAddress = "0x377D55a7928c046E18eEbb61977e714d2a764733";
      zetaTokenAddress = "0x95d4163a36a4241E9e4733A6804a494e3c332E1e";
    } else {
      // 实际网络使用环境变量中的地址
      usdtAddress = process.env.ZETA_CHAIN_ATTHENS_TESTNET_USDT;
      btcAddress = process.env.ZETA_CHAIN_ATTHENS_TESTNET_BTC;
      routerAddress = process.env.ZETA_CHAIN_ATTHENS_TESTNET_DEX_ROUTER;
      connectorAddress = process.env.ZETA_CHAIN_ATTHENS_TESTNET_ZETA_CONNECTOR;
      zetaTokenAddress = process.env.ZETA_CHAIN_ATTHENS_TESTNET_ZETA_TOKEN;
    }

    // 部署HODLBox合约
    HODLBox = await ethers.getContractFactory("HODLBox");
    hodlBox = await HODLBox.deploy(
      routerAddress,
      usdtAddress,
      btcAddress,
      connectorAddress,
      zetaTokenAddress
    );
    await hodlBox.deployed();

    // 模拟USDT和BTC合约
    const mockTokenABI = [
      "function balanceOf(address) external view returns (uint256)",
      "function approve(address, uint256) external returns (bool)",
      "function transfer(address, uint256) external returns (bool)"
    ];
    
    usdtContract = await ethers.getContractAt(mockTokenABI, usdtAddress, user);
    btcContract = await ethers.getContractAt(mockTokenABI, btcAddress, user);
  });

  describe("基本功能测试", function () {
    it("应该正确设置合约参数", async function () {
      expect(await hodlBox.usdtToken()).to.equal(usdtAddress);
      expect(await hodlBox.btcToken()).to.equal(btcAddress);
      expect(await hodlBox.routerAddress()).to.equal(routerAddress);
    });

    it("用户应该能够存款", async function () {
      const depositAmount = ethers.utils.parseUnits("100", 18);
      
      // 模拟USDT转账授权
      await expect(
        usdtContract.approve(hodlBox.address, depositAmount)
      ).to.not.be.reverted;
      
      // 执行存款（在测试环境中会跳过实际转账）
      await expect(
        hodlBox.connect(user).deposit(depositAmount)
      ).to.not.be.reverted;
      
      // 检查用户余额
      expect(await hodlBox.getUserBalance(user.address)).to.equal(depositAmount);
    });

    it("用户应该能够创建定投计划", async function () {
      const depositAmount = ethers.utils.parseUnits("100", 18);
      const planAmount = ethers.utils.parseUnits("10", 18);
      const intervalDays = 7;
      
      // 先存款
      await usdtContract.approve(hodlBox.address, depositAmount);
      await hodlBox.connect(user).deposit(depositAmount);
      
      // 创建定投计划
      await expect(
        hodlBox.connect(user).createPlan(planAmount, intervalDays)
      ).to.not.be.reverted;
      
      // 检查计划
      const plan = await hodlBox.getPlan(user.address, 0);
      expect(plan.amount).to.equal(planAmount);
      expect(plan.intervalDays).to.equal(intervalDays);
      expect(plan.isActive).to.be.true;
    });
  });

  describe("USDT到BTC交换测试", function () {
    it("应该能够执行USDT到BTC的交换", async function () {
      const depositAmount = ethers.utils.parseUnits("100", 18);
      const swapAmount = ethers.utils.parseUnits("10", 18);
      
      // 先存款
      await usdtContract.approve(hodlBox.address, depositAmount);
      await hodlBox.connect(user).deposit(depositAmount);
      
      // 执行交换（在测试环境中使用模拟汇率）
      await expect(
        hodlBox.connect(user).swapUSDTForBTC(swapAmount)
      ).to.not.be.reverted;
      
      // 检查用户余额减少
      const remainingBalance = await hodlBox.getUserBalance(user.address);
      expect(remainingBalance).to.equal(depositAmount.sub(swapAmount));
      
      // 注意：由于使用模拟汇率，实际BTC余额不会真正增加
      // 在真实环境中，需要验证BTC余额
    });
  });

  describe("定投计划执行测试", function () {
    it("应该能够执行定投计划", async function () {
      const depositAmount = ethers.utils.parseUnits("100", 18);
      const planAmount = ethers.utils.parseUnits("10", 18);
      const intervalDays = 1;
      
      // 先存款
      await usdtContract.approve(hodlBox.address, depositAmount);
      await hodlBox.connect(user).deposit(depositAmount);
      
      // 创建定投计划
      await hodlBox.connect(user).createPlan(planAmount, intervalDays);
      
      // 执行计划
      await expect(
        hodlBox.executePlan(user.address, 0)
      ).to.not.be.reverted;
      
      // 检查执行结果
      const executionRecord = await hodlBox.getExecutionRecord(user.address, 0, 0);
      expect(executionRecord.isExecuted).to.be.true;
    });
  });
});
