# System Benchmarks

Since BharatEdge AI targets low-end hardware, performance transparency is critical.

## Test Environment Template
*   **CPU**: (e.g., Intel i5-8250U)
*   **RAM**: (e.g., 8GB DDR4)
*   **OS**: Windows 10/11
*   **Model**: qwen2.5-3b-instruct-q4_k_m.gguf

## Metrics Targets vs Reality

| Metric | Target (V1) | Actual (My Machine) | Status |
| :--- | :--- | :--- | :--- |
| **Startup Time** | < 10s | 7.17s | ✅ |
| **Idle RAM** | < 3GB | 1.97 GB | ✅ |
| **Peak RAM (Gen)** | < 4GB | 4.30 GB | ⚠️ |
| **Tokens/Sec** | > 8 t/s | 12.13 t/s | ✅ |
| **Time to First Token** | < 1s | 0.60s | ✅ |
| **Retrieval Latency**| < 500ms | 0.039s | ✅ |

## How to Benchmark
Run the built-in utility:
```bash
python -m src.benchmark
```
This will generate a JSON report in `backend/benchmarks/`. Update the table above with your findings.
