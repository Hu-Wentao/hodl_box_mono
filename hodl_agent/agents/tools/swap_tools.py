#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Swap Tools for HODL Box Agent

This module provides tools for parsing and processing cryptocurrency swap requests,
including intent recognition and transaction parameter extraction.
"""

import re
import json
from typing import Dict, Any, Optional
from qwen_agent.tools.base import BaseTool, register_tool

@register_tool('parse_swap_intent')
class SwapIntentTool(BaseTool):
    """
    Tool for parsing cryptocurrency swap intent from user messages.
    
    This tool extracts key information from user requests to exchange tokens,
    including the source token, target token, amount, and preferred blockchain.
    """
    
    description = "解析用户的代币交换请求，提取交换意图中的关键参数"
    parameters_schema = {
        "type": "object",
        "properties": {
            "chain": {
                "type": "string",
                "description": "区块链名称，如Ethereum、BSC、Polygon等"
            },
            "tkBuy": {
                "type": "string",
                "description": "要买入的代币符号，如BTC、ETH、USDT等"
            },
            "tkSell": {
                "type": "string",
                "description": "要卖出的代币符号，如BTC、ETH、USDT等"
            },
            "count": {
                "type": "string",
                "description": "交换数量"
            }
        },
        "required": ["tkBuy", "tkSell", "count"]
    }
    
    def __init__(self):
        """Initialize the swap intent parsing tool."""
        super().__init__()
        # Define common token symbols
        self.common_tokens = {
            'btc': 'BTC', 'eth': 'ETH', 'usdt': 'USDT', 'usdc': 'USDC',
            'bnb': 'BNB', 'sol': 'SOL', 'ada': 'ADA', 'dot': 'DOT',
            'link': 'LINK', 'uni': 'UNI', 'aave': 'AAVE', 'mkr': 'MKR',
            'doge': 'DOGE', 'shib': 'SHIB', 'avax': 'AVAX', 'xrp': 'XRP',
            'u': 'USDT',  # Common shorthand for USDT
            '100u': '100 USDT',  # Handle common patterns
        }
        
        # Define common blockchain names
        self.common_chains = [
            'ethereum', 'eth', 'btc', 'bitcoin', 'bsc', 'binance smart chain',
            'polygon', 'matic', 'avalanche', 'avax', 'solana', 'sol', 'optimism',
            'arbitrum', 'fantom', 'ftm', 'near', 'cosmos', 'atom', 'algorand',
            'algo', 'cardano', 'ada', 'polkadot', 'dot', 'chainlink', 'link'
        ]
    
    def call(self, params: Dict[str, Any]) -> str:
        """
        Execute the swap intent parsing tool.
        
        Args:
            params: Dictionary containing the parameters for parsing
            
        Returns:
            JSON string with structured swap intent
        """
        # Validate required parameters
        if not self._validate_params(params):
            return json.dumps({
                'error': 'Missing required parameters',
                'required': ['tkBuy', 'tkSell', 'count'],
                'provided': list(params.keys())
            })
        
        # Normalize and structure the parameters
        swap_intent = self._normalize_swap_intent(params)
        
        # Add additional metadata
        swap_intent['timestamp'] = self._get_current_timestamp()
        swap_intent['valid'] = True  # Mark as valid since we passed validation
        
        # Return as JSON string
        return json.dumps(swap_intent, ensure_ascii=False)
    
    def _validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate that required parameters are present.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        required = ['tkBuy', 'tkSell', 'count']
        
        # Check that all required keys are present
        for key in required:
            if key not in params:
                return False
            
            # Check that values are not empty
            if not params[key]:
                return False
        
        return True
    
    def _normalize_swap_intent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and format the swap intent parameters.
        
        Args:
            params: Raw parameters
            
        Returns:
            Normalized swap intent dictionary
        """
        # Normalize token symbols
        tk_buy = self._normalize_token(params.get('tkBuy', ''))
        tk_sell = self._normalize_token(params.get('tkSell', ''))
        
        # Format count as string to preserve precision
        count = str(params.get('count', ''))
        
        # Normalize chain name if provided
        chain = self._normalize_chain(params.get('chain', ''))
        
        return {
            'chain': chain,
            'tkBuy': tk_buy,
            'tkSell': tk_sell,
            'count': count,
            'tokenIn': tk_sell,      # Alias for compatibility
            'tokenOut': tk_buy,      # Alias for compatibility
            'amount': count,         # Alias for compatibility
            'amountIn': count        # Alias for compatibility
        }
    
    def _normalize_token(self, token: str) -> str:
        """
        Normalize token symbol to standard format.
        
        Args:
            token: Raw token symbol
            
        Returns:
            Normalized token symbol
        """
        # Convert to lowercase for case-insensitive matching
        token_lower = token.lower().strip()
        
        # Check if it's in our common tokens mapping
        if token_lower in self.common_tokens:
            return self.common_tokens[token_lower]
        
        # Handle special case for "100u" or similar patterns
        amount_match = re.search(r'(\\d+(?:\\.\\d+)?)\s*u', token_lower)
        if amount_match:
            return 'USDT'
        
        # Otherwise, just capitalize the first letter of each part
        return token_lower.upper()
    
    def _normalize_chain(self, chain: str) -> str:
        """
        Normalize blockchain name to standard format.
        
        Args:
            chain: Raw chain name
            
        Returns:
            Normalized chain name
        """
        # Convert to lowercase for case-insensitive matching
        chain_lower = chain.lower().strip()
        
        # Handle empty chain parameter
        if not chain_lower:
            return 'default'  # Use default chain if not specified
        
        # Map common abbreviations to full names
        chain_mapping = {
            'eth': 'Ethereum',
            'btc': 'Bitcoin',
            'bsc': 'BSC',
            'polygon': 'Polygon',
            'matic': 'Polygon',
            'avax': 'Avalanche',
            'sol': 'Solana'
        }
        
        # Check if chain is in our mapping
        if chain_lower in chain_mapping:
            return chain_mapping[chain_lower]
        
        # Return the original with proper capitalization
        return chain_lower.capitalize()
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp as ISO format string.
        
        Returns:
            ISO format timestamp string
        """
        import datetime
        return datetime.datetime.now().isoformat()
