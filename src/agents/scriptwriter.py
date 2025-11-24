import google.generativeai as genai
import os
import json
import logging

class ScriptWriter:
    def __init__(self, api_key=None, provider="gemini", model_name="gemini-2.5-flash"):
        self.provider = provider
        self.model_name = model_name

        if self.provider == "gemini":
            if not api_key:
                raise ValueError("API Key required for Gemini")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
        elif self.provider == "foundry":
            try:
                from foundry_local import FoundryLocalManager
                import openai
                # Initialize Foundry Manager with the requested model alias
                self.manager = FoundryLocalManager(self.model_name)
                self.client = openai.OpenAI(
                    base_url=self.manager.endpoint,
                    api_key=self.manager.api_key
                )
            except ImportError:
                raise ImportError("foundry-local-sdk and openai are required for 'foundry' provider.")
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def generate_script(self, repo_data):
        prompt = f"""
        Analyze this GitHub repository and create a video script.
        Repo Name: {repo_data.get('name')}
        Description: {repo_data.get('description')}
        Readme Snippet: {repo_data.get('readme', '')[:2000]}

        Structure the response as JSON with these keys:
        - "hook": The pain point or problem this solves.
        - "solution": How this project solves it.
        - "pros": List of advantages.
        - "cons": List of potential downsides or limitations.
        - "verdict": Professional, honest feedback.
        - "narration": A full narration text for the blog post audio.
        - "narration_20s": A condensed, punchy narration specifically for a 20-second video reel.
        """

        if self.provider == "gemini":
            response = self.model.generate_content(prompt)
            text_response = response.text
        elif self.provider == "foundry":
            # Foundry/OpenAI call
            try:
                # Ensure model is loaded (manager handles this usually, but we need the ID)
                model_id = self.manager.get_model_info(self.model_name).id
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False
                )
                text_response = response.choices[0].message.content
            except Exception as e:
                logging.error(f"Error calling Foundry: {e}")
                return None

        try:
            # Basic cleanup if markdown code blocks are returned
            text = text_response.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None
