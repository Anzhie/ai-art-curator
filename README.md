# AI Art Curator 🎨🤖

An intelligent, interactive Art Curator built with a Retrieval-Augmented Generation (RAG) pipeline. The application helps users discover artworks that resonate with or gently transform their emotional state, while revealing the historical stories behind the art.

While conventional RAG systems operate on a strict linear pipeline (Query -> Retrieval -> Generation), AI Art Curator introduces intent routing, structured output validation, safety guardrails, and real-time user feedback collection.

## 🏗 Architecture & Core Concepts

*   Smart Intent Routing: Pre-filters non-art queries to maintain the curator's persona and save computational resources.
*   Vector Search Retrieval: Uses ChromaDB and sentence-transformers (multilingual-e5-large) to find conceptually relevant artworks from museum collections.
*   Cloud LLM Generation: Powered by Groq API (llama-3.3-70b-versatile) for ultra-fast, low-latency response generation.
*   Structured JSON Output: Guarantees strict schema validation via Pydantic for rich artwork cards (*Why this artwork?*, *Curator's Note*, *What to Notice*).
*   Safety Guardrails: Prevents prompt injection and out-of-domain queries before reaching the LLM.
*   Interactive Rating Feedback: Users can evaluate recommendations using a 1-5 star rating system.

## 🛠 Tech Stack

*   Frontend & UI: Streamlit
*   LLM Engine: Groq API (groq SDK with Qwen 3.8-27b)
*   Vector Database: ChromaDB
*   Embeddings: sentence-transformers (multilingual-e5-large)
*   Data Validation: Pydantic (v2+)
*   Dependency Management: Poetry

## 🔑 Environment Setup

Make sure to set the following environment variables (or add them to Streamlit Secrets / .env):

```bash
GROQ_API_KEY=your_groq_api_key_here

## 🚀 Roadmap Progress

* [x] v0.1.0 — Project Setup & Architecture
  - [x] Initial repository setup & directory structure
  - [x] Project architecture & technical design definition
  - [x] MIT License configuration
* [x] v0.2.0 — Artwork Knowledge Base
  - [x] Robust Ingestion Pipeline (Louvre, The Met, Rijksmuseum, Uffizi)
  - [x] Keyless HTML scraping for Rijksmuseum (IIIF/Micrio via Regex)
  - [x] Unified Data Schema (Pydantic validation)
  - [x] AI-Driven Semantic Enrichment (themes, emotions, keywords)
  - [x] Master Orchestration (pipeline.py & artworks.json)
  - [x] Test Suite (data import, schema validation & URL reachability)
* [x] v0.3.0 — Semantic Retrieval Engine
  - [x] Sentence Transformers (multilingual-e5-large)
  - [x] ChromaDB integration
  - [x] Vector index building
  - [x] Semantic search with Top-K results
  - [x] Unit test suite
* [x] v0.4.0 — Prompt-based Conversational RAG & Public Demo
  - [x] Cloud LLM Migration (Groq API & Qwen 3.8)
  - [x] System Prompt & Structured JSON Output Validation (Pydantic)
  - [x] Pre-LLM Safety Guardrails & Domain Intent Router
  - [x] Rich Artwork Cards (*Why this artwork*, *Curator's Note*, *What to Notice*)
  - [x] Ambiguity Handling & Clarification Flow
  - [x] Streamlit UI with Interactive 1-5 Star Rating Feedback
  - [x] Feedback Logging to Hugging Face Dataset
  - [x] Public Deployment to Streamlit Community Cloud
* [ ] v0.5.0 — Phase 2: Intelligent Dialogue (Data-driven Analyzer Node Integration based on User Feedback)
* [ ] v0.6.0 — Phase 3: LangGraph Workflow (Migration to State Machine Architecture)
* [ ] v0.7.0 — Portfolio Release Candidate (Prompt Optimization & Second-tier Testing)
* [ ] v1.0.0 — Production Release (Docker Deployment, Comprehensive E2E Test Suite)