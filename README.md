# Squarest Notebook Simple

A simplified, reliable notebook application built with Streamlit and SQLite. No complex dependencies, just works!

## Features

- 📚 **Knowledge Sources**: Upload and manage documents (PDF, Word, Text, CSV)
- 💬 **AI Chat**: Chat with multiple AI providers (OpenAI, Anthropic, Google)
- 📝 **Notes**: Create and organize notes linked to sources
- 🎙️ **Podcasts**: (Coming soon) Generate AI podcasts from your content
- 💾 **SQLite Database**: Reliable, zero-configuration database

## Quick Start

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/squarest-notebook-simple.git
cd squarest-notebook-simple
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. Run the application:
```bash
streamlit run app.py
```

The app will open at http://localhost:8501

## Deploy to Render

### One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Manual Deploy

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service
4. Select your forked repository
5. Use these settings:
   - **Runtime**: Docker
   - **Port**: 8501
6. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - (Optional) `ANTHROPIC_API_KEY`: Your Anthropic API key
   - (Optional) `GOOGLE_API_KEY`: Your Google AI API key
7. Deploy!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes (or use another provider) |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude models | No |
| `GOOGLE_API_KEY` | Google API key for Gemini models | No |

## Why This Works

Unlike the original squarest-notebook-lm, this simplified version:

- **Uses SQLite** instead of SurrealDB (no connection issues!)
- **Single process** - No complex worker queues or supervisord
- **Simple deployment** - Just run Streamlit, that's it
- **Reliable** - Works locally and on any cloud platform
- **No timing issues** - Everything runs in the same process

## Tech Stack

- **Frontend**: Streamlit
- **Database**: SQLite (file-based, zero config)
- **AI**: LangChain with multiple providers
- **Language**: Python 3.11+

## Contributing

Feel free to submit issues and pull requests!

## License

MIT License - Use it however you want!
