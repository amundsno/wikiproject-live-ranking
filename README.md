# WikiProject Live Ranking
Real-time ranking of WikiProjects based on Wikipedia edit activity.

## Quick Start
```sh
git clone https://github.com/amundsno/wikiproject-live-ranking.git
cd wikiproject-live-ranking
docker compose up -d --build
```
![wikiproject-live-ranking](https://github.com/user-attachments/assets/15a6475d-c7e3-4b34-9216-711c433a369f)

## Project Overview
This demo project explores real-time processing of stream events using **Kafka** and **microservices in Python**. All services run as Docker containers:

1. **Kafka**  
   Single-node controller and broker in KRaft mode (no ZooKeeper).

2. `wikistream-subscriber`  
   Subscribes to [WikiMedia's public stream of recent change events](https://stream.wikimedia.org/v2/stream/recentchange), filters *real user edits* on *main articles* of the *English Wikipedia*, and sends them to the `wiki-stream` Kafka topic.

3. `wikistream-enricher`  
   Listens to `wiki-stream`, fetches related WikiProjects from Wikipedia's API, and forwards enriched events to the `wiki-stream-enriched` topic.

4. `sse-streamer`  
   Exposes events in the `wiki-stream-enriched` topic via **Server-Sent Events (SSE)** in real-time.

5. `nginx`  
   Serves the UI (frontend) and proxies SSE requests to `sse-streamer`.

### Tech Stack
- **Backend:** Kafka, Python
- **Frontend:** TypeScript, HTML/CSS, SSE (Server-Sent Events)
- **Proxy & Static Hosting:** Nginx
- **Infrastructure:** Docker

## Contributing
PRs and suggestions are welcome! Feel free to fork, modify, and improve this project (MIT license).
