# 🔍 ResearchMate - 5-Agent AI Research Assistant

ResearchMate is an autonomous multi-agent research system coordinated by a **LangGraph Orchestrator**, using **Tavily Search API** for real-time web exploration and **Google Gemini** for fact extraction, verification, strategic analysis, and executive report synthesis.

---

## 🤖 Multi-Agent Architecture

```
                       User Research Topic
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │       🎛️ LangGraph Orchestrator              │
        │  • Manages State                             │
        │  • Decides next agent                        │
        │  • Handles errors & fallbacks                │
        └──────────────────────┬───────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. 🔍 Researcher Agent (Tavily API)                         │
  │    Searches internet, retrieves articles, metadata & URLs   │
  └────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. 📊 Information Extraction Agent (Gemini API)             │
  │    Extracts verified facts, statistics, dates & metrics     │
  └────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. 🛡️ Fact Checker Agent (Gemini API)                       │
  │    Verifies claims against sources, flags unsupported data  │
  └────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. 📈 Analysis Agent (Gemini API)                           │
  │    Identifies trends, comparisons, opportunities & risks    │
  └────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 5. 📝 Report Generator Agent (Gemini API)                   │
  │    Creates publication-grade executive report with links    │
  └────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
                    📄 Final Research Report
```

---

## 📁 Project Directory Structure

```
research_ai/
│
├── .env                       # API keys (GEMINI_API_KEY, TAVILY_API_KEY)
├── .env.example               # Template for API keys
├── requirements.txt           # Python dependencies
├── config.py                  # Configuration, model settings & key verification
│
├── agents/                    # Specialized AI Agents
│   ├── __init__.py            # Agent exports
│   ├── gemini_client.py       # Resilient Gemini API client with fallback
│   ├── researcher_agent.py    # 1. Researcher Agent (Tavily search)
│   ├── extractor_agent.py     # 2. Information Extraction Agent (Facts/Metrics)
│   ├── fact_checker_agent.py  # 3. Fact Checker Agent (Cross-referencing)
│   ├── analysis_agent.py      # 4. Analysis Agent (Trends & Opportunities)
│   └── report_generator_agent.py # 5. Report Generator Agent (Executive Synthesis)
│
├── tools/                     # Agent Tools
│   ├── __init__.py
│   └── search_tool.py         # Tavily web search integration
│
├── graph.py                   # 🎛️ LangGraph Orchestrator (StateGraph & Router)
├── research_pipeline.py       # CLI Runner with real-time agent streaming
├── test_apis.py               # Diagnostic test script for API connectivity
├── app.py                     # 🌐 Interactive Streamlit Dashboard
└── reports/                   # Saved research reports (.md & .txt)
```

---

## ⚡ Setup & Installation

### 1. Python Environment

Ensure Python 3.10+ is installed. Activate the project environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

Or install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables (.env)

Make sure `.env` contains your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## 🚀 Execution Options

### 1. Test API Connectivity
Verify that both Gemini and Tavily keys and network connections work:
```bash
python test_apis.py
```

### 2. Launch Interactive Streamlit Web App
Launch the web interface:
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

### 3. Run via CLI (Terminal)
Execute the multi-agent workflow directly from your command line:
```bash
python research_pipeline.py
```
Or run the orchestrator graph directly:
```bash
python graph.py
```

---

## 📄 Output Reports
All reports are automatically archived in `reports/`:
- Timestamped reports: `reports/YYYYMMDD_HHMMSS_<topic>.md`
- Latest report copy: `reports/research_report.txt`
