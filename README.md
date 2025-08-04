# LLM-Based Insurance Policy Decision System

This is an LLM-powered document query system that extracts structured information from natural language insurance-related queries and returns clause-level decisions with justifications.

---

## 🚀 Features

- Parses age, gender, procedure, location, policy duration from user queries
- Uses semantic similarity to find matching insurance clauses
- Makes decisions (approve/reject) based on policy rules
- Clause-level justifications
- Integration and performance test modules

---

## 🗃️ Files & Purpose

| File/Folder | Description |
|-------------|-------------|
| `everything.py` | Main orchestrator |
| `parse.py` | Extract structured data from query |
| `test_parser.py` | Unit tests for parser |
| `test_decision_engine.py` | Tests for decision logic |
| `test_integration.py` | End-to-end system test |
| `test_performance.py` | Performance evaluation |
| `enter_query.py` | Manual query entry for testing |
| `all_clauses.json` | Raw clauses |
| `all_clauses_with_embeddings.json` | Clause embeddings |
| `clauses/` | Clause text files |
| `models/` | Saved models or embeddings |
| `output/` | Output and logs |
| `myenv/` | Local virtual environment (ignored) |

---

## 💻 How to Run

1. **Create a virtual environment**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
