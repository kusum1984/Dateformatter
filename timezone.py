import os
from datetime import datetime
from typing import Dict, Any
import pytz
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TimezoneAwareDateLLM:
    """
    LLM system capable of understanding and processing dates with timezone awareness
    """
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.setup_prompts()
        self.setup_chains()

    def setup_prompts(self):
        """Initialize all prompt templates"""
        self.date_timezone_prompt = PromptTemplate(
            input_variables=["input_text"],
            template="""
            You are an advanced AI assistant with exceptional date and timezone understanding capabilities.
            Your task is to analyze the following text and:
            1. Identify all date/time references
            2. Detect implied or explicit timezones
            3. Convert all dates to ISO 8601 format with timezone (YYYY-MM-DDTHH:MM:SS±HH:MM)
            4. Show equivalent times in major global timezones (UTC, EST, CST, PST, GMT, IST, etc.)
            
            STRICT RULES:
            1. Always assume local timezone if not specified (based on context clues)
            2. For relative times (e.g., "tomorrow"), calculate from current moment in detected timezone
            3. Always include timezone offset in output
            4. Show conversions for at least 3 major timezones
            5. Handle daylight saving time automatically
            
            Input text: {input_text}
            
            Required output format:
            Original: [original text]
            Detected Timezone: [primary detected timezone]
            Standardized (ISO 8601): [primary date in ISO format]
            Global Equivalents:
            - UTC: [date/time in UTC]
            - EST: [date/time in EST]
            - IST: [date/time in IST]
            - [Other relevant timezones...]
            """
        )

    def setup_chains(self):
        """Setup processing chains"""
        self.date_parser_chain = (
            {"input_text": RunnablePassthrough()}
            | self.date_timezone_prompt
            | self.llm
            | StrOutputParser()
        )

    async def process_datetime_with_timezones(self, text: str) -> Dict[str, Any]:
        """Process text with datetime and timezone information"""
        response = await self.date_parser_chain.ainvoke(text)
        return self._parse_response(response)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM's response"""
        result = {
            "original": "",
            "detected_timezone": "",
            "standardized": "",
            "global_equivalents": {}
        }

        # Parse the structured response
        if "Original:" in response:
            result["original"] = response.split("Original:")[1].split("Detected Timezone:")[0].strip()
        if "Detected Timezone:" in response:
            result["detected_timezone"] = response.split("Detected Timezone:")[1].split("Standardized (ISO 8601):")[0].strip()
        if "Standardized (ISO 8601):" in response:
            result["standardized"] = response.split("Standardized (ISO 8601):")[1].split("Global Equivalents:")[0].strip()
        if "Global Equivalents:" in response:
            equivalents = response.split("Global Equivalents:")[1].strip()
            for line in equivalents.split("\n"):
                if "-" in line:
                    tz, dt = line.split(":", 1)
                    result["global_equivalents"][tz.strip("- ")] = dt.strip()

        return result

# Example usage
async def main():
    # Initialize the timezone-aware LLM
    tz_llm = TimezoneAwareDateLLM()

    # Test cases with different timezone scenarios
    test_cases = [
        "Meeting scheduled for tomorrow at 2pm EST",
        "Deadline: 15th June 2023 5:30pm IST",
        "The webinar starts at 9am PST on Wednesday",
        "Flight departs at 2024-03-15T08:45:00+09:00 (Tokyo time)",
        "New Year's Eve in Sydney, Australia",
        "Our daily standup at 10:30am (team is distributed globally)"
    ]

    print("=== Timezone-Aware Date Processing Demo ===")
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {text}")
        
        # Process the text
        result = await tz_llm.process_datetime_with_timezones(text)
        
        print("\nResults:")
        print(f"Detected Timezone: {result['detected_timezone']}")
        print(f"Standardized: {result['standardized']}")
        print("Global Equivalents:")
        for tz, dt in result['global_equivalents'].items():
            print(f"- {tz}: {dt}")

    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Enter text with dates/times to see timezone-aware conversions (type 'quit' to exit)")
    while True:
        user_input = input("\nEnter text: ")
        if user_input.lower() == 'quit':
            break
        
        result = await tz_llm.process_datetime_with_timezones(user_input)
        print("\nResults:")
        print(f"Detected Timezone: {result['detected_timezone']}")
        print(f"Standardized: {result['standardized']}")
        print("Global Equivalents:")
        for tz, dt in result['global_equivalents'].items():
            print(f"- {tz}: {dt}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



##########################
import os
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TimezoneAwareDateLLM:
    """
    LLM system capable of understanding and processing dates with timezone awareness
    """
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.setup_prompts()
        self.setup_chains()

    def setup_prompts(self):
        """Initialize all prompt templates"""
        self.date_timezone_prompt = PromptTemplate(
            input_variables=["input_text"],
            template="""
            You are an advanced AI assistant with exceptional date and timezone understanding capabilities.
            Your task is to analyze the following text and:
            1. Identify all date/time references
            2. Detect implied or explicit timezones
            3. Convert all dates to ISO 8601 format with timezone (YYYY-MM-DDTHH:MM:SS±HH:MM)
            4. Show equivalent times in major global timezones (UTC, EST, CST, PST, GMT, IST, etc.)
            
            STRICT RULES:
            1. Always assume local timezone if not specified (based on context clues)
            2. For relative times (e.g., "tomorrow"), calculate from current moment in detected timezone
            3. Always include timezone offset in output
            4. Show conversions for at least 3 major timezones
            5. Handle daylight saving time automatically
            
            Input text: {input_text}
            
            Required output format:
            Original: [original text]
            Detected Timezone: [primary detected timezone]
            Standardized (ISO 8601): [primary date in ISO format]
            Global Equivalents:
            - UTC: [date/time in UTC]
            - EST: [date/time in EST]
            - IST: [date/time in IST]
            - [Other relevant timezones...]
            """
        )

    def setup_chains(self):
        """Setup processing chains"""
        self.date_parser_chain = (
            {"input_text": RunnablePassthrough()}
            | self.date_timezone_prompt
            | self.llm
            | StrOutputParser()
        )

    async def process_datetime_with_timezones(self, text: str) -> Dict[str, Any]:
        """Process text with datetime and timezone information"""
        response = await self.date_parser_chain.ainvoke(text)
        return self._parse_response(response)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM's response with robust error handling"""
        result = {
            "original": "",
            "detected_timezone": "",
            "standardized": "",
            "global_equivalents": {}
        }

        try:
            # Parse the structured response with safe splitting
            parts = {
                "original": response.split("Original:")[1] if "Original:" in response else "",
                "detected_timezone": response.split("Detected Timezone:")[1] if "Detected Timezone:" in response else "",
                "standardized": response.split("Standardized (ISO 8601):")[1] if "Standardized (ISO 8601):" in response else "",
                "equivalents": response.split("Global Equivalents:")[1] if "Global Equivalents:" in response else ""
            }

            # Clean each part
            result["original"] = parts["original"].split("Detected Timezone:")[0].strip() if parts["original"] else ""
            result["detected_timezone"] = parts["detected_timezone"].split("Standardized (ISO 8601):")[0].strip() if parts["detected_timezone"] else ""
            result["standardized"] = parts["standardized"].split("Global Equivalents:")[0].strip() if parts["standardized"] else ""

            # Parse equivalents with robust handling
            if parts["equivalents"]:
                for line in parts["equivalents"].split("\n"):
                    line = line.strip()
                    if line.startswith("-") and ":" in line:
                        try:
                            # Split only on first colon
                            tz_part, dt_part = line[1:].split(":", 1)
                            tz = tz_part.strip()
                            dt = dt_part.strip()
                            if tz and dt:  # Only add if both parts exist
                                result["global_equivalents"][tz] = dt
                        except ValueError:
                            continue  # Skip malformed lines

        except Exception as e:
            print(f"Warning: Error parsing response - {str(e)}")

        return result

async def main():
    """Example usage with interactive mode"""
    # Initialize the timezone-aware LLM
    tz_llm = TimezoneAwareDateLLM()

    # Test cases with different timezone scenarios
    test_cases = [
        "Meeting scheduled for tomorrow at 2pm EST",
        "Deadline: 15th June 2023 5:30pm IST",
        "The webinar starts at 9am PST on Wednesday",
        "Flight departs at 2024-03-15T08:45:00+09:00 (Tokyo time)",
        "New Year's Eve in Sydney, Australia",
        "Our daily standup at 10:30am (team is distributed globally)"
    ]

    print("=== Timezone-Aware Date Processing Demo ===")
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {text}")
        
        # Process the text
        result = await tz_llm.process_datetime_with_timezones(text)
        
        print("\nResults:")
        print(f"Original: {result['original']}")
        print(f"Detected Timezone: {result['detected_timezone']}")
        print(f"Standardized: {result['standardized']}")
        print("Global Equivalents:")
        for tz, dt in result['global_equivalents'].items():
            print(f"- {tz}: {dt}")

    # Interactive mode
    print("\n=== Interactive Mode ===")
    print("Enter text with dates/times to see timezone-aware conversions (type 'quit' to exit)")
    while True:
        user_input = input("\nEnter text: ").strip()
        if user_input.lower() in ('quit', 'exit'):
            break
        
        if not user_input:
            print("Please enter some text")
            continue
        
        result = await tz_llm.process_datetime_with_timezones(user_input)
        print("\nResults:")
        print(f"Original: {result['original']}")
        print(f"Detected Timezone: {result['detected_timezone']}")
        print(f"Standardized: {result['standardized']}")
        print("Global Equivalents:")
        for tz, dt in result['global_equivalents'].items():
            print(f"- {tz}: {dt}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
