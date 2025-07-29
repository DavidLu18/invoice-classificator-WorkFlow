import asyncio
import logging
import threading
import gc
from typing import Any, Dict

from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

from .events import (
    StartProcessingEvent,
    OCR1CompletedEvent,
    OCR2CompletedEvent,
    ComparisonCompletedEvent,
    ClassificationCompletedEvent,
)
from .state import WorkflowState

# Import existing agents
from agents.pdf_parser_agent1 import PDFParserAgent1
from agents.pdf_parser_agent2 import PDFParserAgent2
from agents.comparison_agent import ComparisonAgent
from agents.classification_agent import ClassificationAgent


class InvoiceClassificationWorkflow(Workflow):
    """
    LlamaIndex Workflow for Invoice Classification
    
    Workflow:
    1. StartEvent -> OCR1 & OCR2 (parallel)
    2. Wait for both OCR results -> Comparison
    3. Comparison -> Classification
    4. Classification -> StopEvent
    """

    @step
    async def start_processing(
        self, ctx: Context[WorkflowState], ev: StartEvent
    ) -> StartProcessingEvent:
        """Entry point - starts the PDF processing workflow"""
        
        # Initialize state
        async with ctx.store.edit_state() as state:
            state.file_path = ev.file_path
            state.file_name = ev.file_name
        
        logging.info(f"Starting invoice processing for: {ev.file_name}")
        
        # Emit start processing event to trigger OCR steps
        return StartProcessingEvent(
            file_path=ev.file_path,
            file_name=ev.file_name
        )

    @step
    async def ocr_parser_1(
        self, ctx: Context[WorkflowState], ev: StartProcessingEvent
    ) -> OCR1CompletedEvent:
        """OCR Parser 1 - EasyOCR processing"""
        
        task_thread_id = threading.get_ident()
        logging.info(f"Starting OCR1 (EasyOCR) task on file {ev.file_name}, Thread ID: {task_thread_id}")
        
        try:
            # Initialize the PDF parser agent
            agent = PDFParserAgent1()
            
            # Run the agent to parse the invoice
            result = await asyncio.get_event_loop().run_in_executor(
                None, agent.parse_invoice, ev.file_path, ev.file_name
            )
            
            # Update state
            async with ctx.store.edit_state() as state:
                state.ocr1_result = result
            
            logging.info(f"Finished OCR1 task on file {ev.file_name}, Thread ID: {task_thread_id}")
            
            return OCR1CompletedEvent(ocr1_result=result)
            
        finally:
            # Cleanup after task completion
            del agent
            gc.collect()

    @step
    async def ocr_parser_2(
        self, ctx: Context[WorkflowState], ev: StartProcessingEvent
    ) -> OCR2CompletedEvent:
        """OCR Parser 2 - Tesseract processing"""
        
        task_thread_id = threading.get_ident()
        logging.info(f"Starting OCR2 (Tesseract) task on file {ev.file_name}, Thread ID: {task_thread_id}")
        
        try:
            # Initialize the PDF parser agent
            agent = PDFParserAgent2()
            
            # Run the agent to parse the invoice
            result = await asyncio.get_event_loop().run_in_executor(
                None, agent.parse_invoice, ev.file_path, ev.file_name
            )
            
            # Update state
            async with ctx.store.edit_state() as state:
                state.ocr2_result = result
            
            logging.info(f"Finished OCR2 task on file {ev.file_name}, Thread ID: {task_thread_id}")
            
            return OCR2CompletedEvent(ocr2_result=result)
            
        finally:
            # Cleanup after task completion
            del agent
            gc.collect()

    @step
    async def compare_results(
        self, ctx: Context[WorkflowState], ev: OCR1CompletedEvent | OCR2CompletedEvent
    ) -> ComparisonCompletedEvent | None:
        """Compare OCR results - waits for both OCR1 and OCR2 to complete"""
        
        # Wait for both OCR events to arrive
        data = ctx.collect_events(ev, [OCR1CompletedEvent, OCR2CompletedEvent])
        if data is None:
            return None  # Wait for more events
        
        # Unpack the results in order
        ocr1_event, ocr2_event = data
        
        # Get current state
        file_name = await ctx.store.get("file_name")
        
        task_thread_id = threading.get_ident()
        logging.info(f"Starting comparison task on file {file_name}, Thread ID: {task_thread_id}")
        
        try:
            # Create the agent instance
            agent = ComparisonAgent()
            
            # Perform the comparison
            comparison = await asyncio.get_event_loop().run_in_executor(
                None, 
                agent.compare_results,
                file_name,
                ocr1_event.ocr1_result,
                ocr2_event.ocr2_result
            )
            
            # Update state
            async with ctx.store.edit_state() as state:
                state.result = comparison['content']
                state.similarity = comparison['similarity']
            
            logging.info(f"Finished comparison task on file {file_name}, Thread ID: {task_thread_id}")
            
            return ComparisonCompletedEvent(
                result=comparison['content'],
                similarity=comparison['similarity']
            )
            
        finally:
            # Ensure agent is deleted and garbage collection is triggered
            del agent
            gc.collect()

    @step
    async def classify_results(
        self, ctx: Context[WorkflowState], ev: ComparisonCompletedEvent
    ) -> ClassificationCompletedEvent:
        """Classify the comparison results"""
        
        # Get current state
        file_path = await ctx.store.get("file_path")
        file_name = await ctx.store.get("file_name")
        
        task_thread_id = threading.get_ident()
        logging.info(f"Starting classification task on file {file_name}, Thread ID: {task_thread_id}")
        
        try:
            # Create the agent instance
            agent = ClassificationAgent()
            
            # Perform the classification
            report = await asyncio.get_event_loop().run_in_executor(
                None,
                agent.classify_files,
                file_path,
                file_name,
                ev.result,
                ev.similarity
            )
            
            # Update state
            async with ctx.store.edit_state() as state:
                state.report = report
            
            logging.info(f"Finished classification task on file {file_name}, Thread ID: {task_thread_id}")
            
            return ClassificationCompletedEvent(report=report)
            
        finally:
            # Ensure agent is deleted and garbage collection is triggered
            del agent
            gc.collect()

    @step
    async def finalize_processing(
        self, ctx: Context[WorkflowState], ev: ClassificationCompletedEvent
    ) -> StopEvent:
        """Final step - return the results"""
        
        # Get final state
        similarity = await ctx.store.get("similarity")
        report = await ctx.store.get("report")
        result = await ctx.store.get("result")
        
        # Return the final results
        return StopEvent(result={
            "similarity": similarity,
            "report": report,
            "result": result
        })


def create_workflow() -> InvoiceClassificationWorkflow:
    """Factory function to create the workflow instance"""
    return InvoiceClassificationWorkflow(timeout=300, verbose=True)
