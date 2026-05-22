#!/usr/bin/env python3
"""AgentHub Club Auto-Discovery — finds new A2A agents and invites them to the club."""
import httpx, json, time

CLUB_URL = "https://eco.xiangma.ren/agents/api/join"
GITHUB_API = "https://api.github.com"
QUERIES = ["a2a agent server","a2a-sdk agent","agent2agent skills","well-known agent.json a2a","a2a protocol agent"]

def run():
    print(f"[{time.strftime('%Y-%m-%d %H:%M')}] AgentHub Club Auto-Discovery")
    all_repos = {}
    for q in QUERIES:
        try:
            r = httpx.get(f"{GITHUB_API}/search/repositories", params={"q":q,"sort":"updated","per_page":30},
                headers={"Accept":"application/vnd.github.v3+json"}, timeout=15)
            if r.status_code == 200:
                for repo in r.json().get("items",[]):
                    all_repos[repo.get("html_url","")] = repo
        except: pass
        time.sleep(2)

    a2a_kw = ["a2a","agent2agent","agent-card"]
    new = 0
    for url, repo in all_repos.items():
        desc = (repo.get("description","") or "").lower()
        name = (repo.get("name","") or "").lower()
        topics = " ".join(repo.get("topics",[])).lower()
        if not any(kw in f"{desc} {name} {topics}" for kw in a2a_kw):
            continue
        rn = repo.get("name","").replace("-"," ").replace("_"," ").title()
        rd = (repo.get("description","") or "")[:200]
        rt = repo.get("topics",[])[:3] or ["a2a"]
        card = {"name":rn,"description":rd,"url":url,"version":"1.0.0",
                "skills":[{"id":"main","name":rn,"description":rd[:150] or rn,"tags":rt}]}
        try:
            r = httpx.post(CLUB_URL, json={"agent_card":card}, timeout=10)
            if r.status_code == 200 and r.json().get("status") == "welcome_to_the_club":
                new += 1
        except: pass
        time.sleep(0.2)

    stats = httpx.get("https://eco.xiangma.ren/agents/api/stats", timeout=10).json()
    print(f"  Found {len(all_repos)} repos, {new} new members")
    print(f"  Club: {stats['total_members']} members, {stats['total_skills']} skills, {stats.get('shared_data_items',0)} shared items")

if __name__ == "__main__":
    run()
