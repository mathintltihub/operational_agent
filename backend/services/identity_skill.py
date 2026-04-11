"""
Identity skill — handles all non-ticket conversations locally.
Covers: greetings, identity, capabilities, help, thanks, farewells,
        status checks, sample issues, and unknown inputs.
No Gemini API call needed for any of these.
"""

# ---------------------------------------------------------------------------
# Trigger maps — each key is a skill name, value is list of trigger phrases
# ---------------------------------------------------------------------------

SKILL_TRIGGERS = {

    "greeting": [
        "hello", "hi", "hey", "hiya", "howdy", "greetings",
        "good morning", "good afternoon", "good evening", "good night",
        "sup", "what's up", "whats up", "yo", "start", "begin"
    ],

    "identity": [
        "who are you", "what are you", "who r u", "who ru",
        "what is your name", "whats your name", "your name",
        "tell me about yourself", "introduce yourself",
        "are you a bot", "are you ai", "are you human",
        "are you real", "what kind of bot", "what type of ai"
    ],

    "capabilities": [
        "what can you do", "what do you do", "how can you help",
        "what are your skills", "what are your features",
        "what are your capabilities", "show me what you can do",
        "list your features", "what do you support",
        "what issues can you handle", "what problems can you solve"
    ],

    "help": [
        "help", "help me", "i need help", "how does this work",
        "how to use", "how do i use you", "guide me",
        "show me how", "instructions", "tutorial",
        "how do i submit a ticket", "how do i report an issue"
    ],

    "status": [
        "are you online", "are you working", "are you available",
        "are you there", "you there", "ping", "status",
        "system status", "is the system up", "is the agent running"
    ],

    "thanks": [
        "thank you", "thanks", "thank u", "thx", "ty",
        "appreciate it", "great job", "well done", "nice work",
        "that was helpful", "you're helpful", "good job", "awesome"
    ],

    "farewell": [
        "bye", "goodbye", "see you", "see ya", "later",
        "take care", "cya", "good bye", "have a good day",
        "talk later", "i'm done", "im done", "exit", "quit"
    ],

    "sample": [
        "show me an example", "give me an example", "example ticket",
        "sample ticket", "demo", "show demo", "test ticket",
        "what does a ticket look like", "how should i describe my issue",
        "show me a sample", "give me a sample"
    ],

    "issue_types": [
        "what issue types", "what categories", "what types of issues",
        "what kind of issues", "what problems do you classify",
        "list issue types", "show issue types", "what can you classify"
    ],

    "priority": [
        "how do you determine priority", "how is priority set",
        "what is critical", "what is high priority",
        "priority levels", "how do you prioritize",
        "what makes something critical", "explain priority"
    ],

    "team_routing": [
        "which team", "how do you route", "team routing",
        "who handles what", "which team gets what",
        "how are tickets assigned", "how does routing work",
        "what teams do you support"
    ],

    "unknown": []  # catch-all, handled separately
}

# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------

RESPONSES = {

    "greeting": """👋 **Hey! Welcome to Operations Agent.**

I'm your AI-powered IT Operations assistant, ready to triage your support tickets instantly.

Just describe your IT issue and I'll:
- 🔍 Classify the issue type
- 🚨 Detect the priority level
- 👥 Route it to the right team
- 🧭 Suggest troubleshooting steps

What's the issue you're facing today?""",

    "identity": """🤖 **I'm the Operations Agent** — an AI-powered IT triage assistant.

**Built to do one thing exceptionally well:**
Analyze IT support tickets and get them to the right team, fast.

**Who powers me:**
I'm powered by **Ollama with LLaMA 3** — running entirely on your local machine. No external APIs, no cloud dependencies.

**What I'm not:**
I'm not a general-purpose chatbot. I'm purpose-built for IT Operations triage — that's my only job and I do it well.

**My classification engine covers:**
- 🖥️ Server issues
- 🌐 Network issues
- 🗄️ Database issues
- 📱 Application issues
- 🔐 Access & permission requests

Type your IT issue and I'll get to work immediately.""",

    "capabilities": """🛠️ **Here's everything I can do:**

**🔍 Issue Classification**
Identify whether your ticket is a Server, Network, Database, Application, or Access issue.

**🚨 Priority Detection**
Automatically determine if the issue is Critical, High, Medium, or Low priority based on impact signals.

**👥 Team Routing**
Route tickets to the correct team:
- Server Team → infrastructure & VM issues
- Network Team → connectivity, VPN, DNS
- Database Team → DB timeouts, replication, queries
- Application Support → crashes, HTTP errors, deployments
- Service Desk → access requests, password resets
- Security Team → suspicious activity, breaches
- Manual Review → unclear or complex tickets

**🧭 Troubleshooting Steps**
Suggest safe, practical steps to begin resolving the issue immediately.

**📊 Confidence Scoring**
Rate how confident I am in the classification (0–100%) so your team knows when to trust the result.

**💬 Conversational Interface**
Talk to me in plain English — no forms, no dropdowns, just describe the problem.""",

    "help": """📖 **How to use Operations Agent:**

**Step 1 — Describe your issue**
Type a clear description of the IT problem in the chat box below.

**Step 2 — Get instant analysis**
I'll immediately classify the issue, set priority, assign a team, and suggest troubleshooting steps.

**Step 3 — Review the results**
Check the analysis card for full details. Click **View Full Details** for the complete breakdown.

**Tips for better results:**
- ✅ Include what's broken and how it's affecting users
- ✅ Mention when it started
- ✅ Include any error messages or codes
- ✅ Say how many users are affected
- ❌ Avoid vague descriptions like "something is wrong"

**Quick examples to try:**
- *"Production database is timing out, 50+ users affected"*
- *"VPN users can't access the internal portal since 9am"*
- *"Web server returning HTTP 500 on all requests"*
- *"Need admin access to the analytics dashboard"*""",

    "status": """✅ **Operations Agent is online and fully operational.**

**System Status:**
- 🟢 API Backend — Running
- 🟢 Ollama (LLaMA 3) — Connected
- 🟢 Skill Engine — Ready
- 🟢 Logging Service — Active

I'm ready to analyze your IT tickets. Go ahead and describe your issue!""",

    "thanks": """😊 **Happy to help!**

That's what I'm here for — making IT triage faster and smarter.

If you have another issue to report or want to analyze a new ticket, just describe it and I'll get right on it.""",

    "farewell": """👋 **Take care!**

If any IT issues come up, I'll be right here — 24/7, no waiting.

Have a great day! 🚀""",

    "sample": """📋 **Here's an example of a well-described IT ticket:**

---
*"Our production application has been returning HTTP 500 errors on all API endpoints since 2:30 PM. Approximately 200 users are affected and cannot complete transactions. No recent deployments were made. Error logs show a NullPointerException in the payment service."*

---

**What makes this a good ticket:**
- ✅ Describes the exact symptom (HTTP 500)
- ✅ States when it started (2:30 PM)
- ✅ Quantifies impact (200 users)
- ✅ Rules out recent changes (no deployments)
- ✅ Includes error details (NullPointerException)

**My analysis of that ticket would be:**
- 📱 Issue Type: Application
- 🔴 Priority: Critical
- 👥 Team: Application Support
- 📊 Confidence: ~95%

Try describing your own issue now!""",

    "issue_types": """📂 **Issue types I can classify:**

| Type | Examples |
|------|---------|
| 🖥️ **Server** | CPU at 100%, VM down, disk full, host unreachable, SSH failure |
| 🌐 **Network** | VPN issues, DNS failure, high latency, firewall blocks, packet loss |
| 🗄️ **Database** | Connection timeout, replication lag, query failures, DB crash |
| 📱 **Application** | HTTP 500 errors, app crash, deployment failure, service unavailable |
| 🔐 **Access/Request** | Password reset, permission denied, role request, new access needed |
| ❓ **Unknown** | Vague or unclear tickets — routed to Manual Review |

Just describe your issue in plain English and I'll match it to the right category automatically.""",

    "priority": """🚨 **How I determine priority:**

| Level | Criteria |
|-------|---------|
| 🔴 **Critical** | Production down, full outage, all users affected, core service unavailable |
| 🟠 **High** | Major functionality broken, many users impacted, time-sensitive |
| 🟡 **Medium** | Single user or team blocked, workaround may exist |
| 🟢 **Low** | Minor issue, informational request, low urgency access request |

**Key signals I look for:**
- Number of users affected
- Whether production is impacted
- Presence of words like "outage", "down", "critical", "urgent"
- Whether a workaround exists
- Time sensitivity of the issue

The more detail you provide, the more accurate the priority detection.""",

    "team_routing": """👥 **How ticket routing works:**

| Team | Handles |
|------|---------|
| 🖥️ **Server Team** | Physical/virtual server issues, CPU, memory, disk, SSH |
| 🌐 **Network Team** | Connectivity, VPN, DNS, firewall, latency, packet loss |
| 🗄️ **Database Team** | DB timeouts, replication, query failures, credentials |
| 📱 **Application Support** | App crashes, HTTP errors, deployments, service failures |
| 🔐 **Service Desk** | Access requests, password resets, permission changes |
| 🛡️ **Security Team** | Suspicious logins, breaches, unauthorized access attempts |
| 🔍 **Manual Review** | Unclear tickets with confidence score below 50% |

Routing is automatic — I analyze the ticket content and assign the most appropriate team based on the issue type and context.""",

    "unknown": """🤔 **I'm not sure I understood that.**

I'm specialized in IT Operations ticket triage. Here's what I can help with:

- 🔍 Analyze and classify IT support tickets
- 🚨 Detect issue priority
- 👥 Route tickets to the right team
- 🧭 Suggest troubleshooting steps

**Try one of these:**
- Describe an IT issue you're facing
- Type **"help"** for usage instructions
- Type **"what can you do"** to see my capabilities
- Type **"example"** to see a sample ticket

Or just describe your IT problem in plain English and I'll handle the rest!"""
}

# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

def detect_skill(message: str) -> str:
    """Detect which skill should handle this message. Returns skill name."""
    msg = message.lower().strip()

    for skill, triggers in SKILL_TRIGGERS.items():
        if skill == "unknown":
            continue
        if any(trigger in msg for trigger in triggers):
            return skill

    return None  # None means route to ticket analyzer


def is_identity_question(message: str) -> bool:
    """Returns True if the message should be handled by a local skill."""
    return detect_skill(message) is not None


def get_skill_response(message: str) -> str:
    """Returns the appropriate skill response for the message."""
    skill = detect_skill(message)
    if skill and skill in RESPONSES:
        return RESPONSES[skill]
    return RESPONSES["unknown"]


# Keep backward-compatible alias used in main.py
def get_identity_response() -> str:
    return RESPONSES["identity"]
