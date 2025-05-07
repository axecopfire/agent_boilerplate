from openai import AzureOpenAI
import os


def msg(role="user", msg=""):
    return {"role": role, "content": msg}


def is_o1():
    return "o1" in os.getenv("DEPLOYMENT_NAME")


class Agent:
    def __init__(
        self,
        name,
        system_message,
    ):
        self.name = name
        self.system_message = system_message
        if is_o1():
            self.conversation = []
        else:
            self.conversation = [msg("system", system_message)]

        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AOAI_ENDPOINT"),
            api_key=os.getenv("AOAI_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION"),
        )
        self.deployment_name = os.getenv("DEPLOYMENT_NAME")

    def client_chat(self, messages):

        if is_o1:
            response = self.client.chat.completions.create(
                model=self.deployment_name, messages=messages
            )

            return response.choices[0].message.content

        else:
            response = self.client.chat.completions.create(
                model=self.deployment_name, messages=messages
            )
            return response.choices[0].message.content

    def parsed_chat(self, messages, response_format):
        completion = self.client.beta.chat.completions.parse(
            # replace with the model deployment name of your gpt-4o 2024-08-06 deployment
            model=self.deployment_name,
            messages=messages,
            response_format=response_format,
        )
        # print(completion.choices)
        return completion.choices[0].message

    def __call__(self, message, response_format=False):
        if type(message) != str:
            raise ValueError("LLM Message must be a string")

        # o1 doesn't have system message. try to maintain same call signature for all models.
        if is_o1() and len(self.conversation) < 1:
            self.conversation.append(
                msg(
                    "user",
                    f"""## System Message
${self.system_message}
## User Message 
${message}""",
                )
            )

        self.conversation.append(msg("user", message))

        if is_o1():
            raise Exception("o1 currently does not support structured output")

        if response_format:
            response = self.parsed_chat(self.conversation, response_format)
            self.conversation.append(
                {"role": "assistant", "content": response.content})
            return response.parsed

        response = self.client_chat(self.conversation)
        self.conversation.append(msg("assistant", response))
        return response
