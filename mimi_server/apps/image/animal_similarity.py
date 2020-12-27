import numpy as np
import os
import io
import base64
import cv2
# 2. Model 불러오기
from imageio import imread
from tensorflow.python.keras.models import load_model

from mimi_server.celery import app
from mimi_server.apps.image.kakaoFaceAPI import faceDetect
from mimi_server.settings import BASE_DIR
from mimi_server.apps.notification.views import send


@app.task
def determinAnimal(imageData, gender, fcm):
    modelPath = os.path.join(BASE_DIR, 'model')
    if gender == 'male':
        model = load_model(os.path.join(
            modelPath, 'animal_model_man.h5'), compile=False)
    elif gender == 'female':
        model = load_model(os.path.join(
            modelPath, 'animal_model_woman.h5'), compile=False)
    categories = {
        'male': ['dog', 'cat', 'bear', 'hamster', 'horse', 'wolf', 'dinosaur', 'racoon'],
        'female': ['dog', 'cat', 'rabbit', 'squirrel', 'deer', 'fox', 'penguin', 'snake']
    }
    image = base64.b64decode(imageData)
    try:
        x, y, w, h = faceDetect(image)
    except ValueError as e:
        if str(e).startswith('GREAT'):
            send(fcm, dtitle='ANIMAL', dbody={
                "detail": "Please take a picture alone.", "error": 409})
            return {"detail": "Please take a picture alone.", "error": 409}

        elif str(e).startswith('ZERO'):
            send(fcm, dtitle='ANIMAL', dbody={
                "detail": "Take a Face recognition failed.", "error": 404})
            return {"detail": "Take a Face recognition failed.", "error": 404}

    test_img = imread(io.BytesIO(image))

    height, width = test_img.shape[0], test_img.shape[1]
    cropped = test_img[max(0, y - int(h / 4)): min(height, y + h + int(h / 4)),
                       max(0, x - int(w / 4)):min(width, x + w + int(w / 4))]

    test = cropped
    test = test.astype('float32')/255.
    test = cv2.resize(test, (128, 128))
    test = np.expand_dims(test, 0)
    try:
        y_predicted = model.predict(test)
    except ValueError:
        send(fcm, dtitle='ANIMAL', dbody={
             "detail": "The face is not recognized in the picture.", "error": 400})
        return {"detail": "The face is not recognized in the picture.", "error": 400}
    sortedIndex = np.argsort(y_predicted)[0][::-1]
    np.set_printoptions(suppress=True)
    print(y_predicted[0], sortedIndex)
    retunValue = [
        {
            'category': categories[gender][sortedIndex[0]],
            'predict_rate': float(y_predicted[0][sortedIndex[0]])
        },
        {
            'category': categories[gender][sortedIndex[1]],
            'predict_rate': float(y_predicted[0][sortedIndex[1]])
        },
        {
            'category': categories[gender][sortedIndex[2]],
            'predict_rate': float(y_predicted[0][sortedIndex[2]])
        }
    ]
    print(retunValue)
    send(fcm, dtitle='ANIMAL', dbody=retunValue)
    return retunValue
