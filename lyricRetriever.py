import unicodedata
import requests
import tiktoken
import hashlib
import re
from bs4 import BeautifulSoup

def slugify(text: str) -> str:
    # unicode -> ascii
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\-]+", " ", text)
    text = re.sub(r"\s+", "-", text.strip())
    text = re.sub(r"-{2,}", "-", text)

    return text

def formSongAnalytics(lyrics,songName):
    len_chars = 0
    len_words = len(lyrics.split(" "))
    for word in lyrics.split(" "):
        len_chars+= len(word)
    
    enc = tiktoken.get_encoding("cl100k_base")
    token_ids = enc.encode(lyrics)
    len_token_ids = len(token_ids)
    
    songAnalysis = {
        "name": songName,
        "lyrics_lenght_chars": len_chars,
        "lyrics_lenght_words": len_words,
        "lyrics_lenght_tokens": len_token_ids,
        "token_per_word": float(len(token_ids)) / float(len(lyrics.split(" "))),
        "lyrics_hash": hashlib.md5(lyrics.encode("utf-8")).hexdigest()
    } 

    return songAnalysis, len(token_ids)

def getSongLyrics(songUrl,songName):
    songPage = requests.get(songUrl)
    songSoup = BeautifulSoup(songPage.text,"html.parser")
    box = songSoup.find("div", class_=re.compile(r"^Lyrics__Container"))
    if not box:
        print("Couldn't find a lyrics box.")
        return

    for bad in box.find_all(class_=re.compile(r"^LyricsHeader__Container")):
        bad.decompose()

    lyrics = box.get_text(separator="\n", strip=True)
    return formSongAnalytics(lyrics,songName)

def getdebutSongs(debutUrl):
    songs = []
    total_tokens = 0
    debutPage = requests.get(debutUrl)
    debutSoup = BeautifulSoup(debutPage.text,'html.parser')
    debutSongs = debutSoup.find_all("a",class_="u-display_block")
    for a in debutSongs:
        songAnalysis, tokens = getSongLyrics(a.get("href"),a.find("h3").get_text(strip=True)[:-6])
        total_tokens += tokens
        songs.append(songAnalysis)
    
    return songs,total_tokens,len(debutSongs)


def getDebutAlbum(artist:str,debut:str):
    url = f"https://genius.com/albums/{slugify(artist)}/{slugify(debut)}"
    songs, total_tokens, total_songs = getdebutSongs(url)
    analysis = {
        "artist":artist,
        "album_name": debut,
        "songs": songs,
        "total_tokens_all_songs": total_tokens,
        "avg_tokens_per_song": float(total_tokens)/float(total_songs)
    }
    return analysis