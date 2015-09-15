from rest_framework import serializers


class CustomerSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
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
    type = serializers.CharField(read_only=True)
    customer_url = None # TODO
    