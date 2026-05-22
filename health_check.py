"""
AgentHub Batch Health Check — check all registered agents for availability.
Run periodically to update agent status.
"""
import httpx
import time
import sqlite3
import json
from pathlib import Path

DB_PATH = "/opt/agenthub/agenthub.db"  # On Beijing server
# For local: Path(__file__).parent / "agenthub.db"

AGENTHUB_BASE = "https://eco.xiangma.ren/agents"

def check_agent(agent_id, url):
    """Check if an agent's Agent Card is reachable."""
    url = url.rstrip("/")
    card_urls = [
        f"{url}/.well-known/agent.json",
        f"{url}/.well-known/agent-card.json",
    ]
    start = time.time()
    for card_url in card_urls:
        try:
            resp = httpx.get(card_url, timeout=10, follow_redirects=True)
            ms = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                try:
                    card = resp.json()
                    return {
                        "status": "healthy",
                        "response_ms": ms,
                        "card_name": card.get("name", "?"),
                        "card_skills": len(card.get("skills", [])),
                    }
                except:
                    return {"status": "invalid_json", "response_ms": ms}
        except httpx.TimeoutException:
            return {"status": "timeout", "response_ms": int((time.time() - start) * 1000)}
        except Exception as e:
            continue
    return {"status": "unreachable", "response_ms": int((time.time() - start) * 1000)}

def main():
    print(f"[{time.strftime('%Y-%m-%d %H:%M')}] AgentHub Health Check")

    # Get all agents
    resp = httpx.get(f"{AGENTHUB_BASE}/api/agents?page_size=200", timeout=10)
    data = resp.json()
    agents = data.get("agents", [])
    print(f"  Checking {len(agents)} agents...")

    healthy = 0
    unhealthy = 0
    unreachable = 0

    for agent in agents:
        aid = agent["id"]
        url = agent.get("url", "")
        if not url:
            continue

        result = check_agent(aid, url)
        status = result["status"]

        if status == "healthy":
            healthy += 1
            emoji = "✅"
        elif status == "timeout":
            unhealthy += 1
            emoji = "⏱️"
        elif status == "invalid_json":
            unhealthy += 1
            emoji = "⚠️"
        else:
            unreachable += 1
            emoji = "❌"

        print(f"  {emoji} {agent['name'][:40]:40s} {status:15s} {result['response_ms']}ms")
        time.sleep(0.2)

    print(f"\n📊 Results: {healthy} healthy, {unhealthy} unhealthy, {unreachable} unreachable")
    print(f"   Total: {len(agents)} agents")

if __name__ == "__main__":
    main()
