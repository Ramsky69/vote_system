# Distributed Voting System

## Overview
This project implements a distributed voting system using Python, Google Cloud Run, Pub/Sub, and Firestore. It demonstrates edge-to-cloud ingestion, asynchronous processing, idempotency, fault tolerance, and eventual consistency.

## Components
- **edge_node.py**: Simulates edge devices generating and sending votes (with intentional duplication for fault testing).
- **main.py**: Cloud Run API that receives votes via HTTP POST at `/vote`, validates them, and publishes to Pub/Sub.
- **workers.py**: Worker service that subscribes to the Pub/Sub topic, processes votes, ensures idempotency, and stores them in Firestore.

## Setup & Running

### 1. Prerequisites
- Python 3.10+
- Google Cloud project with Pub/Sub and Firestore enabled
- Cloud Run deployment for `main.py` (API)
- Service account with Pub/Sub and Firestore permissions

### 2. Install Dependencies
```
pip install -r requirements.txt
```

### 3. Create Pub/Sub Topic and Subscription
```
gcloud pubsub topics create vote-topic
gcloud pubsub subscriptions create vote-subscription --topic=vote-topic
```

### 4. Deploy API to Cloud Run
Deploy `main.py` to Cloud Run. Set the service URL in `edge_node.py` as `API_URL`.

### 5. Run the Worker
```
python workers.py
```

### 6. Run the Edge Node
```
python edge_node.py
```

## Testing & Fault Injection
- The edge node sends each vote 3 times to simulate network-induced duplication.
- Stop the worker to simulate backend failure; Pub/Sub will buffer messages.
- Restart the worker to process queued votes and observe recovery.

## Endpoints
- `POST /vote` (Cloud Run API): Receives vote JSON payloads.

## Firestore Structure
- Collection: `votes`
- Document ID: `{user_id}_{poll_id}`
- Document fields: All vote data

## Notes
- The root URL of the API returns 404 by design; use `/vote` for POST requests.
- All components log their actions for traceability and analysis.

## Example Vote Payload
```json
{
  "user_id": "...",
  "poll_id": "poll_2024_election",
  "choice": "A",
  "timestamp": 1234567890.0,
  "edge_node_id": "node_phil_01"
}
```

## System Evaluation & Performance Analysis

### 1. End-to-End Latency (Edge to Firestore)
Latency was measured by comparing the `timestamp` in the vote payload (generated at the edge) with the time the vote was processed by the worker and stored in Firestore. Under normal operation, latency was low (typically under a few seconds). During worker downtime, latency increased significantly as votes queued in Pub/Sub and were processed in batch upon recovery.

### 2. System Throughput (Processing Capacity)
Throughput was observed by counting votes generated at the edge, processed by the worker, and stored in Firestore. Under normal conditions, the system processed votes in near real-time. During worker downtime, throughput at the worker dropped to zero, but upon recovery, the worker processed all queued votes rapidly, demonstrating high burst capacity.

### 3. Fault Tolerance Behavior
When the worker was stopped, the API and Pub/Sub continued to accept and buffer votes. No votes were lost during downtime. After restarting the worker, all queued votes were processed and stored in Firestore, confirming the system's resilience and automatic recovery.

### 4. Consistency Across Components
The number of unique votes in Firestore matched the number of unique votes generated at the edge (accounting for intentional duplicates). Idempotency was enforced by using a composite document ID (`user_id` + `poll_id`), ensuring no duplicate records in Firestore even when the same vote was sent multiple times.

### 5. System Trade-Offs
- **Pub/Sub**: Provided reliability and decoupling, but introduced buffering delay during worker downtime.
- **Cloud Run**: Enabled flexible scaling, but cold starts could add slight delay.
- **Edge Computing**: Reduced server load and allowed distributed data generation, but increased system complexity.
- **Idempotency**: Ensured correctness and consistency, but required additional logic in the worker.


## Acknowledgments
CS323 - Distributed Systems Laboratory Activity
