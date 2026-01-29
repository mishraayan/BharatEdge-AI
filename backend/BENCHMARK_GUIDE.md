# Benchmarking Guide

## Prerequisites
1. Ensure `backend/requirements.txt` is installed.
2. Ensure Models are placed in `backend/models/`.
3. (Optional) Index some documents via the API before running to get real retrieval stats.

## How to Run
Run the script directly from the backend directory:

```bash
cd backend
python -m src.benchmark
```

## Metrics Explained

*   **Startup Time**: Time taken to load Python modules + Load GGUF Model into RAM.
    *   *Target (8GB RAM)*: < 10 seconds.
*   **Idle RAM**: Memory usage after model load but before inference.
    *   *Target*: < 3GB.
*   **Peak RAM**: Usage during token generation.
    *   *Target*: < 4GB.
*   **Time to First Token (TTFT)**: System latency perceived by user.
    *   *Target*: < 1.5 seconds.
*   **Tokens Per Second (TPS)**: Reading speed.
    *   *Target*: > 10 tokens/sec associated with fluent reading speed.

## Storing Results
Results are automatically saved to `backend/benchmarks/benchmark_YYYYMMDD_HHMMSS.json`.
You can compare these JSON files over time to track regressions.
