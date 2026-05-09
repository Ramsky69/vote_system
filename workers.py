import os
import json
from google.cloud import pubsub_v1
from google.cloud import firestore

# --- CONFIGURATION ---
PROJECT_ID = "gen-lang-client-0844352843"
SUBSCRIPTION_ID = "vote-subscription"  # Make sure this subscription exists for your topic


# Initialize the Pub/Sub Subscriber Client and Firestore Client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
db = firestore.Client()

def process_vote(message):
    try:
        # Step 1: Decode and parse incoming vote message
        vote = json.loads(message.data.decode("utf-8"))
        print(f"Received vote: {vote}")

        # Step 2: Ensure idempotency (unique per user_id and poll_id)
        if not all(k in vote for k in ("user_id", "poll_id", "choice")):
            print(f"Malformed vote data: {vote}")
            message.ack()  # Ack malformed to avoid poison queue
            return
        doc_id = f"{vote['user_id']}_{vote['poll_id']}"

        # Step 3: Store processed vote in Firestore (idempotent)
        db.collection("votes").document(doc_id).set(vote)
        print(f"Stored vote in Firestore: {doc_id}")

        # Step 4: Acknowledge message
        message.ack()
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()

if __name__ == "__main__":
    print(f"Listening for messages on {subscription_path}...")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=process_vote)
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        print("Worker shutting down.")
        streaming_pull_future.cancel()
    except Exception as e:
        print(f"Error in subscriber: {e}")
        streaming_pull_future.cancel()
