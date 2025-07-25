#!/usr/bin/env python3

import requests
import base64
import json

# Read the current file
with open('vonnegut_ai_app.py', 'r') as f:
    content = f.read()

# GitHub API details
repo_owner = "chweintr"
repo_name = "vonnegut-ai-oracle"
file_path = "vonnegut_ai_app.py"

# You'll need to set this as an environment variable or paste your GitHub token
github_token = input("Enter your GitHub Personal Access Token: ")

# First, get the current file SHA
url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    current_file_sha = response.json()["sha"]
    print(f"Current file SHA: {current_file_sha}")
else:
    print(f"Error getting current file: {response.status_code}")
    print(response.text)
    exit(1)

# Encode the new content
encoded_content = base64.b64encode(content.encode()).decode()

# Update the file
update_data = {
    "message": "Add YouTube video background, fix voice features, and improve biographical accuracy",
    "content": encoded_content,
    "sha": current_file_sha
}

response = requests.put(url, headers=headers, data=json.dumps(update_data))

if response.status_code == 200:
    print("File updated successfully!")
    print("Railway should automatically deploy the changes.")
else:
    print(f"Error updating file: {response.status_code}")
    print(response.text)