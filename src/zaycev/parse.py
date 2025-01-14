import requests
import json
import os


def save_to_file(file_path, data):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {file_path} successfully.")


def fetch_genre_tracks(url_name, num_pages, track_limit):
    all_tracks = {}
    for page in range(1, num_pages + 1):
        url = f"https://zaycev.net/api/external/pages/genres/{url_name}/tracks?limit={track_limit}&page={page}&sort=popularity"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "referrer": f"https://zaycev.net/genres/{url_name}/index.html",
            "referrerPolicy": "strict-origin-when-cross-origin"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_tracks.update(response.json().get('info', {}))
            print(f"Tracks for {url_name} page {page} fetched successfully.")
        else:
            print(f"Failed to fetch tracks for {url_name} page {page}: {response.status_code}")

    file_path = os.path.join(os.path.dirname(__file__), 'data', 'collections', url_name, 'tracks.json')
    save_to_file(file_path, all_tracks)


def fetch_track_metadata(referer, track_ids, genre):
    url = "https://zaycev.net/api/external/track/filezmeta"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "content-type": "application/json;charset=UTF-8",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "referrer": referer
    }
    body = {
        "trackIds": track_ids,
        "subscription": False
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'collections', genre, 'tracks_url.json')
        save_to_file(file_path, response.json())
    else:
        print(f"Failed to fetch data: {response.status_code}")


def download_track(referer, track_id):
    url = f"https://zaycev.net/api/external/track/download/{track_id}"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "referrer": referer
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Track {track_id} linked successfully.")
            return response.content.decode('utf-8')
        else:
            print(f"Failed to download track {track_id}: {response.status_code}")
    except Exception:
        print('Failed')
        return False


def save_track(download_link, track_id, genre):
    headers = {
        "accept": "*/*",
        "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site"
    }
    response = requests.get(download_link, headers=headers)
    if response.status_code == 200:
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'result_dir', genre, f'{track_id}.mp3')
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"Track {track_id} saved successfully.")
    else:
        print(f"Failed to save track {track_id}: {response.status_code}")


genres = ['electronic', 'shanson', 'classical', 'rap', 'jazz']

for genre in genres:
    fetch_genre_tracks(genre, 4, 70)

    data, track_ids = {}, []

    file_path = os.path.join(os.path.dirname(__file__), 'data', 'collections', genre, f'tracks.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        track_ids = list(data.keys())

    fetch_track_metadata("https://zaycev.net/genres/rap/index.html", track_ids, genre)

    file_path = os.path.join(os.path.dirname(__file__), 'data', 'collections', genre, f'tracks_url.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for track in data.get('tracks', []):
            track_id = track.get('id', False)
            if not track_id or track_id == '25028604':
                continue

            file_path = os.path.join(os.path.dirname(__file__), 'data', 'result_dir', genre, f'{track_id}.mp3')
            if os.path.exists(file_path):
                print(f"Track {track_id} already exists. Skipping download.")
                continue

            download_id = track.get('download', False)
            if download_id:
                download_link = download_track(f"https://zaycev.net/genres/{genre}/index.html", download_id)
                if download_link:
                    save_track(download_link, track.get('id'), genre)
