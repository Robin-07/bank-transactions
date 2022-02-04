from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

class TransferAPIView(APIView):

    authentication_classes = ()

    def post(self, request):
        return Response(status = HTTP_200_OK)