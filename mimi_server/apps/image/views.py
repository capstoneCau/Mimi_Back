from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from mimi_server.apps.image.animal_similarity import determinAnimal
from mimi_server.apps.etcInformation.models import Animal
from django.db.models import Q
import random
import os
import base64
from mimi_server.settings import ANIMAL_IMAGE_PATH


@api_view(['POST'])
def detect_face(request):
    if request.method == 'POST':
        imageData = request.data['base64']
        gender = request.data['gender']
        result = determinAnimal(imageData, gender)
        if type(result) is list:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=result['error'])
    else:
        return Response({"not post": "not post"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_animal_image(request):
    if request.method == 'GET':
        imageLabel = request.GET['label']
        imageInstances = list(Animal.objects.filter(Q(label=imageLabel)))
        if len(imageInstances) == 0:
            return Response({"detail": "not found", "error": 404}, status=status.HTTP_404_NOT_FOUND)
        random.shuffle(imageInstances)
        images = []
        for i in range(3):
            obj = {
                'id': imageInstances[i].id
            }
            filename = str(imageInstances[i].imgData).split("/")[2]
            path = os.path.join(os.path.join(
                ANIMAL_IMAGE_PATH, imageLabel), filename)
            with open(path, 'rb') as f:
                obj['base64'] = base64.b64encode(f.read())
                # images.append(base64.b64encode(f.read()))
            images.append(obj)
        return Response({"images": images}, status=status.HTTP_200_OK)
