import open_ai
import inspect
from pydantic import BaseModel
from tools import Tool, ToolChoice

class ReactEnd(BaseModel):
    stop: bool
    final_answer: str


class Agent:
    def __init__(self) -> None:
        self.client = open_ai.client_setup()  
        self.tools = []
        self.messages = []
        self.request = ""
        self.token_count = 0
        self.token_limit = 5000

    def add_tool(self, tool: Tool) -> None:
        self.tools.append(tool)

    def append_message(self, message):
        self.messages.append(message)
        self.token_count += len(message)

        # Check if token_count exceeds the limit
        while self.token_count > self.token_limit and len(self.messages) > 1:
            # Remove messages from the end until token_count is within the limit
            removed_message = self.messages.pop(1)  # Keep the first message, remove the second one
            self.token_count -= len(removed_message)

    @staticmethod
    def extract_first_nested_dict(data_dict):
        for key, value in data_dict.items():
            if isinstance(value, dict):
                return value
        return {}

    def background_info(self) -> str:
        return f"Here are your previous think steps: {self.messages[1:]}" if len(self.messages) > 1 else ""

    def think(self) -> None:

        prompt = f"""Answer the following request as best you can: {self.request}.
                    {self.background_info()}
                    First think about what to do. What action to take first if any.
                    Here are the tools at your disposal: {[tool.name for tool in self.tools]}"""

        self.append_message(prompt)

        response = open_ai.generator(client=self.client,prompt=prompt, max_tokens=100)

        print(f"Thought: {response}")

        self.append_message(response)

        self.choose_action()

    def choose_action(self) -> None:
        prompt = f"""To Answer the following request as best you can: {self.request}.
                    {self.background_info()}
                    Choose the tool to use if need be. The tool should be among:
                    {[tool.name for tool in self.tools]}.
                    """
        self.append_message(prompt)

        response = open_ai.generator(client=self.client,prompt=prompt, output=ToolChoice)

        print(f"""Action: I should use this tool: {response["tool_name"]}.
              {response["reason_of_choice"]}""")

        self.append_message(response)

        tool = [tool for tool in self.tools if tool.name == response["tool_name"]].pop()

        self.action(tool)

    def action(self, tool: Tool) -> None:
        prompt = f"""To Answer the following request as best you can: {self.request}.
                    {self.background_info()}
                    Determine the inputs to send to the tool: {tool.name}
                    Given that the source code of the tool function is: {inspect.getsource(tool.func)}.
                    """
        self.append_message(prompt)

        parameters = inspect.signature(tool.func).parameters

        class DynamicClass(BaseModel):
            pass

        for name, param in parameters.items():
            # Setting default value if it exists, else None
            default_value = param.default if param.default is not inspect.Parameter.empty else None
            setattr(DynamicClass, name, (param.annotation, default_value))

        response = open_ai.generator(client=self.client,prompt=prompt, output=DynamicClass)

        self.append_message(response)

        input_parameters = self.extract_first_nested_dict(response)

        try:
            action_result = tool.func(**input_parameters)

            self.append_message(f"Results of action: {action_result}")

            self.observation()

        except:
            self.action(tool)

    def observation(self) -> None:
        prompt = f"Observation:{self.messages[-1]}."
        self.append_message(prompt)

        check_final = open_ai.generator(client=self.client,prompt=f"Is {self.background_info()} enough to finally answer to this request: {self.messages[0]}",
                 output=ReactEnd)

        if check_final["stop"]:
            print("Thought: I now know the final answer. \n")
            prompt = f"""Give the final answer the following request: {self.request}.
                    given {self.background_info()}
                    """
            print(f"Final Answer: {open_ai.generator(client=self.client,prompt=prompt)}")
        else:
            self.think()


    def react(self, input: str) -> str:
        self.append_message(input)
        self.request = input
        self.think()
