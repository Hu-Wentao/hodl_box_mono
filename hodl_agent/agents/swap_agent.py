#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HODL Box Swap Agent

AI Agent specialized in handling cryptocurrency token swap operations,
including intent parsing and transaction execution.
"""

from typing import Dict, Any, Union
from qwen_agent.llm.schema import ContentItem
from .base_agent import HODLBoxAgent
from .tools.swap_tools import SwapIntentTool

class SwapAgent(HODLBoxAgent):
    """
    Agent specialized in processing token swap requests.
    
    This agent can parse user's swap intent and prepare transactions
    for cryptocurrency exchanges across different blockchains.
    """
    
    def __init__(self):
        """Initialize the swap agent with swap-specific tools and prompts."""
        # Define system prompt for swap agent
        system_prompt = (
            "你是一个区块链交易Agent，专门帮助用户解析和执行Token交换操作。"
            "当用户提出交换请求时，请调用parse_swap_intent工具来解析用户的交易意图。"
            "解析结果将包含交易所需的关键信息，如区块链、买入Token、卖出Token和数量。"
        )
        
        # Initialize with swap tools
        tools = [SwapIntentTool()]
        
        # Initialize base agent
        super().__init__(tools=tools, system_prompt=system_prompt)
    
    def process_swap_request(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user's swap request and return structured swap intent.
        
        Args:
            user_message: User's message containing swap request
            
        Returns:
            Dict containing structured swap intent information
        """
        # Process the message using the base agent
        response = self.process_message(user_message)
        
        # Extract swap intent from response
        swap_intent = self._extract_swap_intent(response)
        
        return {
            'original_message': user_message,
            'response': response,
            'swap_intent': swap_intent,
            'status': 'success' if swap_intent else 'failed'
        }
    
    def _extract_swap_intent(self, response: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """
        Extract structured swap intent from agent response.
        
        Args:
            response: The agent's response
            
        Returns:
            Parsed swap intent or None if not found
        """
        # Check if response contains tool calls
        if 'tool_calls' in response:
            for tool_call in response['tool_calls']:
                if tool_call.get('name') == 'parse_swap_intent':
                    # Return the arguments used for the tool call
                    return tool_call.get('parameters', {})
        
        # Check if response contains tool results
        if 'tool_results' in response:
            for result in response['tool_results']:
                if result.get('name') == 'parse_swap_intent':
                    # Parse and return the result
                    try:
                        import json
                        return json.loads(result.get('content', '{}'))
                    except:
                        return None
        
        return None
    
    def validate_swap_intent(self, swap_intent: Dict[str, Any]) -> bool:
        """
        Validate that the swap intent contains all required fields.
        
        Args:
            swap_intent: The swap intent to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['chain', 'tkBuy', 'tokenOut', 'amount']
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in swap_intent:
                return False
        
        # Check if values are not empty
        for field in required_fields:
            if not swap_intent[field]:
                return False
        
        return True
