"""
Test script for LlamaIndex workflow
Demonstrates how to use the new workflow
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow.invoice_workflow import create_workflow


async def test_workflow():
    """Test the LlamaIndex workflow with sample data"""
    
    # Create workflow instance
    workflow = create_workflow()
    
    # Test with sample file (if exists)
    test_file_path = "./data/input/clean invoice sample.pdf"
    test_file_name = "clean invoice sample.pdf"
    
    if not os.path.exists(test_file_path):
        print(f"Test file not found: {test_file_path}")
        print("Please add a PDF file to ./data/input/ to test the workflow")
        return
    
    print(f"Testing workflow with file: {test_file_name}")
    
    try:
        # Run the workflow
        handler = workflow.run(
            file_path=test_file_path,
            file_name=test_file_name
        )
        
        # Wait for completion
        result = await handler
        
        print("Workflow completed successfully!")
        print(f"Similarity: {result['similarity']:.2f}")
        print(f"Report length: {len(result.get('report', ''))}")
        print(f"Result length: {len(result.get('result', ''))}")
        
    except Exception as e:
        print(f"Error running workflow: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function"""
    print("LlamaIndex Workflow Test")
    print("=" * 30)
    
    await test_workflow()


if __name__ == "__main__":
    asyncio.run(main())
