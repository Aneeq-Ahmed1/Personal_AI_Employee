"""
Silver Tier Reasoning Engine
Analyzes tasks in Needs_Action folder using Gemini AI and generates action plans.
"""

import os
import sys
import re
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

# Import ProviderManager for auto-failover
sys.path.insert(0, str(Path(__file__).parent.parent / 'ai-providers'))
from provider_manager import get_provider_manager, AIResponse

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load environment variables from project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Clear any existing GEMINI_API_KEY from environment to avoid conflicts
# This ensures we always load from the .env file
os.environ.pop('GEMINI_API_KEY', None)

# Load .env file explicitly with override to ensure file values are used
load_dotenv(dotenv_path=ENV_FILE, override=True)

# Gemini configuration
GEMINI_MODEL = "gemini-2.0-flash"  # Using stable model
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Paths
VAULT_PATH = PROJECT_ROOT / "silver" / "vault"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PLANS_PATH = VAULT_PATH / "Plans"
MEMORY_DIR = VAULT_PATH / "memory"
MEMORY_FILE = MEMORY_DIR / "processed_tasks.json"

# Logging configuration
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# =============================================================================
# STEP 1: ENV VALIDATION
# =============================================================================

def validate_environment():
    """
    Validate that all required environment variables are loaded.
    Returns dict with validation results.
    """
    result = {
        'gemini_key_loaded': GEMINI_API_KEY is not None and len(GEMINI_API_KEY) > 10,
        'gemini_key_length': len(GEMINI_API_KEY) if GEMINI_API_KEY else 0,
        'env_file_exists': ENV_FILE.exists(),
        'model_name': GEMINI_MODEL
    }
    
    logger.info("=" * 60)
    logger.info("ENVIRONMENT VALIDATION")
    logger.info("=" * 60)
    logger.info(f"ENV File Path: {ENV_FILE}")
    logger.info(f"ENV File Exists: {result['env_file_exists']}")
    logger.info(f"Gemini API Key Loaded: {'YES' if result['gemini_key_loaded'] else 'NO'}")
    logger.info(f"Gemini API Key Length: {result['gemini_key_length']} characters")
    logger.info(f"Gemini Model: {result['model_name']}")
    logger.info("=" * 60)
    
    return result


# =============================================================================
# STEP 2: REAL API CALL VERIFICATION
# =============================================================================

def test_gemini_connection():
    """
    Test live connection to Gemini API with a simple prompt.
    Returns (success: bool, message: str)
    """
    logger.info("Testing Gemini API connection...")
    
    if not GEMINI_API_KEY:
        logger.error("Gemini API Key not loaded - cannot test connection")
        return False, "API_KEY_NOT_LOADED"
    
    try:
        # Create client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Simple test prompt
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents="Respond with exactly: ACTIVE"
        )
        
        response_text = response.text.strip().upper()
        
        if 'ACTIVE' in response_text:
            logger.info("Gemini Live Call: SUCCESS")
            return True, "SUCCESS"
        else:
            logger.warning(f"Gemini responded but not with expected value: {response_text}")
            return True, "SUCCESS_UNEXPECTED_RESPONSE"
            
    except APIError as e:
        error_code = getattr(e, 'code', 'UNKNOWN')
        error_message = getattr(e, 'message', str(e))
        logger.error(f"Gemini Live Call: FAILED - {error_code}: {error_message}")
        return False, f"API_ERROR: {error_code}"
        
    except Exception as e:
        logger.error(f"Gemini Live Call: FAILED - {type(e).__name__}: {str(e)}")
        return False, f"EXCEPTION: {type(e).__name__}"


# =============================================================================
# MEMORY MANAGEMENT
# =============================================================================

def load_processed_tasks():
    """Load the list of already processed task filenames from memory"""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('processed_files', [])
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not load memory file: {e}")
            return []
    return []

def save_processed_tasks(processed_files):
    """Save the list of processed task filenames to memory"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        'processed_files': processed_files,
        'last_updated': datetime.now().isoformat()
    }
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def is_file_processed(filename):
    """Check if a file has already been processed"""
    processed_files = load_processed_tasks()
    return filename in processed_files

def mark_file_as_processed(filename):
    """Mark a file as processed by adding it to the memory"""
    processed_files = load_processed_tasks()
    if filename not in processed_files:
        processed_files.append(filename)
        save_processed_tasks(processed_files)


# =============================================================================
# STEP 3: CONTENT EXTRACTION WITH EXPLICIT FAILURE LOGGING
# =============================================================================

def extract_content_info(file_path, max_retries=3, base_delay=12):
    """
    Extract title, summary, and other info from a markdown file using AI.
    Uses ProviderManager with auto-failover (Gemini → OpenRouter).
    Falls back to regex only if all AI providers fail.
    """
    logger.info(f"Reading file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title (first heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else Path(file_path).stem

    # Get ProviderManager instance
    provider_manager = get_provider_manager()

    # Create prompt for AI analysis
    prompt = f"""
    Analyze the following task and provide:
    1. A concise summary of the task
    2. A suggested next step to take
    3. A priority level (High, Medium, or Low)

    Task content:
    {content}

    Respond in JSON format with keys: "summary", "suggested_next", "priority".
    """

    # Use ProviderManager with auto-failover
    logger.info(f"AI Provider Mode: {provider_manager.mode}")
    logger.info(f"Current provider: {provider_manager.current_provider}")
    logger.info(f"Gemini exhausted: {provider_manager.gemini_exhausted}")
    
    response = provider_manager.generate(prompt, max_retries=max_retries)

    # Check if AI response was successful
    if response.success and response.text:
        logger.info(f"✅ AI SUCCESS (Provider: {response.provider}, Model: {response.model})")
        
        # Parse response
        response_text = response.text.strip()
        logger.info(f"AI raw response: {response_text[:200]}...")

        # Clean up markdown code blocks
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]

        try:
            # Parse JSON
            result = json.loads(response_text.strip())

            summary = result.get('summary', 'No summary provided')
            suggested_next = result.get('suggested_next', 'Review and determine next action')
            priority = result.get('priority', 'Low')

            # Validate priority
            if priority not in ['High', 'Medium', 'Low']:
                logger.warning(f"Invalid priority '{priority}' from AI, defaulting to Low")
                priority = 'Low'

            logger.info(f"AI reasoning success: Priority={priority}, Provider={response.provider}")

            return {
                'title': title,
                'summary': summary,
                'suggested_next': suggested_next,
                'priority': priority,
                'original_content': content,
                'extraction_method': f'{response.provider.upper()}_AI'
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            logger.warning("Using fallback regex extraction due to JSON parse error")
            return extract_content_fallback(file_path, content, title, f"JSON_PARSE_ERROR: {str(e)}")
    else:
        # All AI providers failed
        logger.error(f"AI FAILED for {file_path.name}: {response.error}")
        logger.warning("All AI providers failed — Using fallback mode (regex-based extraction)")
        return extract_content_fallback(file_path, content, title, f"ALL_PROVIDERS_FAILED: {response.error}")


def extract_content_fallback(file_path, content, title, error_reason):
    """
    Fallback regex-based extraction when Gemini fails.
    Explicitly logged as fallback mode.
    """
    logger.info(f"Using fallback regex extraction for: {file_path.name}")
    
    # Extract summary from markdown
    summary_match = re.search(r'##\s+Summary\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else "No summary provided"

    # Extract next step from markdown
    next_step_match = re.search(r'##\s+Suggested Next Step\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    suggested_next = next_step_match.group(1).strip() if next_step_match else "Review and determine next action"

    # Determine priority from keywords
    content_lower = content.lower()
    if any(keyword in content_lower for keyword in ['urgent', 'high priority', 'asap', 'critical']):
        priority = 'High'
    elif any(keyword in content_lower for keyword in ['medium', 'normal', 'standard']):
        priority = 'Medium'
    else:
        priority = 'Low'

    logger.info(f"Fallback extraction complete: Priority={priority}")

    return {
        'title': title,
        'summary': summary,
        'suggested_next': suggested_next,
        'priority': priority,
        'original_content': content,
        'extraction_method': 'REGEX_FALLBACK',
        'fallback_reason': error_reason
    }


# =============================================================================
# PLAN GENERATION
# =============================================================================

def generate_plan_from_needs_action():
    """
    Generate Plan.md from NEW files in vault/Needs_Action/.
    Skips already processed files.
    """
    logger.info("=" * 60)
    logger.info("PLAN GENERATION STARTED")
    logger.info("=" * 60)
    
    # Create directories
    NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
    PLANS_PATH.mkdir(parents=True, exist_ok=True)

    # Get all markdown files in Needs_Action
    needs_action_files = list(NEEDS_ACTION_PATH.glob("*.md"))

    if not needs_action_files:
        logger.info("No files found in vault/Needs_Action/")
        return None

    # Load already processed files from memory
    processed_files = load_processed_tasks()
    logger.info(f"Memory: {len(processed_files)} previously processed file(s)")

    # Filter to only NEW files
    new_files = []
    skipped_files = []
    for file_path in needs_action_files:
        if file_path.name in processed_files:
            skipped_files.append(file_path.name)
        else:
            new_files.append(file_path)

    logger.info(f"Skipped {len(skipped_files)} already processed file(s): {skipped_files}")
    logger.info(f"Processing {len(new_files)} new file(s): {[f.name for f in new_files]}")

    if not new_files:
        logger.info("No new files to process. Skipping Gemini API calls.")
        return None

    # Process each NEW file
    tasks = []
    newly_processed = []
    
    for file_path in new_files:
        logger.info("-" * 40)
        logger.info(f"File detected: {file_path.name}")
        try:
            info = extract_content_info(file_path)
            info['source_file'] = file_path.name
            tasks.append(info)
            newly_processed.append(file_path.name)
            logger.info(f"Processing complete: {file_path.name}")
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {type(e).__name__}: {str(e)}")

    # Save newly processed files to memory
    if newly_processed:
        all_processed = processed_files + newly_processed
        save_processed_tasks(all_processed)
        logger.info(f"Memory updated: {len(newly_processed)} file(s) marked as processed")

    if not tasks:
        logger.warning("No tasks were successfully processed")
        return None

    # Sort by priority
    priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
    tasks.sort(key=lambda x: priority_order.get(x['priority'], 99))

    # Generate Plan.md content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    plan_content = f"""# Action Plan
Generated on: {timestamp}

## Overview
This plan contains all tasks from the Needs_Action folder organized by priority.

## Tasks by Priority

"""

    for i, task in enumerate(tasks, 1):
        extraction_info = f" (via {task.get('extraction_method', 'UNKNOWN')}"
        if task.get('fallback_reason'):
            extraction_info += f" - Fallback: {task['fallback_reason']}"
        extraction_info += ")"
        
        plan_content += f"### Task {i}: {task['title']} (Priority: {task['priority']}{extraction_info})\n"
        plan_content += f"- **Source File**: {task['source_file']}\n"
        plan_content += f"- **Summary**: {task['summary']}\n"
        plan_content += f"- **Suggested Next Step**: {task['suggested_next']}\n\n"

    # Generate action steps
    plan_content += "## Action Steps\n"
    for i, task in enumerate(tasks, 1):
        plan_content += f"{i}. {task['title']}: {task['suggested_next']}\n"

    # Recommendations
    plan_content += "\n## Recommendations\n"
    high_priority_tasks = [t for t in tasks if t['priority'] == 'High']
    if high_priority_tasks:
        plan_content += f"- Focus on the {len(high_priority_tasks)} high priority task(s) first\n"

    plan_content += f"- Process all {len(tasks)} task(s) in the order listed above\n"
    plan_content += "- Update status as tasks are completed\n"

    # Save the plan
    plan_file_path = PLANS_PATH / f"Plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(plan_file_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)

    logger.info(f"Plan file generated path: {plan_file_path}")
    logger.info(f"Tasks processed: {len(tasks)}")
    logger.info("=" * 60)
    logger.info("PLAN GENERATION COMPLETED")
    logger.info("=" * 60)

    return str(plan_file_path)


# =============================================================================
# SINGLE FILE PROCESSING (for auto-trigger from watcher)
# =============================================================================

def process_single_task(file_path):
    """
    Process a single task file and update the plan.
    Called automatically when watcher detects new file in Needs_Action.
    """
    logger.info("=" * 60)
    logger.info(f"SINGLE FILE TRIGGERED: {file_path}")
    logger.info("=" * 60)
    
    file_path = Path(file_path)
    
    # Check if already processed
    if is_file_processed(file_path.name):
        logger.info(f"File already processed, skipping: {file_path.name}")
        return None
    
    # Process the file
    try:
        info = extract_content_info(file_path)
        info['source_file'] = file_path.name
        
        # Mark as processed
        mark_file_as_processed(file_path.name)
        
        # Generate updated plan
        plan_path = generate_plan_from_needs_action()
        
        logger.info(f"Single file processing complete: {file_path.name}")
        return plan_path
        
    except Exception as e:
        logger.error(f"Error in single file processing: {type(e).__name__}: {str(e)}")
        return None


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize():
    """
    Initialize the reasoning engine with full diagnostics.
    Call this at application startup.
    """
    logger.info("")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 15 + "REASONING ENGINE STARTUP" + " " * 17 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")
    
    # STEP 1: Validate environment
    env_result = validate_environment()
    
    # STEP 2: Test live Gemini connection
    if env_result['gemini_key_loaded']:
        api_success, api_message = test_gemini_connection()
        env_result['api_test_success'] = api_success
        env_result['api_test_message'] = api_message
    else:
        env_result['api_test_success'] = False
        env_result['api_test_message'] = "SKIPPED_NO_KEY"
    
    logger.info("")
    
    return env_result


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main function to run the reasoning loop"""
    # Initialize with diagnostics
    env_result = initialize()
    
    # Run plan generation
    plan_path = generate_plan_from_needs_action()
    
    if plan_path:
        logger.info(f"Reasoning loop completed. Plan saved to: {plan_path}")
    else:
        logger.info("No plan was generated (no new files).")
    
    return plan_path


if __name__ == "__main__":
    main()
