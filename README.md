# AWS Automation System with AI Agents

This project implements an intelligent automation system for AWS using AI agents. It uses a local LLM for agent implementation and a multi-agent orchestrator for coordination.

## Features

- Multi-tenant AWS management
- Intelligent resource provisioning
- Cost optimization
- Security and compliance monitoring
- Automated troubleshooting
- Infrastructure as Code support

## Project Structure

```
.
├── agents/                 # Individual agent implementations
│   ├── provisioning/      # User/resource provisioning agents
│   ├── monitoring/        # Monitoring and alerting agents
│   ├── compliance/        # Compliance checking agents
│   └── troubleshooting/   # Issue diagnosis agents
├── orchestrator/          # Multi-Agent Orchestrator setup
├── core/                  # Core functionality and utilities
├── frontend/             # NextJS frontend application
└── api/                  # FastAPI backend service
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Start the services:
```bash
# Start backend API
uvicorn api.main:app --reload

# Frontend is already set up in the frontend/ directory
```

## Architecture

- Uses local LLM (phi-2) for AWS-specific tasks
- Multi-Agent Orchestrator for agent coordination
- AWS SDK for resource management
- Next.js frontend for user interface

## License

MIT
# aws-agentic
