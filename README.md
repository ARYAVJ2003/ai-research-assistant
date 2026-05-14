# AI Research Assistant

A Python-based AI assistant that can split user queries into tasks, perform research (with optional tool calls), and provide structured answers. Built with **LangGraph**, **LangChain**, and **Google Gemini** LLMs.

---

## Features

- Split complex queries into manageable tasks.
- Perform calculations and web search via tools.
- Maintain conversation history with memory checkpointing.
- Streamlit UI for interactive chat.
- Easily extendable with custom tools.

---


## Setup

1. Clone the repo:

```bash
git clone https://github.com/ARYAVJ2003/ai-research-assistant.git
cd ai-research-assistant

2.Install dependencies:

pip install -r requirements.txt

3. Create a .env file and add your Google API key:

GOOGLE_API_KEY=your_api_key_here


##Usage

Run the Streamlit app:

streamlit run main.py
