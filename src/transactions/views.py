from rest_framework import views, response, status 
from .serializers import BalanceSerializer, TransferAmountSerializer


class CreateAccountAPIView(views.APIView):
    def post(self, request):
        serializer = BalanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(data=serializer.save(), status = status.HTTP_200_OK)

class TransferAmountAPIView(views.APIView):
    def post(self, request):
        serializer = TransferAmountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(data=serializer.save(),status = status.HTTP_200_OK)