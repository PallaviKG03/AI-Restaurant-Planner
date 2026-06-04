import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

# Load environment variables
load_dotenv()

# Initialize the Groq LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

def generate_restaurant_name_and_items(cuisine: str, vibe: str, currency: str) -> dict:
    parser = JsonOutputParser()

    # Dynamic Currency Feature: Injected the specific currency rule into the prompt instructions
    prompt = PromptTemplate(
        template="""You are a world-class restaurant branding expert. 
        I want to open a {vibe} restaurant serving {cuisine} food.
        
        Provide a fancy restaurant name and exactly 10 matching menu items.
        Each menu item must include a realistic price based on the restaurant's vibe.
        
        CRITICAL: All prices MUST be formatted strictly using the '{currency}' currency symbol.
        
        Return ONLY a JSON object with exactly these keys:
        {{
            "restaurant_name": "Name of the restaurant here",
            "menu_items": [
                {{"name": "Item 1", "price": "{currency}12.50"}},
                {{"name": "Item 2", "price": "{currency}15.00"}}
            ]
        }}

        Do not include any introductory or concluding text. Return only raw JSON.
        """,
        input_variables=["cuisine", "vibe", "currency"]
    )

    chain = prompt | llm | parser
    return chain.invoke({"cuisine": cuisine, "vibe": vibe, "currency": currency})


def get_ingredients(item_name: str, cuisine: str) -> str:
    prompt = PromptTemplate(
        template="""List the main ingredients required to make '{item_name}' ({cuisine} style).
        Provide a simple, clear bulleted list of ingredients. Do not write cooking instructions.
        """,
        input_variables=["item_name", "cuisine"]
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"item_name": item_name, "cuisine": cuisine})