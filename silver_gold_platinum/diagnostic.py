"""
Silver Tier Diagnostic Test
Run this to verify all components are working correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "silver" / "skills" / "reasoning-engine"))

print("=" * 70)
print(" " * 20 + "SILVER TIER DIAGNOSTIC TEST")
print("=" * 70)
print()

# =============================================================================
# TEST 1: Environment Variables
# =============================================================================
print("TEST 1: Environment Variables")
print("-" * 70)

from dotenv import load_dotenv

# Load from project root
env_file = PROJECT_ROOT / ".env"
print(f"Loading .env from: {env_file}")
print(f".env exists: {env_file.exists()}")

load_dotenv(dotenv_path=env_file)
load_dotenv()  # Also load from cwd as fallback

gemini_key = os.getenv('GEMINI_API_KEY')
key_loaded = gemini_key is not None and len(gemini_key) > 10

print(f"Gemini API Key loaded: {'YES' if key_loaded else 'NO'}")
if key_loaded:
    print(f"Gemini API Key length: {len(gemini_key)} characters")
    print(f"Gemini API Key prefix: {gemini_key[:10]}...")
else:
    print("ERROR: GEMINI_API_KEY not found or too short!")
    print("Please check your .env file at:", env_file)

print()

# =============================================================================
# TEST 2: Gemini API Connection
# =============================================================================
print("TEST 2: Gemini API Connection")
print("-" * 70)

if key_loaded:
    try:
        from google import genai
        from google.genai.errors import APIError
        
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents="Respond with exactly: ACTIVE"
        )
        
        if 'ACTIVE' in response.text.upper():
            print("Gemini Live Call: SUCCESS")
            print(f"Response: {response.text.strip()}")
        else:
            print(f"Gemini responded unexpectedly: {response.text.strip()}")
            
    except APIError as e:
        print(f"Gemini Live Call: FAILED")
        print(f"Error Code: {getattr(e, 'code', 'UNKNOWN')}")
        print(f"Error Message: {getattr(e, 'message', str(e))}")
        
    except Exception as e:
        print(f"Gemini Live Call: FAILED")
        print(f"Exception: {type(e).__name__}: {str(e)}")
else:
    print("SKIPPED: No API key loaded")

print()

# =============================================================================
# TEST 3: Import Reasoning Engine
# =============================================================================
print("TEST 3: Import Reasoning Engine")
print("-" * 70)

try:
    from reasoning_engine import initialize, generate_plan_from_needs_action
    print("Reasoning engine imported: SUCCESS")
    
    # Run initialization
    print("\nRunning initialization...")
    env_result = initialize()
    
    print(f"\nInitialization Results:")
    print(f"  - ENV File Exists: {env_result.get('env_file_exists')}")
    print(f"  - Gemini Key Loaded: {env_result.get('gemini_key_loaded')}")
    print(f"  - API Test: {env_result.get('api_test_message')}")
    
except Exception as e:
    print(f"Reasoning engine import: FAILED")
    print(f"Exception: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 4: Directory Structure
# =============================================================================
print("TEST 4: Directory Structure")
print("-" * 70)

vault_path = PROJECT_ROOT / "silver" / "vault"
inbox_path = vault_path / "Inbox"
needs_action_path = vault_path / "Needs_Action"
plans_path = vault_path / "Plans"

directories = {
    "Vault": vault_path,
    "Inbox": inbox_path,
    "Needs_Action": needs_action_path,
    "Plans": plans_path
}

for name, path in directories.items():
    exists = path.exists()
    print(f"  {name}: {'EXISTS' if exists else 'MISSING'} - {path}")

# Create missing directories
for name, path in directories.items():
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {name}")

print()

# =============================================================================
# TEST 5: Check for Files to Process
# =============================================================================
print("TEST 5: Files in Needs_Action")
print("-" * 70)

if needs_action_path.exists():
    md_files = list(needs_action_path.glob("*.md"))
    print(f"Found {len(md_files)} markdown file(s):")
    for f in md_files:
        print(f"  - {f.name}")
else:
    print("Needs_Action directory does not exist")

print()

# =============================================================================
# TEST 6: Run Reasoning (Optional)
# =============================================================================
print("TEST 6: Test Reasoning Engine")
print("-" * 70)

if needs_action_path.exists() and list(needs_action_path.glob("*.md")):
    print("Files available for processing.")
    print("Run 'python reasoning_loop.py' to generate a plan.")
else:
    print("No files in Needs_Action to process.")
    print("To test, create a .md file in silver/vault/Inbox/")

print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print(" " * 25 + "DIAGNOSTIC SUMMARY")
print("=" * 70)

issues = []

if not key_loaded:
    issues.append("GEMINI_API_KEY not loaded - check .env file")

if not vault_path.exists():
    issues.append("Vault directory missing")

if issues:
    print("ISSUES FOUND:")
    for issue in issues:
        print(f"  ! {issue}")
else:
    print("All checks passed!")

print()
print("NEXT STEPS:")
print("  1. If API key issues: Edit .env and set GEMINI_API_KEY")
print("  2. To start automation: Run 'python watchers/filesystem_watcher.py'")
print("  3. To start backup scheduler: Run 'python scheduler.py'")
print("  4. To manually generate plan: Run 'python reasoning_loop.py'")
print("=" * 70)
