# AI Art Curator 🎨🤖

An agentic RAG application that helps users discover artworks that resonate with or gently transform their emotional state, while revealing the historical stories behind the art.

While conventional RAG systems operate on a strict linear pipeline (Query -> Retrieval -> Generation), AI Art Curator introduces an interactive agentic loop. It dynamically evaluates conversation context, tracks dialogue state, and decides whether to ask clarifying questions or deliver a curated recommendation.

## 🏗 Architecture & Core Concepts

The project demonstrates advanced LLM orchestration and data-intensive system engineering practices:
* Agentic Routing: State management and transition workflows driven by LangGraph.
* Intelligent Analyzer Node: A custom decision-making component evaluating search ambiguity and context sufficiency before generating responses.
* Semantic Retrieval Engine: High-density vector search leveraging local embeddings and cross-lingual alignment.
* Clean Architecture: Strict separation of data ingestion, retrieval logic, agent workflows, and the presentation layer.

## 🛠 Tech Stack

* AI Frameworks: LangChain, LangGraph (v0.5+)
* LLM & Embeddings: Ollama (Gemma 3 / Qwen), multilingual-e5-large
* Vector Database: ChromaDB
* Backend & UI: FastAPI, Streamlit
* Environment: Python 3.11+, Docker

## 🚀 Roadmap Progress

* [x] v0.1.0 — Repository Setup, Architecture Blueprint & MIT License
* [x] v0.2.0 — Artwork Knowledge Base (Museum APIs Data Ingestion & Pydantic Validation)
* [ ] v0.3.0 — Semantic Retrieval Engine (ChromaDB Indexing & Vector Search)
* [ ] v0.4.0 — Phase 1: Prompt-based Conversational RAG + Public Demo (Streamlit, HF Spaces, Safety Guardrails & Local Feedback Loop)
* [ ] v0.5.0 — Phase 2: Intelligent Dialogue (Data-driven Analyzer Node Integration based on User Feedback)
* [ ] v0.6.0 — Phase 3: LangGraph Workflow (Migration to State Machine Architecture)
* [ ] v0.7.0 — Portfolio Release Candidate (Prompt Optimization & Second-tier Testing)
* [ ] v1.0.0 — Production Release (Docker Deployment, Comprehensive E2E Test Suite)