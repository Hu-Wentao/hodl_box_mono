#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Market Tools for HODL Box Agent

This module provides tools for fetching cryptocurrency market data,
including price information, market trends, and volatility indicators.
"""

import json
import os
from typing import Dict, Any, Optional
from qwen_agent.tools.base import BaseTool, register_tool
import requests
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

@register_tool('get_market_data')
class MarketDataTool(BaseTool):
    """
    Tool for fetching cryptocurrency market data.
    
    This tool retrieves current market information for specified cryptocurrencies,
    including price, 24h change, and market state analysis.
    """
    
    description = "获取加密货币市场数据，包括价格、24小时涨跌幅和市场状态"
    parameters_schema = {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "要查询的加密货币符号，如BTC、ETH、USDT等"
            },
            "vs_currency": {
                "type": "string",
                "description": "计价货币，默认为USD"
            },
            "include_market_state": {
                "type": "boolean",
                "description": "是否包含市场状态分析"
            }
        },
        "required": ["symbol"]
    }
    
    def __init__(self):
        """Initialize the market data tool with API configuration."""
        super().__init__()
        # Set up API configuration
        self.api_key = os.getenv('COINMARKETCAP_API_KEY', '')
        self.api_url = os.getenv('MARKET_DATA_API_URL', 'https://api.coingecko.com/api/v3')
        # Default to a mock implementation if no API key is provided
        self.use_mock = not self.api_key and 'coinmarketcap' in self.api_url.lower()
    
    def call(self, params: Dict[str, Any]) -> str:
        """
        Execute the market data fetching tool.
        
        Args:
            params: Dictionary containing the parameters for market data retrieval
            
        Returns:
            JSON string with cryptocurrency market data
        """
        # Extract and validate parameters
        symbol = params.get('symbol', '').lower()
        vs_currency = params.get('vs_currency', 'usd').lower()
        include_market_state = params.get('include_market_state', True)
        
        if not symbol:
            return json.dumps({
                'error': 'Symbol parameter is required',
                'status': 'error'
            })
        
        try:
            # Fetch market data
            if self.use_mock:
                data = self._get_mock_data(symbol, vs_currency)
            else:
                data = self._fetch_market_data(symbol, vs_currency)
            
            # Add market state analysis if requested
            if include_market_state:
                data['market_state'] = self._analyze_market_state(data)
            
            return json.dumps(data, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                'error': str(e),
                'status': 'error'
            })
    
    def _fetch_market_data(self, symbol: str, vs_currency: str) -> Dict[str, Any]:
        """
        Fetch real market data from an external API.
        
        Args:
            symbol: Cryptocurrency symbol
            vs_currency: Reference currency for pricing
            
        Returns:
            Market data dictionary
        """
        try:
            # Construct URL for CoinGecko API
            url = f"{self.api_url}/simple/price"
            params = {
                'ids': symbol,
                'vs_currencies': vs_currency,
                'include_24hr_change': True,
                'include_7d_change': True
            }
            
            # Make request
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise error for bad status codes
            
            data = response.json()
            
            # Format the data
            if symbol in data:
                price_data = data[symbol]
                return {
                    'symbol': symbol.upper(),
                    'price': price_data.get(vs_currency, 0),
                    'price_change_percentage_24h': price_data.get(f'{vs_currency}_24h_change', 0),
                    'price_change_percentage_7d': price_data.get(f'{vs_currency}_7d_change', 0),
                    'vs_currency': vs_currency.upper(),
                    'timestamp': self._get_current_timestamp(),
                    'source': 'CoinGecko API',
                    'status': 'success'
                }
            else:
                raise ValueError(f"Symbol {symbol} not found")
                
        except Exception as e:
            # If the real API fails, fall back to mock data
            print(f"Error fetching real data: {e}, falling back to mock data")
            return self._get_mock_data(symbol, vs_currency)
    
    def _get_mock_data(self, symbol: str, vs_currency: str) -> Dict[str, Any]:
        """
        Generate mock market data for demonstration purposes.
        
        Args:
            symbol: Cryptocurrency symbol
            vs_currency: Reference currency for pricing
            
        Returns:
            Mock market data dictionary
        """
        # Define some sample prices for common cryptocurrencies
        mock_prices = {
            'btc': 42000.0,
            'eth': 2800.0,
            'usdt': 1.0,
            'usdc': 1.0,
            'bnb': 350.0,
            'sol': 120.0,
            'ada': 0.5,
            'dot': 8.0,
            'link': 15.0,
            'uni': 7.5
        }
        
        # Get price for the requested symbol or use a default
        price = mock_prices.get(symbol, 100.0)
        
        # Generate some random but realistic percentage changes
        import random
        change_24h = round(random.uniform(-5.0, 5.0), 2)
        change_7d = round(random.uniform(-10.0, 10.0), 2)
        
        return {
            'symbol': symbol.upper(),
            'price': price,
            'price_change_percentage_24h': change_24h,
            'price_change_percentage_7d': change_7d,
            'vs_currency': vs_currency.upper(),
            'timestamp': self._get_current_timestamp(),
            'source': 'Mock Data',
            'status': 'success'
        }
    
    def _analyze_market_state(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market state based on price changes.
        
        Args:
            data: Market data dictionary
            
        Returns:
            Market state analysis
        """
        change_24h = data.get('price_change_percentage_24h', 0)
        change_7d = data.get('price_change_percentage_7d', 0)
        
        # Determine market trend
        if change_24h > 5 and change_7d > 10:
            trend = 'bull_market'
            trend_description = '强劲牛市'
        elif change_24h > 0 and change_7d > 0:
            trend = 'uptrend'
            trend_description = '上升趋势'
        elif change_24h < -5 and change_7d < -10:
            trend = 'bear_market'
            trend_description = '熊市'
        elif change_24h < 0 and change_7d < 0:
            trend = 'downtrend'
            trend_description = '下降趋势'
        else:
            trend = 'sideways'
            trend_description = '横盘整理'
        
        # Determine volatility
        volatility = 'high' if abs(change_24h) > 3 else 'medium' if abs(change_24h) > 1 else 'low'
        
        # Provide advice based on market state
        advice = self._get_market_advice(trend, volatility)
        
        return {
            'trend': trend,
            'trend_description': trend_description,
            'volatility': volatility,
            'advice': advice
        }
    
    def _get_market_advice(self, trend: str, volatility: str) -> str:
        """
        Generate market advice based on trend and volatility.
        
        Args:
            trend: Market trend
            volatility: Market volatility level
            
        Returns:
            Market advice string
        """
        advice_map = {
            'bull_market': {
                'high': '牛市高波动，建议谨慎追高，考虑分批获利。',
                'medium': '牛市中等波动，可适度跟进但保持风险控制。',
                'low': '牛市低波动，可能预示更大上涨，关注成交量变化。'
            },
            'uptrend': {
                'high': '上升趋势高波动，适合设置止损的逢低买入策略。',
                'medium': '稳定上升趋势，适合定投策略。',
                'low': '低波动上升，突破阻力位可能加速上涨。'
            },
            'bear_market': {
                'high': '熊市高波动，建议观望或小仓位试探，严格止损。',
                'medium': '熊市中等波动，耐心等待抄底机会，关注基本面。',
                'low': '熊市低波动，可能即将出现方向性突破。'
            },
            'downtrend': {
                'high': '下降趋势高波动，避免抄底，等待趋势反转信号。',
                'medium': '稳定下降趋势，保持观望或考虑对冲策略。',
                'low': '低波动下降，可能是下跌中继，谨慎操作。'
            },
            'sideways': {
                'high': '横盘高波动，适合区间交易策略，关注突破方向。',
                'medium': '横盘整理，等待明确方向，可少量布局。',
                'low': '低波动横盘，即将选择方向，密切关注成交量变化。'
            }
        }
        
        return advice_map.get(trend, {}).get(volatility, '市场状况不明，建议保持谨慎。')
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp as ISO format string.
        
        Returns:
            ISO format timestamp string
        """
        import datetime
        return datetime.datetime.now().isoformat()
