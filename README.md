if response.status_code == 200:
        data = response.json()
        if 'toptracks' in data:
            top_tracks = [{
                'name': track['name'],
                'url': track['url']  # 각 곡의 Last.fm URL을 포함시킴
            } for track in data['toptracks']['track']]
            return {"top_tracks": top_tracks}
        else:
            return {"top_tracks": []}

1. 문제점 트랙과 url이 잘 나오지만 ranking이 나오지 않음 (ranking 추가)
2. 가수와 곡을 모두 검색할 수 있는 방향도 생각 (중복 검색)
3. 곡만 검색하고 해당 가수를 찾아주는 방향
4. 곡을 검색할 때 연관어 추천 or key word 추천 (track 알아서 해줌, 가수를 해결하라)
5. 







100000. 프론트 엔드 꾸미기
