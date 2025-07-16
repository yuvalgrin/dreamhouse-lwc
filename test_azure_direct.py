#!/usr/bin/env python3
"""
Direct test of Azure OpenAI using the official SDK
"""

import openai
import os

def test_azure_openai():
    """Test Azure OpenAI directly"""
    
    # Configure the client
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        
    client = openai.AzureOpenAI(
        api_key=api_key,
        api_version="2024-08-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://secondopinion.openai.azure.com")
    )
    
    try:
        print("=== Testing Azure OpenAI Direct Connection ===")
        
        # Try a chat completion
        print("\n1. Testing chat completion...")
        response = client.chat.completions.create(
            model="gpt-4o",  # Try this deployment name
            messages=[
                {"role": "user", "content": "Say hello in one word"}
            ]
        )
        print(f"✅ Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # If it's a deployment issue, try common names
        if "deployment" in str(e).lower() or "404" in str(e):
            print("\n🔍 Trying common deployment names...")
            common_deployments = ["gpt-4", "gpt-35-turbo", "gpt-4o", "gpt-4o-mini"]
            
            for deployment in common_deployments:
                try:
                    print(f"  Trying deployment: {deployment}")
                    response = client.chat.completions.create(
                        model=deployment,
                        messages=[
                            {"role": "user", "content": "Say hello in one word"}
                        ]
                    )
                    print(f"✅ Success with deployment '{deployment}': {response.choices[0].message.content}")
                    break
                except Exception as e2:
                    print(f"    ❌ Failed: {e2}")

if __name__ == "__main__":
    test_azure_openai() 