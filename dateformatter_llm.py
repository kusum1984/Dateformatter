import os
from datetime import datetime
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOpenAI
import dateutil.parser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DateAwareLLM:
    """
    LLM system capable of understanding and processing dates in any format
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
        self.date_understanding_prompt = PromptTemplate(
            input_variables=["input_text"],
            template="""
            You are an advanced AI assistant with exceptional date understanding capabilities.
            Your task is to analyze the following text and identify all date references,
            then convert them to a standard ISO format (YYYY-MM-DD).

            Rules:
            1. Identify all date references in the text
            2. Convert them to ISO format while preserving context
            3. Handle ambiguous dates intelligently
            4. Preserve all non-date text exactly as is
            5. For date ranges, convert both start and end dates

            Special cases:
            - Relative dates (today, tomorrow, next Monday)
            - Partial dates (June 2023, 2025)
            - Mixed formats (12th Jan '23)
            - Non-Gregorian calendars when specified

            Input text: {input_text}

            Output format should be:
            Original text: [original text with dates]
            Standardized text: [text with dates converted to ISO format]
            Extracted dates: [list of all dates found in ISO format]
            """
        )

        self.date_qa_prompt = PromptTemplate(
            input_variables=["question", "date_context"],
            template="""
            You are a date-aware question answering system. Use the following context about dates
            to answer the question precisely. When answering about dates, always provide both
            the original date reference and the standardized version.

            Date context: {date_context}
            Question: {question}

            Answer the question while:
            1. Showing you understand the date references
            2. Providing date calculations when needed
            3. Maintaining the original date formats when useful
            4. Adding ISO dates in parentheses when helpful

            Answer:
            """
        )

    def setup_chains(self):
        """Setup processing chains using modern Runnable syntax"""
        self.date_parser_chain = (
            {"input_text": RunnablePassthrough()}
            | self.date_understanding_prompt
            | self.llm
            | StrOutputParser()
        )

        self.qa_chain = (
            {"question": RunnablePassthrough(), "date_context": RunnablePassthrough()}
            | self.date_qa_prompt
            | self.llm
            | StrOutputParser()
        )

    async def extract_dates(self, text: str) -> Dict[str, Any]:
        """Identify and standardize dates in text"""
        response = await self.date_parser_chain.ainvoke(text)
        return self._parse_date_response(response)

    def _parse_date_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM's date extraction response"""
        result = {
            "original_text": "",
            "standardized_text": "",
            "extracted_dates": []
        }

        # Parse the structured response
        if "Original text:" in response:
            result["original_text"] = response.split("Original text:")[1].split("Standardized text:")[0].strip()
        if "Standardized text:" in response:
            result["standardized_text"] = response.split("Standardized text:")[1].split("Extracted dates:")[0].strip()
        if "Extracted dates:" in response:
            dates_str = response.split("Extracted dates:")[1].strip()
            result["extracted_dates"] = [d.strip() for d in dates_str.split(",")] if dates_str else []

        return result

    async def answer_date_question(self, question: str, date_context: str = None):
        """Answer questions involving date understanding"""
        if not date_context:
            date_info = await self.extract_dates(question)
            date_context = date_info["standardized_text"]
        return await self.qa_chain.ainvoke({"question": question, "date_context": date_context})

    async def process_text_with_dates(self, text: str) -> Dict[str, Any]:
        """Full processing pipeline for text with dates"""
        # First pass - date extraction and standardization
        date_info = await self.extract_dates(text)
        
        # Second pass - enhanced understanding
        enhanced_info = {
            "original": text,
            "standardized": date_info["standardized_text"],
            "dates": [],
            "relative_dates": [],
            "date_relations": []
        }

        # Analyze each extracted date
        for date_str in date_info["extracted_dates"]:
            try:
                date_obj = dateutil.parser.parse(date_str)
                enhanced_info["dates"].append({
                    "iso_format": date_obj.isoformat(),
                    "day_of_week": date_obj.strftime("%A"),
                    "relative": self._get_relative_date_description(date_obj)
                })
            except:
                continue

        return enhanced_info

    def _get_relative_date_description(self, date_obj: datetime) -> str:
        """Generate human-friendly relative date description"""
        today = datetime.now().date()
        date = date_obj.date()
        delta = date - today

        if delta.days == 0:
            return "today"
        elif delta.days == 1:
            return "tomorrow"
        elif delta.days == -1:
            return "yesterday"
        elif delta.days > 0:
            return f"in {delta.days} days"
        else:
            return f"{abs(delta.days)} days ago"

# Example usage
async def main():
    # Initialize the date-aware LLM
    date_llm = DateAwareLLM()

    # Test cases with different date formats
    test_cases = [
        "The event is scheduled for 03/15/2023 and 2023-03-20",
        "Let's meet next Tuesday at 2 PM",
        "The project started in Q2 2022 and will end in December 2023",
        "Her birthday is on 5th Jan '90",
        "The dates are 15.07.2024, 07/15/24, and July 15 2024",
        "The warranty expires 3 months from today",
        "The conference runs from 10-12 October 2024",
        "The fiscal year 2022-23 ended on 31st March",
        "The ancient manuscript is dated 12 Thermidor CCXXXI (French Republican Calendar)"
    ]

    print("=== Date Understanding Demo ===")
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: {text}")
        
        # Process the text
        result = await date_llm.process_text_with_dates(text)
        
        print("\nStandardized:", result["standardized"])
        print("\nExtracted Dates:")
        for date_info in result["dates"]:
            print(f"- {date_info['iso_format']} ({date_info['day_of_week']}, {date_info['relative']})")
        
        # Ask a question about the dates
        question = "What is the difference between the first and last date mentioned?"
        answer = await date_llm.answer_date_question(question, result["standardized"])
        print(f"\nQ: {question}")
        print(f"A: {answer}")

    # Interactive demo
    print("\n=== Interactive Mode ===")
    while True:
        user_input = input("\nEnter text with dates (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        
        result = await date_llm.process_text_with_dates(user_input)
        print("\nStandardized:", result["standardized"])
        print("\nExtracted Dates:")
        for date_info in result["dates"]:
            print(f"- {date_info['iso_format']} ({date_info['day_of_week']}, {date_info['relative']})")
        
        question = input("\nAsk a question about these dates: ")
        answer = await date_llm.answer_date_question(question, result["standardized"])
        print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
