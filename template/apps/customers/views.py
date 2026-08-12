from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.customers.serializers import CustomerSerializer
from rest_framework.permissions import IsAuthenticated
from apps.customers.models import CustomerProfile
class CustomerCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CustomerSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user=request.user
        customer=CustomerProfile.objects.filter(user=user).first()
        serializer=CustomerSerializer(customer)
        return Response(serializer.data,status=status.HTTP_200_OK)