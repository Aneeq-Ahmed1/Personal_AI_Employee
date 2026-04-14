"""
Silver Tier Reasoning Loop (Dual-Provider Support)
Manual entry point to run the reasoning engine.
This can be run manually or is auto-triggered by the filesystem watcher.

Provider Support:
- Gemini API (Primary - Free)
- OpenRouter API (Backup - Paid, auto-activates when Gemini quota exhausted)
"""

import sys
import os
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
REASONING_ENGINE_PATH = SCRIPT_DIR / "skills" / "reasoning-engine"
AI_PROVIDERS_PATH = SCRIPT_DIR / "skills" / "ai-providers"

# Add paths
sys.path.insert(0, str(REASONING_ENGINE_PATH))
sys.path.insert(0, str(AI_PROVIDERS_PATH))
sys.path.insert(0, str(PROJECT_ROOT))

# Change to project root so relative paths work
os.chdir(PROJECT_ROOT)


def main():
    """Main function to run the reasoning loop"""
    # Import after path is set
    from reasoning_engine_v2 import generate_plan_from_needs_action, initialize

    # Initialize with full diagnostics
    env_result = initialize()

    # Check if we should proceed
    gemini_loaded = env_result.get('gemini_key_loaded', False)
    openrouter_loaded = env_result.get('openrouter_key_loaded', False)
    
    if not gemini_loaded and not openrouter_loaded:
        print("\n" + "=" * 60)
        print("WARNING: No AI Provider configured!")
        print("Please configure at least one provider in your .env file:")
        print(f"  {PROJECT_ROOT / '.env'}")
        print("=" * 60 + "\n")
        print("Configure Gemini API:")
        print("  GEMINI_API_KEY=your_key_here")
        print("\nConfigure OpenRouter API (backup):")
        print("  OPENROUTER_API_KEY=sk-or-v1-your_key_here")
        print("\nThe reasoning engine will use fallback mode (regex extraction).")
        print("=" * 60 + "\n")

    # Run plan generation
    print("\nStarting reasoning loop to generate Plan.md...")
    plan_path = generate_plan_from_needs_action()

    if plan_path:
        print(f"\n[OK] Reasoning loop completed. Plan saved to: {plan_path}")
    else:
        print("\nNo plan was generated (no new files to process).")

    return plan_path


if __name__ == "__main__":
    main()
