# Sahayak — Internship Extraction Chatbot

A web chatbot that extracts internship listings from a local SQLite database and answers natural-language queries by generating SQL (Groq / LangChain → SQL) and formatting results for users.  
Built with Flask + LangChain (Groq LLM wrapper) and supports translation via `deep-translator`. The UI renders conversational messages and a results table for internships.

**Live demo:** https://huggingface.co/spaces/joshi-deepak08/Internship_extraction_chatbot-Sahayak

---

## Highlights

- Converts user questions (any language) → English → SQL (Groq via LangChain) → executes on local SQLite DB.  
- Returns a concise natural-language answer and a formatted table of internships (if applicable).  
- Focused for internship discovery use-cases (filters, stipends, links).  
- Lightweight Flask frontend for demo and quick iteration.

---

