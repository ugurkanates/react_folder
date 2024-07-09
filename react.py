# ReACT Framework example task
# Using GPT to work with ReACT Framework

from agent import Agent
from tasks import current_date, calculator, wiki_search
from tools import Tool


wiki_search = Tool("WikipediaSearch", wiki_search)
calculator = Tool("Calculator", calculator)
current_date = Tool("CurrentDate", current_date)


agent = Agent()

agent.add_tool(wiki_search)
agent.add_tool(calculator)
agent.add_tool(current_date)

agent.react("What is the double of kaan tangoze's age?")