import os
import logging
from llama_cpp import Llama
from typing import Generator, List, Optional
from src.config import (
    LLM_MODEL_PATH, 
    LLM_CONTEXT_WINDOW, 
    CPU_THREADS, 
    LLM_TEMPERATURE, 
    LLM_MAX_TOKENS,
    N_GPU_LAYERS,
    MAX_CONTEXT_WINDOW
)

logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self):
        self.llm = None
        self.load_model()

    def load_model(self):
        """
        Load the GGUF model with CPU optimization.
        """
        if not os.path.exists(LLM_MODEL_PATH):
            logger.error(f"Model not found at {LLM_MODEL_PATH}. Prediction will fail.")
            return

        logger.info(f"Loading LLM from {LLM_MODEL_PATH}...")
        try:
            # CPU-focused loading
            self.llm = Llama(
                model_path=LLM_MODEL_PATH,
                n_ctx=MAX_CONTEXT_WINDOW,
                n_threads=CPU_THREADS,
                n_batch=1024,      # Increased from 512 for faster prompt processing
                n_gpu_layers=N_GPU_LAYERS, # Use GPU if configured
                verbose=False
            )
            logger.info("LLM Loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")

    def generate_response(self, prompt: str, stop: list = ["<|im_end|>", "<|im_start|>", "User:", "<|user|>"]) -> Generator[str, None, None]:
        """
        Stream response from LLM with strict parameters.
        """
        if not self.llm:
            yield "Error: Model not loaded."
            return

        # Estimate prompt tokens to ensure we don't exceed context
        prompt_tokens = len(self.llm.tokenize(prompt.encode('utf-8')))
        available_tokens = LLM_CONTEXT_WINDOW - prompt_tokens
        
        if available_tokens < 100:
            logger.warning("Context limit near! Truncating response potential.")
            # In a real system, we'd truncate the prompt history here.

        stream = self.llm.create_completion(
            prompt=prompt,
            max_tokens=min(LLM_MAX_TOKENS, available_tokens),
            stop=stop,
            stream=True,
            temperature=LLM_TEMPERATURE,
            top_p=0.9,          # Nucleus sampling
            repeat_penalty=1.2, # Increased from 1.1 to prevent looping
            echo=False
        )

        import time
        start_time = time.time()
        token_count = 0

        for output in stream:
            token = output['choices'][0]['text']
            token_count += 1
            yield token
            
        duration = time.time() - start_time
        tps = token_count / duration if duration > 0 else 0
        logger.info(f"Generation Statistics: {token_count} tokens in {duration:.2f}s ({tps:.2f} t/s)")
        
        # Final yield to convey performance metadata
        yield {"type": "meta", "tps": round(tps, 2), "duration": round(duration, 2)}
