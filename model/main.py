import os
import json
from pathlib import Path
import re
import openai

# Azure OpenAI configuration
AZURE_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', 'https://secondopinion.openai.azure.com')
AZURE_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')
AZURE_API_VERSION = '2024-08-01-preview'

if not AZURE_API_KEY:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")

client = openai.AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT
)


prompt1 = """
Step 1 – Ingest the raw requirements

Task: Analyze the user's business process description. Extract every requirement that relates to CRM workflows or automation in Salesforce. Produce a concise, bulleted summary of the facts you extracted (no interpretation yet).

Output: Return ONLY a valid JSON object without any markdown formatting, code blocks, or additional text:
{ "raw_requirements": [ "bullet 1", "bullet 2", … ] }

(Keep the wording faithful to the user's input; do not transform into stories or diagrams in this step.)
"""

prompt2 = """
Step 2 – Refine into a clarified user story

Task: Using the bullets in "raw_requirements" plus the guidance in user_story_q.json, draft a single user-story JSON block.
• Follow the exact field names and structure shown in user_story_q.json.
• Wherever information is missing or ambiguous, ask me (the user) clarification questions inside a "questions_for_user" array. you should ask at least 1 question.
• If all info is sufficient, leave "questions_for_user" empty.

Output: Return ONLY a valid JSON object without any markdown formatting, code blocks, or additional text:
{
 "user_story": { …complete per schema… },
 "questions_for_user": [ …if any… ]
}

(Do not include anything else.)
"""

prompt3 = """
Step 3 – Clarification questions

Task: According to the user answer to the question, update the user story.

Output: Return ONLY a valid JSON object without any markdown formatting, code blocks, or additional text:
{
 "user_story": { …complete per schema… },
 "questions_for_user": [ …if any… ]
}

(Do not include anything else.)
"""


prompt4 = """
Step 4 – Translate the finalized user story into a UPN map

Task: Convert the confirmed "user_story" into a Unified Process Notation (UPN) description, following the rules in process_diagrams.json, and the salesforce capabilities saleforce_flow_caps.json.
• Represent each activity as a UPN box with a clear verb-noun label.
• Show flow connectors and decision points exactly as specified in the guidelines.
• Return a structured JSON with steps array, not a Mermaid diagram string.

Output: Return ONLY a valid JSON object without any markdown formatting, code blocks, or additional text:
{ 
  "upn_diagram": {
    "steps": [
      {
        "id": "step_id",
        "type": "Record Event|Do|Wait|Check|Notify|End",
        "label": "Step description",
        "actor": "Who performs this step",
        "next_step_ids": ["next_step_id1", "next_step_id2"]
      }
    ]
  }
}
"""



prompt5 = """
Step 5 – Technical build specification

Task:
Produce a technical build specification for implementing one of the workflow steps. 
Follow these rules:
	1.	Identify automation type – Choose the most suitable technology mechanism (API Integration, Database Trigger, Scheduled Job, Webhook, etc.)
	2.	Detail configuration – Specify:
        •	System & triggering event
        •	Entry criteria (conditions, parameters, values)
        •	Actions (data updates, notifications, integrations, etc.)
        •	Required permissions / security considerations
        •	Naming conventions for components and resources
	3.	Code vs. configuration – In a "requires_code" field, state "yes" or "no".
	    •	If "yes", list the component names and a one-line purpose for each.
	4.	Testing & limits – Include performance considerations and at least two test scenarios.

Output: Return ONLY a valid JSON object without any markdown formatting, code blocks, or additional text:
{
 "selected_step": "<verbatim label>",
 "implementation": {
   "automation_type": "API Integration",
   "system": "Inventory Management",
   "trigger_event": "stock_update",
   "entry_criteria": [ { "field": "stock_level", "operator": "lt", "value": 10 } ],
   "actions": [ { "type": "notification", "details": "Send low stock alert" } ],
   "permissions_notes": "Requires read access to inventory database.",
   "naming_conventions": {
     "component_name": "Inventory_Alert_System",
     "variables_prefix": "invAlert"
   }
 },
 "requires_code": "no",
 "performance_limits": "API calls ≤1000 per hour; response time ≤2 seconds.",
 "test_scenarios": [
   "Stock level drops to 5 → alert notification sent.",
   "Stock level remains at 15 → no alert triggered."
 ]
}

(Do not include anything else.)
"""


def run_prompt(prompt: str, context_files: list[Path] | None = None) -> str:
    print(f"Running prompt with Azure OpenAI deployment '{AZURE_DEPLOYMENT}'...")
    if context_files:
        contexts = ""
        for context_file in context_files:
            with open(context_file, "r") as f:
                context = "\n".join(f.readlines())
                contexts += f'Context file "{context_file.name}": {context}\n'
        prompt = f'{contexts}\n\n{prompt}'
    
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("LLM returned empty response")
    return content.strip()


def convert_upn_to_png(upn_diagram: str) -> str:
    """Convert UPN diagram to PNG using mermaid-cli."""
    print("Converting UPN to PNG with mermaid...")
    
    # Validate input
    if not upn_diagram or not upn_diagram.strip():
        raise ValueError("UPN diagram content is empty or invalid")
    
    # Ensure the diagram starts with a valid mermaid directive
    if not upn_diagram.strip().startswith(('flowchart', 'graph', 'sequenceDiagram', 'classDiagram')):
        # Add flowchart directive if missing
        upn_diagram = f"flowchart TD\n{upn_diagram}"
    
    try:
        # Write mermaid file
        mermaid_file = "company_workflow_process.mmd"
        with open(mermaid_file, "w") as f:
            f.write(upn_diagram)
        
        # Convert to PNG using mmdc
        png_file = "company_workflow_process.png"
        result = os.system(f"mmdc -i {mermaid_file} -o {png_file} --quiet")
        
        if result != 0:
            raise RuntimeError(f"mmdc conversion failed with exit code {result}")
        
        # Verify PNG file was created
        if not os.path.exists(png_file):
            raise RuntimeError("PNG file was not created")
        
        # Get file size to verify it's not empty
        file_size = os.path.getsize(png_file)
        if file_size == 0:
            raise RuntimeError("Generated PNG file is empty")
        
        print(f"✓ PNG created successfully ({file_size} bytes)")
        return png_file
        
    except Exception as e:
        print(f"❌ Error converting to PNG: {e}")
        # Clean up any partial files
        for file in [mermaid_file, png_file]:
            if os.path.exists(file):
                os.remove(file)
        raise

def get_user_answer(question: str) -> str:
    """Get user input for a clarification question."""
    print(f"\n🤔 Question: {question}")
    print("Please provide your answer:")
    return input("> ").strip()


def save_result(content: str, filename: str, step_name: str) -> None:
    """Save step result to file with progress indication."""
    
    # Clean up markdown code blocks if present
    cleaned_content = content.strip()
    
    # Remove markdown code blocks using regex
    # Pattern: ```json\n...\n``` or ```\n...\n```
    pattern = r'^```(?:json)?\n(.*?)\n```$'
    match = re.search(pattern, cleaned_content, re.DOTALL)
    
    if match:
        cleaned_content = match.group(1).strip()
    else:
        # Fallback: simple string replacement
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
        
        cleaned_content = cleaned_content.strip()
    
    filepath = f"company-goldenfood-result/{filename}"
    with open(filepath, "w") as f:
        f.write(cleaned_content)
    print(f"✓ Saved to {filepath}")


def step1_extract_requirements() -> str:
    """Step 1: Extract raw requirements from company requirements file."""
    print("\n=== Step 1: Extracting Raw Requirements ===")
    try:
        result = run_prompt(
            prompt1, 
            context_files=[Path("test-data/company_reqs_examples.json")]
        )
        print("✓ Raw requirements extracted")
        save_result(result, "step1_raw_requirements.json", "Step 1")
        return result
    except Exception as e:
        print(f"❌ Error in Step 1: {e}")
        raise


def step2_create_user_story() -> str:
    """Step 2: Create user story from raw requirements."""
    print("\n=== Step 2: Creating User Story ===")
    try:
        result = run_prompt(
            prompt2,
            context_files=[
                Path("context-data/user_story_q.json"),
                Path("company-goldenfood-result/step1_raw_requirements.json")
            ]
        )
        print("✓ User story created")
        save_result(result, "step2_user_story.json", "Step 2")
        return result
    except Exception as e:
        print(f"❌ Error in Step 2: {e}")
        raise


def step3_handle_clarifications(result: str) -> str:
    """Step 3: Handle clarification questions until resolved."""
    print("\n=== Step 3: Handling Clarification Questions ===")
    try:
        # Loop until all questions are answered
        result_json = json.loads(result)
        while len(result_json["questions_for_user"]) > 0:
            question = result_json["questions_for_user"][0]
            user_answer = get_user_answer(question)
            prompt3_with_user_answer = f'{prompt3}\n\nQuestion: {question}\n\nUser answer: {user_answer}'
            result = run_prompt(
                prompt3_with_user_answer,
                context_files=[
                    Path("context-data/user_story_q.json"),
                    Path("company-goldenfood-result/step2_user_story.json")
                ]
            )
            result_json = json.loads(result)

        # Save final step 3 result
        save_result(result, "step3_finalized_user_story.json", "Step 3")
        return result
    except Exception as e:
        print(f"❌ Error in Step 3: {e}")
        raise


def step4_generate_upn_diagram() -> str:
    """Step 4: Generate UPN diagram from finalized user story."""
    print("\n=== Step 4: Generating UPN Diagram ===")
    try:
        result = run_prompt(
            prompt4,
            context_files=[
                Path("context-data/process_diagrams.json"),
                Path("context-data/saleforce_flow_caps.json"),
                Path("company-goldenfood-result/step3_finalized_user_story.json")
            ]
        )
        print("✓ UPN diagram generated")
        save_result(result, "step4_upn_diagram.json", "Step 4")
        
        # Try to convert to PNG
        try:
            # Extract UPN diagram text from JSON response
            import json
            upn_data = json.loads(result)
            upn_diagram = upn_data.get("upn_diagram", "")
            
            if upn_diagram:
                png_file = convert_upn_to_png(upn_diagram)
                print(f"✓ Converted to PNG: {png_file}")
        except Exception as e:
            print(f"⚠️ Could not convert to PNG: {e}")
        
        return result
    except Exception as e:
        print(f"❌ Error in Step 4: {e}")
        raise


def step5_create_tech_spec() -> str:
    """Step 5: Create technical specification from UPN diagram."""
    print("\n=== Step 5: Creating Technical Specification ===")
    try:
        result = run_prompt(
            prompt5,
            context_files=[
                Path("context-data/saleforce_flow_caps.json"),
                Path("company-goldenfood-result/step4_upn_diagram.json")
            ]
        )
        print("✓ Technical specification created")
        save_result(result, "step5_tech_spec.json", "Step 5")
        return result
    except Exception as e:
        print(f"❌ Error in Step 5: {e}")
        raise


def print_completion_summary() -> None:
    """Print summary of all generated files."""
    print("\n🎉 Analysis Complete!")
    print("All results saved to company-goldenfood-result/ directory")
    print("Files created:")
    print("  - step1_raw_requirements.json")
    print("  - step2_user_story.json") 
    print("  - step3_finalized_user_story.json")
    print("  - step4_upn_diagram.json")
    print("  - step5_tech_spec.json")
    print("  - company_workflow_process.png (if mermaid available)")


def main():
    """Main function orchestrating the 5-step analysis process."""
    print("Starting GoldenFoods CRM Workflow Analysis...")
    
    try:
        # Step 1: Extract raw requirements
        step1_extract_requirements()
        
        # Step 2: Create user story
        result = step2_create_user_story()
        
        # Step 3: Handle clarification questions
        step3_handle_clarifications(result)
        
        # Step 4: Generate UPN diagram
        step4_generate_upn_diagram()
        
        # Step 5: Create technical specification
        step5_create_tech_spec()
        
        # Print completion summary
        print_completion_summary()
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        print("Check the error above and try again.")
        return


if __name__ == "__main__":
    main()
