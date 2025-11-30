# OpenAI Agents RAG Backend

This is a FastAPI backend utilizing the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) connected to Google Gemini (via OpenAI compatibility) and QDrant Cloud.

## Features

1.  **RAG Chat**: Context-aware chat using coursebook content stored in QDrant.
2.  **Selected Text Chat**: Explain specific text selections.
3.  **Latest Developments**: Fetches recent papers from Arxiv based on book sections.

## Prerequisites

*   **Gemini API Key**: Get one from Google AI Studio.
*   **QDrant Cloud**: Get a URL and API Key from QDrant Cloud.

## Deployment to Railway

1.  Fork or push this repository to GitHub.
2.  Create a new project on [Railway.app](https://railway.app).
3.  Select "Deploy from GitHub repo".
4.  Once the service is created, go to the **Variables** tab.
5.  Add the following Environment Variables:

| Variable | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your Google Gemini API Key |
| `QDRANT_URL` | Your QDrant Cluster URL (e.g., `https://xyz.us-east4-0.gcp.cloud.qdrant.io:6333`) |
| `QDRANT_API_KEY` | Your QDrant API Key |
| `PORT` | (Optional) Railway sets this automatically to `8000` |

6.  Railway will detect the `Dockerfile` and build the application automatically.

## Local Development

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Env Setup**:
    Create a `.env` file with the variables listed above.

3.  **Run**:
    ```bash
    uvicorn app.main:app --reload
    ```

## API Usage

**Ingest Data (Required first):**
```http
POST /api/ingest
{
  "text": "Photosynthesis is the process used by plants...",
  "metadata": {"chapter": "1"}
}