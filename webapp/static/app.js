class WorkflowAnalyzer {
    constructor() {
        this.sessionId = null;
        this.currentStep = 1;
        this.questions = [];
        this.answers = [];
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Initial analysis button
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.startAnalysis();
        });

        // Submit answers button
        document.getElementById('submitAnswersBtn').addEventListener('click', () => {
            this.submitAnswers();
        });

        // Generate diagram button
        document.getElementById('generateDiagramBtn').addEventListener('click', () => {
            this.generateDiagram();
        });

        // New analysis button
        document.getElementById('newAnalysisBtn').addEventListener('click', () => {
            this.resetApplication();
        });

        // Preset example buttons
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const preset = e.target.closest('.preset-btn').dataset.preset;
                this.loadPreset(preset);
            });
        });

        // Enter key support for textarea
        document.getElementById('userInput').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.startAnalysis();
            }
        });
    }

    loadPreset(preset) {
        const userInput = document.getElementById('userInput');
        
        const presets = {
            goldenfoods: `Hi there—Jamie here at GoldenFoods. I craft gourmet kibble, wet food, treats, and even subscription boxes specially made for Golden Retrievers.

We sell nationwide through indie pet boutiques and big retail chains, and I'm aiming for a 40% boost in physical-store coverage this year.

Right now, leads come in from trade shows, our website, social media, referrals, and outbound calls—but keeping track of everything in spreadsheets is slowing us down when it comes to follow-ups.

When I log a lead, I usually track product interest, estimated monthly volume in pounds, region, and their preferred contact method.

Our sales pipeline is set up to mirror Salesforce's default stages: Qualification, Proposal/Price Quote, Negotiation/Review, and Closed Won.

Any quote with a discount over 15% needs my sign-off, so I'd love to automate that approval step.

The dashboards I need include lead-to-opportunity conversion by region, average days to convert, and a heat map for store coverage.

Also, every new opportunity should automatically create two tasks: one to send a sample pack within three days, and another to schedule a pricing call within ten.

And lastly, it's important that email replies are logged back to Salesforce, so we can stay on top of response times and keep them under 24 hours.`,
            
            techstartup: `Hi, I'm Sarah from CloudFlow, a B2B SaaS startup that provides workflow automation tools for small businesses.

We're growing fast and need to streamline our sales process. Currently, we get leads from our website, LinkedIn ads, and partner referrals.

Our sales cycle typically involves: initial demo, proposal creation, technical review, contract negotiation, and onboarding setup.

I need automation for:
- Lead scoring based on company size, industry, and engagement level
- Automatic follow-up sequences for different lead types
- Quote generation with dynamic pricing based on features selected
- Integration with our billing system for contract creation
- Customer success team notifications when deals close

We also need dashboards showing conversion rates by lead source, average deal size, and sales cycle length.

The system should automatically assign leads to the right sales rep based on territory and workload.

For enterprise deals over $50k, we need approval from our VP of Sales before sending proposals.`
        };

        if (presets[preset]) {
            userInput.value = presets[preset];
            userInput.focus();
            
            // Show a brief success message
            this.showAlert(`Loaded ${preset === 'goldenfoods' ? 'GoldenFoods Pet Supply' : 'Tech Startup CRM'} example`, 'success');
            
            // Scroll to the analyze button
            document.getElementById('analyzeBtn').scrollIntoView({ behavior: 'smooth' });
        }
    }

    async startAnalysis() {
        const userInput = document.getElementById('userInput').value.trim();
        
        if (!userInput) {
            this.showAlert('Please enter your business process description.', 'error');
            return;
        }

        this.showLoading(true);
        this.updateStepIndicator(1, 'active');

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_input: userInput })
            });

            const data = await response.json();

            if (response.ok) {
                this.sessionId = data.session_id;
                this.handleAnalysisResponse(data);
            } else {
                throw new Error(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showAlert(`Analysis failed: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    handleAnalysisResponse(data) {
        // Display user story
        this.displayUserStory(data.step2_result);
        this.updateStepIndicator(2, 'completed');

        if (data.questions && data.questions.length > 0) {
            // Show questions
            this.questions = data.questions;
            this.displayQuestions(data.questions);
            this.updateStepIndicator(3, 'active');
        } else {
            // No questions, ready for diagram generation
            this.showGenerateDiagramButton();
            this.updateStepIndicator(3, 'completed');
            this.updateStepIndicator(4, 'active');
        }

        this.showResultsSection();
    }

    displayUserStory(userStory) {
        const userStorySection = document.getElementById('userStorySection');
        const userStoryContent = document.getElementById('userStoryContent');

        // Format the user story nicely
        let formattedStory = '';
        if (typeof userStory === 'object') {
            formattedStory = this.formatUserStoryObject(userStory);
        } else {
            formattedStory = userStory;
        }

        userStoryContent.innerHTML = formattedStory;
        userStorySection.classList.remove('hidden');
    }

    formatUserStoryObject(userStory) {
        let html = '<div style="line-height: 1.6;">';
        
        // Recursive function to render any object structure
        const renderObject = (obj, level = 0) => {
            if (obj === null || obj === undefined) return '';
            
            let result = '';
            const indent = '  '.repeat(level);
            const marginLeft = level * 20;
            
            if (typeof obj === 'string') {
                return `<p style="margin-left: ${marginLeft}px; margin-bottom: 8px;">${obj}</p>`;
            } else if (typeof obj === 'number' || typeof obj === 'boolean') {
                return `<p style="margin-left: ${marginLeft}px; margin-bottom: 8px;">${obj}</p>`;
            } else if (Array.isArray(obj)) {
                if (obj.length === 0) return '';
                result += `<ul style="margin-left: ${marginLeft}px; margin-bottom: 12px;">`;
                obj.forEach(item => {
                    if (typeof item === 'object' && item !== null) {
                        result += '<li style="margin-bottom: 8px;">';
                        result += renderObject(item, level + 1);
                        result += '</li>';
                    } else {
                        result += `<li style="margin-bottom: 5px;">${item}</li>`;
                    }
                });
                result += '</ul>';
                return result;
            } else if (typeof obj === 'object') {
                Object.keys(obj).forEach(key => {
                    const value = obj[key];
                    
                    // Skip empty values
                    if (value === null || value === undefined || value === '') return;
                    
                    // Format the key name (convert camelCase to Title Case)
                    const formattedKey = key.replace(/([A-Z])/g, ' $1')
                        .replace(/^./, str => str.toUpperCase())
                        .replace(/_/g, ' ');
                    
                    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                        // Nested object
                        result += `<div style="margin-left: ${marginLeft}px; margin-bottom: 12px;">`;
                        result += `<h6 style="color: #3b82f6; font-weight: 600; margin-bottom: 8px; font-size: 0.9rem;">${formattedKey}:</h6>`;
                        result += renderObject(value, level + 1);
                        result += '</div>';
                    } else if (Array.isArray(value)) {
                        // Array
                        if (value.length > 0) {
                            result += `<div style="margin-left: ${marginLeft}px; margin-bottom: 12px;">`;
                            result += `<h6 style="color: #3b82f6; font-weight: 600; margin-bottom: 8px; font-size: 0.9rem;">${formattedKey}:</h6>`;
                            result += renderObject(value, level + 1);
                            result += '</div>';
                        }
                    } else {
                        // Simple value
                        result += `<p style="margin-left: ${marginLeft}px; margin-bottom: 8px;">`;
                        result += `<strong style="color: #374151;">${formattedKey}:</strong> `;
                        result += `<span style="color: #6b7280;">${value}</span>`;
                        result += '</p>';
                    }
                });
                return result;
            }
            
            return result;
        };
        
        // Render the entire user story object
        html += renderObject(userStory);
        html += '</div>';
        return html;
    }

    displayQuestions(questions) {
        const questionsSection = document.getElementById('questionsSection');
        const questionsList = document.getElementById('questionsList');

        questionsList.innerHTML = '';
        
        questions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-item';
            questionDiv.innerHTML = `
                <h4>Question ${index + 1}</h4>
                <p style="margin-bottom: 15px;">${question}</p>
                <textarea 
                    class="form-control" 
                    id="answer_${index}" 
                    placeholder="Please provide your answer..."
                    rows="3"
                ></textarea>
            `;
            questionsList.appendChild(questionDiv);
        });

        questionsSection.classList.remove('hidden');
    }

    async submitAnswers() {
        const answers = [];
        let allAnswered = true;

        this.questions.forEach((question, index) => {
            const answer = document.getElementById(`answer_${index}`).value.trim();
            if (!answer) {
                allAnswered = false;
                return;
            }
            answers.push({
                question: question,
                answer: answer
            });
        });

        if (!allAnswered) {
            this.showAlert('Please answer all questions before submitting.', 'error');
            return;
        }

        this.showLoading(true, 'Processing your answers...');

        try {
            const response = await fetch('/api/answer-questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    answers: answers
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.handleAnswersResponse(data);
            } else {
                throw new Error(data.error || 'Failed to process answers');
            }
        } catch (error) {
            console.error('Answer submission error:', error);
            this.showAlert(`Failed to process answers: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    handleAnswersResponse(data) {
        // Update user story if it changed
        if (data.user_story) {
            this.displayUserStory(data.user_story);
        }

        this.updateStepIndicator(3, 'completed');

        if (data.questions && data.questions.length > 0) {
            // More questions
            this.questions = data.questions;
            this.displayQuestions(data.questions);
        } else {
            // No more questions, ready for diagram
            document.getElementById('questionsSection').classList.add('hidden');
            this.showGenerateDiagramButton();
            this.updateStepIndicator(4, 'active');
        }
    }

    showGenerateDiagramButton() {
        const actionButtons = document.getElementById('actionButtons');
        const generateDiagramBtn = document.getElementById('generateDiagramBtn');
        
        generateDiagramBtn.style.display = 'inline-flex';
        actionButtons.classList.remove('hidden');
    }

    async generateDiagram() {
        this.showLoading(true, 'Generating workflow diagram...');

        try {
            const response = await fetch('/api/generate-diagram', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.handleDiagramResponse(data);
            } else {
                throw new Error(data.error || 'Failed to generate diagram');
            }
        } catch (error) {
            console.error('Diagram generation error:', error);
            this.showAlert(`Failed to generate diagram: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    handleDiagramResponse(data) {
        this.updateStepIndicator(4, 'completed');

        // Display diagram
        if (data.mermaid_diagram) {
            this.displayMermaidDiagram(data.mermaid_diagram);
        }

        // Display technical specification
        if (data.tech_spec) {
            this.displayTechnicalSpec(data.tech_spec);
        }

        // Show completion message
        this.showAlert('Workflow analysis completed successfully!', 'success');
    }

    displayDiagram(pngFile) {
        const diagramSection = document.getElementById('diagramSection');
        const workflowDiagram = document.getElementById('workflowDiagram');
        
        // Set the image source with cache-busting
        workflowDiagram.src = `/api/diagram/${this.sessionId}/workflow_diagram.png?t=${Date.now()}`;
        
        diagramSection.classList.remove('hidden');
    }

    displayMermaidDiagram(mermaidCode) {
        const diagramSection = document.getElementById('diagramSection');
        const mermaidDiv = document.getElementById('mermaidDiagram');
        
        // Clear previous content
        mermaidDiv.innerHTML = '';
        
        // Set the Mermaid code
        mermaidDiv.textContent = mermaidCode;
        
        // Initialize and render Mermaid diagram
        mermaid.initialize({ 
            startOnLoad: false,
            theme: 'default',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true
            }
        });
        
        try {
            mermaid.render('mermaid-diagram', mermaidCode).then(({svg}) => {
                mermaidDiv.innerHTML = svg;
            }).catch(error => {
                console.error('Mermaid rendering error:', error);
                mermaidDiv.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #6b7280;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                        <p>Error rendering diagram. Here's the Mermaid code:</p>
                        <pre style="background: #f8f9fa; padding: 15px; border-radius: 8px; overflow-x: auto; text-align: left; margin-top: 10px;">${mermaidCode}</pre>
                    </div>
                `;
            });
        } catch (error) {
            console.error('Mermaid error:', error);
            mermaidDiv.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #6b7280;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                    <p>Error rendering diagram. Here's the Mermaid code:</p>
                    <pre style="background: #f8f9fa; padding: 15px; border-radius: 8px; overflow-x: auto; text-align: left; margin-top: 10px;">${mermaidCode}</pre>
                </div>
            `;
        }
        
        diagramSection.classList.remove('hidden');
    }

    displayTechnicalSpec(techSpec) {
        const techSpecSection = document.getElementById('techSpecSection');
        const techSpecContent = document.getElementById('techSpecContent');

        let html = '<div style="line-height: 1.6;">';
        
        if (techSpec.selected_step) {
            html += `<h4 style="color: #0ea5e9; margin-bottom: 15px;">Selected Step: ${techSpec.selected_step}</h4>`;
        }

        if (techSpec.implementation) {
            html += '<div style="margin-bottom: 20px;">';
            html += '<h5 style="color: #374151; margin-bottom: 10px;">Implementation Details:</h5>';
            
            const impl = techSpec.implementation;
            if (impl.automation_type) {
                html += `<p><strong>Automation Type:</strong> ${impl.automation_type}</p>`;
            }
            if (impl.object) {
                html += `<p><strong>Object:</strong> ${impl.object}</p>`;
            }
            if (impl.trigger_event) {
                html += `<p><strong>Trigger Event:</strong> ${impl.trigger_event}</p>`;
            }
            if (impl.entry_criteria && Array.isArray(impl.entry_criteria)) {
                html += '<p><strong>Entry Criteria:</strong></p><ul>';
                impl.entry_criteria.forEach(criteria => {
                    html += `<li>${criteria.field} ${criteria.operator} ${criteria.value}</li>`;
                });
                html += '</ul>';
            }
            if (impl.actions && Array.isArray(impl.actions)) {
                html += '<p><strong>Actions:</strong></p><ul>';
                impl.actions.forEach(action => {
                    html += `<li>${action.type}: ${action.details}</li>`;
                });
                html += '</ul>';
            }
            html += '</div>';
        }

        if (techSpec.requires_code) {
            html += `<p><strong>Requires Code:</strong> ${techSpec.requires_code}</p>`;
        }

        if (techSpec.governor_limits) {
            html += `<p><strong>Governor Limits:</strong> ${techSpec.governor_limits}</p>`;
        }

        if (techSpec.test_scenarios && Array.isArray(techSpec.test_scenarios)) {
            html += '<div style="margin-top: 15px;">';
            html += '<h5 style="color: #374151; margin-bottom: 10px;">Test Scenarios:</h5>';
            html += '<ul>';
            techSpec.test_scenarios.forEach(scenario => {
                html += `<li style="margin-bottom: 5px;">${scenario}</li>`;
            });
            html += '</ul>';
            html += '</div>';
        }

        html += '</div>';
        techSpecContent.innerHTML = html;
        techSpecSection.classList.remove('hidden');
    }

    showLoading(show, message = 'Processing...') {
        const loadingSection = document.getElementById('loadingSection');
        const inputSection = document.getElementById('inputSection');
        const resultsSection = document.getElementById('resultsSection');

        if (show) {
            loadingSection.querySelector('p').textContent = message;
            loadingSection.style.display = 'block';
            inputSection.style.display = 'none';
            resultsSection.style.display = 'none';
        } else {
            loadingSection.style.display = 'none';
            inputSection.style.display = 'block';
            resultsSection.style.display = 'block';
        }
    }

    showResultsSection() {
        document.getElementById('resultsSection').classList.remove('hidden');
    }

    updateStepIndicator(stepNumber, status) {
        const stepElement = document.getElementById(`step${stepNumber}`);
        if (stepElement) {
            stepElement.className = `step ${status}`;
        }
    }

    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';

        alertDiv.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        `;

        // Insert at the top of the card content
        const cardContent = document.querySelector('.card-content');
        cardContent.insertBefore(alertDiv, cardContent.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    resetApplication() {
        // Reset all form fields
        document.getElementById('userInput').value = '';
        
        // Hide all sections
        document.getElementById('userStorySection').classList.add('hidden');
        document.getElementById('questionsSection').classList.add('hidden');
        document.getElementById('diagramSection').classList.add('hidden');
        document.getElementById('techSpecSection').classList.add('hidden');
        document.getElementById('actionButtons').classList.add('hidden');
        document.getElementById('resultsSection').classList.add('hidden');

        // Reset step indicators
        for (let i = 1; i <= 4; i++) {
            const stepElement = document.getElementById(`step${i}`);
            if (stepElement) {
                stepElement.className = 'step';
                if (i === 1) stepElement.classList.add('active');
            }
        }

        // Reset state
        this.sessionId = null;
        this.currentStep = 1;
        this.questions = [];
        this.answers = [];

        // Clean up session if exists
        if (this.sessionId) {
            fetch(`/api/cleanup/${this.sessionId}`, { method: 'DELETE' })
                .catch(error => console.error('Cleanup error:', error));
        }

        // Show input section
        document.getElementById('inputSection').style.display = 'block';
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new WorkflowAnalyzer();
}); 