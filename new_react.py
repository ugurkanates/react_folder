# Basic version 
import datetime
from openai import OpenAI

client = OpenAI(api_key="sk")
import re
import httpx
import json
import requests

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluates a mathematical expression, e.g. 4 * 7 / 3,uses Python\
            to be sure to use floating point syntax if necessary",
            "parameters": {
                "type": "object",
                "properties": {
                    "what": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate",
                    },
                },
                "required": ["what"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "current_date",
            "description": "Returns current date",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "number_comparison",
            "description": "Compares two numbers and returns a string",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number",
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wikipedia",
            "description": "Searches wikipedia for the given query,Returns a summary from searching Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Search query for wikipedia",
                    },
                },
                "required": ["q"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches the web for the given query,returns 10 search results",
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
class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        self.tools = tools
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
        # if result:
        #     self.messages.append({"role": "assistant", "content": result})
        #     return result
        # else :
        #     return None

    def execute(self):
        completion = client.chat.completions.create(model="gpt-4o", messages=self.messages,tools=self.tools)
        tool_calls = completion.choices[0].message.tool_calls
        if tool_calls:
            self.messages.append({"role": "assistant", "content": completion.choices[0].message.content})
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                if function_name == "search_web":
                    function_response = search_web(
                        function_args["thing_to_search_on_web"]
                    )
                elif function_name == "wikipedia":
                    function_response = wikipedia(
                        function_args["q"]
                    )
                elif function_name == "calculate":
                    function_response = calculate(
                        function_args["what"]
                    )
                elif function_name == "current_date":
                    function_response = str(current_date())
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "assistant", # there is a bug recent june4 tool role is not working
                        "name": function_name,
                        "content": function_response,
                    }
            )            
        if completion.choices[0].message.content:
            return completion.choices[0].message.content
  

        # tool_calls = response_message.tool_calls
        """ tool_calls = response.message.tool_calls
        if tool_calls:
            # If true the model will return the name of the tool / function to call and the argument(s)  
            tool_call_id = tool_calls[0].id
            tool_function_name = tool_calls[0].function.name
            tool_query_string = eval(tool_calls[0].function.arguments)# ['query']
            
            # Step 3: Call the function and retrieve results. Append the results to the messages list.      
            if tool_function_name == 'search_web':
                results = search_web(tool_query_string)
                
                self.messages.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_function_name, 
                    "content":results
                })
                
                # Step 4: Invoke the chat completions API with the function response appended to the messages list
                # Note that messages with role 'tool' must be a response to a preceding message with 'tool_calls'
                model_response_with_function_call = client.chat.completions.create(
                    model="gpt-4",
                    messages=self.messages,
                )  # get a new response from the model where it can see the function response
                print(model_response_with_function_call.choices[0].message.content)
            else: 
                print(f"Error: function {tool_function_name} does not exist")
        else: 
            # Model did not identify a function to call, result can be returned to the user 
            print(response.message.content)  """

prompt = """
You run in a loop of Thought, Tools, Pause, Observation.
In each step explicitly put your thoughts
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked and print your thoughts.
Use Tools to run one of the tools available to you ,print which tools you choose, execute tool- then return Pause.
Observation will be the result of running those tools, analyze response of tool if return of tools satisfy the question print as answer if not continue the loop, print your observation either way.

Always look things up on Web by using tool if you have the opportunity to do so.
Example session would look like this:

Question: What is the capital of Turkiye?
Thought: I should look up Turkiye on Web
Tools: search_web: Turkiye
Pause
You will be called again with this:
Observation: Turkiye is a country. The capital is Istanbul. 

If You Believe you have answer to User's Question then output:

Answer: The capital of Turkiye is Istanbul

else continue the loop with your thoughts and tools.
""".strip()


# action_re = re.compile('^Action: (\w+): (.*)$')


def query(question, max_turns=5):
    i = 0
    bot = Agent(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        if result:
            print(result)
        # actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        # if actions:
        #     # There is an action to run
        #     action, action_input = actions[0].groups()
        #     if action not in known_actions:
        #         raise Exception("Unknown action: {}: {}".format(action, action_input))
        #     print(" -- running {} {}".format(action, action_input))
        #     observation = known_actions[action](action_input)
        #     print("Observation:", observation)
        #     next_prompt = "Observation: {}".format(observation)
        # else:
        #     return


def wikipedia(q):
    return httpx.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }).json()["query"]["search"][0]["snippet"]


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


def calculate(what):
    return eval(what)

# date func
def current_date():
    return datetime.date.today()

# number comparison
def number_comparison(a, b):
    if a > b:
        return f"{a} is greater than {b}"
    elif a < b:
        return f"{a} is less than {b}"
    else:
        return f"{a} is equal to {b}"



known_actions = {
    "wikipedia": wikipedia,
    "calculate": calculate,
    "search_web": search_web,
    "current_date": current_date,
    "number_comparison": number_comparison,
}

# query("11 Temmuz 2024 istanbul hava durumu nedir?")
query ("bugün istanbulda hava durumu nedir?")
# query("arda güler hangi takımda oynuyor ve o takım hangi ligde? Türkçe cevap ver")
# query("ABD başkanlarını listele. Türkçe cevap ver")
# query ("euro 2024 son maç")