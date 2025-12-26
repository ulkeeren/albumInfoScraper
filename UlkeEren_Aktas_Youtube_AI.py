import json
import hashlib
import asyncio
import requests
import sys
from apify_client import ApifyClientAsync
import lyricRetriever
from sentence_transformers import SentenceTransformer

APIFY_API_TOKEN = ""
OPENROUTER_API_KEY = ""

def requestArtistNameAndDebut(title, uploader):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}"
        },
        data=json.dumps({
            "model": "openai/gpt-5.2", 
            "messages": [
            {
                "role": "user",
                "content": f"I'll now share you the title and uploader of a music video. Who is the artist of this song and what's the name of the debut album of this artist? Respond in \"Artist | Album\" format.\n Title: {title}, Uploader:{uploader}."
            }
            ],
            "reasoning": {"enabled": True}
            }
        )
    )
    return response.json()["choices"][0]["message"]["content"]

def encodeThenHash(analysis):
    all_tokens = ""
    for song in analysis["songs"]:
        all_tokens += f"{song["lyrics_lenght_tokens"]},"
    all_tokens = all_tokens[:-2]

    model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
    embeddings = model.encode(all_tokens,)
    string_embeddings = ",".join([f"{embedding:.10f}" for embedding in embeddings])
    print(hashlib.md5(string_embeddings.encode("utf-8")).hexdigest())

async def main(url):
    analysis = None

    #apify object initializations
    apify_client = ApifyClientAsync(token=APIFY_API_TOKEN)
    youtube_actor_client = apify_client.actor('streamers/youtube-scraper')

    #scrapes information about the given youtube url
    input_data = {"startUrls":[{"url":url}],"maxResults":1}
    run = await youtube_actor_client.call(run_input=input_data,logger=None)
    if run is None:
        print("Actor Failed, there isn't a YouTube video with this url.")
    
    #retrieves the scraped information
    dataset_client = youtube_actor_client.last_run().dataset()
    artist_name = ""

    async for item in dataset_client.iterate_items():
        try:
            response = requestArtistNameAndDebut(item["title"],item["channelName"])
            artist_name, debut = response.split("|")

        except Exception as e:
            raise("Video is unavailable.")
    
    analysis = lyricRetriever.getDebutAlbum(artist=artist_name,debut=debut)
    if sys.argv[2] == "json":
        print(analysis)
        quit()
    encodeThenHash(analysis)
    
if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))