#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HODL Box AI Agent Base Class

Base class for all HODL Box AI Agents, providing common functionality
and configuration for AI-driven cryptocurrency investment assistance.
"""

import os
import json
from typing import Dict, List, Optional, Any

from qwen_agent.agents import Assistant
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HODLBoxAgent:
    """
    Base class for HODL Box AI Agents.
    
    Provides common functionality and configuration for all agents,
    including LLM initialization, message handling, and tool integration.
    """
    
    def __init__(self, tools: Optional[List] = None, system_prompt: Optional[str] = None):
        """
        Initialize the base agent with LLM configuration and tools.
        
        Args:
            tools: List of tools to be used by the agent
            system_prompt: System prompt to guide the agent's behavior
        """
        # Configure LLM
        self.llm_cfg = {
            'model': 'qwen-flash',  # Default model
            'model_server': os.getenv("BASE_URL", "https://api.example.com/v1"),
            'api_key': os.getenv("API_KEY", ""),
        }
        
        # Set system prompt
        self.system_prompt = system_prompt or "你是一个区块链投资助手，擅长回答加密货币相关问题。"
        
        # Initialize agent with tools
        self.tools = tools or []
        self.assistant = Assistant(llm=self.llm_cfg, function_list=self.tools)
        
        # Initialize conversation history
        self.messages = [{'role': 'system', 'content': self.system_prompt}]
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: The user's message to process
            
        Returns:
            Dict containing the response and any additional information
        """
        # Add user message to conversation history
        self.messages.append({'role': 'user', 'content': user_message})
        
        # Generate response
        responses = []
        for response in self.assistant.run(messages=self.messages):
            responses.append(response)
        
        # Get the last response
        last_response = responses[-1] if responses else {}
        
        # Add assistant response to conversation history
        if 'content' in last_response:
            self.messages.append({'role': 'assistant', 'content': last_response['content']})
        
        return last_response
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.messages = [{'role': 'system', 'content': self.system_prompt}]
    
    def save_conversation(self, filepath: str):
        """
        Save the conversation history to a file.
        
        Args:
            filepath: Path to the file where the conversation should be saved
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
    
    def load_conversation(self, filepath: str):
        """
        Load a conversation history from a file.
        
        Args:
            filepath: Path to the file containing the conversation
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self.messages = json.load(f)
        
        # Ensure system prompt is preserved
        if not any(msg['role'] == 'system' for msg in self.messages):
            self.messages.insert(0, {'role': 'system', 'content': self.system_prompt})
