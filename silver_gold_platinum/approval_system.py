import sys
from pathlib import Path

# Add the skills directory to the path so we can import the human approval module
sys.path.append(str(Path(__file__).parent / "skills" / "human-approval"))

from human_approval import check_approval_needed