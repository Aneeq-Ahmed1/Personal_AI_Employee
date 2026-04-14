# Reasoning Engine Skill

## Purpose
This skill analyzes tasks from the Needs_Action folder and generates prioritized action plans in the Plans folder.

## Functionality
- Reads all markdown files in vault/Needs_Action/
- Extracts title, summary, and priority information
- Sorts tasks by priority (High, Medium, Low)
- Generates Plan.md files with organized action steps
- Creates timestamped plan files in vault/Plans/

## Input
- None required (reads from vault/Needs_Action/)
- Optionally accepts a specific file path to process

## Output
- Plan.md file in vault/Plans/ with organized task list
- Returns path to generated plan file