# Product Overview

## Purpose
Operations Agent is a local-first MVP for an AI-based IT Operations platform that automates ticket triage and classification for IT support teams. It eliminates manual ticket sorting by using AI to analyze, classify, prioritize, and route support tickets to the appropriate teams.

## Value Proposition
- **Automated Triage**: Instantly analyzes incoming IT support tickets without manual intervention
- **Intelligent Classification**: Categorizes tickets into server, network, database, application, or access/request issues
- **Priority Detection**: Automatically identifies critical, high, medium, or low priority levels
- **Smart Routing**: Recommends the appropriate team for ticket assignment based on issue type
- **Actionable Guidance**: Provides practical, safe troubleshooting steps for each ticket
- **Local-First**: All data stays local with JSON-based logging, no external dependencies required
- **Flexible AI**: Works with OpenAI API or in mock mode using keyword-based analysis

## Key Features

### Core Capabilities
- **Ticket Analysis Engine**: Powered by LangChain + OpenAI (or mock mode) for intelligent ticket processing
- **Issue Classification**: Automatically categorizes tickets into 5 main types:
  - Server issues (CPU, memory, disk, connectivity)
  - Network issues (VPN, latency, connectivity)
  - Database issues (connections, replication, performance)
  - Application issues (crashes, errors, performance)
  - Access/Request issues (permissions, password resets)
- **Priority Detection**: Identifies urgency levels (critical, high, medium, low)
- **Team Routing**: Recommends assignment to appropriate teams (Infrastructure, Network, Database, Application, Access Management)
- **Troubleshooting Suggestions**: Generates practical, safe troubleshooting steps
- **Confidence Scoring**: Provides 0-1 confidence score for each analysis
- **Reasoning Summary**: Explains the classification logic

### Technical Features
- **Local JSON Logging**: Saves all request/response pairs for audit and analysis
- **Mock Mode**: Keyword-based analysis when no API key is available
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Sample Tickets**: 12 pre-configured sample tickets for testing
- **Health Monitoring**: Built-in health check endpoint

## Target Users

### Primary Users
- **IT Support Teams**: First-line support staff who need to quickly triage and route tickets
- **IT Operations Managers**: Team leads who need to ensure proper ticket distribution
- **DevOps Engineers**: Technical staff who want to automate ticket classification

### Use Cases
1. **Ticket Triage**: Automatically classify incoming support tickets during business hours
2. **After-Hours Routing**: Ensure critical tickets reach on-call teams immediately
3. **Workload Balancing**: Distribute tickets evenly across specialized teams
4. **Training Tool**: Help new support staff learn proper ticket classification
5. **Demo/Testing**: Evaluate AI-based ticket triage without production integration
6. **Offline Operations**: Process tickets without internet connectivity using mock mode

## Deployment Model
- **Local MVP**: Runs entirely on local machine with Python backend and HTML/CSS/JS frontend
- **No Cloud Dependencies**: Works offline with mock mode
- **Optional AI**: Can use OpenAI API for enhanced analysis or run keyword-based mock mode
- **Simple Setup**: Virtual environment, pip install, and run - no complex infrastructure
