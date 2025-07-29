"""
Workflow visualization example
Shows how to visualize the LlamaIndex workflow
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.invoice_workflow import create_workflow


async def visualize_workflow():
    """Create and visualize the workflow"""
    
    try:
        # Install visualization utils if needed
        try:
            from llama_index.utils.workflow import (
                draw_all_possible_flows,
                draw_most_recent_execution,
            )
        except ImportError:
            print("Installing workflow visualization utils...")
            import subprocess
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "llama-index-utils-workflow"
            ])
            from llama_index.utils.workflow import (
                draw_all_possible_flows,
                draw_most_recent_execution,
            )
        
        # Create workflow
        workflow = create_workflow()
        
        # Draw all possible flows
        print("Creating workflow visualization...")
        draw_all_possible_flows(
            workflow.__class__, 
            filename="invoice_workflow_all_flows.html"
        )
        print("✅ All possible flows diagram saved to: invoice_workflow_all_flows.html")
        
        # Test with a sample execution if file exists
        test_file_path = "./data/input/clean invoice sample.pdf"
        if os.path.exists(test_file_path):
            print("Running sample execution for visualization...")
            
            handler = workflow.run(
                file_path=test_file_path,
                file_name="clean invoice sample.pdf"
            )
            
            # Wait for completion
            result = await handler
            
            # Draw the execution
            draw_most_recent_execution(
                workflow, 
                filename="invoice_workflow_recent_execution.html"
            )
            print("✅ Recent execution diagram saved to: invoice_workflow_recent_execution.html")
            print(f"Execution completed. Similarity: {result['similarity']:.2f}")
        else:
            print("⚠️  No test file found. Only all possible flows diagram was created.")
            
    except Exception as e:
        print(f"Error in visualization: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function"""
    print("LlamaIndex Workflow Visualization")
    print("=" * 40)
    
    await visualize_workflow()


if __name__ == "__main__":
    asyncio.run(main())
