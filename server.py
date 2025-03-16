from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Your GitHub API token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

@app.route("/")
def home():
    """Root endpoint to indicate server status"""
    return "GitHub Assistant API is running! Try /mcp/discover"

@app.route("/mcp/discover", methods=["GET"])
def discover():
    """Endpoint for service discovery"""
    return jsonify({
        "name": "GitHub Assistant",
        "description": "Interact with GitHub repositories, issues, and PRs",
        "endpoints": [
            {
                "name": "search_repositories",
                "description": "Search for GitHub repositories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query string"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_repo_issues",
                "description": "Get issues for a specific repository",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        }
                    },
                    "required": ["owner", "repo"]
                }
            }
        ]
    })

@app.route("/mcp/execute", methods=["POST"])
def execute():
    """Endpoint for executing operations"""
    data = request.json
    endpoint = data.get("endpoint")
    parameters = data.get("parameters", {})
    
    if endpoint == "search_repositories":
        return search_repositories(parameters)
    elif endpoint == "get_repo_issues":
        return get_repo_issues(parameters)
    else:
        return jsonify({"error": "Unknown endpoint"})

def search_repositories(parameters):
    """Search GitHub repositories"""
    query = parameters.get("query")
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(
        f"https://api.github.com/search/repositories?q={query}",
        headers=headers
    )
    
    repos = response.json().get("items", [])
    simplified_repos = [
        {
            "name": repo["full_name"],
            "description": repo["description"],
            "stars": repo["stargazers_count"],
            "url": repo["html_url"]
        }
        for repo in repos[:5]  # Limit to 5 results
    ]
    
    return jsonify({"repositories": simplified_repos})

def get_repo_issues(parameters):
    """Get issues for a repository"""
    owner = parameters.get("owner")
    repo = parameters.get("repo")
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        headers=headers
    )
    
    issues = response.json()
    simplified_issues = [
        {
            "title": issue["title"],
            "number": issue["number"],
            "state": issue["state"],
            "url": issue["html_url"]
        }
        for issue in issues[:5]  # Limit to 5 results
    ]
    
    return jsonify({"issues": simplified_issues})

# Print a message when the server starts
print("Server is starting on http://127.0.0.1:8080")
print("Press Ctrl+C to stop the server")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8080)
