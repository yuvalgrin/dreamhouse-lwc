# Workflow Analysis Web Application

A modern web application that transforms business requirements into Salesforce workflow diagrams using AI-powered analysis.

## Features

- **Free Text Input**: Users can describe their business processes in natural language
- **Interactive User Stories**: Beautifully formatted user stories with structured information
- **Clarification Questions**: AI asks targeted questions to better understand the process
- **Mermaid Diagrams**: Generates visual workflow diagrams using Mermaid syntax
- **Technical Specifications**: Provides detailed Salesforce implementation guidance
- **Modern UI**: Responsive design with step-by-step progress indicators

## Architecture

The application consists of:

- **Backend**: Flask API server that integrates with the existing workflow analysis model
- **Frontend**: Modern HTML/CSS/JavaScript interface with real-time updates
- **AI Integration**: Uses the existing LangChain-based analysis pipeline

## Setup Instructions

### Prerequisites

1. Python 3.8 or higher
2. Node.js (for mermaid-cli if you want PNG generation)
3. The existing workflow analysis model files

### Installation

1. **Navigate to the webapp directory:**
   ```bash
   cd webapp
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install mermaid-cli (optional, for PNG generation):**
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

4. **Set up environment variables:**
   Create a `.env` file in the webapp directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_ENV=development
   ```

### Running the Application

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Usage Guide

### Step 1: Input Requirements
- Enter your business process description in the text area
- Be as detailed as possible about triggers, conditions, and actions
- Example: "When a sales rep creates an opportunity over $100k, send approval email to manager"

### Step 2: Review User Story
- The AI generates a structured user story from your input
- Review the "As a... I want... So that..." format
- Check the acceptance criteria and additional details

### Step 3: Answer Clarification Questions
- If the AI needs more information, it will ask specific questions
- Answer each question thoroughly to improve the analysis
- You can submit answers and get follow-up questions if needed

### Step 4: Generate Diagram
- Once all questions are answered, generate the workflow diagram
- View the Mermaid diagram code and PNG image
- Review the technical specification for Salesforce implementation

## API Endpoints

### POST /api/analyze
Starts the workflow analysis process.

**Request:**
```json
{
  "user_input": "Your business process description"
}
```

**Response:**
```json
{
  "session_id": "session_abc123",
  "step2_result": { /* user story object */ },
  "questions": ["question1", "question2"],
  "status": "ready_for_questions"
}
```

### POST /api/answer-questions
Submits answers to clarification questions.

**Request:**
```json
{
  "session_id": "session_abc123",
  "answers": [
    {
      "question": "What triggers this process?",
      "answer": "When opportunity amount exceeds $100k"
    }
  ]
}
```

### POST /api/generate-diagram
Generates the final workflow diagram and technical specification.

**Request:**
```json
{
  "session_id": "session_abc123"
}
```

**Response:**
```json
{
  "upn_diagram": "flowchart TD\nA[Start] --> B[Check Amount]",
  "png_file": "/path/to/diagram.png",
  "tech_spec": { /* technical specification */ },
  "status": "complete"
}
```

### GET /api/diagram/{session_id}/{filename}
Serves generated diagram files.

### DELETE /api/cleanup/{session_id}
Cleans up temporary files for a session.

## File Structure

```
webapp/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   └── app.js           # Frontend JavaScript
└── temp_uploads/         # Temporary session files (created at runtime)
```

## Customization

### Styling
The application uses a modern design with CSS custom properties. You can customize colors, fonts, and layout by modifying the CSS in `templates/index.html`.

### AI Prompts
The application uses the existing prompts from the model. You can modify these in the `model/main.py` file to change the analysis behavior.

### Mermaid Integration
For better diagram rendering, you can integrate mermaid.js directly in the frontend:

1. Add mermaid.js to the HTML:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
   ```

2. Initialize and render diagrams:
   ```javascript
   mermaid.initialize({ startOnLoad: true });
   mermaid.render('diagram', mermaidCode);
   ```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is set in the environment or in the model file
   - Check that the key has sufficient credits

2. **Mermaid PNG Generation Fails**
   - Install mermaid-cli: `npm install -g @mermaid-js/mermaid-cli`
   - Ensure Node.js is in your PATH

3. **File Permission Errors**
   - Ensure the webapp directory has write permissions for temp_uploads

4. **Port Already in Use**
   - Change the port in `app.py`: `app.run(debug=True, host='0.0.0.0', port=5001)`

### Debug Mode
Run the application in debug mode to see detailed error messages:
```bash
export FLASK_ENV=development
python app.py
```

## Security Considerations

- The application stores temporary files locally
- API keys should be stored securely (use environment variables)
- Consider adding authentication for production use
- Implement rate limiting for API endpoints
- Sanitize user inputs to prevent injection attacks

## Production Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up proper logging
3. Configure environment variables securely
4. Add authentication and authorization
5. Set up monitoring and error tracking
6. Use HTTPS with proper SSL certificates
7. Implement proper session management
8. Add database storage for persistent sessions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Dreamhouse LWC sample application and follows the same licensing terms. 