# Human Approval Skill

## Purpose
This skill manages human-in-the-loop approvals for sensitive actions.

## Functionality
- Determines if an action is sensitive based on content
- Creates approval request records in the Approvals folder
- Monitors approval files for user response
- Waits for user to approve/reject actions

## Input
- action_type: Type of action requiring approval
- action_data: Data associated with the action

## Output
- Boolean indicating whether the action was approved or rejected