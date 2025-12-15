// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@zetachain/protocol-contracts/contracts/zevm/interfaces/IGatewayZEVM.sol";
import "@zetachain/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol";
import "@zetachain/protocol-contracts/contracts/zevm/interfaces/UniversalContract.sol";

contract HodlBoxUniversalApp is UniversalContract {
    // Gateway is inherited from UniversalContract
    
    struct DCAPlan {
        bytes user;
        address fromToken;    // ZRC-20 address
        address toToken;      // ZRC-20 address
        uint256 totalAmount;    
        uint256 remainingAmount; 
        uint256 amountPerInterval;
        uint256 interval;     
        uint256 startTime;
        uint256 lastExecutionTime;
        bool isActive;
        uint256 targetChainId;
        bytes recipient;      // Changed to bytes
    }

    mapping(bytes32 => DCAPlan) public dcaPlans;
    
    event PlanCreated(bytes32 indexed planId, bytes user);
    event PlanExecuted(bytes32 indexed planId, uint256 amount, uint256 timestamp);
    event PlanCompleted(bytes32 indexed planId);
    
    constructor(address _gateway) {
        gateway = IGatewayZEVM(_gateway);
    }
    
    function onCall(
        MessageContext calldata context,
        address zrc20,
        uint256 amount,
        bytes calldata message
    ) external override {
        (
         address toToken, 
         uint256 interval, 
         uint256 targetChainId,
         bytes memory recipient,
         uint256 amountPerInterval
        ) = abi.decode(message, (address, uint256, uint256, bytes, uint256));
        
        bytes32 planId = keccak256(abi.encode(block.timestamp, context.sender, zrc20, toToken));
        
        dcaPlans[planId] = DCAPlan({
            user: context.sender,
            fromToken: zrc20,
            toToken: toToken,
            totalAmount: amount,
            remainingAmount: amount,
            amountPerInterval: amountPerInterval,
            interval: interval,
            startTime: block.timestamp,
            lastExecutionTime: 0,
            isActive: true,
            targetChainId: targetChainId,
            recipient: recipient
        });
        
        emit PlanCreated(planId, context.sender);
    }

    function executeDCAPlan(bytes32 planId) external {
        DCAPlan storage plan = dcaPlans[planId];
        require(plan.isActive, "Plan not active");
        require(block.timestamp >= plan.lastExecutionTime + plan.interval, "Too early");
        require(plan.remainingAmount >= plan.amountPerInterval, "Insufficient funds");

        plan.lastExecutionTime = block.timestamp;
        plan.remainingAmount -= plan.amountPerInterval;
        
        // Prepare RevertOptions
        RevertOptions memory revertOptions = RevertOptions({
            revertAddress: address(this),
            callOnRevert: false,
            abortAddress: address(0),
            revertMessage: "",
            onRevertGasLimit: 0 // Correct field name
        });
        
        // Execute Withdraw (Cross-Chain Transfer)
        gateway.withdraw(
            plan.recipient,
            plan.amountPerInterval,
            plan.fromToken,
            revertOptions
        );
        
        emit PlanExecuted(planId, plan.amountPerInterval, block.timestamp);
        
        if (plan.remainingAmount < plan.amountPerInterval) {
            plan.isActive = false;
            emit PlanCompleted(planId);
        }
    }
}
