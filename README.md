# YouTube → Debut Album Lyrics Analyzer (Hash/JSON) 

This project takes a **YouTube music video URL**, tries to infer the **artist + debut album**, fetches the debut album’s songs/lyrics from song/lyrics database Genius, computes token/length statistics of songs and the debut album:

- prints the full analysis as JSON, or
- prints a deterministic hash derived from embedding the song-token-length sequence.

## What it does 

1. Scrapes the YouTube video information with Apify (`streamers/youtube-scraper` actor).
2. Calls OpenRouter (chat compilations) to infer: `Artist | DebutAlbum`
3. Builds the Genius album URL and scrapes all debut-album songs + lyrics via BeautifulSoup4, though it is clearly stated we should use Apify for album search, since Apify also has BeaufitulSoup-based BeautifulSoupCrawler object to navigate and scrape websites, to enhance deterministism in my project I decided to write my own scraper just for this task.
5. Computes per-song and album statistics:
   - char count, word count, token count (`tiktoken`), per-song lyrics md5
6. If output mode is `hash`:
   - concatenates token lengths,
   - embeds with `SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")`,
   - hashes the embedding vector (md5) and prints it.

## Requirements

- Python 3.9+ (recommended 3.10+)
- Internet access (Apify, OpenRouter, Genius, model download)
- apify_client, beautifulsoup4, einops, sentence_transformers, tiktoken, requests

## Setup

### 1) Create a virtual environment 

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### 2) API Keys and tokens
    Modify APIFY_API_TOKEN and OPENROUTER_API_KEY variables with your own API keys and tokens.

## Usage
      python3 UlkeEren_Aktas_Youtube_AI.py <url> <mode> (mode = hash | json)

