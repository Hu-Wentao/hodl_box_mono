// interact.js - 用于与HODLBox合约交互的脚本
require('dotenv').config();
const { ethers } = require('hardhat');

async function main() {
  console.log('开始与HODLBox合约交互...');

  // 获取签名者
  const [deployer] = await ethers.getSigners();
  console.log('使用账户:', deployer.address);
  console.log('账户余额:', (await ethers.provider.getBalance(deployer.address)).toString());

  // 合约ABI（简化版，用于交互）
  const hodlBoxAbi = [
    'function deposit(uint256 amount) external',
    'function createDCAPlan(uint256 amountPerInterval, uint256 intervalSeconds, uint256 totalIntervals) external returns (uint256)',
    'function executeDCAPlan(uint256 planId) external',
    'function getUserBalance(address user) external view returns (uint256)',
    'function getUserBTCBalance(address user) external view returns (uint256)',
    'function getDCAPlan(uint256 planId) external view returns (address, uint256, uint256, uint256, uint256, uint256, bool)',
    'function cancelDCAPlan(uint256 planId) external'
  ];

  // 这里需要替换为实际部署的合约地址
  // 由于我们没有实际部署（余额不足），这里使用一个示例地址
  const hodlBoxAddress = '0x1234567890123456789012345678901234567890';
  
  try {
    // 连接到合约
    const hodlBox = new ethers.Contract(hodlBoxAddress, hodlBoxAbi, deployer);
    console.log('已连接到HODLBox合约:', hodlBoxAddress);

    // ===== 演示功能1: 存款 =====
    console.log('\n=== 演示存款功能 ===');
    const depositAmount = ethers.parseUnits('100', 18); // 100 USDT (假设18位小数)
    console.log(`准备存款: ${ethers.formatUnits(depositAmount, 18)} USDT`);
    
    // 实际交互时取消注释下面的代码
    /*
    const depositTx = await hodlBox.deposit(depositAmount);
    console.log('存款交易已发送，等待确认...');
    await depositTx.wait();
    console.log('存款成功！交易哈希:', depositTx.hash);
    */

    // ===== 演示功能2: 查询余额 =====
    console.log('\n=== 演示查询余额功能 ===');
    
    // 实际交互时取消注释下面的代码
    /*
    const userBalance = await hodlBox.getUserBalance(deployer.address);
    console.log(`用户USDT余额: ${ethers.formatUnits(userBalance, 18)} USDT`);
    
    const userBTCBalance = await hodlBox.getUserBTCBalance(deployer.address);
    console.log(`用户BTC余额: ${ethers.formatUnits(userBTCBalance, 8)} BTC`); // BTC通常是8位小数
    */

    // ===== 演示功能3: 创建定投计划 =====
    console.log('\n=== 演示创建定投计划功能 ===');
    const amountPerInterval = ethers.parseUnits('10', 18); // 每次定投10 USDT
    const intervalSeconds = 86400; // 24小时 (1天)
    const totalIntervals = 30; // 总共30次
    
    console.log(`准备创建定投计划:\n  - 每次金额: ${ethers.formatUnits(amountPerInterval, 18)} USDT\n  - 间隔: ${intervalSeconds / 3600} 小时\n  - 总次数: ${totalIntervals}`);
    
    // 实际交互时取消注释下面的代码
    /*
    const createTx = await hodlBox.createDCAPlan(amountPerInterval, intervalSeconds, totalIntervals);
    console.log('创建定投计划交易已发送，等待确认...');
    const receipt = await createTx.wait();
    
    // 解析事件获取planId
    const planCreatedEvent = receipt.logs.find(log => log.topics[0] === ethers.id('DCAPlanCreated(uint256,address,uint256,uint256,uint256)'));
    if (planCreatedEvent) {
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(['uint256'], planCreatedEvent.data);
      const planId = decoded[0];
      console.log('定投计划创建成功！计划ID:', planId.toString());
      
      // 查询创建的计划
      const plan = await hodlBox.getDCAPlan(planId);
      console.log('定投计划详情:', {
        user: plan[0],
        amountPerInterval: ethers.formatUnits(plan[1], 18),
        intervalSeconds: plan[2].toString(),
        totalIntervals: plan[3].toString(),
        executedIntervals: plan[4].toString(),
        createdAt: new Date(plan[5].toNumber() * 1000).toLocaleString(),
        active: plan[6]
      });
    }
    */

    // ===== 演示功能4: 执行定投计划 =====
    console.log('\n=== 演示执行定投计划功能 ===');
    const planId = 1; // 假设这是我们创建的计划ID
    
    console.log(`准备执行定投计划 ID: ${planId}`);
    
    // 实际交互时取消注释下面的代码
    /*
    const executeTx = await hodlBox.executeDCAPlan(planId);
    console.log('执行定投计划交易已发送，等待确认...');
    await executeTx.wait();
    console.log('定投计划执行成功！USDT已兑换为BTC');
    
    // 再次查询BTC余额确认
    const updatedBTCBalance = await hodlBox.getUserBTCBalance(deployer.address);
    console.log(`更新后的BTC余额: ${ethers.formatUnits(updatedBTCBalance, 8)} BTC`);
    */

    // ===== 演示功能5: 取消定投计划 =====
    console.log('\n=== 演示取消定投计划功能 ===');
    
    // 实际交互时取消注释下面的代码
    /*
    const cancelTx = await hodlBox.cancelDCAPlan(planId);
    console.log('取消定投计划交易已发送，等待确认...');
    await cancelTx.wait();
    console.log('定投计划已取消！');
    */

    console.log('\n所有功能演示完成！请注意：由于当前是模拟环境，实际交易被注释掉了。');
    console.log('要实际执行交易，请取消相应代码块的注释。');
    
  } catch (error) {
    console.error('交互过程中发生错误:', error.message);
    console.error('请注意：如果合约未部署，需要先部署合约再进行交互。');
  }
}

// 执行主函数
main()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error);
    process.exit(1);
  });
