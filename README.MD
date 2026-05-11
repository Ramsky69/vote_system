# Distributed Voting System

## Overview
This project implements a distributed voting system using Python, Google Cloud Run, Pub/Sub, and Firestore. It demonstrates edge-to-cloud ingestion, asynchronous processing, idempotency, fault tolerance, and eventual consistency.

## Architecture
Edge Nodes → Cloud Run API → Pub/Sub → Worker Service → Firestore

![Architecture Diagram](architecture-diagram.svg)

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

### 1. End-to-End Latency
Under normal operation, latency from edge to Firestore was low (under a few seconds). During worker downtime, latency increased significantly as votes queued in Pub/Sub and were processed in batch upon recovery.

### 2. System Throughput
The system processed votes in near real-time under normal conditions. During worker downtime, throughput dropped to zero, but upon recovery, the worker processed queued votes rapidly.

### 3. Fault Tolerance Behavior
When the worker was stopped, the API and Pub/Sub continued to accept and buffer votes. No votes were lost. After restarting the worker, all queued votes were processed and stored in Firestore.

### 4. Consistency Across Components
Idempotency was enforced using a composite document ID (`user_id` + `poll_id`), ensuring no duplicate records in Firestore even when the same vote was sent multiple times.

### 5. System Trade-Offs
- **Pub/Sub**: Reliability and decoupling, but introduced buffering delay.
- **Cloud Run**: Flexible scaling, but cold starts added slight delay.
- **Edge Computing**: Reduced server load but increased system complexity.
- **Idempotency**: Ensured correctness but required additional logic.

## Individual Reflections

### Abraham Roxas (Ramsky69)
Tbh the GCP setup took me longer than expected. There were a few APIs to enable and the IAM permissions kept giving me errors when I tried to publish to Pub/Sub. I had to redeploy the Cloud Run service a few times before it finally worked. Once it was running though I just watched the team plug in their parts and the whole thing came together. The thing that really stuck with me was that the API didn't even care when the worker was off, it kept accepting votes like nothing was wrong. That's when I got that fault tolerance isn't about nothing breaking, it's that when one part breaks the rest still runs.

### Jiane Rackyle Sarting (rackyroadt)
My part was mostly the documentation, the architecture diagram, and adding tracking counters and logging to the worker. Doing the diagram was harder than I thought because I had to actually understand how the components connect, not just draw boxes. The fault injection test was the most interesting for me. We turned off the worker and the votes just stacked in Pub/Sub, then once we turned it back on, Firestore got hit with the whole batch at once. It was kinda cool to see the recovery actually happen on its own.

### Samuel Vincent Aque (BacnonCod)
I added the acknowledgments section and helped check the README. During testing it was kinda fun watching the votes show up in Firestore one by one. When we stopped the worker I thought the whole thing would crash but the API kept running and the votes just waited in Pub/Sub. That's when fault tolerance made sense to me, like the system can lose a part but still keep going.

### John Lloyd Arvin Bajolo (johnskie149)
I worked on the documentation formatting and ran the edge node during testing. Honestly at first I didn't really know what was going on with all the cloud services, it was kinda overwhelming. But once the pipeline was running it got easier to follow. My favorite part was the worker shutdown test because the system didn't break, and when we turned the worker back on it just caught up by itself. We didn't have to fix anything manually.
