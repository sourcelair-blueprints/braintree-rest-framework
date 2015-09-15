from rest_framework import viewsets
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
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


class CustomerNamespacedMixin(object):
    def get_customer(self):
        return braintree.Customer.find(self.kwargs.get('customer_id'))


class PaymentMethodViewset(viewsets.ViewSet):
    serializer_class = serializers.PaymentMethodSerializer

    def retrieve(self, request, pk=None, *args, **kwargs):
        payment_method = braintree.PaymentMethod.find(pk)
        serializer = self.serializer_class(payment_method, many=False,
                                           context={'request': request})
        return Response(serializer.data)

    def delete(self, request, pk):
        result = braintree.PaymentMethod.delete(pk)
        if result.is_success:
            return Response({'message': 'Deleted payment method successfully'})
        response = Response({
            'message': 'Could not delete payment method.'
        }, status=500)
        return response


class PaymentMethodFormView(generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of a given user.
    """
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, customer_id):
        client_token = braintree.ClientToken.generate({
            "customer_id": customer_id
        })
        context = {
            'client_token': client_token,
            'customer_id': customer_id
        }
        return Response(context, template_name='payment-method-form.html')


class CustomerPaymentMethodViewset(CustomerNamespacedMixin,
                                   viewsets.ViewSet):
    serializer_class = serializers.PaymentMethodSerializer

    def list(self, request, *args, **kwargs):
        payment_methods = self.get_customer().payment_methods
        serializer = self.serializer_class(payment_methods, many=True,
                                           context={'request': request})
        return Response(serializer.data)


class TransactionViewset(viewsets.ViewSet):
    serializer_class = serializers.TransactionSerializer

    def retrieve(self, request, pk=None, *args, **kwargs):
        transaction = braintree.Transaction.find(pk)
        serializer = self.serializer_class(transaction, many=False,
                                           context={'request': request})
        return Response(serializer.data)
