#!/bin/bash

# Workflow Analysis Web Application Startup Script

echo "🚀 Starting Workflow Analysis Web Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the webapp directory."
    echo "   cd webapp && ./start.sh"
    exit 1
fi

# Check if requirements are installed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if mermaid-cli is installed (optional)
if ! command -v mmdc &> /dev/null; then
    echo "⚠️  mermaid-cli not found. PNG generation will be disabled."
    echo "   To enable PNG generation, install mermaid-cli:"
    echo "   npm install -g @mermaid-js/mermaid-cli"
fi

# Create temp_uploads directory if it doesn't exist
mkdir -p temp_uploads

# Start the application
echo "🌐 Starting Flask server..."
echo "   Open your browser and navigate to: http://localhost:5003"
echo "   Press Ctrl+C to stop the server"
echo ""

python app.py 