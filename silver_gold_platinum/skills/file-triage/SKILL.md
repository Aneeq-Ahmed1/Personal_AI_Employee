# File Triage Skill

## Purpose
This skill enables the AI employee to process incoming markdown files from the Inbox, understand their content, and route them appropriately to either Needs_Action or Done folders.

## Procedure

### Step 1: Reading Inbox Files
- Monitor the vault/Inbox/ directory for new .md files
- Open each new file using UTF-8 encoding
- Read the entire content into memory
- Parse the markdown structure to identify headings, paragraphs, and lists

### Step 2: Understanding the Task
- Identify the main heading (#) as the primary task title
- Extract any sub-headings (##, ###) as supporting details
- Read the first paragraph as the task summary
- Scan for keywords indicating urgency, priority, or deadlines
- Look for numbered lists or bullet points as specific action items

### Step 3: Creating a Summary
- Write a 1-2 sentence summary of the main request
- Identify the key deliverables mentioned in the file
- Note any specific requirements or constraints
- Highlight any deadlines or time-sensitive elements

### Step 4: Decision Framework
- If the file contains actionable items or requests requiring work: Route to Needs_Action
- If the file contains information that only needs filing or archiving: Route to Done
- If the file contains questions requiring research or external input: Route to Needs_Action
- If the file contains completed work or reports: Route to Done
- When uncertain: Default to Needs_Action

### Step 5: Writing Clean Markdown Output
- Use proper markdown formatting (headers, lists, emphasis)
- Maintain consistent heading hierarchy
- Include the original content under an "Original Request" section
- Add a "Summary" section with your understanding
- Add a "Next Steps" section with recommended actions when routing to Needs_Action
- Preserve all original formatting and links
- Use bullet points for multiple action items
- Keep paragraphs concise and scannable