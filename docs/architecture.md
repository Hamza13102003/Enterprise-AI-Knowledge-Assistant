# System Architecture

## 1. Overview

The Enterprise AI Knowledge Assistant is an end-to-end AI application that combines a web frontend, REST API, relational database, document processing pipeline, vector database, and local AI models.

The high-level architecture is:

```text
┌─────────────────────────────────────────────────────────────┐
│                        User                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  React + TypeScript Frontend                │
│                                                             │
│  Login │ Register │ Dashboard │ Documents │ AI Assistant   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ REST API + JWT
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                        │
│                                                             │
│  Authentication │ Documents │ RAG │ Users │ Health         │
└───────┬─────────────────────┬───────────────────┬───────────┘
        │                     │                   │
        ▼                     ▼                   ▼
┌───────────────┐      ┌───────────────┐   ┌────────────────┐
│  PostgreSQL   │      │    Qdrant     │   │    Ollama      │
│               │      │               │   │                │
│ Users         │      │ Embeddings    │   │ Embeddings     │
│ Documents     │      │ Chunks        │   │ Local LLM      │
│ Metadata      │      │ Metadata      │   │                │
└───────────────┘      └───────────────┘   └────────────────┘