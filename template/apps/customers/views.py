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

    def patch(self, request):

        customer = CustomerProfile.objects.filter(
            user=request.user
        ).first()

        if not customer:
            return Response(
                {
                    "success": False,
                    "message": "Customer profile not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CustomerSerializer(
            customer,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(
            raise_exception=True
        )

        customer = serializer.save()

        return Response(
            {
                "success": True,
                "message": "Customer profile updated successfully.",
                "data": CustomerSerializer(
                    customer
                ).data,
            },
            status=status.HTTP_200_OK,
        )