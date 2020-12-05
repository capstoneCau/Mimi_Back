import requests
import json
from secret import KAKAO_REST_API_KEY


def faceDetect(image):
    headers = {'Authorization': 'KakaoAK {}'.format(KAKAO_REST_API_KEY)}
    try:
        files = {'image': image}
        resp = requests.post(
            'https://dapi.kakao.com/v2/vision/face/detect', headers=headers, files=files)
        resp.raise_for_status()
        print(resp.json())
        result = resp.json()['result']
        width, height = int(result['width']), int(result['height'])
        faces = result['faces']
        print(len(faces))
        if len(faces) > 1:
            raise ValueError('GREAT, Please take a picture alone.')
        if len(faces) == 0:
            raise ValueError('ZERO, Take a Face recognition failed.')
        return int(faces[0]['x'] * width), int(faces[0]['y'] * height), int(faces[0]['w'] * width), int(faces[0]['h'] * height)
    except Exception as e:
        print(str(e))
        if type(e) is ValueError:
            raise ValueError(str(e))
    # return res.json()
