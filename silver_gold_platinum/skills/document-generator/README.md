# Document Generator Skill

Silver Tier skill for generating reports, briefings, and documents from templates.

## Features

- ✅ CEO Briefing documents
- ✅ Meeting notes/reports
- ✅ Project status reports
- ✅ Custom document templates
- ✅ Human-in-the-loop approval
- ✅ Export to Markdown, TXT (PDF with additional setup)

## Setup

### 1. Install Dependencies

```bash
cd silver/skills/document-generator
pip install -r requirements.txt
```

### 2. Configure Output Directory

Documents are saved to: `silver/vault/Generated/`

## Usage

### Generate CEO Briefing

```bash
python document_generator.py --ceo-briefing --format md
```

Interactive prompts will guide you through:
- Briefing title
- Executive summary
- Key metrics
- Highlights
- Challenges
- Action items

### Generate Meeting Report

```bash
python document_generator.py --meeting-report --format md
```

Prompts include:
- Meeting title
- Date
- Attendees
- Agenda items
- Discussion notes
- Decisions
- Action items

### Generate Status Report

```bash
python document_generator.py --status-report --format md
```

### Generate Custom Document

```bash
python document_generator.py --custom --format md
```

### Skip Approval (for automation)

```bash
python document_generator.py --ceo-briefing --format md --no-approval
```

## Python API

```python
from document_generator import generate_ceo_briefing, generate_meeting_report, generate_status_report

# CEO Briefing
result = generate_ceo_briefing(
    title="Weekly CEO Briefing - March 2026",
    executive_summary="Strong performance across all metrics...",
    key_metrics={
        "Revenue": "$1.2M",
        "Growth": "+15%",
        "Customers": "450"
    },
    highlights=["Launched new product", "Closed enterprise deal"],
    challenges=["Hiring delay in engineering"],
    action_items=["Review hiring plan", "Approve marketing budget"],
    output_format='md',
    require_approval=True
)

# Meeting Report
result = generate_meeting_report(
    meeting_title="Q2 Planning Session",
    date="2026-03-25",
    attendees=["Alice", "Bob", "Charlie"],
    agenda=["Review Q1", "Set Q2 goals", "Budget allocation"],
    discussion_notes="Key discussion points...",
    decisions=["Approved budget", "New hire approved"],
    action_items=["Alice: Draft job description", "Bob: Update roadmap"],
    output_format='md',
    require_approval=True
)

# Status Report
result = generate_status_report(
    project_name="Website Redesign",
    reporting_period="Week 12, March 2026",
    status="Green",
    completed_this_period=["Homepage mockup", "User testing"],
    planned_next_period=["Development sprint 1", "Content migration"],
    risks=["Designer availability"],
    budget_status="On track",
    timeline_status="On schedule",
    output_format='md',
    require_approval=True
)
```

## Output Formats

- **md** (Markdown): Default, recommended for Obsidian vault
- **txt** (Plain Text): Stripped of markdown formatting
- **pdf**: Saves as MD with note to convert manually (requires pandoc/wkhtmltopdf)

## Document Templates

### CEO Briefing Structure
```
# Title
- Executive Summary
- Key Metrics
- Highlights
- Challenges
- Action Items
```

### Meeting Report Structure
```
# Meeting Title
- Attendees
- Agenda
- Discussion Notes
- Decisions Made
- Action Items
```

### Status Report Structure
```
# Project Status
- Overall Status (Green/Yellow/Red)
- Budget Status
- Timeline Status
- Completed This Period
- Planned Next Period
- Risks & Concerns
```

## Response Format

```json
{
  "success": true,
  "file_path": "D:/.../silver/vault/Generated/CEO_Briefing_20260324_103000.md",
  "filename": "CEO_Briefing_20260324_103000.md",
  "format": "md",
  "details": {
    "title": "Weekly CEO Briefing",
    "type": "CEO Briefing",
    "metrics_count": 3,
    "highlights_count": 2,
    "challenges_count": 1,
    "action_items_count": 2
  }
}
```

## Tips

- Documents integrate with Obsidian vault for easy viewing
- Use consistent naming for better organization
- Consider automating weekly status reports
- Link related documents using Obsidian wikilinks `[[ ]]`
