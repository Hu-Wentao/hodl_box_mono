// 加载环境变量
require('dotenv').config();

async function main() {
  const [deployer] = await ethers.getSigners();
  const network = await ethers.provider.getNetwork();
  const networkName = network.name;

  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await ethers.provider.getBalance(deployer.address)).toString());
  console.log("Network:", networkName, "(Chain ID:", network.chainId, ")");

  // 根据不同网络使用不同的参数
  let routerAddress, usdtAddress, btcAddress, zetaConnectorAddress, zetaTokenAddress;

  // 使用ethers.utils.getAddress修复地址校验和问题
  function normalizeAddress(address) {
    if (!address || typeof address !== 'string') return address;
    try {
      return ethers.utils.getAddress(address);
    } catch (e) {
      console.warn(`Warning: Invalid address format: ${address}`);
      return address;
    }
  }
  
  // ZetaChain Athens测试网参数 (chainId 7001)
  if (network.chainId === 7001 || networkName === "zeta-athens-testnet") {
    console.log("Using ZetaChain Athens Testnet configuration");
    // 从环境变量加载地址
    routerAddress = normalizeAddress(process.env.ZETA_CHAIN_ATTHENS_TESTNET_DEX_ROUTER || "0xYourZetaChainDEXRouterAddress");
    usdtAddress = normalizeAddress(process.env.ZETA_CHAIN_ATTHENS_TESTNET_USDT || "0xYourZetaChainUSDTAddress");
    btcAddress = normalizeAddress(process.env.ZETA_CHAIN_ATTHENS_TESTNET_BTC || "0xYourZetaChainBTCAddress");
    // 使用正确校验和的ZetaConnector地址
      zetaConnectorAddress = "0x377d55a7928c046e18eebb61977e714d2a764733";
    // 使用正确校验和的ZetaToken地址
      zetaTokenAddress = "0x95d4163a36a4241e9e4733a6804a494e3c332e1e";
    
    console.log("Using addresses from environment variables:");
    console.log(`  Router: ${routerAddress}`);
    console.log(`  USDT: ${usdtAddress}`);
    console.log(`  BTC: ${btcAddress}`);
    console.log(`  Connector: ${zetaConnectorAddress}`);
    console.log(`  Zeta Token: ${zetaTokenAddress}`);
  }
  // ZetaChain本地开发网络参数
  else if (network.chainId === 7000) {
    console.log("Using ZetaChain Local Development configuration");
    routerAddress = normalizeAddress(process.env.ZETA_CHAIN_LOCAL_DEX_ROUTER || "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D");
    usdtAddress = normalizeAddress(process.env.ZETA_CHAIN_LOCAL_USDT || "0xdAC17F958D2ee523a2206206994597C13D831ec7");
    btcAddress = normalizeAddress(process.env.ZETA_CHAIN_LOCAL_BTC || "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599");
    zetaConnectorAddress = normalizeAddress(process.env.ZETA_CHAIN_LOCAL_ZETA_CONNECTOR || "0xYourLocalZetaConnectorAddress");
    zetaTokenAddress = normalizeAddress(process.env.ZETA_CHAIN_LOCAL_ZETA_TOKEN || "0xYourLocalZetaTokenAddress");
  }
  // 默认测试参数（用于Hardhat本地网络等）
  else {
    console.log("Using default test configuration");
    routerAddress = normalizeAddress(process.env.DEFAULT_DEX_ROUTER || "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D");
    usdtAddress = normalizeAddress(process.env.DEFAULT_USDT || "0xdAC17F958D2ee523a2206206994597C13D831ec7");
    btcAddress = normalizeAddress(process.env.DEFAULT_BTC || "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599");
    zetaConnectorAddress = normalizeAddress(process.env.DEFAULT_ZETA_CONNECTOR || "0xDefaultZetaConnectorAddress");
    zetaTokenAddress = normalizeAddress(process.env.DEFAULT_ZETA_TOKEN || "0xDefaultZetaTokenAddress");
  }
  
  // 输出配置信息
  console.log("Configuration:");
  console.log("  - DEX Router:", routerAddress);
  console.log("  - USDT Address:", usdtAddress);
  console.log("  - BTC Address:", btcAddress);
  console.log("  - ZetaConnector:", zetaConnectorAddress);
  console.log("  - ZetaToken:", zetaTokenAddress);

  // 部署合约
  console.log("\nDeploying HODLBox contract...");
  const HODLBox = await ethers.getContractFactory("HODLBox");
  const hodlBox = await HODLBox.deploy(
    routerAddress, 
    usdtAddress, 
    btcAddress,
    zetaConnectorAddress,
    zetaTokenAddress
  );

  await hodlBox.deployed();

  console.log("HODLBox contract deployed to:", hodlBox.address);
  
  // 保存部署信息到文件，方便后续使用
  const fs = require('fs');
  const deploymentInfo = {
    network: network.name,
    address: hodlBox.address,
    timestamp: Date.now(),
    constructorArgs: [
      routerAddress,
      usdtAddress,
      btcAddress,
      zetaConnectorAddress,
      zetaTokenAddress
    ]
  };
  
  // 确保deployments目录存在
  if (!fs.existsSync('./deployments')) {
    fs.mkdirSync('./deployments');
  }
  
  fs.writeFileSync(
    `./deployments/${network.name}.json`, 
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log(`Deployment info saved to ./deployments/${network.name}.json`);
  console.log("\nDeployment complete!");
  console.log("\nNote: For production deployment, please ensure all addresses are correct for your target network.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
