import braintree

from rest_framework import serializers


class CustomerSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='customer-detail',
        lookup_field='id',
        lookup_url_kwarg='pk',
        read_only=True
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
#     payment_method = serializers.CharField()
#     payment_method_url = None # TODO


class TransactionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    amount = serializers.FloatField()
    payment_method = serializers.CharField()
    payment_method_url = None # TODO
    customer_url = None # TODO


class PaymentMethodSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    customer_url = serializers.HyperlinkedIdentityField(
        many=True,
        read_only=True,
        view_name='customer-detail',
        source='customer_id'
    )

    def get_type(self, payment_method):
        print dir(payment_method)
        return type(payment_method).__name__
