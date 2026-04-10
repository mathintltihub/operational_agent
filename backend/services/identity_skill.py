"""
Identity skill — handles greetings and identity questions locally.
No OpenAI call needed for these.
"""

IDENTITY_TRIGGERS = [
    "who are you", "what are you", "who r u", "who ru",
    "what is your name", "whats your name", "your name",
    "tell me about yourself", "introduce yourself",
    "what can you do", "what do you do", "how can you help",
    "hello", "hi", "hey", "hiya", "howdy", "greetings",
    "good morning", "good afternoon", "good evening",
    "help", "start", "begin"
]

IDENTITY_RESPONSE = """👋 **Hey there! I'm the Operations Agent.**

I'm an AI-powered IT Operations assistant. Here's what I do:

🎯 **My Role:**
I triage and analyze IT support tickets so your team can respond faster and smarter.

🛠️ **My Skills:**
- 🔍 **Classify** issues — Server, Network, Database, Application, or Access
- 🚨 **Detect priority** — Critical, High, Medium, or Low
- 👥 **Route tickets** to the right team automatically
- 🧭 **Suggest troubleshooting steps** that are safe and practical
- 📊 **Score confidence** so you know how reliable the analysis is

💬 **How to use me:**
Just describe your IT issue in plain English — I'll handle the rest.

*Example: "Our production database is timing out and users can't log in."*"""


def is_identity_question(message: str) -> bool:
    """Returns True if the message is a greeting or identity question."""
    msg = message.lower().strip()
    return any(trigger in msg for trigger in IDENTITY_TRIGGERS)


def get_identity_response() -> str:
    return IDENTITY_RESPONSE
