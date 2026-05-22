"""
Discover A2A Agents from GitHub — search for repos with Agent Card patterns.
"""
import httpx
import json
import re
import time
import hashlib

GITHUB_API = "https://api.github.com"
AGENTHUB_API = "https://eco.xiangma.ren/agents/api/register"

# GitHub search queries to find A2A agents
QUERIES = [
    "agent-card.json a2a",
    "AgentCard a2a protocol",
    "a2a-agent server python",
    "a2a server agent_card",
    "well-known agent.json a2a",
    '"a2a" "agent" "skills" in:filename',
    "a2a-sdk agent example",
]

def search_github(query, per_page=30):
    """Search GitHub for A2A-related repos."""
    try:
        resp = httpx.get(
            f"{GITHUB_API}/search/repositories",
            params={"q": query, "sort": "updated", "per_page": per_page},
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json().get("items", [])
        elif resp.status_code == 403:
            print(f"  ⚠️ Rate limited, waiting 60s...")
            time.sleep(60)
            return []
        else:
            print(f"  ❌ GitHub API {resp.status_code}")
            return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []

def extract_agent_info(repo):
    """Extract agent info from a GitHub repo."""
    name = repo.get("name", "")
    desc = repo.get("description", "") or ""
    html_url = repo.get("html_url", "")
    topics = repo.get("topics", [])
    stars = repo.get("stargazers_count", 0)
    language = repo.get("language", "")
    updated = repo.get("updated_at", "")

    return {
        "name": name.replace("-", " ").replace("_", " ").title(),
        "description": desc[:300],
        "url": html_url,
        "version": "1.0.0",
        "stars": stars,
        "language": language,
        "topics": topics,
        "updated": updated,
        "skills": [
            {
                "id": "main",
                "name": name.replace("-", " ").replace("_", " ").title(),
                "description": desc[:200] if desc else f"A2A agent: {name}",
                "tags": topics[:5] if topics else ["a2a", language.lower() if language else "unknown"],
            }
        ],
    }

def register_to_agenthub(agent_info):
    """Register an agent to AgentHub."""
    card = {
        "name": agent_info["name"],
        "description": agent_info["description"],
        "url": agent_info["url"],
        "version": agent_info["version"],
        "capabilities": {"streaming": False},
        "skills": agent_info["skills"],
    }
    try:
        resp = httpx.post(
            AGENTHUB_API,
            json={"agent_card_url": agent_info["url"], "agent_card": card},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return True, data.get("agent_id", "?")
        else:
            return False, resp.json().get("error", "unknown")
    except Exception as e:
        return False, str(e)

def main():
    print("🔍 Discovering A2A Agents from GitHub...")
    print()

    all_repos = {}  # url -> repo (dedup)

    for query in QUERIES:
        print(f"  Searching: {query}")
        repos = search_github(query)
        for repo in repos:
            url = repo.get("html_url", "")
            if url not in all_repos:
                all_repos[url] = repo
        print(f"    Found {len(repos)} repos (total unique: {len(all_repos)})")
        time.sleep(2)  # Rate limit

    print(f"\n📊 Total unique repos found: {len(all_repos)}")
    print()

    # Filter for likely A2A agents
    a2a_keywords = ["a2a", "agent2agent", "agent-card", "agent_card", "well-known/agent"]
    likely_a2a = {}
    for url, repo in all_repos.items():
        desc = (repo.get("description", "") or "").lower()
        name = (repo.get("name", "") or "").lower()
        topics = " ".join(repo.get("topics", [])).lower()
        combined = f"{desc} {name} {topics}"

        if any(kw in combined for kw in a2a_keywords):
            likely_a2a[url] = repo

    print(f"🎯 Likely A2A agents: {len(likely_a2a)}")
    print()

    # Register to AgentHub
    ok = 0
    fail = 0
    seen_names = set()

    for url, repo in likely_a2a.items():
        info = extract_agent_info(repo)

        # Skip if we already have this name
        if info["name"].lower() in seen_names:
            continue
        seen_names.add(info["name"].lower())

        success, result = register_to_agenthub(info)
        if success:
            print(f"  ✅ {info['name']} (⭐{info['stars']}) → {result}")
            ok += 1
        else:
            if "already" in str(result).lower() or "unique" in str(result).lower():
                print(f"  ⏭️  {info['name']} (already registered)")
            else:
                print(f"  ❌ {info['name']} → {result}")
                fail += 1

        time.sleep(0.3)

    print(f"\n📊 Results: {ok} new, {fail} failed")

    # Final stats
    resp = httpx.get("https://eco.xiangma.ren/agents/api/stats", timeout=10)
    stats = resp.json()
    print(f"📈 AgentHub now has: {stats}")

if __name__ == "__main__":
    main()
