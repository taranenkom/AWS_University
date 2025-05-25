from openai import OpenAI

with open(".creds", "r") as f:
    api_key = f.read().strip()
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)
SOC_PROMPT = """
You are an alert-analysis assistant in SOC. Given a single alert record, do the following in one response:

Extract Key Attributes: parse out the most important identifying fields and output each on its own line in the exact format “KEY: VALUE”. For example:
User: JohnnyBravo  
Host: CourageTheCowardlyDog  
Process: ruby (PID 36016)  
File: ngrok (SHA256: 174aacf79ee1a1c22913bc52e31b94c7678fa9976daf0d89fada207f80b9a481)  

Event Summary: produce a concise “What happened” description in this format:
What: {WHAT_HAPPENED}
(e.g. “usage of ngrok was detected, which could be used to bypass firewall via tunneling (used by attackers)”)

Next-Step Analysis: recommend the logical next steps for investigation (e.g., verify parent process chain, check file provenance and hashes, scan other endpoints for the same hash).

True-Positive Response: if the alert is confirmed malicious, list concrete remediation and containment actions (e.g., isolate host, revoke credentials, remove the malicious binary, update detection signatures).

Closure Comment Drafts: draft two brief closing comments—one for a True Positive (confirming the malicious finding and summarizing actions taken) and one for a False Positive (explaining why it was benign and any tuning or rule suppression performed).

Return all sections together, clearly labeled. Do not use any markdown formatting, just plain text. Do not include any additional commentary or explanations outside of the specified sections.  
"""

with open("demo_alert.json", "r") as f:
    alert = f.read().strip()

completion = client.chat.completions.create(
  extra_body={},
  model="deepseek/deepseek-prover-v2:free",
  messages=[
    {
      "role": "user",
      "content": SOC_PROMPT + "\n\n" + alert
    }
  ]
)
print(completion.choices[0].message.content)
with open("alert_analysis.md", "w") as f:
    f.write(completion.choices[0].message.content)