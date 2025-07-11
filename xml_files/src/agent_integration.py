#!/usr/bin/env python3
"""
LLM Agent Integration for XML Processing

This module provides integration with various LLM providers for XML document analysis.
It includes:

1. Multi-provider LLM integration (OpenAI, Anthropic, local models)
2. Intelligent prompt routing and optimization
3. Result aggregation and synthesis
4. Error handling and retry logic
5. Cost optimization strategies

Usage:
    agent = XMLLLMAgent(provider='openai', model='gpt-4')
    result = agent.process_document('/path/to/file.xml')
"""

import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import pickle
from pathlib import Path

# Import our XML framework
from xml_framework import XMLAgentFramework, DocumentSchema, DocumentChunk

@dataclass
class LLMResponse:
    """Response from LLM processing"""
    prompt_id: str
    content: str
    tokens_used: int
    cost_estimate: float
    processing_time: float
    metadata: Dict[str, Any]

@dataclass
class ProcessingResult:
    """Final processing result"""
    document_path: str
    document_type: str
    schema_analysis: str
    chunk_results: List[Dict[str, Any]]
    extracted_data: Dict[str, Any]
    processing_summary: Dict[str, Any]
    total_cost: float
    total_time: float

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"

class XMLLLMAgent:
    """Main agent class for XML document processing with LLMs"""
    
    def __init__(self, 
                 provider: str = "openai",
                 model: str = "gpt-4",
                 api_key: Optional[str] = None,
                 max_parallel: int = 3,
                 cache_enabled: bool = True,
                 cost_limit: float = 10.0):
        
        self.provider = LLMProvider(provider)
        self.model = model
        self.api_key = api_key
        self.max_parallel = max_parallel
        self.cache_enabled = cache_enabled
        self.cost_limit = cost_limit
        
        self.xml_framework = XMLAgentFramework()
        self.cache_dir = Path(".xml_agent_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM client
        self._init_llm_client()
        
        # Cost tracking
        self.total_cost = 0.0
        self.processing_stats = {
            'prompts_sent': 0,
            'tokens_used': 0,
            'cache_hits': 0,
            'errors': 0
        }
    
    def _init_llm_client(self):
        """Initialize the appropriate LLM client"""
        try:
            if self.provider == LLMProvider.OPENAI:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                
            elif self.provider == LLMProvider.ANTHROPIC:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                
            elif self.provider == LLMProvider.LOCAL:
                # For local models (e.g., via Ollama)
                import requests
                self.client = requests.Session()
                self.base_url = "http://localhost:11434"  # Default Ollama URL
                
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
            self.logger.info(f"Initialized {self.provider.value} client with model {self.model}")
            
        except ImportError as e:
            self.logger.error(f"Failed to import {self.provider.value} client: {e}")
            raise
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key for prompt"""
        return hashlib.md5(f"{self.provider.value}:{self.model}:{prompt}".encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[LLMResponse]:
        """Retrieve cached response if available"""
        if not self.cache_enabled:
            return None
            
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    response = pickle.load(f)
                self.processing_stats['cache_hits'] += 1
                self.logger.debug(f"Cache hit for {cache_key}")
                return response
            except Exception as e:
                self.logger.warning(f"Failed to load cache {cache_key}: {e}")
        
        return None
    
    def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache LLM response"""
        if not self.cache_enabled:
            return
            
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(response, f)
            self.logger.debug(f"Cached response for {cache_key}")
        except Exception as e:
            self.logger.warning(f"Failed to cache response {cache_key}: {e}")
    
    def _estimate_cost(self, prompt: str, response: str) -> float:
        """Estimate cost based on token usage"""
        # Rough token estimation (actual costs vary by provider)
        input_tokens = len(prompt) // 4  # Rough approximation
        output_tokens = len(response) // 4
        
        cost_per_1k_tokens = {
            LLMProvider.OPENAI: {'input': 0.03, 'output': 0.06},  # GPT-4 pricing
            LLMProvider.ANTHROPIC: {'input': 0.015, 'output': 0.075},  # Claude pricing
            LLMProvider.LOCAL: {'input': 0.0, 'output': 0.0},  # Local is free
            LLMProvider.AZURE: {'input': 0.03, 'output': 0.06}  # Similar to OpenAI
        }
        
        rates = cost_per_1k_tokens.get(self.provider, {'input': 0.02, 'output': 0.04})
        
        cost = (input_tokens / 1000 * rates['input'] + 
                output_tokens / 1000 * rates['output'])
        
        return cost
    
    async def _call_llm(self, prompt: str, prompt_id: str) -> LLMResponse:
        """Call LLM with prompt and return response"""
        
        # Check cache first
        cache_key = self._get_cache_key(prompt)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Check cost limit
        if self.total_cost >= self.cost_limit:
            raise RuntimeError(f"Cost limit exceeded: ${self.total_cost:.2f}")
        
        start_time = time.time()
        
        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000,
                    temperature=0.1
                )
                content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
                
            elif self.provider == LLMProvider.LOCAL:
                # Ollama API call
                response = self.client.post(f"{self.base_url}/api/generate", json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                })
                response.raise_for_status()
                content = response.json()["response"]
                tokens_used = len(prompt) // 4 + len(content) // 4  # Estimate
                
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            processing_time = time.time() - start_time
            cost_estimate = self._estimate_cost(prompt, content)
            
            llm_response = LLMResponse(
                prompt_id=prompt_id,
                content=content,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                processing_time=processing_time,
                metadata={"provider": self.provider.value, "model": self.model}
            )
            
            # Update stats
            self.processing_stats['prompts_sent'] += 1
            self.processing_stats['tokens_used'] += tokens_used
            self.total_cost += cost_estimate
            
            # Cache response
            self._cache_response(cache_key, llm_response)
            
            self.logger.info(f"LLM call completed: {prompt_id}, "
                           f"tokens: {tokens_used}, cost: ${cost_estimate:.4f}")
            
            return llm_response
            
        except Exception as e:
            self.processing_stats['errors'] += 1
            self.logger.error(f"LLM call failed for {prompt_id}: {e}")
            raise
    
    def _extract_structured_data(self, schema_response: str, chunk_responses: List[LLMResponse]) -> Dict[str, Any]:
        """Extract and structure data from LLM responses"""
        
        extracted_data = {
            'document_summary': {},
            'security_findings': [],
            'compliance_data': [],
            'configuration_items': [],
            'relationships': [],
            'metadata': {}
        }
        
        # Parse schema analysis
        try:
            # Look for structured sections in schema response
            lines = schema_response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('1.') or 'primary purpose' in line.lower():
                    current_section = 'purpose'
                elif line.startswith('2.') or 'key data entities' in line.lower():
                    current_section = 'entities'
                elif line.startswith('3.') or 'processing patterns' in line.lower():
                    current_section = 'patterns'
                elif line.startswith('4.') or 'critical elements' in line.lower():
                    current_section = 'critical_elements'
                elif line.startswith('5.') or 'compliance' in line.lower():
                    current_section = 'compliance'
                
                if current_section and line and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    if current_section not in extracted_data['document_summary']:
                        extracted_data['document_summary'][current_section] = []
                    extracted_data['document_summary'][current_section].append(line)
        
        except Exception as e:
            self.logger.warning(f"Failed to parse schema response: {e}")
        
        # Parse chunk responses
        for response in chunk_responses:
            try:
                content = response.content
                
                # Look for structured data patterns
                if 'rule' in content.lower() or 'check' in content.lower():
                    # Security/compliance finding
                    finding = {
                        'chunk_id': response.prompt_id,
                        'content': content[:500],  # Truncate for summary
                        'type': 'security_check'
                    }
                    extracted_data['security_findings'].append(finding)
                
                elif 'configuration' in content.lower() or 'setting' in content.lower():
                    # Configuration item
                    config = {
                        'chunk_id': response.prompt_id,
                        'content': content[:500],
                        'type': 'configuration'
                    }
                    extracted_data['configuration_items'].append(config)
                
                # Extract key-value pairs (simple pattern matching)
                kv_pattern = r'(\w+):\s*([^\n]+)'
                import re
                matches = re.findall(kv_pattern, content)
                for key, value in matches[:5]:  # Limit to avoid noise
                    extracted_data['metadata'][key] = value
                    
            except Exception as e:
                self.logger.warning(f"Failed to parse chunk response {response.prompt_id}: {e}")
        
        return extracted_data
    
    async def process_document(self, file_path: str) -> ProcessingResult:
        """Process XML document with LLM analysis"""
        
        self.logger.info(f"Starting document processing: {file_path}")
        start_time = time.time()
        
        try:
            # Step 1: Analyze document structure
            self.logger.info("Analyzing document structure...")
            schema = self.xml_framework.analyze_document(file_path)
            
            # Step 2: Create chunks
            self.logger.info("Creating document chunks...")
            chunks = self.xml_framework.chunk_document(file_path, schema)
            
            # Step 3: Generate prompts
            self.logger.info("Generating LLM prompts...")
            prompts = self.xml_framework.generate_llm_prompts(schema, chunks, file_path)
            
            # Step 4: Process schema analysis with LLM
            self.logger.info("Sending schema analysis to LLM...")
            schema_response = await self._call_llm(
                prompts['schema_analysis'], 
                'schema_analysis'
            )
            
            # Step 5: Process chunks in parallel (with concurrency limit)
            self.logger.info(f"Processing {len(chunks)} chunks with LLM...")
            chunk_prompts = [(k, v) for k, v in prompts.items() if k.startswith('chunk_')]
            
            # Limit concurrent requests
            chunk_responses = []
            chunk_semaphore = asyncio.Semaphore(self.max_parallel)
            
            async def process_chunk(prompt_id, prompt_content):
                async with chunk_semaphore:
                    return await self._call_llm(prompt_content, prompt_id)
            
            # Process chunks concurrently
            tasks = [process_chunk(prompt_id, prompt) for prompt_id, prompt in chunk_prompts]
            chunk_responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_responses = [r for r in chunk_responses if isinstance(r, LLMResponse)]
            
            # Step 6: Extract structured data
            self.logger.info("Extracting structured data...")
            extracted_data = self._extract_structured_data(
                schema_response.content, 
                valid_responses
            )
            
            # Step 7: Create processing summary
            processing_time = time.time() - start_time
            
            chunk_results = []
            for response in valid_responses:
                chunk_results.append({
                    'chunk_id': response.prompt_id,
                    'processing_time': response.processing_time,
                    'tokens_used': response.tokens_used,
                    'cost': response.cost_estimate,
                    'summary': response.content[:200] + "..." if len(response.content) > 200 else response.content
                })
            
            processing_summary = {
                'total_chunks': len(chunks),
                'successful_chunks': len(valid_responses),
                'failed_chunks': len(chunks) - len(valid_responses),
                'total_tokens': sum(r.tokens_used for r in [schema_response] + valid_responses),
                'total_cost': self.total_cost,
                'processing_time': processing_time,
                'cache_hits': self.processing_stats['cache_hits'],
                'provider': self.provider.value,
                'model': self.model
            }
            
            result = ProcessingResult(
                document_path=file_path,
                document_type=schema.document_type,
                schema_analysis=schema_response.content,
                chunk_results=chunk_results,
                extracted_data=extracted_data,
                processing_summary=processing_summary,
                total_cost=self.total_cost,
                total_time=processing_time
            )
            
            self.logger.info(f"Document processing completed successfully")
            self.logger.info(f"Total cost: ${self.total_cost:.4f}, Time: {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            raise
    
    def save_results(self, result: ProcessingResult, output_path: str):
        """Save processing results to file"""
        
        output_data = {
            'document_path': result.document_path,
            'document_type': result.document_type,
            'processing_summary': result.processing_summary,
            'schema_analysis': result.schema_analysis,
            'extracted_data': result.extracted_data,
            'chunk_results': result.chunk_results
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        self.logger.info(f"Results saved to: {output_path}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        return {
            **self.processing_stats,
            'total_cost': self.total_cost,
            'provider': self.provider.value,
            'model': self.model
        }

# Helper functions for easy usage

async def analyze_xml_with_llm(file_path: str, 
                              provider: str = "openai",
                              model: str = "gpt-4",
                              api_key: Optional[str] = None,
                              output_file: Optional[str] = None) -> ProcessingResult:
    """Convenience function to analyze XML file with LLM"""
    
    agent = XMLLLMAgent(
        provider=provider,
        model=model,
        api_key=api_key,
        max_parallel=3,
        cache_enabled=True
    )
    
    result = await agent.process_document(file_path)
    
    if output_file:
        agent.save_results(result, output_file)
    
    return result

def analyze_xml_sync(file_path: str, **kwargs) -> ProcessingResult:
    """Synchronous wrapper for async analysis"""
    return asyncio.run(analyze_xml_with_llm(file_path, **kwargs))

# Example usage and testing
if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python llm_agent.py <xml_file> [provider] [model]")
        print("\nExample:")
        print("  python llm_agent.py stig-file.xml openai gpt-4")
        print("  python llm_agent.py stig-file.xml anthropic claude-3-sonnet-20240229")
        print("  python llm_agent.py stig-file.xml local llama2")
        sys.exit(1)
    
    file_path = sys.argv[1]
    provider = sys.argv[2] if len(sys.argv) > 2 else "openai"
    model = sys.argv[3] if len(sys.argv) > 3 else "gpt-4"
    
    # Get API key from environment
    api_key = None
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key and provider != "local":
        print(f"Please set the appropriate API key environment variable for {provider}")
        sys.exit(1)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        print(f"🚀 Processing {file_path} with {provider}:{model}")
        
        result = analyze_xml_sync(
            file_path=file_path,
            provider=provider,
            model=model,
            api_key=api_key,
            output_file=f"{Path(file_path).stem}_llm_analysis.json"
        )
        
        print(f"\n✅ Processing completed successfully!")
        print(f"📊 Summary:")
        print(f"   Document Type: {result.document_type}")
        print(f"   Chunks Processed: {result.processing_summary['successful_chunks']}")
        print(f"   Total Cost: ${result.total_cost:.4f}")
        print(f"   Processing Time: {result.total_time:.2f}s")
        print(f"   Tokens Used: {result.processing_summary['total_tokens']:,}")
        
        print(f"\n🎯 Key Findings:")
        if 'security_findings' in result.extracted_data:
            print(f"   Security Findings: {len(result.extracted_data['security_findings'])}")
        if 'configuration_items' in result.extracted_data:
            print(f"   Configuration Items: {len(result.extracted_data['configuration_items'])}")
        
        print(f"\n💾 Results saved to: {Path(file_path).stem}_llm_analysis.json")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        sys.exit(1)