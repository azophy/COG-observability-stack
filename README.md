# COG Stack: ClickHouse, OpenTelemetry, Grafana Observability Stack

## Overview

COG Stack is a powerful, self-hosted observability solution that combines:
- **ClickHouse**: High-performance columnar database for storing observability data
- **OpenTelemetry**: Vendor-neutral observability framework for data collection
- **Grafana**: Visualization and dashboarding platform

This stack provides a complete solution for:
- Log aggregation and analysis
- Infrastructure and application metrics
- Distributed tracing
- Performance monitoring
- Real-time dashboards

## Features

- **High Performance**: ClickHouse's columnar storage enables fast queries over large datasets
- **Scalable**: Each component can be scaled independently
- **Open Source**: Full stack of open-source components
- **Vendor Neutral**: OpenTelemetry provides standardized data collection
- **Modern Architecture**: Container-based deployment with Docker Compose
- **Complete Observability**: Collects logs, metrics, and traces in one place

## Prerequisites

- Docker and Docker Compose
- At least 4GB of RAM
- Linux-based system (for direct Docker log access)
- Root/sudo access (for Docker socket access)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-org/cog-stack
cd cog-stack
```

2. Start the stack:
```bash
docker-compose up -d
```

3. Access the services:
- Grafana: http://localhost:3000
- ClickHouse HTTP interface: http://localhost:8123
- OpenTelemetry Collector metrics: http://localhost:8888

## Architecture

```
┌──────────────┐    ┌──────────────┐
│  Your Apps   │    │ Docker Logs   │
└──────┬───────┘    └──────┬───────┘
       │                   │
       ▼                   ▼
┌────────────────────────────────┐
│    OpenTelemetry Collector     │
└─────────────┬─────────────────┘
              │
              ▼
┌────────────────────────────────┐
│          ClickHouse            │
└─────────────┬─────────────────┘
              │
              ▼
┌────────────────────────────────┐
│           Grafana              │
└────────────────────────────────┘
```

## Component Details

### OpenTelemetry Collector

Configured to collect:
- Container logs via Docker log files
- Container metrics via Docker API
- Application traces via OTLP protocol

Key ports:
- 4317: OTLP gRPC receiver
- 4318: OTLP HTTP receiver
- 8888: Prometheus metrics

### ClickHouse

Stores all observability data in optimized tables:
- `docker_logs`: Container log entries
- `docker_metrics`: Container performance metrics
- `traces`: Distributed tracing data

Key ports:
- 8123: HTTP interface
- 9000: Native interface

### Grafana

Provides visualization and dashboarding. Default dashboards include:
- Container Resource Usage
- Log Analytics
- Trace Explorer
- Application Performance

## Data Model

### Logs Table
```sql
CREATE TABLE docker_logs (
    timestamp DateTime64(9),
    container_id String,
    container_name String,
    log_message String,
    stream String,
    attrs Map(String, String)
) ENGINE = MergeTree()
ORDER BY (timestamp, container_id)
```

### Metrics Table
```sql
CREATE TABLE docker_metrics (
    timestamp DateTime64(9),
    container_id String,
    container_name String,
    metric_name String,
    metric_value Float64,
    metric_type String
) ENGINE = MergeTree()
ORDER BY (timestamp, container_id, metric_name)
```

### Traces Table
```sql
CREATE TABLE traces (
    timestamp DateTime64(9),
    trace_id String,
    span_id String,
    parent_span_id String,
    service_name String,
    operation_name String,
    duration_ms Float64,
    status_code String,
    status_message String,
    attributes Map(String, String)
) ENGINE = MergeTree()
ORDER BY (timestamp, trace_id, span_id)
```

## Example Queries

### Container CPU Usage
```sql
SELECT 
    timestamp,
    container_name,
    metric_value as cpu_usage
FROM docker_metrics
WHERE metric_name = 'container.cpu.usage'
ORDER BY timestamp DESC
LIMIT 100;
```

### Error Logs
```sql
SELECT 
    timestamp,
    container_name,
    log_message
FROM docker_logs
WHERE log_message ILIKE '%error%'
ORDER BY timestamp DESC
LIMIT 100;
```

### Trace Latency
```sql
SELECT 
    service_name,
    operation_name,
    avg(duration_ms) as avg_duration,
    count() as span_count
FROM traces
GROUP BY service_name, operation_name
ORDER BY avg_duration DESC;
```

## Instrumenting Applications

### Python Example
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize tracing
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Create spans
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("my_operation") as span:
    span.set_attribute("my.attribute", "value")
    # Your code here
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
