#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HODL Box Mental Support Agent

AI Agent specialized in providing emotional support and motivation
for cryptocurrency investors during market volatility.
"""

import json
import random
from typing import Dict, Any, List
from .base_agent import HODLBoxAgent

class MentalSupportAgent(HODLBoxAgent):
    """
    Agent specialized in providing psychological support to crypto investors.
    
    This agent can analyze user emotions, provide motivational messages,
    and help users maintain a disciplined investment approach during
    different market conditions.
    """
    
    def __init__(self):
        """
        Initialize the mental support agent with appropriate prompts and resources.
        """
        # Define system prompt for mental support agent
        system_prompt = (
            "你是一个加密货币投资心理顾问，专注于为投资者提供情绪支持和鼓励。"
            "在市场波动期间，帮助用户保持理性和纪律，坚持长期投资策略。"
            "根据用户的情绪状态和当前市场状况，提供适当的心理按摩和投资建议。"
        )
        
        # Initialize with no specific tools initially
        tools = []
        
        # Initialize base agent
        super().__init__(tools=tools, system_prompt=system_prompt)
        
        # Load motivational resources
        self.motivational_quotes = self._load_motivational_quotes()
        self.market_advice = self._load_market_advice()
    
    def _load_motivational_quotes(self) -> List[str]:
        """Load motivational quotes for different market conditions."""
        return [
            "市场波动是暂时的，价值积累是永恒的。",
            "不要让恐惧或贪婪控制你的投资决策。",
            "在别人恐惧时贪婪，在别人贪婪时恐惧。",
            "投资是一场马拉松，不是短跑。",
            "熊市为长期投资者创造最佳入场机会。",
            "耐心是投资者最宝贵的品质之一。",
            "不要试图预测市场底部或顶部，关注长期价值。",
            "波动性是加密市场的常态，保持冷静是成功的关键。",
            "持续定投策略能帮助你平滑市场波动风险。",
            "坚持你的投资计划，不要被短期价格波动干扰。"
        ]
    
    def _load_market_advice(self) -> Dict[str, List[str]]:
        """Load specialized advice for different market conditions."""
        return {
            "bull_market": [
                "牛市中保持谨慎，不要过度杠杆或FOMO追高。",
                "考虑在价格大幅上涨时分批获利，设置止盈点。",
                "牛市往往伴随着泡沫，保持理性评估资产价值。",
                "记住历史规律：牛市之后通常会有调整。",
                "利用牛市积累的利润为熊市做准备。"
            ],
            "bear_market": [
                "熊市是积累优质资产的最佳时机。",
                "坚持定投计划，降低平均成本。",
                "关注项目基本面，而非短期价格走势。",
                "熊市不会永远持续，历史上每次熊市后都会迎来复苏。",
                "利用这段时间学习和提升你的投资知识。"
            ],
            "volatile_market": [
                "市场剧烈波动时，保持冷静尤为重要。",
                "避免在高波动期间做出冲动决策。",
                "考虑增加稳定币储备，等待更好的入场机会。",
                "回顾你的长期投资目标，重新聚焦。",
                "波动性增加意味着风险上升，确保你的风险暴露在可控范围内。"
            ]
        }
    
    def analyze_emotion(self, user_message: str) -> str:
        """
        Analyze user's emotional state from their message.
        
        Args:
            user_message: The user's message to analyze
            
        Returns:
            String representing the detected emotion
        """
        # Simple emotion detection based on keywords
        user_lower = user_message.lower()
        
        if any(keyword in user_lower for keyword in ['怕', '担心', '恐惧', '恐慌', '焦虑']):
            return "fearful"
        elif any(keyword in user_lower for keyword in ['赚', '涨', '激动', '贪婪', '期待']):
            return "excited"
        elif any(keyword in user_lower for keyword in ['亏', '跌', '失望', '沮丧', '伤心']):
            return "frustrated"
        else:
            return "neutral"
    
    def provide_support(self, user_message: str, market_state: str = "neutral") -> Dict[str, Any]:
        """
        Provide mental support based on user message and market state.
        
        Args:
            user_message: The user's message
            market_state: Current market state (bull_market, bear_market, volatile_market)
            
        Returns:
            Dict containing support response and additional information
        """
        # Analyze user emotion
        emotion = self.analyze_emotion(user_message)
        
        # Generate response based on emotion and market state
        response = self.process_message(user_message)
        
        # Add motivational content
        motivational_content = self._generate_motivational_content(emotion, market_state)
        
        return {
            'original_message': user_message,
            'detected_emotion': emotion,
            'market_state': market_state,
            'response': response,
            'motivational_content': motivational_content,
            'status': 'success'
        }
    
    def _generate_motivational_content(self, emotion: str, market_state: str) -> str:
        """
        Generate motivational content based on emotion and market state.
        
        Args:
            emotion: The detected user emotion
            market_state: Current market state
            
        Returns:
            Motivational message string
        """
        # Start with a random motivational quote
        content = random.choice(self.motivational_quotes) + "\n\n"
        
        # Add market-specific advice if market state is provided
        if market_state in self.market_advice:
            content += "市场建议：\n"
            content += random.choice(self.market_advice[market_state])
        
        # Add emotion-specific encouragement
        if emotion == "fearful":
            content += "\n\n记住，长期来看，坚持投资纪律比短期市场波动更重要。"
        elif emotion == "excited":
            content += "\n\n保持冷静，理性评估市场，不要被短期收益冲昏头脑。"
        elif emotion == "frustrated":
            content += "\n\n市场调整是正常的，这往往是为下一次上涨做准备。"
        
        return content
