#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HODL Box Agent - 韭菜罐子智能心理按摩助手

此模块提供用户心理按摩功能，帮助用户坚持投资计划，无论市场涨跌都能保持理性投资心态。
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 初始化OpenAI客户端
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 定义市场状态
MARKET_STATES = {
    "BULL": "牛市",
    "BEAR": "熊市",
    "SIDE": "横盘",
    "VOLATILE": "剧烈波动"
}

# 定义用户情绪
USER_EMOTIONS = {
    "ANXIOUS": "焦虑",
    "FEARFUL": "恐惧",
    "GREEDY": "贪婪",
    "CALM": "平静",
    "FRUSTRATED": "沮丧",
    "EXCITED": "兴奋"
}

class HODLBoxAgent:
    """
    HODL Box 心理按摩助手类
    """
    
    def __init__(self):
        """
        初始化HODL Box助手
        """
        self.user_profiles = {}
        self.load_user_profiles()
        self.positive_quotes = self._load_positive_quotes()
    
    def _load_positive_quotes(self) -> List[str]:
        """
        加载积极正面的投资语录
        """
        return [
            "投资是一场马拉松，不是短跑比赛。",
            "市场波动是正常的，长期趋势才是关键。",
            "不要试图预测市场，专注于你的投资计划。",
            "成功的投资来自于耐心，而非频繁交易。",
            "市场恐慌时保持冷静，市场贪婪时保持警惕。",
            "定投的力量在于时间的复利效应。",
            "熊市为聪明的投资者提供了最好的入场机会。",
            "坚持执行你的投资计划，不要被短期波动所干扰。",
            "市场会奖励那些能够控制情绪的投资者。",
            "投资是关于纪律和坚持，而非运气。"
        ]
    
    def load_user_profiles(self):
        """
        加载用户配置文件
        """
        try:
            if os.path.exists("user_profiles.json"):
                with open("user_profiles.json", "r", encoding="utf-8") as f:
                    self.user_profiles = json.load(f)
        except Exception as e:
            logger.error(f"加载用户配置文件时出错: {e}")
            self.user_profiles = {}
    
    def save_user_profiles(self):
        """
        保存用户配置文件
        """
        try:
            with open("user_profiles.json", "w", encoding="utf-8") as f:
                json.dump(self.user_profiles, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"保存用户配置文件时出错: {e}")
    
    def create_user_profile(self, user_id: str, name: str, risk_profile: str, investment_goal: str):
        """
        创建用户配置文件
        
        Args:
            user_id: 用户ID
            name: 用户名称
            risk_profile: 风险偏好
            investment_goal: 投资目标
        """
        self.user_profiles[user_id] = {
            "name": name,
            "risk_profile": risk_profile,
            "investment_goal": investment_goal,
            "created_at": datetime.datetime.now().isoformat(),
            "last_interaction": datetime.datetime.now().isoformat(),
            "investment_plan": None,
            "mood_history": [],
            "motivational_boosts": 0
        }
        self.save_user_profiles()
    
    def update_investment_plan(self, user_id: str, plan: Dict[str, Any]):
        """
        更新用户的投资计划
        
        Args:
            user_id: 用户ID
            plan: 投资计划详情
        """
        if user_id in self.user_profiles:
            self.user_profiles[user_id]["investment_plan"] = plan
            self.user_profiles[user_id]["last_interaction"] = datetime.datetime.now().isoformat()
            self.save_user_profiles()
    
    def analyze_user_emotion(self, message: str) -> str:
        """
        分析用户情绪
        
        Args:
            message: 用户消息
        
        Returns:
            情绪类型
        """
        try:
            # 使用OpenAI API进行情绪分析
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的情绪分析助手。请分析用户的最后一条消息，判断用户当前的情绪状态，只能从以下选项中选择一个：焦虑、恐惧、贪婪、平静、沮丧、兴奋。请直接返回情绪类型，不要添加任何其他内容。"},
                    {"role": "user", "content": message}
                ],
                max_tokens=5,
                temperature=0
            )
            
            emotion = response.choices[0].message.content.strip()
            return emotion if emotion in USER_EMOTIONS.values() else "平静"
        except Exception as e:
            logger.error(f"情绪分析出错: {e}")
            return "平静"
    
    def get_market_state(self) -> str:
        """
        获取当前市场状态（简化版，实际应从API获取）
        
        Returns:
            市场状态
        """
        # 这里是简化实现，实际应用中应该从市场数据API获取真实的市场状态
        # 这里随机返回一种市场状态
        import random
        return random.choice(list(MARKET_STATES.values()))
    
    def generate_motivational_response(self, user_id: str, emotion: str, market_state: str) -> str:
        """
        生成激励性回应
        
        Args:
            user_id: 用户ID
            emotion: 用户情绪
            market_state: 市场状态
        
        Returns:
            激励性回应
        """
        try:
            if user_id not in self.user_profiles:
                return "您好！欢迎使用韭菜罐子心理按摩助手。请问您想了解什么？"
            
            user_profile = self.user_profiles[user_id]
            name = user_profile["name"]
            risk_profile = user_profile["risk_profile"]
            investment_goal = user_profile["investment_goal"]
            investment_plan = user_profile["investment_plan"]
            
            # 使用OpenAI API生成个性化回应
            system_prompt = f"""
你是韭菜罐子(HODL Box)的心理按摩助手，专门帮助加密货币投资者坚持他们的投资计划，尤其是在市场波动期间。

用户信息：
- 姓名：{name}
- 风险偏好：{risk_profile}
- 投资目标：{investment_goal}
- 当前情绪：{emotion}
- 当前市场状态：{market_state}

投资计划：{json.dumps(investment_plan, ensure_ascii=False) if investment_plan else "未设置"}

请根据用户的情况，生成一个富有同理心、鼓励性且专业的回应。
回应应该：
1. 先共情用户当前的情绪
2. 提供符合用户风险偏好的专业建议
3. 强调长期投资和定投策略的好处
4. 用简单易懂的语言解释市场波动的必然性
5. 鼓励用户坚持他们的投资计划
6. 回应要温暖、专业且简短，不超过150字
"""
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "请给我一些心理按摩，我需要坚持我的投资计划。"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            # 记录激励次数
            user_profile["motivational_boosts"] += 1
            user_profile["last_interaction"] = datetime.datetime.now().isoformat()
            user_profile["mood_history"].append({
                "timestamp": datetime.datetime.now().isoformat(),
                "emotion": emotion,
                "market_state": market_state
            })
            
            self.save_user_profiles()
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"生成激励回应出错: {e}")
            import random
            return f"不要担心，{user_profile['name'] if user_id in self.user_profiles and 'name' in self.user_profiles[user_id] else '朋友'}，市场波动是暂时的，坚持你的定投计划！" + random.choice(self.positive_quotes)
    
    def handle_user_message(self, user_id: str, message: str) -> str:
        """
        处理用户消息
        
        Args:
            user_id: 用户ID
            message: 用户消息
        
        Returns:
            回复消息
        """
        # 分析用户情绪
        emotion = self.analyze_user_emotion(message)
        
        # 获取市场状态
        market_state = self.get_market_state()
        
        # 生成回应
        return self.generate_motivational_response(user_id, emotion, market_state)
    
    def generate_market_insight(self) -> str:
        """
        生成市场洞察
        
        Returns:
            市场洞察
        """
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的加密货币市场分析师。请提供一段简短、客观的市场洞察，包括当前市场趋势、潜在风险和机遇。内容要简洁明了，不超过100字。"},
                    {"role": "user", "content": "请给我一个简短的加密货币市场洞察。"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"生成市场洞察出错: {e}")
            return "市场波动是投资的一部分，坚持你的长期投资策略是明智之选。"
    
    def create_investment_report(self, user_id: str) -> str:
        """
        创建投资报告
        
        Args:
            user_id: 用户ID
        
        Returns:
            投资报告
        """
        if user_id not in self.user_profiles or not self.user_profiles[user_id]["investment_plan"]:
            return "您还没有设置投资计划，请先创建一个投资计划。"
        
        try:
            user_profile = self.user_profiles[user_id]
            name = user_profile["name"]
            investment_plan = user_profile["investment_plan"]
            
            # 使用OpenAI API生成投资报告
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的投资顾问。请根据用户的投资计划，生成一份简短的投资进度报告和建议。报告要包含投资计划分析、潜在改进空间和鼓励性话语。内容要温暖、专业且简短，不超过150字。"},
                    {"role": "user", "content": f"用户名：{name}\n投资计划：{json.dumps(investment_plan, ensure_ascii=False)}\n请生成一份简短的投资报告。"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"生成投资报告出错: {e}")
            return f"{user_profile['name'] if user_id in self.user_profiles and 'name' in self.user_profiles[user_id] else '朋友'}，继续坚持你的投资计划，定投是积累财富的有效方式！"


# 简单的命令行界面演示
def main():
    agent = HODLBoxAgent()
    
    print("欢迎使用韭菜罐子(HODL Box)心理按摩助手！")
    print("输入 'exit' 退出程序")
    
    # 假设用户ID为test_user
    user_id = "test_user"
    
    # 检查用户是否存在，不存在则创建
    if user_id not in agent.user_profiles:
        name = input("请输入您的姓名: ")
        risk_profile = input("请输入您的风险偏好 (保守/平衡/激进): ")
        investment_goal = input("请输入您的投资目标: ")
        agent.create_user_profile(user_id, name, risk_profile, investment_goal)
        
        # 设置一个简单的投资计划
        plan = {
            "type": "定投",
            "asset": "BTC",
            "currency": "USDT",
            "amount_per_period": 100,
            "period": "每周",
            "start_date": datetime.datetime.now().isoformat(),
            "duration": "长期"
        }
        agent.update_investment_plan(user_id, plan)
    
    while True:
        message = input("\n您：")
        
        if message.lower() == "exit":
            print("谢谢使用韭菜罐子心理按摩助手！再见！")
            break
        elif message.lower() == "market":
            print("\n市场洞察：", agent.generate_market_insight())
        elif message.lower() == "report":
            print("\n投资报告：", agent.create_investment_report(user_id))
        else:
            response = agent.handle_user_message(user_id, message)
            print(f"\n助手：{response}")


if __name__ == "__main__":
    main()
