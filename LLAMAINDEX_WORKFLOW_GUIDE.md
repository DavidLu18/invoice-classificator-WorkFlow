# LlamaIndex Workflow Implementation

## Tổng quan

Dự án đã được chuyển đổi thành công từ LangGraph sang LlamaIndex Workflows. Implementation mới cung cấp:

- ✅ **Event-driven architecture** với type safety
- ✅ **Async-first design** cho better performance  
- ✅ **Pydantic state management** với validation
- ✅ **Native parallel processing** cho OCR tasks
- ✅ **Better error handling** và logging
- ✅ **Workflow visualization** capabilities

## Quick Start

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy với LlamaIndex Workflow

```bash
python app_llamaindex.py
```

### 3. Chạy với LangGraph (legacy)

```bash  
python app.py
```

## Architecture

### Workflow Flow

```
StartEvent
    ↓
StartProcessingEvent
    ↓
┌─ OCR1 (EasyOCR) ─┐
│                  │
│  OCR2 (Tesseract)│
│                  │
└─ ComparisonEvent ─┘
    ↓
ClassificationEvent
    ↓
StopEvent (Results)
```

### Key Components

#### 1. Events (`workflow/events.py`)
```python
class StartProcessingEvent(Event):
    file_path: str
    file_name: str

class OCR1CompletedEvent(Event):
    ocr1_result: str

class OCR2CompletedEvent(Event):
    ocr2_result: str
    
# ... các events khác
```

#### 2. State Management (`workflow/state.py`)
```python
class WorkflowState(BaseModel):
    file_path: str = Field(default="")
    file_name: str = Field(default="")
    ocr1_result: str = Field(default="")
    ocr2_result: str = Field(default="")
    similarity: float = Field(default=0.0)
    result: str = Field(default="")
    report: str = Field(default="")
```

#### 3. Main Workflow (`workflow/invoice_workflow.py`)
```python
class InvoiceClassificationWorkflow(Workflow):
    @step
    async def start_processing(self, ctx: Context[WorkflowState], ev: StartEvent):
        # Entry point
    
    @step
    async def ocr_parser_1(self, ctx: Context[WorkflowState], ev: StartProcessingEvent):
        # EasyOCR processing
    
    @step 
    async def ocr_parser_2(self, ctx: Context[WorkflowState], ev: StartProcessingEvent):
        # Tesseract processing
    
    @step
    async def compare_results(self, ctx: Context[WorkflowState], ev: OCR1CompletedEvent | OCR2CompletedEvent):
        # Waits for both OCR results, then compares
    
    @step
    async def classify_results(self, ctx: Context[WorkflowState], ev: ComparisonCompletedEvent):
        # Classification based on comparison
    
    @step
    async def finalize_processing(self, ctx: Context[WorkflowState], ev: ClassificationCompletedEvent):
        # Return final results
```

## Testing

### 1. Test workflow import
```bash
python -c "from workflow.invoice_workflow import create_workflow; print('Success!')"
```

### 2. Test với sample file
```bash
python test_workflow.py
```

### 3. Visualize workflow
```bash
python visualize_workflow.py
```

## Advanced Features

### 1. Workflow Visualization

```python
from llama_index.utils.workflow import draw_all_possible_flows

# Install first: pip install llama-index-utils-workflow
workflow = create_workflow()
draw_all_possible_flows(workflow.__class__, filename="workflow.html")
```

### 2. Event Streaming

```python
handler = workflow.run(file_path="sample.pdf", file_name="sample.pdf")

async for event in handler.stream_events():
    print(f"Event: {type(event).__name__}")
    
result = await handler
```

### 3. Context Management

```python
@step
async def my_step(self, ctx: Context[WorkflowState], ev: MyEvent):
    # Access state
    file_name = await ctx.store.get("file_name")
    
    # Update state
    async with ctx.store.edit_state() as state:
        state.ocr1_result = "new_result"
    
    # Send manual events
    ctx.send_event(MyCustomEvent())
```

## Comparison với LangGraph

| Feature | LangGraph | LlamaIndex Workflows |
|---------|-----------|---------------------|
| Type Safety | Basic | Full Pydantic validation |
| Async Support | Limited | Native async/await |
| Event Handling | Node-based | Event-driven |
| State Management | TypedDict | Pydantic models |
| Parallel Processing | Manual edges | Automatic event collection |
| Debugging | Basic | Built-in visualization |
| Error Handling | Manual | Built-in retry policies |

## Performance Benefits

1. **Parallel OCR Processing**: OCR1 và OCR2 chạy song song
2. **Async I/O**: Non-blocking file operations
3. **Memory Management**: Better cleanup với context managers
4. **Event Batching**: Efficient event collection và processing

## Migration Benefits

1. **Better Developer Experience**: Type hints, IDE support
2. **Easier Testing**: Isolated steps với clear interfaces  
3. **Better Observability**: Built-in instrumentation
4. **Future-proof**: Extensible event-driven architecture
5. **Production Ready**: Error handling, retries, timeouts

## Next Steps

1. **Add Retry Policies**: Configure retry cho failed OCR operations
2. **Human-in-the-loop**: Add human intervention points
3. **Workflow Checkpointing**: Save/resume workflow state
4. **Advanced Routing**: Conditional workflow paths
5. **Resource Injection**: Better dependency management

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `llama-index-core` installed
2. **Async Issues**: Always use `await` với workflow operations  
3. **State Access**: Use `ctx.store.get()` và `ctx.store.edit_state()`
4. **Event Collection**: Check event types trong `collect_events()`

### Debug Mode

```python
workflow = create_workflow()
workflow = InvoiceClassificationWorkflow(timeout=300, verbose=True)
```

### Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
```
