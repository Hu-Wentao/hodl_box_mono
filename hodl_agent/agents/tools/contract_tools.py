#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Contract Tools for HODL Box Agent

This module provides tools for interacting with blockchain smart contracts,
including token swaps, approval, and other contract interactions.
"""

import json
import os
import time
from typing import Dict, Any, Optional, Union
from qwen_agent.tools.base import BaseTool, register_tool
from web3 import Web3, HTTPProvider
from eth_account import Account
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

@register_tool('execute_contract_call')
class ContractTool(BaseTool):
    """
    Tool for executing smart contract calls on blockchain.
    
    This tool handles interactions with Ethereum and compatible blockchains,
    including token swaps, approvals, and other contract operations.
    """
    
    description = "在区块链上执行智能合约调用，如代币交换、授权等操作"
    parameters_schema = {
        "type": "object",
        "properties": {
            "contract_address": {
                "type": "string",
                "description": "智能合约地址"
            },
            "function_name": {
                "type": "string",
                "description": "要调用的合约函数名"
            },
            "function_args": {
                "type": "array",
                "description": "函数参数数组"
            },
            "abi": {
                "type": "object",
                "description": "合约ABI（应用二进制接口）"
            },
            "is_write_operation": {
                "type": "boolean",
                "description": "是否为写入操作（需要交易签名）"
            },
            "gas_limit": {
                "type": "integer",
                "description": "交易Gas上限"
            }
        },
        "required": ["contract_address", "function_name"]
    }
    
    def __init__(self):
        """Initialize the contract interaction tool."""
        super().__init__()
        # Load blockchain configuration
        self.rpc_url = os.getenv('ETH_RPC_URL', 'https://mainnet.infura.io/v3/YOUR_INFURA_KEY')
        self.private_key = os.getenv('PRIVATE_KEY', '')
        self.chain_id = int(os.getenv('CHAIN_ID', '1'))  # Default to Ethereum mainnet
        
        # Initialize Web3 connection
        self.web3 = self._init_web3()
        
        # Default ABIs for common operations
        self.erc20_abi = self._get_erc20_abi()
        
        # Use mock implementation if no private key is provided
        self.use_mock = not self.private_key
    
    def call(self, params: Dict[str, Any]) -> str:
        """
        Execute a smart contract call.
        
        Args:
            params: Dictionary containing contract call parameters
            
        Returns:
            JSON string with contract call result or transaction details
        """
        # Validate required parameters
        if 'contract_address' not in params or 'function_name' not in params:
            return json.dumps({
                'error': 'Missing required parameters: contract_address and function_name',
                'status': 'error'
            })
        
        try:
            # Format parameters
            contract_address = Web3.to_checksum_address(params['contract_address'])
            function_name = params['function_name']
            function_args = params.get('function_args', [])
            is_write_operation = params.get('is_write_operation', False)
            gas_limit = params.get('gas_limit', 300000)
            
            # Get ABI from params or use default for common operations
            abi = params.get('abi', None)
            if not abi and self._is_erc20_operation(function_name):
                abi = self.erc20_abi
            
            if not abi:
                return json.dumps({
                    'error': 'ABI is required for this operation',
                    'status': 'error'
                })
            
            # Execute based on whether it's a read or write operation
            if self.use_mock or not is_write_operation:
                # For mock or read operations, use call
                result = self._call_contract_function(
                    contract_address, function_name, function_args, abi
                )
                
                return json.dumps({
                    'status': 'success',
                    'result': result,
                    'type': 'read' if not is_write_operation else 'mock_write',
                    'contract_address': contract_address,
                    'function_name': function_name
                }, ensure_ascii=False)
            else:
                # For write operations, send a transaction
                tx_hash = self._send_transaction(
                    contract_address, function_name, function_args, abi, gas_limit
                )
                
                return json.dumps({
                    'status': 'success',
                    'tx_hash': tx_hash,
                    'type': 'write',
                    'contract_address': contract_address,
                    'function_name': function_name,
                    'chain_id': self.chain_id,
                    'explorer_url': f"https://etherscan.io/tx/{tx_hash}"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                'error': str(e),
                'status': 'error'
            }, ensure_ascii=False)
    
    def _init_web3(self) -> Web3:
        """
        Initialize Web3 connection.
        
        Returns:
            Web3 instance
        """
        web3 = Web3(HTTPProvider(self.rpc_url))
        # web3.middleware_onion.inject(geth_poa_middleware, layer=0) # Removed in v7
        return web3
    
    def _call_contract_function(self, contract_address: str, function_name: str, 
                              function_args: list, abi: dict) -> Any:
        # Same as before
        if self.use_mock:
            return self._get_mock_call_result(function_name, function_args)
        
        contract = self.web3.eth.contract(address=contract_address, abi=abi)
        func = getattr(contract.functions, function_name)
        result = func(*function_args).call()
        return result
    
    def _send_transaction(self, contract_address: str, function_name: str, 
                         function_args: list, abi: dict, gas_limit: int) -> str:
        if self.use_mock:
            return self._get_mock_tx_hash()
        
        account = Account.from_key(self.private_key)
        address = account.address
        
        contract = self.web3.eth.contract(address=contract_address, abi=abi)
        nonce = self.web3.eth.get_transaction_count(address)
        func = getattr(contract.functions, function_name)
        
        tx = func(*function_args).build_transaction({
            'from': address,
            'nonce': nonce,
            'gas': gas_limit,
            'chainId': self.chain_id,
            'gasPrice': self.web3.eth.gas_price
        })
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.web3.to_hex(tx_hash)
    
    def _is_erc20_operation(self, function_name: str) -> bool:
        erc20_functions = [
            'name', 'symbol', 'decimals', 'totalSupply',
            'balanceOf', 'transfer', 'allowance',
            'approve', 'transferFrom'
        ]
        return function_name in erc20_functions
    
    def _get_erc20_abi(self) -> list:
        return [
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "symbol",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"},
                    {"name": "_spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "remaining", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "success", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "success", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_from", "type": "address"},
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transferFrom",
                "outputs": [{"name": "success", "type": "bool"}],
                "type": "function"
            }
        ]
    
    def _get_mock_call_result(self, function_name: str, function_args: list) -> Any:
        if function_name == 'name':
            return 'Mock Token'
        elif function_name == 'symbol':
            return 'MOCK'
        elif function_name == 'decimals':
            return 18
        elif function_name == 'totalSupply':
            return self.web3.to_wei(1000000, 'ether')
        elif function_name == 'balanceOf':
            return self.web3.to_wei(100, 'ether')
        elif function_name == 'allowance':
            return self.web3.to_wei(50, 'ether')
        elif function_name in ['transfer', 'approve', 'transferFrom']:
            return True
        else:
            return 'Mock result for ' + function_name
    
    def _get_mock_tx_hash(self) -> str:
        import random
        return '0x' + ''.join(random.choices('0123456789abcdef', k=64))
