import requests

API_KEY = '3165ed803092cb7d6e1087d1a389c45e'
API_URL = 'https://liiiqueur.github.io/music/main.html'

# 예제: 사용자의 최근 듣기 기록 가져오기
params = {
    'method': 'user.getRecentTracks',
    'user': 'geonwoo2473',
    'api_key': API_KEY,
    'format': 'json'
}

response = requests.get(API_URL, params=params)

if response.status_code == 200:
    data = response.json()
    # 데이터를 처리하거나 출력합니다.
    print(data)
else:
    print("Error:", response.status_code)
