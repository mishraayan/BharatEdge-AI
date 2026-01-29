from typing import List, Generator
from src.vector_db import VectorDBClient
from src.llm_engine import LLMEngine
from src.models import DocumentChunk
from src.config import TOP_K_RETRIEVAL, MAX_RETRIEVAL_TOKENS
import logging

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.vector_db = VectorDBClient()
        self.llm_engine = LLMEngine()

    def retrieve_context(self, query: str, sources: List[str] = None) -> List[DocumentChunk]:
        """
        Retrieve and rank snippets, enforcing context window budget.
        """
        # 1. Fetch raw top-k from VectorDB
        raw_chunks = self.vector_db.search(query, k=TOP_K_RETRIEVAL, sources=sources)
        
        if not raw_chunks:
            return []

        # 2. Re-ranking (optional) - For now, trust cosine similarity from Chroma
        # 3. Budget enforcement
        selected_chunks = []
        current_tokens = 0
        # Estimation: 1 char ~= 0.25 - 0.3 tokens. Let's be conservative: 1 token = 3 chars.
        
        for chunk in raw_chunks:
            # Estimate token count (naive) or use tiktoken if needed (avoid dependency if simple)
            est_tokens = len(chunk.text) / 3.0
            
            if current_tokens + est_tokens > MAX_RETRIEVAL_TOKENS:
                # If adding this chunk exceeds budget, stop adding (or try next smaller one)
                # Simple greedy approach: just stop to fit what matches best.
                continue
                
            selected_chunks.append(chunk)
            current_tokens += est_tokens
            
        logger.info(f"Selected {len(selected_chunks)} chunks (~{int(current_tokens)} tokens) for context.")
        return selected_chunks

    def build_prompt(self, query: str, context_chunks: List[DocumentChunk], history: List[dict] = [], sources: List[str] = None) -> str:
        """
        Constructs the strict RAG prompt.
        """
        # Format Context with Citations
        context_str = ""
        if not context_chunks:
            if sources:
                context_str = f"WARNING: No text content found for the selected files: {', '.join(sources)}. This might happen if the files are scanned and OCR failed, or if they are empty."
            else:
                context_str = "No relevant context found in any indexed documents."
        else:
            for i, chunk in enumerate(context_chunks):
                citation_ref = f"[{i+1}] Source: {chunk.source} (Page {chunk.page})"
                context_str += f"{citation_ref}\n{chunk.text}\n\n"

        # System Prompt
        system_prompt = (
            "You are BharatEdge, a helpful offline AI assistant constructed for Indian users.\n"
            "1. GROUNDING: Use ONLY the provided context. If the context is empty or labeled WARNING, explain that you have no data to answer from.\n"
            "2. CITATIONS: Use [doc_id] for every fact mentioned. You MUST use the provided context.\n"
            "3. LANGUAGE: Answer in the EXACT same language as the user. If the question is in Bengali (বাংলা), you MUST answer in Bengali.\n"
            "4. BEHAVIOR: Do not say 'I cannot access files' if context is provided; the context IS the file content.\n"
            "5. SOURCE PICKER: If specific documents are filtered, prioritize them above all else.\n"
        )
        
        history_str = ""
        for turn in history[-1:]: 
            role = "User" if turn['role'] == 'user' else "Assistant"
            history_str += f"{role}: {turn['content']}\n"

        source_hint = f"Note: User has filtered for: {', '.join(sources)}" if sources else "Analyzing all documents."

        full_prompt = f"""<|im_start|>system
{system_prompt}

{source_hint}

Relevant Context:
{context_str}<|im_end|>
<|im_start|>user
{history_str}Question: {query}<|im_end|>
<|im_start|>assistant
"""
        return full_prompt

    def query(self, message: str, history: List[dict] = [], sources: List[str] = None) -> Generator[str, None, None]:
        """
        Main RAG pipeline execution.
        """
        # 1. Retrieve
        chunks = self.retrieve_context(message, sources=sources)
        
        if not chunks:
             logger.warning(f"No context found for {sources or 'all documents'}. Prompt will be grounded but limited.")

        # 2. Build Prompt
        prompt = self.build_prompt(message, chunks, history, sources=sources)
        
        # 3. Generate
        # 3. Generate with ChatML stop tokens
        stop_tokens = ["<|im_end|>", "<|im_start|>", "Question:", "User:"]
        for piece in self.llm_engine.generate_response(prompt, stop=stop_tokens):
            yield piece

    def validate_response(self, response_text: str, context_chunks: List[DocumentChunk]) -> dict:
        """
        Post-generation check:
        1. Does it contain refusal text?
        2. Does it cite the provided sources?
        """
        result = {
            "refusal": False,
            "cited_sources": [],
            "hallucination_warning": False
        }
        
        # 1. Refusal Check
        refusal_phrases = [
            "cannot find the answer",
            "not in the provided documents",
            "no relevant information",
            "context does not contain"
        ]
        if any(phrase in response_text.lower() for phrase in refusal_phrases):
            result["refusal"] = True
            return result
        
        # 2. Citation Check
        # Expecting [1], [2] etc.
        import re
        citation_pattern = r"\[(\d+)\]"
        found_indices = [int(x) for x in re.findall(citation_pattern, response_text)]
        
        valid_indices = [i+1 for i in range(len(context_chunks))]
        
        for idx in found_indices:
            if idx in valid_indices:
                chunk = context_chunks[idx-1]
                result["cited_sources"].append(chunk.source)
            else:
                # Cited a source ID that doesn't exist?
                result["hallucination_warning"] = True
        
        if not found_indices and not result["refusal"]:
             # Answered without refusal BUT no citations? Warning.
             result["hallucination_warning"] = True
             
        return result

    def get_citations(self, message: str, sources: List[str] = None) -> List[DocumentChunk]:
        """
        Public expose for citations. Deduplicated by (source, page).
        """
        raw_chunks = self.retrieve_context(message, sources=sources)
        
        seen = set()
        deduped = []
        for c in raw_chunks:
            key = (c.source, c.page)
            if key not in seen:
                seen.add(key)
                deduped.append(c)
        
        return deduped
