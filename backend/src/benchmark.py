import time
import psutil
import os
import json
import logging
from datetime import datetime
from statistics import mean
# Import Engines (lazy load inside functions to measure startup imports if needed, 
# but for startup time we might need an external runner. 
# Here we verify internal performance).

# We will import these globally to assume "warm" start for inference bench, 
# or measure import time separately.
from src.config import BACKEND_DIR

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Benchmark")

BENCHMARK_DIR = os.path.join(BACKEND_DIR, "benchmarks")
os.makedirs(BENCHMARK_DIR, exist_ok=True)

class SystemMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def get_ram_usage_mb(self):
        """Returns RSS memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024

    def get_cpu_percent(self):
        return self.process.cpu_percent(interval=0.1)

class BenchmarkSuite:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "cpu_cores": psutil.cpu_count(logical=False),
                "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 2)
            },
            "metrics": {}
        }
        
    def benchmark_startup(self):
        """
        Measure time to initialize the RAG and LLM engines.
        """
        logger.info("Running Startup Benchmark...")
        start_mem = self.monitor.get_ram_usage_mb()
        start_time = time.time()
        
        # Lazy import to measure initialization time
        from src.rag_engine import RAGEngine
        rag_engine = RAGEngine()
        
        end_time = time.time()
        end_mem = self.monitor.get_ram_usage_mb()
        
        self.results["metrics"]["startup"] = {
            "time_seconds": round(end_time - start_time, 4),
            "ram_increase_mb": round(end_mem - start_mem, 2),
            "final_ram_mb": round(end_mem, 2)
        }
        return rag_engine

    def benchmark_retrieval(self, rag_engine, queries: list):
        """
        Measure latency of vector search.
        """
        logger.info("Running Retrieval Benchmark...")
        latencies = []
        
        for q in queries:
            start = time.time()
            rag_engine.retrieve_context(q)
            latencies.append(time.time() - start)
            
        self.results["metrics"]["retrieval"] = {
            "avg_latency_seconds": round(mean(latencies), 4),
            "min_latency": round(min(latencies), 4),
            "max_latency": round(max(latencies), 4),
            "queries_run": len(queries)
        }

    def benchmark_inference(self, rag_engine, prompt: str):
        """
        Measure Tokens/Sec and Peak RAM.
        """
        logger.info("Running Inference Benchmark...")
        
        # Generator
        start_time = time.time()
        token_count = 0
        peak_ram = self.monitor.get_ram_usage_mb()
        
        # We manually call generate_response from internal LLM engine
        stream = rag_engine.llm_engine.generate_response(prompt)
        
        first_token_time = None
        
        for _ in stream:
            if not first_token_time:
                first_token_time = time.time()
            token_count += 1
            current_ram = self.monitor.get_ram_usage_mb()
            if current_ram > peak_ram:
                peak_ram = current_ram
                
        end_time = time.time()
        total_time = end_time - start_time
        generation_time = end_time - (first_token_time or start_time)
        
        tps = token_count / generation_time if generation_time > 0 else 0
        
        self.results["metrics"]["inference"] = {
            "tokens_per_sec": round(tps, 2),
            "total_tokens": token_count,
            "time_to_first_token": round((first_token_time or end_time) - start_time, 4),
            "peak_ram_mb": round(peak_ram, 2)
        }

    def save_results(self):
        filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(BENCHMARK_DIR, filename)
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Results saved to {path}")

if __name__ == "__main__":
    # Ensure models are present before running!
    print("Starting Benchmark Suite for BharatEdge AI...")
    suite = BenchmarkSuite()
    
    # 1. Startup
    engine = suite.benchmark_startup()
    
    # 2. Retrieval (Needs data indexed ideally, but will run empty/light if not)
    # Helper: Index a dummy doc if needed, or assume user has data.
    # We will use generic queries.
    queries = ["What is the summary?", "financial report 2024", "project deadlines"]
    suite.benchmark_retrieval(engine, queries)
    
    # 3. Inference
    dummy_prompt = "User: Write a poem about a futuristic India.\nAssistant:"
    suite.benchmark_inference(engine, dummy_prompt)
    
    # 4. Save
    suite.save_results()
