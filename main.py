from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

API_KEY = '3165ed803092cb7d6e1087d1a389c45e'
LAST_FM_API_URL = 'http://ws.audioscrobbler.com/2.0/'

@app.get("/artist/{artist_name}")
async def get_artist_info(artist_name: str):
    params = {
        'method': 'artist.getInfo',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }
    
    response = requests.get(LAST_FM_API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        similar_artists = data['artist']['similar']['artist'] if 'similar' in data['artist'] else []
        return {"similar_artists": similar_artists}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch artist info")
    
@app.get("/artist/{artist_name}/toptracks")
async def get_artist_top_tracks(artist_name: str):
    params = {
        'method': 'artist.getTopTracks',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }
    
    response = requests.get(LAST_FM_API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        top_tracks = data['toptracks']['track'] if 'toptracks' in data else []
        return {"top_tracks": top_tracks}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch artist top tracks")
