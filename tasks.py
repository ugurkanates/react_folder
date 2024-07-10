import datetime
import wikipedia
import requests
import json

# calculator
def calculator(operation, a, b):
    if operation not in ['add', 'subtract', 'multiply', 'divide']:
        return f"Invalid operation: {operation}, should be among ['add', 'subtract', 'multiply', 'divide']"

    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        if b == 0:
            return "Division by zero"
        return a / b

# number comparison
def number_comparison(a, b):
    if a > b:
        return f"{a} is greater than {b}"
    elif a < b:
        return f"{a} is less than {b}"
    else:
        return f"{a} is equal to {b}"

# wiki search
def wiki_search(search_query):
    page = wikipedia.page(search_query)
    text = page.content
    return text[:300]

# date func
def current_date():
    return datetime.date.today()

# serper web scraper
# Equivalent of the search web function
def search_web(thing_to_search_on_web: str):
    url = "https://google.serper.dev/search"
    # auto from API key - n_results = 10
    payload = json.dumps({
    "q": thing_to_search_on_web,
    "gl": "tr"
    })
    headers = {
    'X-API-KEY': 'faaa409f4026dd319021517c68dae39539b751d8',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.text)
    if 'organic' in results:
        results = results['organic']
        string = []
        for result in results:
            try:
                string.append('\n'.join([
                        f"Title: {result['title']}",
                        f"Link: {result['link']}",
                        f"Snippet: {result['snippet']}",
                        "---"
                ]))
            except KeyError:
                next

        content = '\n'.join(string)
        return f"\nSearch results: {content}\n"
    else:
        return results

def openai_tools():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Basic calculator can do add, subtract, multiply, divide between two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Add, subtract, multiply, divide",
                        },
                        "a": {
                            "type": "number",
                            "description": "First number",
                        },
                        "b": {
                            "type": "number",
                            "description": "Second number",
                        },
                    },
                    "required": ["operation", "a", "b"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "current_date",
                "description": "Returns current date",
            },
            "type": "function",
            "function": {
                "name": "wiki_search",
                "description": "Searches wikipedia for the given query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "Search query for wikipedia",
                        },
                    },
                    "required": ["search_query"],
                },
            },
            "type": "function",
            "function": {
                "name": "web_scraper",
                "description": "Searches the web for the given query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "thing_to_search_on_web": {
                            "type": "string",
                            "description": "Thing to search on the web",
                        },
                    },
                    "required": ["thing_to_search_on_web"],
                },
            },
        },
    ]
    return tools