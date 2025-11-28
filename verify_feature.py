import urllib.request
import urllib.parse
import json
import time
import uuid

API_URL = "http://localhost:8000"

def make_request(method, endpoint, data=None):
    url = f"{API_URL}{endpoint}"
    if data is not None:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 204:
                return json.loads(response.read().decode('utf-8'))
            return None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        raise

def test_auto_download_setting():
    print("--- Testing Auto Download Setting ---")
    
    # 1. Disable Auto Download
    print("Disabling Auto Download...")
    make_request("POST", "/settings", {"auto_download": False})
    
    settings = make_request("GET", "/settings")
    assert settings["AUTO_DOWNLOAD"] == "false"
    print("Auto Download disabled successfully.")

    unique_id = str(uuid.uuid4())[:8]
    query = f"Test Artist - Test Title {unique_id}"
    
    print(f"Testing manual download for: {query}")
    
    # 3. Trigger download manually
    make_request("POST", "/download", {
        "query": query,
        "artist": "Test Artist",
        "title": f"Test Title {unique_id}",
        "album": "Test Album",
        "image": ""
    })
    print("Download queued.")
    
    # 4. Wait for completion
    print("Waiting for download to complete...")
    found = False
    for _ in range(30):
        time.sleep(1)
        # Check if it appears in downloads list
        # We need to handle pagination params manually in URL if using urllib, 
        # but here we just want the list.
        # urllib.parse.urlencode can be used but let's just append ?limit=100
        response = make_request("GET", "/downloads?limit=100")
        downloads = response["items"]
        
        for item in downloads:
            if item["query"] == query:
                print(f"Found item status: {item['status']}")
                if item["status"] == "completed":
                    found = True
                    break
        if found:
            break
    
    if found:
        print("Download completed successfully.")
    else:
        print("Download timed out or failed.")
        
    # 5. Re-enable Auto Download (cleanup)
    print("Re-enabling Auto Download...")
    make_request("POST", "/settings", {"auto_download": True})
    settings = make_request("GET", "/settings")
    assert settings["AUTO_DOWNLOAD"] == "true"
    print("Auto Download re-enabled.")

if __name__ == "__main__":
    try:
        test_auto_download_setting()
        print("\nALL TESTS PASSED")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
