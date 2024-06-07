from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

app = FastAPI()

API_KEY = '3165ed803092cb7d6e1087d1a389c45e'
LAST_FM_API_URL = 'http://ws.audioscrobbler.com/2.0/'

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/artist_info")
async def artist_info(request: Request, artist_name: str):
    params = {
        'method': 'artist.getInfo',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }

    response = requests.get(LAST_FM_API_URL, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="아티스트 정보를 가져오지 못했습니다")

    data = response.json()
    try:
        artist_data = data['artist']
        similar_artists = artist_data['similar']['artist'] if 'similar' in artist_data else []
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"예상치 못한 응답 구조: {str(e)}")

    return templates.TemplateResponse("artist_info.html", {
        "request": request,
        "artist_name": artist_name,
        "similar_artists": similar_artists
    })

@app.get("/artist/{artist_name}/toptracks", response_class=HTMLResponse)
async def get_artist_top_tracks(request: Request, artist_name: str):
    params = {
        'method': 'artist.getTopTracks',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }

    response = requests.get(LAST_FM_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'toptracks' in data:
            top_tracks = [{
                'rank': track['@attr']['rank'],
                '곡명': track['name'],
                '시청 횟수': track['playcount'],
                '청취자 수': track['listeners'],
                'url': track['url']
            } for track in data['toptracks']['track']]
        else:
            top_tracks = []
    else:
        raise HTTPException(status_code=response.status_code, detail="아티스트의 인기 트랙을 가져오지 못했습니다")

    # 유사한 아티스트와 관련된 트랙 정보 가져오기
    similar_artists = await get_similar_artists(artist_name)
    related_tracks = []
    for artist in similar_artists:
        related_tracks += await get_artist_top_tracks_data(artist['name'])

    return templates.TemplateResponse("artist_toptracks.html", {
        "request": request,
        "artist_name": artist_name,
        "top_tracks": top_tracks,
        "related_tracks": related_tracks
    })

async def get_similar_artists(artist_name: str):
    params = {
        'method': 'artist.getSimilar',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(LAST_FM_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['similarartists']['artist'] if 'similarartists' in data else []
    else:
        return []

async def get_artist_top_tracks_data(artist_name: str):
    params = {
        'method': 'artist.getTopTracks',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(LAST_FM_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'toptracks' in data:
            return [{
                'artist': artist_name,
                'rank': track['@attr']['rank'],
                '곡명': track['name'],
                '시청 횟수': track['playcount'],
                '청취자 수': track['listeners'],
                'url': track['url']
            } for track in data['toptracks']['track']]
    return []

@app.get("/track/{track_name}", response_class=HTMLResponse)
async def get_track_info_and_similar_artists(request: Request, track_name: str, artist: str):
    params = {
        'method': 'track.getInfo',
        'track': track_name,
        'artist': artist,
        'api_key': API_KEY,
        'format': 'json'
    }

    response = requests.get(LAST_FM_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        track_info = data.get('track')
        artist_info = track_info.get('artist') if track_info else None

        if artist_info:
            similar_artists = await get_similar_artists(artist_info['name'])
        else:
            similar_artists = []

        similar_tracks_params = {
            'method': 'track.getSimilar',
            'track': track_name,
            'artist': artist,
            'api_key': API_KEY,
            'format': 'json'
        }
        similar_tracks_response = requests.get(LAST_FM_API_URL, params=similar_tracks_params)
        if similar_tracks_response.status_code == 200:
            similar_tracks_data = similar_tracks_response.json()
            similar_tracks = similar_tracks_data['similartracks']['track'] if 'similartracks' in similar_tracks_data else []
        else:
            similar_tracks = []

        return templates.TemplateResponse("track_info.html", {
            "request": request,
            "track_info": track_info,
            "artist_info": artist_info,
            "similar_artists": similar_artists,
            "similar_tracks": similar_tracks
        })
    else:
        raise HTTPException(status_code=response.status_code, detail="트랙 정보를 가져오지 못했습니다")

@app.get("/track_search")
async def track_search(track_name: str, artist_name: str):
    return RedirectResponse(url=f"/track/{track_name}?artist={artist_name}")

@app.get("/track/{track_name}/lyrics")
async def get_track_lyrics(track_name: str, artist: str):
    return {"lyrics": "가사 정보가 여기 표시됩니다."}

@app.get("/artist/{artist_name}/albums")
async def get_artist_albums(artist_name: str):
    params = {
        'method': 'artist.getTopAlbums',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json'
    }

    response = requests.get(LAST_FM_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'topalbums' in data:
            albums = [{
                'album_name': album['name'],
                'playcount': album['playcount'],
                'url': album['url']
            } for album in data['topalbums']['album']]
            return {"albums": albums}
        else:
            return {"albums": []}
    else:
        raise HTTPException(status_code=response.status_code, detail="아티스트의 앨범 정보를 가져오지 못했습니다")