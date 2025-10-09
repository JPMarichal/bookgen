#!/usr/bin/env python3
"""
Demo script for the download-output endpoint

This script demonstrates how to use the ZIP export endpoint to download
all publication files for a character.
"""
import requests
import os
from pathlib import Path


def demo_download_output(character: str, output_dir: str = "."):
    """
    Demonstrate downloading publication output as ZIP
    
    Args:
        character: Character name (normalized, e.g., 'harry_s_truman')
        output_dir: Directory to save the ZIP file
    """
    print("=" * 70)
    print("BookGen ZIP Export Endpoint Demo")
    print("=" * 70)
    print()
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"/api/v1/biographies/{character}/download-output"
    url = f"{base_url}{endpoint}"
    
    print(f"Character: {character}")
    print(f"Endpoint: {endpoint}")
    print(f"Full URL: {url}")
    print()
    
    # Make request
    print("Requesting ZIP download...")
    try:
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            # Get filename from Content-Disposition header
            content_disposition = response.headers.get('content-disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = f"{character}_publicacion.zip"
            
            # Save file
            output_path = Path(output_dir) / filename
            
            print(f"✓ Download successful!")
            print(f"  Status Code: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            print(f"  Content-Length: {response.headers.get('content-length')} bytes")
            print(f"  Filename: {filename}")
            print()
            
            # Save to file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(output_path)
            print(f"✓ File saved to: {output_path}")
            print(f"  Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
            print()
            
            # List ZIP contents
            import zipfile
            print("ZIP Contents:")
            with zipfile.ZipFile(output_path, 'r') as zipf:
                for name in sorted(zipf.namelist()):
                    info = zipf.getinfo(name)
                    print(f"  - {name} ({info.file_size:,} bytes)")
            
            print()
            print("=" * 70)
            print("Demo completed successfully!")
            print("=" * 70)
            
        elif response.status_code == 404:
            print(f"✗ Character not found or no output files available")
            print(f"  Status Code: {response.status_code}")
            print(f"  Error: {response.json()}")
            
        elif response.status_code == 400:
            print(f"✗ Invalid character name")
            print(f"  Status Code: {response.status_code}")
            print(f"  Error: {response.json()}")
            
        else:
            print(f"✗ Unexpected error")
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection error: Could not connect to {base_url}")
        print("  Make sure the BookGen API server is running.")
        print("  Start it with: python -m src.main")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Main demo function"""
    import sys
    
    if len(sys.argv) > 1:
        character = sys.argv[1]
    else:
        character = "test_character"
    
    output_dir = "."
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    demo_download_output(character, output_dir)


if __name__ == "__main__":
    main()
