import time
from groq import Groq # Import Groq instead of OpenAI
from .base import BaseClient

class GroqClient(BaseClient):
    def __init__(
        self,
        model: str = "llama3-8b-8192",  # Update model to Groq model (replace with the actual Groq model name)
        api_config: dict = None,
        max_requests_per_minute=200,
        request_window=60,
    ):
        super().__init__(model, api_config, max_requests_per_minute, request_window)
        self.client = Groq(api_key=self.api_config["GROQ_API_KEY"])  # Initialize Groq client

    def _call(self, messages: str, **kwargs):
        seed = kwargs.get("seed", 42)  # default seed is 42
        assert type(seed) is int, "Seed must be an integer."

        response = self.client.chat.completions.create(  # Use groq.completions.create for Groq
            response_format={"type": "json_object"},
            seed=seed,
            model=self.model,
            messages=messages,
        )
        r = response.choices[0].message.content

        if hasattr(response, "usage"):
            self._log_usage(usage_dict=response.usage)
        else:
            print("Warning: Groq API Usage is not logged.")

        return r

    def _log_usage(self, usage_dict):
        try:
            self.usage.prompt_tokens += usage_dict.prompt_tokens
            self.usage.completion_tokens += usage_dict.completion_tokens
        except:  # noqa E722
            print("Warning: prompt_tokens or completion_token not found in usage_dict")

    def get_request_length(self, messages):
        # TODO: check if we should return the len(menages) instead
        return 1

    def construct_message_list(
        self,
        prompt_list: list[str],
        system_role: str = "You are a helpful assistant designed to output JSON.",
    ):
        messages_list = list()
        for prompt in prompt_list:
            messages = [
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ]
            messages_list.append(messages)
        return messages_list
