# ReACT Framework example task
# Using GPT to work with ReACT Framework

from agent import Agent
from tasks import current_date, calculator, wiki_search,search_web,number_comparison
from tools import Tool


# wiki_search = Tool("Wikipedia Search", wiki_search)
calculator = Tool("Calculator", calculator)
current_date = Tool("Get Current Date", current_date)
search_web = Tool("Internet search", search_web)
number_comparison = Tool("Number Comparison", number_comparison)

agent = Agent()

# agent.add_tool(wiki_search)
agent.add_tool(calculator)
agent.add_tool(current_date)
agent.add_tool(search_web)
agent.add_tool(number_comparison)

# agent.react("What is the double of kaan tangoze's age ?")
# agent.react("how old is Turkish republic ? find that and return number by doubling it ")
# agent.react("Traffic situation in New York City for today") 