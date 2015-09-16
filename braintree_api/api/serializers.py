import braintree

from django.template import loader
from rest_framework import serializers


class CustomerSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='customer-detail',
        lookup_field='id',
        lookup_url_kwarg='pk'
    )
    payment_methods_url = serializers.HyperlinkedIdentityField(
        view_name='customer-payment-method-list',
        lookup_field='id',
        lookup_url_kwarg='customer_id'
    )
    new_payment_method_form_url = serializers.HyperlinkedIdentityField(
        view_name='customer-payment-method-form',
        lookup_field='id',
        lookup_url_kwarg='customer_id'
    )
    transactions_url = serializers.HyperlinkedIdentityField(
        view_name='customer-transaction-list',
        lookup_field='id',
        lookup_url_kwarg='customer_id'
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    transactions = serializers.SerializerMethodField(read_only=True)

    def get_transactions(self, customer):
        transactions = braintree.Transaction.search(
            braintree.TransactionSearch.customer_id == customer.id
        ).items
        return [
            TransactionSerializer(t, context=self.context).data
            for t in transactions
        ]


class TransactionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    amount = serializers.FloatField()
    url = serializers.HyperlinkedIdentityField(
        view_name='transaction-detail',
        lookup_field='id',
        lookup_url_kwarg='pk'
    )
    customer_url = serializers.HyperlinkedIdentityField(
        view_name='customer-detail',
        lookup_field='id',
        lookup_url_kwarg='pk'
    )
    payment_method_token = serializers.CharField(write_only=True)


class PaymentMethodSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    customer_url = serializers.HyperlinkedIdentityField(
        many=False,
        view_name='customer-detail',
        lookup_url_kwarg='pk',
        lookup_field='customer_id',
        required=False,
    )
    url = serializers.HyperlinkedIdentityField(
        many=False,
        view_name='payment-method-detail',
        lookup_url_kwarg='pk',
        lookup_field='token',
        required=False,
    )

    def get_type(self, payment_method):
        return type(payment_method).__name__


class BraintreeSettingsSerializer(serializers.Serializer):
    environment = serializers.ChoiceField(
        choices=[('sandbox', 'Sandbox'),('production', 'Production')]
    )
    merchant_id = serializers.CharField()
    public_key = serializers.CharField()
    private_key = serializers.CharField()

    def create(self, validated_data):
        t = loader.get_template('settings.txt')
        settings = t.render(context=validated_data)
        with open('braintree_api/settings_local.py', 'wb') as settings_file:
            settings_file.write(settings)
