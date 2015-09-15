from rest_framework import viewsets
from rest_framework.response import Response
from api import serializers
import braintree


class CustomerViewset(viewsets.ViewSet):
    serializer_class = serializers.CustomerSerializer

    def list(self, request):
        customers = braintree.Customer.all().items
        serializer = self.serializer_class(
            customers, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def retrieve(self, request, pk):
        customer = braintree.Customer.find(pk)
        serializer = self.serializer_class(
            customer,context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request):
        result = braintree.Customer.create({
            'first_name': request.data['first_name'],
            'last_name': request.data['last_name'],
            'email': request.data['email'],
        })

        if result.is_success:
            serializer = self.serializer_class(result.customer, context={
                'request': request
            })
            return Response(serializer.data)
        else:
            return Response({'message': 'Shit happens.'})

    def delete(self, request, pk):
        result = braintree.Customer.delete(pk)
        if result.is_success:
            return Response({'message': 'Deleted customer successfully'})
        return Response({'message': 'Could not delete customer.'}, status=500)
