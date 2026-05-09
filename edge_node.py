import uuid
import random
import time
import requests
import os

# --- CONFIGURATION ---
# Replace this with your actual Cloud Run URL after you deploy the ingestion service
API_URL = "https://ingestion-service-300760955798.asia-southeast1.run.app/vote" 

# Distinguish this node from others (each group member should change this)
NODE_ID = "node_phil_01" 

def generate_vote():
    """
    Generates a unique vote payload.
    Added 'edge_node_id' to distinguish the source of the data.
    """
    return {
        "user_id": str(uuid.uuid4()),
        "poll_id": "poll_2024_election",
        "choice": random.choice(["A", "B", "C"]),
        "timestamp": time.time(),
        "edge_node_id": NODE_ID  # Extended to identify the specific edge node
    }

def send_vote(vote, retries=3):
    """
    Sends data to the Cloud Run API with basic retry logic.
    Simulates resilience against unreliable network conditions.
    """
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, json=vote, timeout=5)
            if response.status_code == 200:
                print(f"[{NODE_ID}] Success: Sent vote for {vote['choice']}")
                return True
            else:
                print(f"[{NODE_ID}] Warning: Server returned {response.status_code}")
        except Exception as e:
            wait_time = 2 ** attempt  # Exponential backoff (1s, 2s, 4s...)
            print(f"[{NODE_ID}] Transmission failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    print(f"[{NODE_ID}] Error: Failed to send vote after {retries} attempts.")
    return False

def run_edge_node():
    """
    Simulates real-world edge behavior with continuous execution 
    and random intermittent delays.
    """
    print(f"Starting Edge Node: {NODE_ID}...")
    try:
        while True:
            vote = generate_vote()
            print(f"Vote generated: {vote['user_id']} | Choice: {vote['choice']} | Time: {vote['timestamp']}")
            # Simulate message duplication (send the same vote 3 times)
            for i in range(3):
                send_vote(vote)
            # Simulate real-world variability: 
            # A node might burst data or pause for longer intervals.
            sleep_duration = random.uniform(1.0, 5.0) 
            time.sleep(sleep_duration)
    except KeyboardInterrupt:
        print(f"Edge Node {NODE_ID} shutting down.")

if __name__ == "__main__":
    # Ensure you have the requests library installed: pip install requests
    run_edge_node()
