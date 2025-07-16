#!/usr/bin/env python3
"""
Script to list Azure OpenAI deployments
"""

import os
import requests
import json

def list_deployments():
    """List available deployments in Azure OpenAI"""
    
    # Your Azure OpenAI configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://secondopinion.openai.azure.com")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
    
    # Headers for the request
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # URL to list deployments
    url = f"{endpoint}/openai/deployments?api-version=2024-08-01-preview"
    
    try:
        print(f"Fetching deployments from: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            deployments = response.json()
            print("\n✅ Available deployments:")
            print(json.dumps(deployments, indent=2))
            
            if 'data' in deployments:
                print("\n📋 Deployment names:")
                for deployment in deployments['data']:
                    print(f"  - {deployment['id']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    list_deployments() 