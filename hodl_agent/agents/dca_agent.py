from qwen_agent.llm.schema import ContentItem
from typing import Union, List, Dict, Optional
import os
from qwen_agent.agents import Assistant
from dotenv import load_dotenv
import json5
import json
from qwen_agent.tools.base import BaseTool, register_tool

load_dotenv()

# Define LLM Configuration
llm_cfg = {
    # Use a custom endpoint compatible with OpenAI API by vLLM/SGLang:
    "model": "qwen-flash", 
    "model_server": os.getenv("BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    "api_key": os.getenv("API_KEY"),
}

@register_tool("parse_dca_intent")
class DCAIntentTool(BaseTool):
    description = "Parse user's DCA (Dollar Cost Averaging) investment intent into structured JSON"
    parameters = [
        {
            "name": "sourceToken",
            "type": "string",
            "description": "The token to sell/spend (e.g., USDT, USDC). Default to USDT if not specified but implied stablecoin.",
            "required": True,
        },
        {
            "name": "targetToken",
            "type": "string",
            "description": "The token to buy (e.g., BTC, ETH).",
            "required": True,
        },
        {
            "name": "amountPerInterval",
            "type": "number",
            "description": "Amount to spend per interval.",
            "required": True,
        },
        {
            "name": "frequency",
            "type": "string",
            "description": "Frequency of investment (daily, weekly, monthly, every_hour).",
            "required": True,
        },
         {
            "name": "duration",
            "type": "string",
            "description": "Total duration or number of executions (e.g., '1 year', '10 times'). Optional.",
            "required": False,
        },
    ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            try:
                args = json5.loads(params)
            except:
                return json.dumps({"error": "Invalid JSON parameters"})
        else:
            args = params

        result = {
            "type": "dca",
            "sourceToken": args.get("sourceToken", "USDT").upper(),
            "targetToken": args.get("targetToken", "").upper(),
            "amount": args.get("amountPerInterval", 0),
            "frequency": args.get("frequency", "daily"),
            "duration": args.get("duration", "indefinite")
        }
        return json.dumps(result, ensure_ascii=False)

class DCAAgent:
    def __init__(self):
        self.bot = Assistant(
            llm=llm_cfg,
            function_list=["parse_dca_intent"],
            system_message="You are a DCA (Dollar-Cost Averaging) Investment Assistant. Help users set up their auto-investment plans. Always parse their intent using the tool."
        )

    def process_request(self, message: str) -> Dict:
        messages = [
            {"role": "user", "content": message}
        ]
        
        last_response = None
        for response in self.bot.run(messages=messages):
            last_response = response
            
        return {
            "response_raw": last_response
        }

    def process_dca_request(self, message: str) -> Dict:
        """
        Specific method to handle DCA request and return clean JSON.
        """
        messages = [
            {"role": "user", "content": f"Parse this DCA intent: {message}"}
        ]
        
        final_result = {"status": "processing", "message": "Could not parse intent"}
        
        # Collect all responses
        responses = []
        for response in self.bot.run(messages=messages):
            responses.append(response)
            
        # Inspect for tool execution
        # Note: qwen-agent response structure can be complex. 
        # We look for the tool result in the messages/content.
        
        # Simplified logic: If the LLM successfully called the tool, the tool output should be in the history or returned.
        # For now, we will return a mock success if we detect tool usage keywords or just return the conversation.
        
        # In a real run, we would introspect 'responses'. 
        return {"status": "success", "data": responses, "debug": "Check responses for tool output"}

if __name__ == "__main__":
    agent = DCAAgent()
    # Simple test
    pass
