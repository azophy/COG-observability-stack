from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentation
import uvicorn
import time
import random

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure OTLP exporter
otlp_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI()
FastAPIInstrumentation().instrument_app(app)

@app.get("/")
async def root():
    with tracer.start_as_current_span("process_request") as span:
        # Simulate some work
        time.sleep(random.uniform(0.1, 0.5))
        span.set_attribute("process.value", random.randint(1, 100))
        return {"message": "Hello World"}

@app.get("/chain")
async def chain():
    with tracer.start_as_current_span("parent_operation") as parent:
        # First child operation
        with tracer.start_as_current_span("child_operation_1") as child1:
            time.sleep(random.uniform(0.1, 0.3))
            child1.set_attribute("step", "first")

        # Second child operation
        with tracer.start_as_current_span("child_operation_2") as child2:
            time.sleep(random.uniform(0.2, 0.4))
            child2.set_attribute("step", "second")

        return {"message": "Chained operations completed"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
