import os
import json
from flask import Flask, request
from google.cloud import pubsub_v1

app = Flask(__name__)

# --- CONFIGURATION ---
PROJECT_ID = "gen-lang-client-0844352843"
TOPIC_ID = "vote-topic"

# Initialize the Pub/Sub Publisher Client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@app.route("/vote", methods=["POST"])
def receive_vote():
    vote = request.get_json()

    # Step 1: Validation
    # Ensure user_id, poll_id, and choice exist in the payload
    required_fields = ["user_id", "poll_id", "choice"]
    if not vote or not all(field in vote for field in required_fields):
        print(f"Validation failed for payload: {vote}")
        return {"error": "Invalid payload: missing user_id, poll_id, or choice"}, 400

    # Step 2: Publishing to Pub/Sub
    try:
        # Data must be serialized to bytes for Pub/Sub
        message_data = json.dumps(vote).encode("utf-8")
        
        # Publish the validated vote asynchronously
        future = publisher.publish(topic_path, message_data)
        
        # Non-blocking: We return 'accepted' as soon as the message is queued
        print(f"Vote accepted and published: {vote['user_id']}")
        return {"status": "accepted", "message_id": future.result()}, 200

    except Exception as e:
        print(f"Error publishing to Pub/Sub: {str(e)}")
        return {"error": "Internal server error during ingestion"}, 500

if __name__ == "__main__":
    # Cloud Run passes the port as an environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
