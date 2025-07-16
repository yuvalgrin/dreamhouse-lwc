# Azure OpenAI Setup Guide

This guide explains how to configure the Workflow Analysis Tool to use Azure OpenAI instead of the standard OpenAI API.

## Prerequisites

1. An Azure subscription
2. Azure OpenAI Service deployed in your subscription
3. A deployed model (e.g., GPT-4, GPT-3.5-turbo)

## Setup Steps

### 1. Get Azure OpenAI Credentials

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" in the left sidebar
4. Copy the following information:
   - **Endpoint**: The base URL (e.g., `https://your-resource.openai.azure.com`)
   - **Key 1 or Key 2**: Your API key
   - **Deployment name**: The name of your deployed model

### 2. Configure Environment Variables

Create a `.env` file in the `webapp` directory with the following configuration:

```bash
# Set provider to Azure
LLM_PROVIDER=azure

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Model Configuration (optional - will use deployment name)
LLM_TEMPERATURE=0
```

### 3. Example Configuration

Here's a complete example:

```bash
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=sk-1234567890abcdef1234567890abcdef1234567890abcdef
AZURE_OPENAI_ENDPOINT=https://my-openai-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
LLM_TEMPERATURE=0
```

### 4. Start the Application

```bash
cd webapp
./start.sh
```

The application will now use Azure OpenAI instead of the standard OpenAI API.

## Troubleshooting

### Common Issues

1. **"Azure endpoint not found"**: Make sure `AZURE_OPENAI_ENDPOINT` is set correctly
2. **"Azure deployment not found"**: Verify your deployment name in `AZURE_OPENAI_DEPLOYMENT`
3. **Authentication errors**: Check that your API key is correct and has proper permissions

### Verification

When the application starts, you should see a message like:
```
Running prompt with Azure OpenAI (gpt-4 at https://your-resource.openai.azure.com)...
```

## Switching Back to OpenAI

To switch back to standard OpenAI, update your `.env` file:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0
```

## Benefits of Azure OpenAI

- **Enterprise security**: Data stays within your Azure environment
- **Compliance**: Meets enterprise compliance requirements
- **Cost control**: Predictable pricing and usage tracking
- **Custom models**: Ability to fine-tune models for your specific use case
- **Regional deployment**: Deploy in your preferred Azure region 