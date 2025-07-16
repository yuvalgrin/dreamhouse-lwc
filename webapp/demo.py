#!/usr/bin/env python3
"""
Demo script for testing the workflow analysis functionality.
This script demonstrates the complete workflow without the web interface.
"""

import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the model
sys.path.append(str(Path(__file__).parent.parent))

from model.main import (
    run_prompt, 
    convert_upn_to_png, 
    prompt1, 
    prompt2, 
    prompt3, 
    prompt4, 
    prompt5
)

def demo_workflow_analysis():
    """Demonstrate the complete workflow analysis process."""
    
    print("🎯 Workflow Analysis Demo")
    print("=" * 50)
    
    # Sample user input
    user_input = """
    When a sales representative creates a new opportunity with an amount greater than $100,000, 
    the system should automatically send an email notification to the regional sales manager 
    and create an approval record. The approval record should include the opportunity details 
    and require the manager to either approve or reject the opportunity within 48 hours. 
    If approved, the opportunity status should be updated to "Approved" and a confirmation 
    email should be sent to the sales representative. If rejected, the opportunity status 
    should be updated to "Rejected" and a notification should be sent to the sales representative 
    with the rejection reason.
    """
    
    print(f"📝 User Input:\n{user_input.strip()}\n")
    
    try:
        # Step 1: Extract raw requirements
        print("🔍 Step 1: Extracting Raw Requirements...")
        step1_result = run_prompt(
            prompt1,
            context_files=[Path("test-data/company_reqs_examples.json")]
        )
        print("✅ Step 1 completed\n")
        
        # Step 2: Create user story
        print("📖 Step 2: Creating User Story...")
        step2_result = run_prompt(
            prompt2,
            context_files=[
                Path("context-data/user_story_q.json"),
                Path("test-data/company_reqs_examples.json")
            ]
        )
        print("✅ Step 2 completed\n")
        
        # Parse step 2 result
        step2_data = json.loads(step2_result)
        user_story = step2_data.get('user_story', {})
        questions = step2_data.get('questions_for_user', [])
        
        print("📋 Generated User Story:")
        print(json.dumps(user_story, indent=2))
        print()
        
        if questions:
            print("❓ Clarification Questions:")
            for i, question in enumerate(questions, 1):
                print(f"  {i}. {question}")
            print()
            
            # Simulate user answers
            print("💬 Simulating User Answers...")
            sample_answers = [
                "The process is triggered when an opportunity is created or updated with amount > $100k",
                "The regional sales manager is responsible for approval decisions",
                "The approval record should include opportunity ID, amount, sales rep info, and creation date",
                "If no response within 48 hours, send reminder email to manager and escalate to director"
            ]
            
            # Process answers
            current_result = step2_result
            for i, (question, answer) in enumerate(zip(questions, sample_answers)):
                print(f"  Q{i+1}: {question}")
                print(f"  A{i+1}: {answer}")
                
                prompt3_with_answer = f'{prompt3}\n\nQuestion: {question}\n\nUser answer: {answer}'
                current_result = run_prompt(
                    prompt3_with_answer,
                    context_files=[
                        Path("context-data/user_story_q.json"),
                        Path("test-data/company_reqs_examples.json")
                    ]
                )
            
            # Parse final result
            final_data = json.loads(current_result)
            user_story = final_data.get('user_story', {})
            remaining_questions = final_data.get('questions_for_user', [])
            
            if remaining_questions:
                print(f"\n⚠️  Still have {len(remaining_questions)} questions remaining")
            else:
                print("\n✅ All questions answered!")
        
        # Step 4: Generate UPN diagram
        print("\n🎨 Step 4: Generating UPN Diagram...")
        step4_result = run_prompt(
            prompt4,
            context_files=[
                Path("context-data/process_diagrams.json"),
                Path("context-data/saleforce_flow_caps.json"),
                Path("test-data/company_reqs_examples.json")
            ]
        )
        
        step4_data = json.loads(step4_result)
        upn_diagram = step4_data.get('upn_diagram', '')
        
        print("📊 Generated UPN Diagram:")
        print(upn_diagram)
        print()
        
        # Try to convert to PNG
        try:
            print("🖼️  Converting to PNG...")
            png_file = convert_upn_to_png(upn_diagram)
            print(f"✅ PNG created: {png_file}")
        except Exception as e:
            print(f"⚠️  PNG conversion failed: {e}")
        
        # Step 5: Generate technical specification
        print("\n⚙️  Step 5: Creating Technical Specification...")
        step5_result = run_prompt(
            prompt5,
            context_files=[
                Path("context-data/saleforce_flow_caps.json"),
                Path("test-data/company_reqs_examples.json")
            ]
        )
        
        tech_spec = json.loads(step5_result)
        print("🔧 Technical Specification:")
        print(json.dumps(tech_spec, indent=2))
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_workflow_analysis() 