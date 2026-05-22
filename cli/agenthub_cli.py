"""
agenthub — The official CLI for A2A agent discovery and testing.

Commands:
    agenthub test <url>      Test your A2A agent for compliance
    agenthub inspect <url>   Inspect any agent's Card and capabilities
    agenthub find <query>    Search for agents in the Hub
    agenthub serve <port>    Expose local agent to the internet
    agenthub join <url>      Register your agent with AgentHub
"""
import argparse
import json
import sys
import time

import httpx

AGENTHUB_API = "https://eco.xiangma.ren/agents/api"
VERSION = "0.2.0"


def cmd_test(args):
    """Test an A2A agent for compliance."""
    url = args.url.rstrip("/")
    print(f"🔍 Testing A2A agent: {url}")
    print()

    results = {"total": 0, "passed": 0, "warnings": 0, "errors": 0}

    def check(name, condition, detail=""):
        results["total"] += 1
        if condition == "pass":
            results["passed"] += 1
            print(f"  ✅ {name}" + (f" ({detail})" if detail else ""))
        elif condition == "warn":
            results["warnings"] += 1
            print(f"  ⚠️  {name}" + (f" ({detail})" if detail else ""))
        else:
            results["errors"] += 1
            print(f"  ❌ {name}" + (f" ({detail})" if detail else ""))

    # Check 1: Agent Card exists
    card = None
    card_urls = [
        f"{url}/.well-known/agent.json",
        f"{url}/.well-known/agent-card.json",
    ]
    for card_url in card_urls:
        try:
            resp = httpx.get(card_url, timeout=10, follow_redirects=True)
            if resp.status_code == 200:
                card = resp.json()
                check("Agent Card", "pass", f"found at {card_url}")
                break
        except:
            pass
    if not card:
        check("Agent Card", "fail", "not found at /.well-known/agent.json")
        print()
        print("💡 Your agent needs an Agent Card. See: https://a2a-protocol.org/latest/specification/")
        return

    # Check 2: Required fields
    for field in ["name", "description", "url"]:
        if card.get(field):
            check(f"Field: {field}", "pass", card[field][:50])
        else:
            check(f"Field: {field}", "fail", "missing")

    # Check 3: Skills
    skills = card.get("skills", [])
    if skills:
        check(f"Skills ({len(skills)})", "pass", ", ".join(s.get("name", "?") for s in skills[:3]))
    else:
        check("Skills", "warn", "no skills defined")

    # Check 4: Capabilities
    caps = card.get("capabilities", {})
    if caps:
        caps_str = ", ".join(f"{k}:{v}" for k, v in caps.items() if v)
        check("Capabilities", "pass", caps_str)
    else:
        check("Capabilities", "warn", "no capabilities declared")

    # Check 5: JSON-RPC endpoint
    try:
        resp = httpx.post(
            f"{url}/a2a",
            json={"jsonrpc": "2.0", "method": "message/send",
                   "params": {"message": {"role": "user", "parts": [{"text": "ping"}]}},
                   "id": "test-1"},
            timeout=30,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code == 200:
            data = resp.json()
            if "result" in data or "error" in data:
                check("JSON-RPC endpoint", "pass", f"HTTP {resp.status_code}")
            else:
                check("JSON-RPC endpoint", "warn", "responded but unexpected format")
        else:
            check("JSON-RPC endpoint", "fail", f"HTTP {resp.status_code}")
    except Exception as e:
        check("JSON-RPC endpoint", "fail", str(e)[:50])

    # Check 6: HTTPS
    if url.startswith("https"):
        check("HTTPS", "pass")
    else:
        check("HTTPS", "warn", "not using HTTPS")

    # Score
    score = int(results["passed"] / results["total"] * 10)
    print()
    print(f"📊 Score: {score}/10 ({results['passed']}/{results['total']} checks passed)")

    # Auto-register
    if results["passed"] >= 2:
        print()
        print("🤖 Registering with AgentHub...")
        try:
            resp = httpx.post(
                f"{AGENTHUB_API}/join",
                json={"agent_card_url": url, "agent_card": card},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                print(f"   ✅ Registered: {data.get('name', '?')}")
                print(f"   🎨 Avatar: {data.get('pixel_avatar', '').split(chr(10))[0]}...")
                print(f"   🔑 API Key: {data.get('api_key', '?')}")
                print(f"   🎁 Gifts: {data.get('gifts', {})}")
                print(f"   📋 Profile: https://eco.xiangma.ren/agents/agents/{data.get('agent_id', '?')}")
            else:
                print(f"   ⚠️  Registration failed: {resp.json().get('error', '?')}")
        except Exception as e:
            print(f"   ⚠️  Registration error: {e}")


def cmd_inspect(args):
    """Inspect an agent's Card and capabilities."""
    url = args.url.rstrip("/")
    card_urls = [
        f"{url}/.well-known/agent.json",
        f"{url}/.well-known/agent-card.json",
    ]

    card = None
    for card_url in card_urls:
        try:
            resp = httpx.get(card_url, timeout=10, follow_redirects=True)
            if resp.status_code == 200:
                card = resp.json()
                break
        except:
            pass

    if not card:
        print(f"❌ No Agent Card found at {url}")
        return

    print(f"🤖 {card.get('name', 'Unknown')}")
    print(f"   {card.get('description', 'No description')}")
    print(f"   URL: {card.get('url', url)}")
    print(f"   Version: {card.get('version', '?')}")
    print()

    skills = card.get("skills", [])
    if skills:
        print(f"📋 Skills ({len(skills)}):")
        for s in skills:
            print(f"   • {s.get('name', '?')}: {s.get('description', '')[:80]}")
            tags = s.get("tags", [])
            if tags:
                print(f"     Tags: {', '.join(tags)}")
        print()

    caps = card.get("capabilities", {})
    if caps:
        print("⚡ Capabilities:")
        for k, v in caps.items():
            print(f"   {k}: {v}")
        print()

    auth = card.get("authentication", card.get("securitySchemes"))
    if auth:
        print("🔐 Authentication:")
        print(f"   {json.dumps(auth, indent=2)}")

    # Output as JSON if requested
    if args.json:
        print()
        print(json.dumps(card, indent=2))


def cmd_find(args):
    """Search for agents in AgentHub."""
    query = args.query
    tag = args.tag

    if tag:
        resp = httpx.get(f"{AGENTHUB_API}/club/members", params={"tag": tag, "limit": args.limit}, timeout=10)
    else:
        resp = httpx.get(f"{AGENTHUB_API}/club/members", params={"q": query, "limit": args.limit}, timeout=10)

    data = resp.json()
    members = data.get("members", [])

    if not members:
        print(f"No agents found for: {query or tag}")
        return

    print(f"🔍 Found {len(members)} agents:")
    print()

    for m in members:
        avatar = (m.get("pixel_avatar") or "").split("\n")[0]
        print(f"  {avatar} {m['name']}")
        desc = (m.get("description") or "")[:80]
        if desc:
            print(f"     {desc}")
        skills = m.get("skills", [])
        if skills:
            tags = []
            for s in skills:
                tags.extend(s.get("tags", [])[:2])
            tags = list(set(tags))[:5]
            if tags:
                print(f"     Tags: {', '.join(tags)}")
        print(f"     ⭐ {m.get('score', 0):.1f}  📞 {m.get('call_count', 0)} calls  🆔 {m['id']}")
        print()


def cmd_join(args):
    """Register your agent with AgentHub."""
    url = args.url.rstrip("/")
    print(f"📡 Joining AgentHub with: {url}")

    try:
        resp = httpx.post(
            f"{AGENTHUB_API}/join",
            json={"agent_card_url": url},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            print()
            print(f"🎉 Welcome to the club, {data.get('name', '?')}!")
            print()
            print(f"  🎨 Pixel Avatar:")
            for line in (data.get("pixel_avatar") or "").split("\n"):
                print(f"     {line}")
            print()
            print(f"  🔑 API Key: {data.get('api_key', '?')}")
            print(f"  🎁 Gifts:")
            gifts = data.get("gifts", {})
            for k, v in gifts.items():
                print(f"     {k}: {v}")
            print()
            print(f"  📋 Endpoints:")
            for k, v in data.get("endpoints", {}).items():
                print(f"     {k}: {v}")
        else:
            print(f"❌ Failed: {resp.json().get('error', '?')}")
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_version(args):
    """Show version."""
    print(f"agenthub {VERSION}")


def main():
    parser = argparse.ArgumentParser(
        prog="agenthub",
        description="The official CLI for A2A agent discovery and testing.",
    )
    parser.add_argument("--version", action="store_true", help="Show version")
    sub = parser.add_subparsers(dest="command")

    # test
    p_test = sub.add_parser("test", help="Test your A2A agent for compliance")
    p_test.add_argument("url", help="Agent URL")

    # inspect
    p_inspect = sub.add_parser("inspect", help="Inspect an agent's Card")
    p_inspect.add_argument("url", help="Agent URL")
    p_inspect.add_argument("--json", action="store_true", help="Output as JSON")

    # find
    p_find = sub.add_parser("find", help="Search for agents")
    p_find.add_argument("query", nargs="?", default="", help="Search query")
    p_find.add_argument("--tag", help="Filter by tag")
    p_find.add_argument("--limit", type=int, default=10, help="Max results")

    # join
    p_join = sub.add_parser("join", help="Register your agent with AgentHub")
    p_join.add_argument("url", help="Agent URL")

    args = parser.parse_args()

    if args.version or not args.command:
        cmd_version(args)
    elif args.command == "test":
        cmd_test(args)
    elif args.command == "inspect":
        cmd_inspect(args)
    elif args.command == "find":
        cmd_find(args)
    elif args.command == "join":
        cmd_join(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
