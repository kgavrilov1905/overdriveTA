# 🆓 Free Gemini API Setup for RAG System

This application now uses Google's **Gemini API** for both embeddings AND LLM generation - completely **FREE**!

## Why Gemini API?

- **🆓 Completely Free**: 1,500 requests per day for both embeddings AND chat
- **🔑 Simple Setup**: Just need one API key for everything
- **📏 High Quality**: 768-dimensional embeddings from `text-embedding-004`
- **🚀 Latest LLM**: Gemini 2.0 Flash for lightning-fast responses
- **⚡ Optimized**: Task-specific embeddings + cutting-edge language model

## Quick Setup (2 minutes)

### 1. Get Your Free API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 2. Add to Environment

Add this to your `.env` file:

```bash
# Gemini API (Free tier - 1,500 requests/day for EVERYTHING!)
GOOGLE_API_KEY=your_gemini_api_key_here

# Supabase Configuration  
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# OpenAI (optional fallback)
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

That's it! The system will automatically use Gemini embeddings.

## Model Information

### Embeddings
- **Model**: `models/text-embedding-004`
- **Dimensions**: 768
- **Max Input**: ~20,000 characters
- **Task Types**: Optimized for both documents and queries

### LLM
- **Model**: `gemini-2.0-flash-exp`
- **Speed**: Lightning fast responses
- **Max Output**: 1,000 tokens
- **Context**: Large context window

### Shared Limits
- **Daily Limit**: 1,500 requests total (free tier)

## Fallback System

### For Embeddings:
1. **Gemini API** (Primary - Free)
2. **OpenAI** (If API key provided)
3. **Local Sentence Transformers** (Always available)

### For LLM:
1. **Gemini 2.0 Flash** (Primary - Free)
2. **OpenAI GPT-4** (If API key provided)
3. **Fallback text response** (Basic functionality)

## Cost Comparison

| Provider | Free Tier | Cost After |
|----------|-----------|------------|
| **Gemini** | 1,500/day | $0.0001/1K chars |
| OpenAI | $5 credit | $0.0001/1K tokens |
| Local | Unlimited | Hardware only |

## Troubleshooting

If you see "Using local sentence transformers" or "LLM functionality limited":

1. Check `GOOGLE_API_KEY` is set correctly
2. Verify you haven't exceeded the daily limit (1,500 requests total)
3. Check [AI Studio](https://aistudio.google.com/) for any issues
4. Make sure the API key has access to both Gemini models

## Pro Tips

- The free tier of 1,500 requests/day is usually enough for development
- Gemini embeddings work great for multilingual content
- Task-specific optimization improves retrieval quality 