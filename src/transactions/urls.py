from django.urls import path
from .views import CreateAccountAPIView,TransferAmountAPIView


urlpatterns = [
    path('account/', CreateAccountAPIView.as_view(), name='create-account'),
    path('transfer/', TransferAmountAPIView.as_view(), name='transfer')
]