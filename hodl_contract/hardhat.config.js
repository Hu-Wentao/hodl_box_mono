require("@nomicfoundation/hardhat-toolbox");
require('dotenv').config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.26",
  networks: {
    hardhat: {},
    localhost: {
      url: "http://127.0.0.1:8545"
    },
    "zeta-athens-testnet": {
      url: "https://zetachain-athens-evm.blockpi.network/v1/rpc/public",
      accounts: process.env.PRIVATE_KEY !== undefined ? [process.env.PRIVATE_KEY] : [],
      chainId: 7001,
      gasPrice: 20000000000, // 20 Gwei
      gasMultiplier: 1.5
    },
    "zeta-local": {
      url: "http://localhost:8545",
      accounts: process.env.PRIVATE_KEY !== undefined ? [process.env.PRIVATE_KEY] : [],
      chainId: 7000
    }
  },
  paths: {
    artifacts: "./artifacts",
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    deploy: "./scripts"
  },
  mocha: {
    timeout: 200000
  }
};
