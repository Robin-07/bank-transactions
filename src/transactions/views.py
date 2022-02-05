from rest_framework import views, response, status 
from .serializers import BalanceSerializer, TransferAmountSerializer


class CreateAccountAPIView(views.APIView):
    def post(self, request):
        serializer = BalanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(data=serializer.validated_data, status = status.HTTP_200_OK)

class TransferAmountAPIView(views.APIView):
    def post(self, request):
        return response.Response(status = status.HTTP_200_OK)