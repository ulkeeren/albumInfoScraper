import json
import asyncio
import requests

from apify_client import ApifyClientAsync

APIFY_API_TOKEN = "apify_api_gDAV9YRn609MMToyO4HHx2T2NKn9E60iVQAt"
OPENROUTER_API_KEY = "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"

def requestArtistName(title, uploader):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}"
        },
        data=json.dumps({
            "model": "xiaomi/mimo-v2-flash:free", 
            "messages": [
            {
                "role": "user",
                "content": f"I'll now share you the title and uploader of a music video, respond the name of the artists that sings the song, Title: {title}, Uploader:{uploader} . Respond the name of the artist only and in plaintext."
            }
            ],
            "reasoning": {"enabled": True}
            }
        )
    )
    return response.json()["choices"][0]["message"]["content"]
        

async def main() -> None:
    #apify object initializations
    apify_client = ApifyClientAsync(token=APIFY_API_TOKEN)
    youtube_actor_client = apify_client.actor('streamers/youtube-scraper')
    genius_actor_client = apify_client.actor('epctex/genius-scraper')
    #scrapes information about the given youtube url
    url = "https://youtu.be/8aomt1gQ6So?si=Tg2evf9XF6wv19np"
    input_data = {"startUrls":[{"url":url}],"maxResults":1}
    run = await youtube_actor_client.call(run_input=input_data)
    if run is None:
        print("Actor Failed, there isn't a YouTube video with this url.")
    
    #retrieves the scraped information
    dataset_client = youtube_actor_client.last_run().dataset()
    artist_name = ""
    async for item in dataset_client.iterate_items():
        try:
            artist_name = requestArtistName(item["title"],item["channelName"])

        except Exception as e:
            raise("Video is unavailable.")



if __name__ == '__main__':
    asyncio.run(main())