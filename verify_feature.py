import urllib.request
import urllib.parse
import json
import time
import uuid
import sqlite3
import os

API_URL = "http://localhost:8000"
DB_PATH = os.path.join("backend", "data", "downloads.db")

def insert_pending_download(query, artist, title, album):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO downloads (query, artist, title, album, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (query, artist, title, album, 'pending', time.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    print(f"Inserted pending item: {query}")

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

def test_undownloaded_filtering():
    print("\n--- Testing Undownloaded Filtering ---")
    
    unique_id = str(uuid.uuid4())[:8]
    query = f"Pending Test - {unique_id}"
    
    print(f"Inserting pending item: {query}")
    insert_pending_download(query, "Pending Artist", f"Pending Title {unique_id}", "Pending Album")
    
    # 2. Check 'undownloaded' (status=pending)
    print("Checking /downloads?status=pending...")
    response = make_request("GET", "/downloads?status=pending&limit=100")
    pending_items = response["items"]
    
    found_pending = False
    for item in pending_items:
        if item["query"] == query:
            found_pending = True
            print("Found item in pending list.")
            break
            
    if not found_pending:
        print("FAILED: Item not found in pending list.")
        raise Exception("Item should be pending")
        
    # 3. Check 'library' (status=completed)
    print("Checking /downloads?status=completed...")
    response = make_request("GET", "/downloads?status=completed&limit=100")
    completed_items = response["items"]
    
    found_completed = False
    for item in completed_items:
        if item["query"] == query:
            found_completed = True
            print("Found item in completed list (Unexpected).")
            break
            
    if found_completed:
        print("FAILED: Item found in completed list but should be pending.")
        raise Exception("Item should not be completed")
        
    print("Item correctly absent from completed list.")
    print("Test Passed: Filtering works correctly.")

def test_pending_to_completed_flow():
    print("\n--- Testing Pending -> Completed Flow (Bug Fix) ---")
    
    # 1. Create a pending item
    unique_id = str(uuid.uuid4())[:8]
    # Use a real query that exists on YouTube to ensure download succeeds
    query = f"1 second silence {unique_id}"
    
    print(f"Inserting pending item: {query}")
    insert_pending_download(query, "Test Artist", "1 Second Silence", "Test Album")
    
    # Verify it is pending
    response = make_request("GET", "/downloads?status=pending&limit=100")
    pending_items = response["items"]
    if not any(item["query"] == query for item in pending_items):
        raise Exception("Failed to create pending item")
    print("Pending item created.")
    
    # 2. Trigger download again (simulate manual download)
    print("Triggering manual download for pending item...")
    make_request("POST", "/download", {
        "query": query,
        "artist": "Bug Fix Artist",
        "title": f"Bug Fix Title {unique_id}",
        "album": "Bug Fix Album",
        "image": ""
    })
    
    # 3. Wait for completion
    print("Waiting for completion...")
    found_completed = False
    for _ in range(30):
        time.sleep(1)
        response = make_request("GET", "/downloads?status=completed&limit=100")
        completed_items = response["items"]
        if any(item["query"] == query for item in completed_items):
            found_completed = True
            break
            
    if found_completed:
        print("Test Passed: Pending item successfully updated to completed.")
    else:
        print("FAILED: Pending item did not update to completed.")
        raise Exception("Bug fix failed")

if __name__ == "__main__":
    try:
        test_auto_download_setting()
        test_undownloaded_filtering()
        test_pending_to_completed_flow()
        print("\nALL TESTS PASSED")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
