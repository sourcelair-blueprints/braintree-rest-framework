from api import serializers
from django.conf import settings
from rest_framework import generics
from rest_framework import views
from rest_framework import viewsets
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
import braintree


class CustomerViewset(viewsets.ViewSet):
    """
    This view allows listing, creating, and deleting customers for the
    currently set up Braintree merchant.
    """
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
    """
    This view allows inspecting and deleting payment methods.
    """
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
    """
    Lists all payment methods that belong to the given customer.
    """
    serializer_class = serializers.PaymentMethodSerializer

    def list(self, request, *args, **kwargs):
        payment_methods = self.get_customer().payment_methods
        serializer = self.serializer_class(payment_methods, many=True,
                                           context={'request': request})
        return Response(serializer.data)


class TransactionViewset(viewsets.ViewSet):
    """
    This view allows inspection of the given transaction.
    """
    serializer_class = serializers.TransactionSerializer

    def retrieve(self, request, pk=None, *args, **kwargs):
        transaction = braintree.Transaction.find(pk)
        serializer = self.serializer_class(transaction, many=False,
                                           context={'request': request})
        return Response(serializer.data)


class CustomerTransactionViewset(CustomerNamespacedMixin,
                                   viewsets.ViewSet):
    """
    Lists all transactions of the given customer and allows charging the
    customer with a new transaction.
    """
    serializer_class = serializers.TransactionSerializer

    def list(self, request, customer_id):
        customer = self.get_customer()
        customer_serializer = serializers.CustomerSerializer(
            customer, context={'request': request}
        )
        transactions = customer_serializer.get_transactions(customer)
        return Response(transactions)

    def create(self, request, customer_id):
        customer = self.get_customer()

        payment_method_token = request.data.get(
            'payment_method_token', customer.payment_methods[0].token
        )

        result = braintree.Transaction.sale({
            'amount': request.data['amount'],
            'customer_id': customer_id,
            'payment_method_token': payment_method_token,
            'options': {
                'submit_for_settlement': True
            }
        })

        if result.is_success:
            response_data = {'message': 'Charged customer successfully.'}
        else:
            response_data = {'message': 'Could not charge customer.'}
        return Response(response_data)


class BraintreeSettingsView(views.APIView):
    """
    Update the Braintree API settings.
    """
    serializer_class = serializers.BraintreeSettingsSerializer

    def get(self, request):
        data = {
            'environment': settings.BRAINTREE_ENVIRONMENT,
            'merchant_id': settings.BRAINTREE_MERCHANT_ID,
            'public_key': settings.BRAINTREE_PUBLIC_KEY,
            'private_key': settings.BRAINTREE_PRIVATE_KEY
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.data)
        return Response(data=serializer.data)
