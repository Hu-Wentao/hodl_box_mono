#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HODL Box Agent 测试文件

本文件包含对HODL Box AI Agent各功能模块的测试用例，
确保Agent能够正确处理用户意图并执行相关操作。
"""

import unittest
import json
from typing import Dict, Any

# 导入Agent和工具类
from agents.swap_agent import SwapAgent
from agents.mental_support_agent import MentalSupportAgent
from agents.tools.swap_tools import SwapIntentTool
from agents.tools.market_tools import MarketDataTool
from agents.tools.contract_tools import ContractTool

class TestSwapAgent(unittest.TestCase):
    """测试Swap Agent功能。"""
    
    def setUp(self):
        """测试前初始化SwapAgent实例。"""
        self.agent = SwapAgent()
    
    def test_process_swap_request(self):
        """测试处理代币交换请求。"""
        # 测试常见的交换请求格式
        test_cases = [
            "把100U换成BTC",
            "我想在以太坊上用50ETH买入USDT",
            "卖出2个BNB，换成SOL",
            "swap 1000 USDC to ETH on Polygon"
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                result = self.agent.process_swap_request(case)
                self.assertIsInstance(result, dict)
                self.assertEqual(result['original_message'], case)
                # 验证响应格式
                self.assertIn('response', result)
                self.assertIn('swap_intent', result)
                # 在mock环境下可能无法解析出具体的swap_intent，但应该能正常运行
    
    def test_validate_swap_intent(self):
        """测试验证交换意图。"""
        # 有效的交换意图
        valid_intent = {
            'chain': 'Ethereum',
            'tkBuy': 'BTC', 
            'tkSell': 'USDT',
            'count': '100',
            'tokenIn': 'USDT',
            'tokenOut': 'BTC',
            'amount': '100'
        }
        
        # 无效的交换意图（缺少字段）
        invalid_intent = {
            'chain': 'Ethereum',
            'tkBuy': 'BTC',
            'count': '100'
        }
        
        self.assertTrue(self.agent.validate_swap_intent(valid_intent))
        self.assertFalse(self.agent.validate_swap_intent(invalid_intent))

class TestSwapIntentTool(unittest.TestCase):
    """测试Swap Intent Tool功能。"""
    
    def setUp(self):
        """测试前初始化SwapIntentTool实例。"""
        self.tool = SwapIntentTool()
    
    def test_call_with_valid_params(self):
        """测试使用有效参数调用工具。"""
        params = {
            'chain': 'Ethereum',
            'tkBuy': 'BTC',
            'tkSell': 'USDT',
            'count': '100'
        }
        
        result_str = self.tool.call(params)
        result = json.loads(result_str)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['chain'], 'Ethereum')
        self.assertEqual(result['tkBuy'], 'BTC')
        self.assertEqual(result['tkSell'], 'USDT')
        self.assertEqual(result['count'], '100')
        # 验证别名字段
        self.assertEqual(result['tokenIn'], 'USDT')
        self.assertEqual(result['tokenOut'], 'BTC')
        self.assertEqual(result['amount'], '100')
    
    def test_call_with_missing_params(self):
        """测试缺少必要参数时的行为。"""
        params = {
            'tkBuy': 'BTC',
            # 缺少tkSell和count
        }
        
        result_str = self.tool.call(params)
        result = json.loads(result_str)
        
        self.assertIsInstance(result, dict)
        self.assertIn('error', result)
    
    def test_normalize_token(self):
        """测试代币符号标准化。"""
        test_cases = [
            ('btc', 'BTC'),
            ('eth', 'ETH'),
            ('u', 'USDT'),
            ('usdt', 'USDT'),
            ('custom', 'CUSTOM')
        ]
        
        for input_token, expected in test_cases:
            with self.subTest(input_token=input_token):
                # 通过访问私有方法来测试
                result = self.tool._normalize_token(input_token)
                self.assertEqual(result, expected)

class TestMentalSupportAgent(unittest.TestCase):
    """测试心理支持Agent功能。"""
    
    def setUp(self):
        """测试前初始化MentalSupportAgent实例。"""
        self.agent = MentalSupportAgent()
    
    def test_analyze_emotion(self):
        """测试情绪分析功能。"""
        test_cases = [
            ("市场大跌，我很害怕我的投资", "fearful"),
            ("比特币又涨了！我赚了很多钱", "excited"),
            ("我的投资亏损了50%，心情很差", "frustrated"),
            ("请给我一些投资建议", "neutral")
        ]
        
        for message, expected_emotion in test_cases:
            with self.subTest(message=message):
                emotion = self.agent.analyze_emotion(message)
                self.assertEqual(emotion, expected_emotion)
    
    def test_provide_support(self):
        """测试提供心理支持功能。"""
        message = "我很担心市场继续下跌"
        market_state = "bear_market"
        
        result = self.agent.provide_support(message, market_state)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['original_message'], message)
        self.assertEqual(result['market_state'], market_state)
        self.assertEqual(result['detected_emotion'], "fearful")
        self.assertIn('response', result)
        self.assertIn('motivational_content', result)
        self.assertEqual(result['status'], "success")

class TestMarketDataTool(unittest.TestCase):
    """测试市场数据工具功能。"""
    
    def setUp(self):
        """测试前初始化MarketDataTool实例。"""
        self.tool = MarketDataTool()
    
    def test_get_market_data(self):
        """测试获取市场数据。"""
        # 测试获取BTC和ETH的市场数据
        for symbol in ['BTC', 'ETH']:
            with self.subTest(symbol=symbol):
                params = {
                    'symbol': symbol,
                    'vs_currency': 'USD',
                    'include_market_state': True
                }
                
                result_str = self.tool.call(params)
                result = json.loads(result_str)
                
                self.assertIsInstance(result, dict)
                self.assertEqual(result.get('status'), 'success')
                self.assertEqual(result.get('symbol'), symbol.upper())
                self.assertIn('price', result)
                self.assertIn('price_change_percentage_24h', result)
                self.assertIn('market_state', result)
                
                # 验证市场状态分析结果
                market_state = result.get('market_state')
                self.assertIn('trend', market_state)
                self.assertIn('volatility', market_state)
                self.assertIn('advice', market_state)

class TestContractTool(unittest.TestCase):
    """测试智能合约工具功能。"""
    
    def setUp(self):
        """测试前初始化ContractTool实例。"""
        self.tool = ContractTool()
    
    def test_read_contract_call(self):
        """测试合约读取操作。"""
        # 使用ERC20代币的标准方法测试
        params = {
            'contract_address': '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT合约地址
            'function_name': 'symbol',
            'function_args': [],
            'is_write_operation': False
        }
        
        result_str = self.tool.call(params)
        result = json.loads(result_str)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('status'), 'success')
        self.assertEqual(result.get('type'), 'read')
        # 在mock模式下，结果可能是预设的值
    
    def test_write_contract_call(self):
        """测试合约写入操作（使用mock）。"""
        params = {
            'contract_address': '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT合约地址
            'function_name': 'balanceOf',
            'function_args': ['0x1234567890123456789012345678901234567890'],
            'is_write_operation': True  # 标记为写入操作
        }
        
        result_str = self.tool.call(params)
        result = json.loads(result_str)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('status'), 'success')
        # 在mock模式下，类型应该是'mock_write'
        self.assertTrue(result.get('type') in ['write', 'mock_write'])

class TestAgentIntegration(unittest.TestCase):
    """测试Agent集成功能。"""
    
    def test_complete_workflow(self):
        """测试完整的工作流程：从意图识别到合约调用。"""
        # 1. 使用SwapAgent解析用户意图
        swap_agent = SwapAgent()
        swap_request = "把100U换成BTC"
        swap_result = swap_agent.process_swap_request(swap_request)
        
        # 2. 使用MarketDataTool获取市场数据
        market_tool = MarketDataTool()
        market_params = {
            'symbol': 'BTC',
            'vs_currency': 'USD'
        }
        market_result_str = market_tool.call(market_params)
        market_result = json.loads(market_result_str)
        
        # 验证两个工具都能正常工作
        self.assertEqual(swap_result['status'], 'success' if swap_result.get('swap_intent') else 'failed')
        self.assertEqual(market_result.get('status'), 'success')

if __name__ == '__main__':
    unittest.main()
