from rest_framework import viewsets
from rest_framework.response import Response
from api import serializers
import braintree


class CustomerViewset(viewsets.ViewSet):
    serializer_class = serializers.CustomerSerializer

    def list(self, request):
        customers = braintree.Customer.all().items
        serializer = self.serializer_class(customers, many=True,
                                           context={'request': request})
        return Response(serializer.data)
