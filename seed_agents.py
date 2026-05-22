"""
Seed AgentHub with known A2A Agents from GitHub.
These are reference implementations — developers can clone and run them.
"""
import httpx
import json
import time

AGENTHUB_URL = "https://eco.xiangma.ren/agents/api/register"

# Known A2A Agents from GitHub
AGENTS = [
    # === a2a-samples Python agents ===
    {
        "name": "Google ADK Facts Agent",
        "description": "Fun facts agent using Grounding with Google Search and Google ADK. Demonstrates A2A protocol integration with Google's Agent Development Kit.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/adk_facts",
        "version": "1.0.0",
        "skills": [
            {"id": "fun-facts", "name": "Fun Facts", "description": "Provides interesting fun facts using Google Search grounding", "tags": ["search", "facts", "google", "adk"]}
        ],
    },
    {
        "name": "ADK Expense Reimbursement Agent",
        "description": "Mock expense report filling agent. Showcases multi-turn interactions and webform handling through A2A protocol.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/adk_expense_reimbursement",
        "version": "1.0.0",
        "skills": [
            {"id": "expense-report", "name": "Expense Report", "description": "Fill out expense reports via multi-turn conversation", "tags": ["finance", "expense", "forms", "enterprise"]}
        ],
    },
    {
        "name": "AG2 MCP Agent",
        "description": "MCP-enabled agent built with AG2 framework, exposed through A2A protocol. Bridges MCP tool ecosystem with A2A interop.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/ag2",
        "version": "1.0.0",
        "skills": [
            {"id": "mcp-tools", "name": "MCP Tools", "description": "Access MCP tools via A2A protocol", "tags": ["mcp", "tools", "ag2", "interop"]}
        ],
    },
    {
        "name": "Azure AI Foundry Agent",
        "description": "Agent built with Azure AI Foundry Agent Service, exposed through A2A protocol. Enterprise-grade Azure integration.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/azureaifoundry_sdk",
        "version": "1.0.0",
        "skills": [
            {"id": "azure-ai", "name": "Azure AI Services", "description": "Enterprise AI capabilities via Azure AI Foundry", "tags": ["azure", "enterprise", "ai", "cloud"]}
        ],
    },
    {
        "name": "LangGraph Currency Agent",
        "description": "Currency conversion agent built with LangGraph. Showcases multi-turn dialogue, tool usage, and streaming updates via A2A.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/langgraph",
        "version": "1.0.0",
        "skills": [
            {"id": "currency-conversion", "name": "Currency Conversion", "description": "Real-time currency exchange rates using Frankfurter API", "tags": ["currency", "finance", "langgraph", "streaming"]}
        ],
    },
    {
        "name": "CrewAI Image Agent",
        "description": "Image generation agent built with CrewAI framework. Demonstrates multimodal A2A communication with image artifacts.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/crewai",
        "version": "1.0.0",
        "skills": [
            {"id": "image-generation", "name": "Image Generation", "description": "Generate images using CrewAI agents", "tags": ["image", "generation", "crewai", "multimodal"]}
        ],
    },
    {
        "name": "LlamaIndex File Chat Agent",
        "description": "File parsing and chat agent built with LlamaIndex. Supports file upload, parsing, and contextual Q&A via A2A.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/llama_index_file_chat",
        "version": "1.0.0",
        "skills": [
            {"id": "file-chat", "name": "File Chat", "description": "Upload files and chat with their content", "tags": ["file", "chat", "llamaindex", "rag", "parsing"]}
        ],
    },
    {
        "name": "Marvin Contact Extractor",
        "description": "Structured contact information extraction agent using Marvin framework. Demonstrates structured data extraction via A2A.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/marvin",
        "version": "1.0.0",
        "skills": [
            {"id": "contact-extraction", "name": "Contact Extraction", "description": "Extract structured contact info from text", "tags": ["extraction", "contacts", "marvin", "structured-data"]}
        ],
    },
    {
        "name": "MindsDB Enterprise Data Agent",
        "description": "Answer questions from any database, data warehouse, or app. Powered by Gemini 2.5 Flash + MindsDB.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/mindsdb",
        "version": "1.0.0",
        "skills": [
            {"id": "data-query", "name": "Data Query", "description": "Query any database or data warehouse using natural language", "tags": ["database", "data", "mindsdb", "enterprise", "sql"]}
        ],
    },
    {
        "name": "Semantic Kernel Travel Agent",
        "description": "Travel agent built on Microsoft Semantic Kernel. Demonstrates enterprise travel planning via A2A protocol.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/semantickernel",
        "version": "1.0.0",
        "skills": [
            {"id": "travel-planning", "name": "Travel Planning", "description": "Plan trips with flights, hotels, and itineraries", "tags": ["travel", "planning", "semantic-kernel", "microsoft"]}
        ],
    },
    {
        "name": "Travel Planner Agent",
        "description": "Travel assistant using Google's official a2a-python SDK. Demonstrates standard A2A travel planning workflow.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/travel_planner_agent",
        "version": "1.0.0",
        "skills": [
            {"id": "travel", "name": "Travel Assistant", "description": "Plan trips and itineraries", "tags": ["travel", "planning", "assistant"]}
        ],
    },
    {
        "name": "Any-Agent Adversarial Multi-Agent",
        "description": "Adversarial multi-agent system with competing attacker and defender agents. Demonstrates security testing patterns via A2A.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/any_agent_adversarial_multiagent",
        "version": "1.0.0",
        "skills": [
            {"id": "adversarial", "name": "Adversarial Testing", "description": "Multi-agent adversarial security testing", "tags": ["security", "adversarial", "testing", "multi-agent"]}
        ],
    },
    {
        "name": "Content Planner Agent",
        "description": "Creates detailed content outlines using Google Search and ADK. Demonstrates research + planning via A2A.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/content_planner",
        "version": "1.0.0",
        "skills": [
            {"id": "content-planning", "name": "Content Planning", "description": "Create detailed content outlines with research", "tags": ["content", "planning", "research", "google", "adk"]}
        ],
    },
    # === a2a-samples JS agents ===
    {
        "name": "Movie Info Agent",
        "description": "Movie information agent using TMDB API via Genkit. Answers questions about movies, actors, and ratings.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/js/src/agents/movie-agent",
        "version": "1.0.0",
        "skills": [
            {"id": "movie-info", "name": "Movie Information", "description": "Search movies, actors, ratings via TMDB", "tags": ["movies", "entertainment", "genkit", "search"]}
        ],
    },
    {
        "name": "Coder Agent",
        "description": "Code writing agent that generates full code files as A2A artifacts. Built with Genkit.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/js/src/agents/coder",
        "version": "1.0.0",
        "skills": [
            {"id": "code-generation", "name": "Code Generation", "description": "Generate complete code files as artifacts", "tags": ["coding", "generation", "genkit", "developer"]}
        ],
    },
    {
        "name": "Content Editor Agent",
        "description": "Proofreading and content polishing agent. Part of a multi-agent content creation system via A2A.",
        "url": "https://github.com/a2aproject/a2a-samples/tree/main/samples/js/src/agents/content-editor",
        "version": "1.0.0",
        "skills": [
            {"id": "content-editing", "name": "Content Editing", "description": "Proofread and polish content", "tags": ["editing", "proofreading", "content", "genkit"]}
        ],
    },
    # === ADK samples ===
    {
        "name": "ADK Multi-Agent System",
        "description": "Basic multi-agent system with dice rolling and prime number checking. Demonstrates A2A agent composition patterns.",
        "url": "https://github.com/google/adk-python/tree/main/contributing/samples/a2a_basic",
        "version": "1.0.0",
        "skills": [
            {"id": "dice-roll", "name": "Dice Roll", "description": "Roll dice and check prime numbers", "tags": ["demo", "multi-agent", "adk", "basic"]}
        ],
    },
    {
        "name": "ADK OAuth Auth Agent",
        "description": "A2A agent with OAuth authentication workflow. Demonstrates secure agent-to-agent authentication patterns.",
        "url": "https://github.com/google/adk-python/tree/main/contributing/samples/a2a_auth",
        "version": "1.0.0",
        "skills": [
            {"id": "oauth-auth", "name": "OAuth Authentication", "description": "OAuth-based authentication for A2A agents", "tags": ["auth", "oauth", "security", "adk"]}
        ],
    },
    {
        "name": "ADK Human-in-the-Loop Agent",
        "description": "A2A agent with human-in-the-loop workflows. Demonstrates approval and escalation patterns.",
        "url": "https://github.com/google/adk-python/tree/main/contributing/samples/a2a_human_in_loop",
        "version": "1.0.0",
        "skills": [
            {"id": "hitl", "name": "Human-in-the-Loop", "description": "Human approval and escalation workflows", "tags": ["hitl", "approval", "enterprise", "adk"]}
        ],
    },
    # === Third-party A2A agents from GitHub topics ===
    {
        "name": "Easy A2A",
        "description": "Use the A2A protocol with any OpenAI API compatible endpoint. Universal adapter for adding A2A to existing agents.",
        "url": "https://github.com/the-artinet-project/easy-a2a",
        "version": "1.0.0",
        "skills": [
            {"id": "a2a-adapter", "name": "A2A Adapter", "description": "Add A2A protocol support to any OpenAI-compatible agent", "tags": ["adapter", "openai", "interop", "developer"]}
        ],
    },
    {
        "name": "A2A Adapter SDK",
        "description": "Open source A2A Protocol Adapter SDK for different agent frameworks. Universal bridge between frameworks and A2A.",
        "url": "https://github.com/hybroai/a2a-adapter",
        "version": "1.0.0",
        "skills": [
            {"id": "framework-adapter", "name": "Framework Adapter", "description": "Bridge any agent framework to A2A protocol", "tags": ["adapter", "sdk", "framework", "interop"]}
        ],
    },
    {
        "name": "A2A Chat Hub",
        "description": "Chat application with A2UI support for talking to any A2A agent. Universal A2A client.",
        "url": "https://github.com/vladkol/a2a-chat-hub",
        "version": "1.0.0",
        "skills": [
            {"id": "chat-hub", "name": "A2A Chat Hub", "description": "Chat with any A2A agent via web UI", "tags": ["chat", "client", "ui", "a2a"]}
        ],
    },
    {
        "name": "OpenCode A2A",
        "description": "Expose OpenCode through A2A with an inbound server surface and embedded outbound client.",
        "url": "https://github.com/Intelligent-Internet/opencode-a2a",
        "version": "1.0.0",
        "skills": [
            {"id": "opencode", "name": "OpenCode A2A", "description": "Coding agent exposed via A2A protocol", "tags": ["coding", "opencode", "developer", "a2a"]}
        ],
    },
    {
        "name": "PlanPilot",
        "description": "AI-powered travel concierge using specialized agents for weather, transport, hotels, and itineraries via A2A.",
        "url": "https://github.com/Waqar-743/PlanPilot",
        "version": "1.0.0",
        "skills": [
            {"id": "travel-concierge", "name": "Travel Concierge", "description": "Complete trip planning with weather, transport, hotels", "tags": ["travel", "concierge", "planning", "multi-agent"]}
        ],
    },
    {
        "name": "PiQrypt",
        "description": "Encryption and security platform for A2A agents. Demonstrates secure agent communication patterns.",
        "url": "https://github.com/PiQrypt/piqrypt",
        "version": "1.0.0",
        "skills": [
            {"id": "encryption", "name": "Agent Encryption", "description": "End-to-end encryption for A2A agent communication", "tags": ["security", "encryption", "privacy", "a2a"]}
        ],
    },
    {
        "name": "AgentUp",
        "description": "Portable, scalable, secure AI Agents with A2A protocol support.",
        "url": "https://github.com/always-further/AgentUp",
        "version": "1.0.0",
        "skills": [
            {"id": "portable-agents", "name": "Portable Agents", "description": "Build portable and secure A2A agents", "tags": ["portable", "scalable", "security", "framework"]}
        ],
    },
    {
        "name": "MultiGen",
        "description": "Multi-agent end-to-end application for multimodal agent collaboration via A2A protocol.",
        "url": "https://github.com/LiXiaoYaoCareFree/MultiGen",
        "version": "1.0.0",
        "skills": [
            {"id": "multimodal", "name": "Multimodal Collaboration", "description": "Multi-agent multimodal collaboration system", "tags": ["multimodal", "collaboration", "multi-agent", "generation"]}
        ],
    },
]

def register_agent(agent_data):
    """Register an agent into AgentHub."""
    card = {
        "name": agent_data["name"],
        "description": agent_data["description"],
        "url": agent_data["url"],
        "version": agent_data.get("version", "1.0.0"),
        "capabilities": {"streaming": False, "pushNotifications": False},
        "skills": agent_data.get("skills", []),
    }
    try:
        resp = httpx.post(
            AGENTHUB_URL,
            json={"agent_card_url": agent_data["url"], "agent_card": card},
            timeout=10,
        )
        data = resp.json()
        if resp.status_code == 200:
            print(f"  ✅ {agent_data['name']} → id={data.get('agent_id')}")
            return True
        else:
            print(f"  ❌ {agent_data['name']} → {data.get('error', 'unknown')}")
            return False
    except Exception as e:
        print(f"  ❌ {agent_data['name']} → {e}")
        return False

def main():
    print(f"🏪 AgentHub Seed — Registering {len(AGENTS)} agents...")
    print(f"   Target: {AGENTHUB_URL}")
    print()

    ok = 0
    fail = 0
    for agent in AGENTS:
        if register_agent(agent):
            ok += 1
        else:
            fail += 1
        time.sleep(0.2)  # Rate limit

    print()
    print(f"📊 Results: {ok} registered, {fail} failed")

    # Verify
    resp = httpx.get("https://eco.xiangma.ren/agents/api/stats", timeout=10)
    stats = resp.json()
    print(f"📈 AgentHub stats: {stats}")

if __name__ == "__main__":
    main()
