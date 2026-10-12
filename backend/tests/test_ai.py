import json
from ollama import chat

TASK_PROMPT = """
Analyze this task: apply  1 AI eng role
tasks description: coop role, resume, cover letter

Return a JSON object containing:
- category: short task category
- estimated_hours: estimated focused work hours
- importance: integer from 1 to 5
- reason: brief explanation

Estimate work hours, not time until the deadline.
Use reasonable assumptions for missing details.
"""

response = chat(
    model="qwen3:4b",
    messages=[{"role": "user", "content": TASK_PROMPT}],
    format="json",
)

data = json.loads(response.message.content)
print(data)
print(data["estimated_hours"])