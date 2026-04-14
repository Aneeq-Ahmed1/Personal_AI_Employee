"""
File Triage Skill
Automatically categorizes and organizes files based on content analysis.

This skill:
1. Analyzes file content
2. Determines appropriate category (Task, Reference, Meeting, etc.)
3. Suggests destination folder
4. Can auto-move files if configured
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path("silver/vault")
CATEGORIES = {
    'task': ['task', 'todo', 'action', 'do', 'complete', 'finish', 'urgent', 'asap'],
    'meeting': ['meeting', 'call', 'zoom', 'teams', 'conference', 'appointment', 'schedule'],
    'reference': ['reference', 'doc', 'documentation', 'guide', 'manual', 'handbook'],
    'financial': ['invoice', 'payment', 'receipt', 'bill', 'budget', 'financial', 'money'],
    'client': ['client', 'customer', 'prospect', 'lead', 'contract'],
    'personal': ['personal', 'home', 'family', 'private'],
}


def categorize_content(content: str) -> dict:
    """
    Analyze content and determine category.
    
    Args:
        content: The text content to analyze
        
    Returns:
        dict with category, confidence, and reasoning
    """
    content_lower = content.lower()
    
    scores = {}
    
    for category, keywords in CATEGORIES.items():
        score = sum(1 for keyword in keywords if keyword in content_lower)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return {
            'category': 'general',
            'confidence': 1.0,
            'reasoning': 'No specific category keywords detected'
        }
    
    best_category = max(scores, key=scores.get)
    confidence = scores[best_category] / len(CATEGORIES[best_category])
    
    return {
        'category': best_category,
        'confidence': min(confidence, 1.0),
        'reasoning': f"Matched {scores[best_category]} keywords for '{best_category}' category"
    }


def triage_file(file_path: str, auto_move: bool = False) -> dict:
    """
    Triage a single file.
    
    Args:
        file_path: Path to the file to triage
        auto_move: If True, automatically move file to category folder
        
    Returns:
        dict with triage results
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {
            'success': False,
            'error': f'File not found: {file_path}'
        }
    
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Analyze content
        category_info = categorize_content(content)
        
        # Extract metadata
        file_stats = file_path.stat()
        
        result = {
            'success': True,
            'file': str(file_path),
            'category': category_info['category'],
            'confidence': category_info['confidence'],
            'reasoning': category_info['reasoning'],
            'size_bytes': file_stats.st_size,
            'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'suggested_destination': f'silver/vault/Categories/{category_info["category"].title()}/'
        }
        
        # Auto-move if requested
        if auto_move and category_info['category'] != 'general':
            dest_folder = VAULT_PATH / "Categories" / category_info['category'].title()
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            dest_path = dest_folder / file_path.name
            
            # Don't move if destination already exists
            if not dest_path.exists():
                shutil.move(str(file_path), str(dest_path))
                result['moved_to'] = str(dest_path)
                result['auto_moved'] = True
            else:
                result['auto_moved'] = False
                result['move_blocked'] = 'Destination file already exists'
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'{type(e).__name__}: {str(e)}'
        }


def triage_folder(folder_path: str, auto_move: bool = False) -> dict:
    """
    Triage all markdown files in a folder.
    
    Args:
        folder_path: Path to the folder to triage
        auto_move: If True, automatically move files to category folders
        
    Returns:
        dict with triage summary
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        return {
            'success': False,
            'error': f'Folder not found: {folder_path}'
        }
    
    results = []
    category_counts = {}
    
    for md_file in folder_path.glob("*.md"):
        result = triage_file(md_file, auto_move=auto_move)
        results.append(result)
        
        if result['success']:
            category = result['category']
            category_counts[category] = category_counts.get(category, 0) + 1
    
    return {
        'success': True,
        'files_processed': len(results),
        'category_distribution': category_counts,
        'results': results
    }


def create_category_folders():
    """Create category folder structure in vault"""
    categories_path = VAULT_PATH / "Categories"
    
    for category in CATEGORIES.keys():
        folder = categories_path / category.title()
        folder.mkdir(parents=True, exist_ok=True)
    
    # Create General category
    (categories_path / "General").mkdir(parents=True, exist_ok=True)
    
    return {
        'success': True,
        'categories_path': str(categories_path),
        'folders_created': list(CATEGORIES.keys()) + ['General']
    }


if __name__ == "__main__":
    # Test the file triage skill
    print("File Triage Skill - Test")
    print("=" * 50)
    
    # Create category folders
    print("\nCreating category folders...")
    result = create_category_folders()
    print(f"Categories path: {result['categories_path']}")
    print(f"Folders: {', '.join(result['folders_created'])}")
    
    # Test content categorization
    test_contents = [
        ("Complete this task by Friday", "Should be categorized as 'task'"),
        ("Meeting scheduled for Monday at 10am", "Should be categorized as 'meeting'"),
        ("Invoice #12345 - Payment due", "Should be categorized as 'financial'"),
        ("Random notes about nothing", "Should be categorized as 'general'"),
    ]
    
    print("\nTesting content categorization:")
    print("-" * 50)
    
    for content, expected in test_contents:
        result = categorize_content(content)
        status = "✓" if result['category'] in expected.lower() else "✗"
        print(f"{status} Content: '{content[:40]}...'")
        print(f"  Expected: {expected}")
        print(f"  Got: {result['category']} (confidence: {result['confidence']:.2f})")
        print(f"  Reasoning: {result['reasoning']}")
        print()
