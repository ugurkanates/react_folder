import datetime
from openai import OpenAI

client = OpenAI(api_key="sk")
import re
import httpx
import json
import requests

 
class ChatBot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
    
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def execute(self):
        completion = client.chat.completions.create(model="gpt-4", messages=self.messages)
        return completion.choices[0].message.content

prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

search_web:
e.g. search_web: Django
Returns a list of search results from the web

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia



Always look things up on web search if you have the opportunity to do so.

Example session:

Question: What is the capital of Türkiye?
Thought: I should look up Türkiye on web search
Action: search_web: Türkiye
PAUSE

You will be called again with this:

Observation: Türkiye is a country. The capital is Istanbul.

You then output:

Answer: The capital of Türkiye is Istanbul.
""".strip()


action_re = re.compile('^Action: (\w+): (.*)$')

def query(question, max_turns=5):
    i = 0
    bot = ChatBot(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [action_re.match(a) for a in result.split('\n') if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return


def wikipedia(q):
    return httpx.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }).json()["query"]["search"][0]["snippet"]


def simon_blog_search(q):
    results = httpx.get("https://datasette.simonwillison.net/simonwillisonblog.json", params={
        "sql": """
        select
          blog_entry.title || ': ' || substr(html_strip_tags(blog_entry.body), 0, 1000) as text,
          blog_entry.created
        from
          blog_entry join blog_entry_fts on blog_entry.rowid = blog_entry_fts.rowid
        where
          blog_entry_fts match escape_fts(:q)
        order by
          blog_entry_fts.rank
        limit
          1""".strip(),
        "_shape": "array",
        "q": q,
    }).json()
    return results[0]["text"]

def calculate(what):
    return eval(what)
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


known_actions = {
    "wikipedia": wikipedia,
    "calculate": calculate,
    "search_web": search_web
}
# query("Turkiye nerede")
# query ("euro 2024 son maç kimle oynandı ve golleri kim attı")