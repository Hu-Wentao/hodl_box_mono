#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HODL Box API 测试文件

本文件包含对API接口的测试用例，确保HTTP端点能够正确响应请求。
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from fastapi.testclient import TestClient
from api import app  # 导入FastAPI应用

class TestAPIEndpoints(unittest.TestCase):
    """测试API接口功能。"""
    
    def setUp(self):
        """测试前初始化测试客户端。"""
        self.client = TestClient(app)
    
    def test_health_check(self):
        """测试健康检查接口。"""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy", "service": "HODL Box AI Agent API"})
    
    @patch('api.SwapAgent.process_swap_request')
    def test_swap_endpoint(self, mock_process_swap_request):
        """测试代币交换处理接口。"""
        # 配置模拟返回值
        mock_result = {
            "status": "success",
            "original_message": "把100U换成BTC",
            "response": "已解析交换请求",
            "swap_intent": {
                "chain": "Ethereum",
                "tokenIn": "USDT",
                "tokenOut": "BTC",
                "amount": "100"
            }
        }
        mock_process_swap_request.return_value = mock_result
        
        # 发送测试请求
        request_data = {
            "message": "把100U换成BTC",
            "user_id": "test_user_123"
        }
        response = self.client.post("/api/swap", json=request_data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data, mock_result)
        
        # 验证函数调用
        mock_process_swap_request.assert_called_once_with("把100U换成BTC")
    
    @patch('api.MentalSupportAgent.provide_support')
    def test_mental_support_endpoint(self, mock_provide_support):
        """测试心理支持接口。"""
        # 配置模拟返回值
        mock_result = {
            "status": "success",
            "original_message": "我很担心市场继续下跌",
            "response": "别担心，市场波动是正常的...",
            "detected_emotion": "fearful",
            "motivational_content": "长期投资通常会获得更好的回报..."
        }
        mock_provide_support.return_value = mock_result
        
        # 发送测试请求
        request_data = {
            "message": "我很担心市场继续下跌",
            "user_id": "test_user_123",
            "market_state": "bear_market"
        }
        response = self.client.post("/api/mental-support", json=request_data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data, mock_result)
        
        # 验证函数调用
        mock_provide_support.assert_called_once_with("我很担心市场继续下跌", "bear_market")
    
    @patch('api.MarketDataTool')
    def test_market_data_endpoint(self, mock_MarketDataTool):
        """测试市场数据接口。"""
        # 配置模拟对象
        mock_tool = MagicMock()
        mock_MarketDataTool.return_value = mock_tool
        
        mock_result_str = json.dumps({
            "status": "success",
            "symbol": "BTC",
            "price": 50000,
            "price_change_percentage_24h": 2.5,
            "market_state": {
                "trend": "upward",
                "volatility": "medium",
                "advice": "保持观望"
            }
        })
        mock_tool.call.return_value = mock_result_str
        
        # 发送测试请求
        request_data = {
            "symbol": "BTC",
            "vs_currency": "USD"
        }
        response = self.client.post("/api/market-data", json=request_data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['symbol'], 'BTC')
        
        # 验证函数调用
        mock_tool.call.assert_called_once()
    
    @patch('api.ContractTool')
    def test_contract_call_endpoint(self, mock_ContractTool):
        """测试智能合约调用接口。"""
        # 配置模拟对象
        mock_tool = MagicMock()
        mock_ContractTool.return_value = mock_tool
        
        mock_result_str = json.dumps({
            "status": "success",
            "type": "read",
            "result": "USDT"
        })
        mock_tool.call.return_value = mock_result_str
        
        # 发送测试请求
        request_data = {
            "contract_address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "function_name": "symbol",
            "function_args": [],
            "is_write_operation": False
        }
        response = self.client.post("/api/contract-call", json=request_data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['type'], 'read')
        
        # 验证函数调用
        mock_tool.call.assert_called_once_with(request_data)
    
    @patch('api.SwapAgent')
    def test_chat_endpoint(self, mock_SwapAgent):
        """测试通用聊天路由接口。"""
        # 配置模拟对象
        mock_agent = MagicMock()
        mock_SwapAgent.return_value = mock_agent
        
        mock_agent.chat.return_value = "这是一个测试回复"
        
        # 发送测试请求
        request_data = {
            "message": "我想交换一些代币",
            "user_id": "test_user_123",
            "agent_type": "swap"
        }
        response = self.client.post("/api/chat", json=request_data)
        
        # 验证响应
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "这是一个测试回复"})
        
        # 验证函数调用
        mock_agent.chat.assert_called_once_with("我想交换一些代币")
    
    def test_invalid_endpoint(self):
        """测试不存在的接口。"""
        response = self.client.get("/invalid_endpoint")
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
    
    def test_invalid_agent_type_in_chat(self):
        """测试无效的Agent类型。"""
        request_data = {
            "message": "测试消息",
            "user_id": "test_user_123",
            "agent_type": "invalid_agent_type"
        }
        response = self.client.post("/api/chat", json=request_data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Invalid agent_type. Must be 'swap' or 'mental'.")

if __name__ == "__main__":
    unittest.main()
