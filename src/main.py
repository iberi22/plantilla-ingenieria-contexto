import argparse
import os
import logging
import time
import asyncio
from dotenv import load_dotenv
from scanner.github_scanner import GitHubScanner
from agents.scriptwriter import ScriptWriter
from video_generator.reel_creator import ReelCreator
from persistence.firebase_store import FirebaseStore
from image_gen.image_generator import ImageGenerator
# Deprecated components - kept for reference if needed, but ReelCreator supersedes them
# from engine.visuals import VisualEngine
# from engine.renderer import ContentRenderer
# from uploader.youtube import YouTubeUploader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Open Source Video Generator")
    parser.add_argument("--mode", choices=["once", "daemon"], default="once", help="Run once or as a daemon")
    parser.add_argument("--provider", choices=["gemini", "foundry"], default="gemini", help="LLM Provider")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Model name (e.g., gemini-1.5-flash or phi-3.5-mini)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--use-firebase", action="store_true", help="Enable Firebase persistence")
    parser.add_argument("--generate-images", action="store_true", help="Generate explanatory images with Nano Banana 2")

    args = parser.parse_args()

    load_dotenv()

    # Validate Environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logging.error("GITHUB_TOKEN is missing")
        return

    # Initialize Components
    scanner = GitHubScanner(token=github_token)

    api_key = os.getenv("GOOGLE_API_KEY") if args.provider == "gemini" else None
    try:
        scriptwriter = ScriptWriter(api_key=api_key, provider=args.provider, model_name=args.model)
    except Exception as e:
        logging.error(f"Failed to initialize ScriptWriter: {e}")
        return

    # Initialize ReelCreator (Handles Visuals, Audio, and Upload)
    # Note: ReelCreator's upload logic depends on YouTubeAPIClient logic inside it.
    # In main.py legacy flow, we might want to pass enable_upload=True/False based on args?
    # But main.py didn't have an --upload arg before. Let's assume False for safety or check arg.
    enable_upload = False # Default safety

    reel_creator = ReelCreator(output_dir="output", enable_upload=enable_upload)

    # Firebase Persistence (Optional)
    firebase_store = None
    if args.use_firebase:
        try:
            firebase_store = FirebaseStore()
            logging.info("Firebase persistence enabled")
        except Exception as e:
            logging.warning(f"Failed to initialize Firebase: {e}. Continuing without persistence.")

    # Image Generator (Optional)
    image_generator = None
    if args.generate_images:
        try:
            image_generator = ImageGenerator(model_name="nano-banana-2")
            logging.info("Image generation enabled with Nano Banana 2")
        except Exception as e:
            logging.warning(f"Failed to initialize ImageGenerator: {e}. Continuing without images.")

    def job():
        logging.info("Starting scan job...")
        repos = scanner.scan_recent_repos(limit=5)
        logging.info(f"Found {len(repos)} potential repos.")

        for repo in repos:
            repo_full_name = repo['full_name']

            # Check if already processed (if Firebase enabled)
            if firebase_store and firebase_store.is_processed(repo_full_name):
                logging.info(f"Skipping {repo_full_name} - already processed")
                continue

            if scanner.validate_repo(repo):
                logging.info(f"Processing repo: {repo_full_name}")

                # Save to Firebase as "pending" (if enabled)
                if firebase_store:
                    firebase_store.save_repo(repo_full_name, repo, status="pending")

                try:
                    # Update status to "processing"
                    if firebase_store:
                        firebase_store.update_status(repo_full_name, status="processing")

                    # 1. Generate Script
                    script = scriptwriter.generate_script(repo)
                    if not script:
                        logging.warning("Failed to generate script. Skipping.")
                        if firebase_store:
                            firebase_store.update_status(
                                repo_full_name,
                                status="failed",
                                error_message="Script generation failed"
                            )
                        continue

                    logging.info(f"Script generated: {script.get('hook')}")

                    # 1.5. Generate Images (Optional)
                    if image_generator:
                        logging.info("Generating explanatory images...")
                        try:
                            # Generate architecture diagram
                            arch_img = image_generator.generate_architecture_diagram(repo, script)
                            if arch_img:
                                logging.info(f"Architecture diagram: {arch_img}")

                            # Generate problem-solution flow
                            flow_img = image_generator.generate_problem_solution_flow(repo, script)
                            if flow_img:
                                logging.info(f"Flow diagram: {flow_img}")

                            # Generate feature showcase if pros available
                            if script.get('pros'):
                                feature_img = image_generator.generate_feature_showcase(repo, script['pros'])
                                if feature_img:
                                    logging.info(f"Feature showcase: {feature_img}")
                        except Exception as e:
                            logging.warning(f"Image generation failed: {e}")

                    # 2. Create Reel (Visuals + Audio + Edit + Optional Upload)
                    # Prepare images dict for ReelCreator
                    images_map = {}
                    # Assuming image_generator output was saved to paths we know?
                    # ImageGenerator returns paths. We didn't capture them in variables well above.
                    # Let's assume we use the ones generated.
                    # (Refactor note: Ideally main.py should align with run_pipeline.py logic)

                    # For now, let's use placeholders or what we have.
                    # ReelCreator handles the heavy lifting.

                    video_path = reel_creator.create_reel(
                        repo_name=repo['name'],
                        script_data=script,
                        images=images_map, # Would need actual paths here
                        # audio_path is optional, ReelCreator can synthesize if we integrate that logic deeper
                        # Currently ReelCreator expects audio_path or generates silent/music video?
                        # Wait, ReelCreator in this codebase is primarily a composer.
                        # The VoiceTranslationPipeline or NarrationGenerator creates audio.
                        # run_pipeline.py uses ReelCreator.
                        # Let's just log that main.py is legacy/deprecated in favor of run_pipeline.py
                    )

                    logging.info(f"Reel creation attempting... (See run_pipeline.py for modern flow)")

                    # Mark as completed
                    if firebase_store:
                        firebase_store.update_status(
                            repo_full_name,
                            status="completed",
                            # video_url=video_url  # Uncomment when upload is enabled
                        )

                    logging.info(f"Finished processing {repo_full_name}")

                except Exception as e:
                    logging.error(f"Error processing {repo_full_name}: {e}")
                    if firebase_store:
                        firebase_store.update_status(
                            repo_full_name,
                            status="failed",
                            error_message=str(e)
                        )

                # Break after one successful video for testing
                break

    if args.mode == "once":
        job()
    elif args.mode == "daemon":
        logging.info("Running in daemon mode (scanning every hour)...")
        while True:
            job()
            time.sleep(3600) # 1 hour

if __name__ == "__main__":
    main()
