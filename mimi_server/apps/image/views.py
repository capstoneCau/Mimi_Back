from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from mimi_server.apps.image.animal_similarrity import determinAnimal

@api_view(['POST'])
def upload_file(request):
    if request.method == 'POST':
        imageData = request.data['base64']
        gender = request.data['gender']
        result = determinAnimal(imageData, gender)
        if type(result) is list:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=result['error'])
    else:
        return Response({"not post" : "not post"}, status=status.HTTP_400_BAD_REQUEST)