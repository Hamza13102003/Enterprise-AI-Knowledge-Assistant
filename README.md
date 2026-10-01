# Enterprise AI Knowledge Assistant

An end-to-end AI-powered knowledge assistant that allows authenticated users to upload documents and ask natural-language questions about their own documents.

The project demonstrates how modern AI application components can be combined into a complete system:

**Document Upload → Text Extraction → Chunking → Embeddings → Vector Search → RAG → Local LLM → Answer + Sources**

This is a portfolio project focused on demonstrating practical AI engineering, backend development, RAG architecture, authentication, vector databases, Docker, and frontend integration.

---

## Overview

The Enterprise AI Knowledge Assistant is designed to provide a private, document-based question-answering experience.

Users can:

- Create an account and authenticate securely
- Upload documents
- Store and process their documents
- Ask questions about their uploaded knowledge base
- Retrieve relevant information using semantic search
- Generate answers using a locally running LLM
- See the retrieved source information used for the answer

A major part of the project is **per-user document isolation**. During retrieval, the system filters documents using the authenticated user's identity so that one user's documents are not retrieved for another user.

---

## Main Features

- User registration
- JWT-based authentication
- Password hashing
- Protected API endpoints
- Per-user document ownership
- PDF document ingestion
- DOCX document ingestion
- TXT document ingestion
- Text extraction
- Text chunking
- Local embedding generation using Ollama
- Vector storage using Qdrant
- Semantic similarity search
- Retrieval-Augmented Generation (RAG)
- Local LLM inference using Ollama
- Source-aware responses
- PostgreSQL database
- FastAPI REST API
- React + TypeScript frontend
- Docker Compose infrastructure
- Backend testing with Pytest
- Code quality checks with Ruff
- Static type checking with MyPy
- Frontend linting with ESLint
- Frontend production build validation

---

# System Architecture

```text
                         ┌─────────────────────────┐
                         │     React Frontend      │
                         │   React + TypeScript     │
                         └────────────┬────────────┘
                                      │
                                      │ HTTP / JWT
                                      ▼
                         ┌─────────────────────────┐
                         │      FastAPI Backend    │
                         │                         │
                         │ Authentication          │
                         │ Document APIs            │
                         │ RAG API                  │
                         └───────┬─────────┬───────┘
                                 │         │
                    ┌────────────┘         └─────────────┐
                    ▼                                    ▼
          ┌──────────────────┐                 ┌──────────────────┐
          │   PostgreSQL     │                 │      Qdrant      │
          │                  │                 │                  │
          │ Users             │                 │ Document vectors │
          │ Documents         │                 │ Metadata         │
          │ Application data  │                 │ Semantic search  │
          └──────────────────┘                 └────────┬─────────┘
                                                        │
                                                        │ Retrieved
                                                        │ Context
                                                        ▼
                                               ┌──────────────────┐
                                               │      Ollama      │
                                               │                  │
                                               │ Embeddings       │
                                               │ Local LLM        │
                                               └──────────────────┘