import re
from typing import Dict, Any, Optional

class NLPEngine:
    """
    A simple rule-based NLP engine to extract intents and entities 
    from natural language commands for data generation.
    """
    
    PATTERNS = {
        "count": r"(\d+)\s*(?:records|rows|users|customers|accounts|transactions|items)?",
        "format": r"(csv|json|xml)",
        "type": r"(customer|account|transaction)"
    }
    
    DEFAULT_COUNT = 10
    DEFAULT_FORMAT = "csv"
    DEFAULT_TYPE = "customer"

    @staticmethod
    def parse_command(text: str) -> Dict[str, Any]:
        """
        Parse the user's input text and return a structured command dictionary.
        
        Args:
            text (str): The user's natural language request.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - type (str): The type of data to generate (customer, account, transaction)
                - count (int): Number of records
                - format (str): Output format (csv, json)
                - intent (str): Currently always "generate" if patterns match
        """
        text = text.lower()
        
        # 1. Detect Count
        count_match = re.search(NLPEngine.PATTERNS["count"], text)
        count = int(count_match.group(1)) if count_match else NLPEngine.DEFAULT_COUNT
        
        # 2. Detect Format
        format_match = re.search(NLPEngine.PATTERNS["format"], text)
        fmt = format_match.group(1) if format_match else NLPEngine.DEFAULT_FORMAT
        
        # 3. Detect Data Type (Entity)
        # Check patterns; priority given to explicit mentions
        data_type = NLPEngine.DEFAULT_TYPE
        if "account" in text:
            data_type = "account"
        elif "transaction" in text:
            data_type = "transaction"
        elif "customer" in text or "user" in text:
            data_type = "customer"
            
        return {
            "intent": "generate",
            "type": data_type,
            "count": min(count, 10000), # Safety cap
            "format": fmt
        }

    @staticmethod
    def process_request(text: str) -> Dict[str, Any]:
        """
        Process the text and return a response message plus the structured command.
        """
        command = NLPEngine.parse_command(text)
        
        response_msg = (
            f"Understood. I will generate {command['count']} {command['type']} records "
            f"in {command['format'].upper()} format."
        )
        
        return {
            "message": response_msg,
            "command": command
        }
