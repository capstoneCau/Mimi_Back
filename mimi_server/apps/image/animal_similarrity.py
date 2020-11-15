from tensorflow.python.keras.models import load_model
import numpy as np
import cv2
import os
import io
import base64
from imageio import imread
# 2. Model 불러오기
from tensorflow.python.keras.models import load_model
from mimi_server.settings import BASE_DIR

def determinAnimal(imageData, gender) :
    cascadePath = os.path.join(BASE_DIR, 'CascadeClassifier')
    modelPath = os.path.join(BASE_DIR, 'model')
    if gender == 'male' :
        model = load_model(os.path.join(modelPath, 'animal_model_man.h5'), compile = False)
    elif gender == 'female' :
        model = load_model(os.path.join(modelPath, 'animal_model_woman.h5'), compile = False)
    categories = ['dog','cat','bear','hamster','horse', 'wolf']
    
    test_img = imread(io.BytesIO(base64.b64decode(imageData)))
    face_cascade = cv2.CascadeClassifier(os.path.join(cascadePath, 'haarcascade_frontalface_default.xml'))
    eye_casecade = cv2.CascadeClassifier(os.path.join(cascadePath, 'haarcascade_eye.xml'))

    test = np.empty(1, dtype=np.float32)
    try:
        gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1,3)
    except Exception as e:
        return {"detail" : "Image file is not found", "error" : 400}
    for (x,y,w,h) in faces:
        try:
            cropped = test_img[y - int(h / 4):y + h + int(h / 4), x - int(w / 4):x + w + int(w / 4)]
            if cropped.shape > test.shape:
                test = cropped
        except Exception as e:
            return {"detail" : "The face is not recognized in the picture.", "error" : 404}
    test = test.astype('float32')/255.            
    test = cv2.resize(test,(128,128))
    test = np.expand_dims(test,0)
    try:
        y_predicted = model.predict(test)
    except ValueError:
        return {"detail" : "The face is not recognized in the picture.", "error" : 404}
    sortedIndex = np.argsort(y_predicted)[0][::-1]
    np.set_printoptions(suppress=True)
    # print(y_predicted[0], sortedIndex)
    retunValue = [
        {
            'category' : categories[sortedIndex[0]],
            'predict_rate' : y_predicted[0][sortedIndex[0]]
        },
        {
            'category' : categories[sortedIndex[1]],
            'predict_rate' : y_predicted[0][sortedIndex[1]]
        },
        {
            'category' : categories[sortedIndex[2]],
            'predict_rate' : y_predicted[0][sortedIndex[2]]
        }
    ]
    # print(retunValue)
    return retunValue