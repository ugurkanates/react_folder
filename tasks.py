import datetime
import wikipedia

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


# wiki search
def wiki_search(search_query):
    page = wikipedia.page(search_query)
    text = page.content
    return text[:300]

# date func
def current_date():
    return datetime.date.today()