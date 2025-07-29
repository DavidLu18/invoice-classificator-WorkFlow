from llama_index.core.workflow import Event


class StartProcessingEvent(Event):
    """Event to start the invoice processing workflow"""
    file_path: str
    file_name: str


class OCR1CompletedEvent(Event):
    """Event emitted when OCR1 processing is completed"""
    ocr1_result: str


class OCR2CompletedEvent(Event):
    """Event emitted when OCR2 processing is completed"""
    ocr2_result: str


class ComparisonCompletedEvent(Event):
    """Event emitted when comparison is completed"""
    result: str
    similarity: float


class ClassificationCompletedEvent(Event):
    """Event emitted when classification is completed"""
    report: str
