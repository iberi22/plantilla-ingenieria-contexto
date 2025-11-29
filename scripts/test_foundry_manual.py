import argparse
import os
from src.agents.scriptwriter import ScriptWriter

def test_foundry(model_name):
    print(f"Testing Foundry Local with model: {model_name}")
    try:
        writer = ScriptWriter(provider="foundry", model_name=model_name)

        # Mock repo data
        repo_data = {
            "name": "test-repo",
            "description": "A test repository to verify Foundry Local integration.",
            "readme": "This is a test readme. The project helps developers test their local LLM setup."
        }

        print("Sending request to Foundry Local...")
        script = writer.generate_script(repo_data)

        if script:
            print("\n--- Generated Script ---")
            print(f"Hook: {script.get('hook')}")
            print(f"Verdict: {script.get('verdict')}")
            print("------------------------")
            print("Success!")
        else:
            print("Failed to generate script.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="phi-3.5-mini")
    args = parser.parse_args()

    test_foundry(args.model)
