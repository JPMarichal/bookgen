"""
Automatic Biography Generation Examples

This module demonstrates how to use BookGen's three generation modes:
- Automatic: Fully automated source discovery
- Hybrid: Mix of user sources + automatic completion
- Manual: User provides all sources

Requirements:
    pip install requests

Usage:
    python automatic_generation_examples.py
"""

import requests
import time
import json
from typing import Dict, List, Optional


class BookGenClient:
    """Simple client for BookGen API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def generate_biography(
        self,
        character: str,
        mode: str = "automatic",
        sources: Optional[List[str]] = None,
        min_sources: int = 40,
        quality_threshold: float = 0.8,
        chapters: int = 20,
        total_words: int = 51000
    ) -> Dict:
        """
        Generate a biography
        
        Args:
            character: Name of the person
            mode: Generation mode ('automatic', 'hybrid', 'manual')
            sources: User-provided sources (for manual/hybrid)
            min_sources: Minimum sources to generate
            quality_threshold: Quality threshold (0-1)
            chapters: Number of chapters
            total_words: Target word count
            
        Returns:
            Job creation response
        """
        payload = {
            "character": character,
            "mode": mode,
            "chapters": chapters,
            "total_words": total_words,
            "quality_threshold": quality_threshold
        }
        
        if mode in ["manual", "hybrid"] and sources:
            payload["sources"] = sources
        
        if mode in ["automatic", "hybrid"]:
            payload["min_sources"] = min_sources
        
        response = requests.post(
            f"{self.api_base}/biographies/generate",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get job status"""
        response = requests.get(f"{self.api_base}/biographies/{job_id}/status")
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(
        self,
        job_id: str,
        timeout: int = 7200,
        poll_interval: int = 10
    ) -> Dict:
        """
        Wait for job to complete
        
        Args:
            job_id: Job identifier
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between status checks
            
        Returns:
            Final job status
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)
            
            if status["status"] in ["completed", "failed"]:
                return status
            
            print(f"Status: {status['status']}", end="")
            if status.get("progress"):
                print(f" - {status['progress'].get('percentage', 0):.1f}%", end="")
            print()
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")


# Example 1: Automatic Mode - Fully Automated
def example_automatic_mode():
    """
    Example: Generate biography with fully automatic source discovery
    
    This is the simplest mode - just provide a character name!
    """
    print("=" * 60)
    print("Example 1: Automatic Mode")
    print("=" * 60)
    
    client = BookGenClient()
    
    # Create biography job with automatic source generation
    job = client.generate_biography(
        character="Marie Curie",
        mode="automatic",
        min_sources=50,
        quality_threshold=0.8,
        chapters=20,
        total_words=51000
    )
    
    print(f"✓ Job created: {job['job_id']}")
    print(f"  Character: {job['character']}")
    print(f"  Mode: {job['mode']}")
    print(f"  Sources generated: {job['source_count']}")
    print(f"  Automatic: {job['sources_generated_automatically']}")
    print(f"  Status: {job['status']}")
    
    return job['job_id']


# Example 2: Hybrid Mode - User Sources + Auto-completion
def example_hybrid_mode():
    """
    Example: Start with key sources, auto-complete the rest
    
    Perfect when you have 5-10 essential sources and want to reach 40-60 total.
    """
    print("\n" + "=" * 60)
    print("Example 2: Hybrid Mode")
    print("=" * 60)
    
    client = BookGenClient()
    
    # Provide your key sources
    my_sources = [
        "https://en.wikipedia.org/wiki/Albert_Einstein",
        "https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/",
        "https://einsteinpapers.press.princeton.edu/",
        "https://www.britannica.com/biography/Albert-Einstein"
    ]
    
    # System will auto-complete to reach min_sources
    job = client.generate_biography(
        character="Albert Einstein",
        mode="hybrid",
        sources=my_sources,
        min_sources=50,  # Will generate 46 more sources
        quality_threshold=0.8
    )
    
    print(f"✓ Job created: {job['job_id']}")
    print(f"  Character: {job['character']}")
    print(f"  Mode: {job['mode']}")
    print(f"  Total sources: {job['source_count']}")
    print(f"  User provided: {len(my_sources)}")
    print(f"  Auto-generated: {job['source_count'] - len(my_sources)}")
    
    return job['job_id']


# Example 3: Manual Mode - Complete Control
def example_manual_mode():
    """
    Example: Provide all sources manually
    
    Use when you have complete control over source selection.
    """
    print("\n" + "=" * 60)
    print("Example 3: Manual Mode")
    print("=" * 60)
    
    client = BookGenClient()
    
    # Must provide at least 10 sources
    my_sources = [
        "https://en.wikipedia.org/wiki/Isaac_Newton",
        "https://www.britannica.com/biography/Isaac-Newton",
        "https://mathshistory.st-andrews.ac.uk/Biographies/Newton/",
        "https://www.newtonproject.ox.ac.uk/",
        "https://plato.stanford.edu/entries/newton/",
        "https://royalsocietypublishing.org/newton",
        "https://www.cambridge.org/newton-biography",
        "https://archive.org/details/newton-works",
        "https://www.gutenberg.org/newton",
        "https://www.biography.com/scientist/isaac-newton",
        # Add more sources as needed
    ]
    
    job = client.generate_biography(
        character="Isaac Newton",
        mode="manual",
        sources=my_sources
    )
    
    print(f"✓ Job created: {job['job_id']}")
    print(f"  Character: {job['character']}")
    print(f"  Mode: {job['mode']}")
    print(f"  Sources: {job['source_count']}")
    print(f"  Automatic: {job.get('sources_generated_automatically', False)}")
    
    return job['job_id']


# Example 4: Monitoring Job Progress
def example_monitor_job(job_id: str):
    """
    Example: Monitor job progress and get final results
    """
    print("\n" + "=" * 60)
    print("Example 4: Monitoring Job Progress")
    print("=" * 60)
    
    client = BookGenClient()
    
    print(f"Monitoring job: {job_id}")
    print("Checking status every 10 seconds...")
    
    try:
        # Wait for completion (with timeout)
        final_status = client.wait_for_completion(job_id, timeout=7200)
        
        print(f"\n✓ Job completed!")
        print(f"  Status: {final_status['status']}")
        print(f"  Character: {final_status['character']}")
        
        if final_status.get('download_url'):
            print(f"  Download: {final_status['download_url']}")
        
        if final_status.get('error'):
            print(f"  Error: {final_status['error']}")
        
        # Show source metadata if available
        if 'source_metadata' in final_status:
            metadata = final_status['source_metadata']
            print("\n  Source Metadata:")
            
            if metadata.get('validation_summary'):
                summary = metadata['validation_summary']
                print(f"    - Valid sources: {summary.get('valid_sources', 'N/A')}")
                print(f"    - Avg relevance: {summary.get('average_relevance', 'N/A'):.2f}")
                print(f"    - Avg credibility: {summary.get('average_credibility', 'N/A'):.1f}")
        
        return final_status
        
    except TimeoutError as e:
        print(f"\n✗ {e}")
        return None


# Example 5: Batch Generation
def example_batch_generation():
    """
    Example: Generate multiple biographies with different modes
    """
    print("\n" + "=" * 60)
    print("Example 5: Batch Generation")
    print("=" * 60)
    
    client = BookGenClient()
    
    characters = [
        {"name": "Ada Lovelace", "mode": "automatic"},
        {"name": "Alan Turing", "mode": "automatic"},
        {"name": "Grace Hopper", "mode": "automatic"}
    ]
    
    jobs = []
    for char_info in characters:
        job = client.generate_biography(
            character=char_info["name"],
            mode=char_info["mode"],
            min_sources=40
        )
        jobs.append(job)
        print(f"✓ Created job for {char_info['name']}: {job['job_id']}")
        time.sleep(2)  # Small delay between requests
    
    print(f"\nTotal jobs created: {len(jobs)}")
    return jobs


# Example 6: Quality Threshold Comparison
def example_quality_thresholds():
    """
    Example: Compare different quality thresholds
    """
    print("\n" + "=" * 60)
    print("Example 6: Quality Threshold Comparison")
    print("=" * 60)
    
    client = BookGenClient()
    
    thresholds = [0.7, 0.8, 0.9]
    
    for threshold in thresholds:
        job = client.generate_biography(
            character="Charles Darwin",
            mode="automatic",
            min_sources=40,
            quality_threshold=threshold,
            chapters=10,  # Smaller for testing
            total_words=25000
        )
        
        print(f"\nQuality Threshold: {threshold}")
        print(f"  Job ID: {job['job_id']}")
        print(f"  Sources: {job['source_count']}")
        
        time.sleep(1)


# Example 7: Error Handling
def example_error_handling():
    """
    Example: Proper error handling
    """
    print("\n" + "=" * 60)
    print("Example 7: Error Handling")
    print("=" * 60)
    
    client = BookGenClient()
    
    # Example: Manual mode without enough sources (should fail)
    print("\nAttempting manual mode with insufficient sources...")
    try:
        job = client.generate_biography(
            character="Test Subject",
            mode="manual",
            sources=["https://example.com"]  # Only 1 source, need 10+
        )
        print(f"✓ Job created: {job['job_id']}")
    except requests.exceptions.HTTPError as e:
        print(f"✗ Expected error: {e.response.status_code}")
        print(f"  Detail: {e.response.json().get('detail', 'Unknown error')}")
    
    # Example: Invalid mode (should fail)
    print("\nAttempting invalid mode...")
    try:
        response = requests.post(
            f"{client.api_base}/biographies/generate",
            json={
                "character": "Test Subject",
                "mode": "invalid_mode"  # Invalid
            }
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"✗ Expected error: {e.response.status_code}")


# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BookGen Automatic Generation Examples")
    print("=" * 60)
    
    try:
        # Run examples
        job_id_1 = example_automatic_mode()
        job_id_2 = example_hybrid_mode()
        job_id_3 = example_manual_mode()
        
        # Monitor one of the jobs
        example_monitor_job(job_id_1)
        
        # Additional examples
        example_batch_generation()
        example_quality_thresholds()
        example_error_handling()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to BookGen API")
        print("  Make sure the API is running at http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
