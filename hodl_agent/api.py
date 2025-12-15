#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HODL Box API

RESTful API endpoints for interacting with the HODL Box AI Agent.
Provides HTTP interfaces for processing user intents and executing blockchain operations.
"""

import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agent modules
from agents.swap_agent import SwapAgent
from agents.mental_support_agent import MentalSupportAgent
from agents.dca_agent import DCAAgent
from agents.tools.market_tools import MarketDataTool
from agents.tools.contract_tools import ContractTool

# Initialize FastAPI application
app = FastAPI(
    title="HODL Box API",
    description="API for HODL Box AI Agent - Cryptocurrency Investment, DCA, and Mental Support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
swap_agent = SwapAgent()
mental_support_agent = MentalSupportAgent()
dca_agent = DCAAgent()
market_tool = MarketDataTool()
contract_tool = ContractTool()

# Request and response models
class SwapRequest(BaseModel):
    """Model for token swap request."""
    message: str
    chain: Optional[str] = None

class DCARequest(BaseModel):
    """Model for DCA request."""
    message: str

class MentalSupportRequest(BaseModel):
    """Model for mental support request."""
    message: str
    market_state: Optional[str] = "neutral"

class MarketDataRequest(BaseModel):
    """Model for market data request."""
    symbol: str
    vs_currency: Optional[str] = "USD"
    include_market_state: Optional[bool] = True

class ContractCallRequest(BaseModel):
    """Model for smart contract call request."""
    contract_address: str
    function_name: str
    function_args: Optional[List[Any]] = []
    abi: Optional[Dict[str, Any]] = None
    is_write_operation: Optional[bool] = False
    gas_limit: Optional[int] = 300000

class ResponseModel(BaseModel):
    """Generic API response model."""
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/health")
def health_check():
    """Health check endpoint to verify API is running."""
    return {
        "status": "healthy",
        "service": "HODL Box API",
        "version": "1.0.0"
    }

@app.post("/api/swap", response_model=ResponseModel)
async def process_swap_request(request: SwapRequest):
    """
    Process a token swap request.
    
    Args:
        request: SwapRequest containing user message and optional chain
        
    Returns:
        ResponseModel with swap intent analysis
    """
    try:
        # Combine message with chain if provided
        full_message = request.message
        if request.chain:
            full_message += f" (在{request.chain}链上)"
        
        # Process the swap request
        result = swap_agent.process_swap_request(full_message)
        
        return ResponseModel(
            status="success",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dca", response_model=ResponseModel)
async def process_dca_request(request: DCARequest):
    """
    Process a DCA request.
    """
    try:
        result = dca_agent.process_dca_request(request.message)
        return ResponseModel(status="success", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mental-support", response_model=ResponseModel)
async def provide_mental_support(request: MentalSupportRequest):
    """
    Provide mental support to the user.
    
    Args:
        request: MentalSupportRequest containing user message and optional market state
        
    Returns:
        ResponseModel with support response
    """
    try:
        # Provide mental support based on message and market state
        result = mental_support_agent.provide_support(
            request.message,
            request.market_state
        )
        
        return ResponseModel(
            status="success",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/market-data", response_model=ResponseModel)
async def get_market_data(request: MarketDataRequest):
    """
    Fetch cryptocurrency market data.
    
    Args:
        request: MarketDataRequest containing symbol and optional parameters
        
    Returns:
        ResponseModel with market data
    """
    try:
        # Convert request to parameters dictionary
        params = {
            "symbol": request.symbol,
            "vs_currency": request.vs_currency,
            "include_market_state": request.include_market_state
        }
        
        # Call market data tool
        result_json = market_tool.call(params)
        result = json.loads(result_json)
        
        # Check for errors in the result
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return ResponseModel(
            status="success",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contract-call", response_model=ResponseModel)
async def execute_contract_call(request: ContractCallRequest):
    """
    Execute a smart contract call.
    
    Args:
        request: ContractCallRequest containing contract details
        
    Returns:
        ResponseModel with contract call result
    """
    try:
        # Convert request to parameters dictionary
        params = {
            "contract_address": request.contract_address,
            "function_name": request.function_name,
            "function_args": request.function_args,
            "is_write_operation": request.is_write_operation,
            "gas_limit": request.gas_limit
        }
        
        # Add ABI if provided
        if request.abi:
            params["abi"] = request.abi
        
        # Call contract tool
        result_json = contract_tool.call(params)
        result = json.loads(result_json)
        
        # Check for errors in the result
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return ResponseModel(
            status="success",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """
    Generic chat endpoint that routes to appropriate agent based on message content.
    
    Args:
        request: HTTP request containing chat message
        
    Returns:
        JSON response with appropriate agent response
    """
    try:
        # Parse request body
        body = await request.json()
        message = body.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Simple routing logic based on message content
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ["定投", "dca", "invest", "auto buy"]):
            # Route to DCA agent
            result = dca_agent.process_dca_request(message)
            return {
                "type": "dca",
                "response": result
            }
        elif any(keyword in message_lower for keyword in ["换", "交换", "swap", "buy", "sell", "买", "卖"]):
            # Route to swap agent
            result = swap_agent.process_swap_request(message)
            return {
                "type": "swap",
                "response": result
            }
        elif any(keyword in message_lower for keyword in ["心情", "焦虑", "担心", "恐惧", "支持", "鼓励"]):
            # Route to mental support agent
            result = mental_support_agent.provide_support(message)
            return {
                "type": "mental_support",
                "response": result
            }
        elif any(keyword in message_lower for keyword in ["价格", "市场", "行情", "price", "market", "trend"]):
            # Try to extract symbol for market data
            import re
            symbol_match = re.search(r'[a-zA-Z]{2,5}', message_lower)
            if symbol_match:
                symbol = symbol_match.group(0)
                params = {"symbol": symbol}
                result_json = market_tool.call(params)
                result = json.loads(result_json)
                return {
                    "type": "market_data",
                    "response": result
                }
            else:
                # If no symbol found, ask for clarification
                return {
                    "type": "clarification",
                    "response": "请提供您想查询的加密货币符号，例如BTC、ETH等"
                }
        else:
            # Default response for unrecognized intent
            return {
                "type": "general",
                "response": {
                    "message": "我是HODL Box助手，我可以帮您处理代币交换、提供投资心理支持或查询市场数据。请告诉我您需要什么帮助？"
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_server():
    """Run the FastAPI server."""
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    # Run the server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )

if __name__ == "__main__":
    run_server()
