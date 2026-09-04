# AI Art Curator 🎨🤖

🌐 Live Demo: [ai-art-curator.streamlit.app](https://ai-art-curator-app.streamlit.app/)

An intelligent, interactive Art Curator built with a Retrieval-Augmented Generation (RAG) pipeline. The application helps users discover artworks that resonate with or gently transform their emotional state, while revealing the historical stories behind the art.

While conventional RAG systems operate on a strict linear pipeline (Query -> Retrieval -> Generation), AI Art Curator introduces an intelligent Query Analyzer node, dynamic conversational history resolution, structured output validation, safety guardrails, and real-time user feedback collection.

## 🏗 Architecture & Core Concepts

*   Intelligent Query Analyzer: Replaces legacy routing with a dedicated LLM node that evaluates domain relevance (is_off_topic), detects abstract requests (is_ambiguous), and performs history-aware query rewriting (search_intent).
*   Conversational History Resolution: Resolves short or contextual user follow-ups (e.g., "green ones") against past conversation context before performing vector retrieval.
*   Vector Search Retrieval: Uses ChromaDB and sentence-transformers (multilingual-e5-large) to find conceptually relevant artworks from museum collections using optimized search intents.
*   3-Way Branching Architecture: Routes execution cleanly into OFF_TOPIC guardrails, CLARIFY questions, or RECOMMEND artwork cards via strict ResponseStatus enums.
*   Cloud LLM Generation: Powered by Groq API (llama-3.3-70b-versatile / qwen-2.5-32b) for ultra-fast, low-latency response generation.
*   Structured JSON Output: Guarantees strict schema validation via Pydantic for rich artwork cards (*Why this artwork?*, *Curator's Note*, *What to Notice*).
*   Safety Guardrails: Prevents prompt injection and out-of-domain queries before reaching the LLM.
*   Interactive Rating Feedback: Users evaluate genuine recommendations using a 1-5 star rating system, with state management suppressing feedback widgets on clarification or off-topic turns.

## 🛠 Tech Stack

*   Frontend & UI: Streamlit
*   LLM Engine: Groq API (groq SDK with native JSON mode)
*   Vector Database: ChromaDB (Git LFS pre-built index)
*   Embeddings: sentence-transformers (multilingual-e5-large)
*   Data Validation: Pydantic (v2+)
*   Dependency Management: Poetry

## 🔑 Environment Setup

Make sure to set the following environment variables (or add them to Streamlit Secrets / .env):

```bash
GROQ_API_KEY=your_groq_api_key_here
```

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
  - [x] Rich Artwork Cards (*Why this artwork*, *Curator\'s Note*, *What to Notice*)
  - [x] Ambiguity Handling & Clarification Flow
  - [x] Streamlit UI with Interactive 1-5 Star Rating Feedback
  - [x] Feedback Logging to Hugging Face Dataset
  - [x] Public Deployment to Streamlit Community Cloud
* [x] v0.5.0 — Intelligent Query Analyzer & Contextual Dialogue Engine
  - [x] Dedicated QueryAnalyzer module with AnalyzerDecision schema (Pydantic v2)
  - [x] History-Aware Query Rewriting & Anaphora Resolution
  - [x] 3-Way Branching Architecture (OFF_TOPIC, CLARIFY, RECOMMEND)
  - [x] Deprecated Legacy intent_router.py
  - [x] UI State Management Polish (Feedback Widget Suppressed on Non-Recommendations)
  - [x] Comprehensive Test Suite (QueryAnalyzer unit tests & mocked RAG engine flow)
* [ ] v0.6.0 — Phase 3: LangGraph Workflow (Migration to State Machine Architecture)
* [ ] v0.7.0 — Portfolio Release Candidate (Prompt Optimization & Second-tier Testing)
* [ ] v1.0.0 — Production Release (Docker Deployment, Comprehensive E2E Test Suite)