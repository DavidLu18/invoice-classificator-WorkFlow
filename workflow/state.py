from pydantic import BaseModel, Field
from typing import Optional


class WorkflowState(BaseModel):
    """State model for the invoice classification workflow"""
    model_config = {"arbitrary_types_allowed": True}
    
    file_path: str = Field(default="")
    file_name: str = Field(default="")
    ocr1_result: str = Field(default="")
    ocr2_result: str = Field(default="")
    similarity: float = Field(default=0.0)
    result: str = Field(default="")
    report: str = Field(default="")
