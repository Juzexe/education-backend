from rest_framework import serializers

from tinkoff.models import CreditNotification
from tinkoff.models import DolyameNotification
from tinkoff.models import PaymentNotification


class PaymentNotificationSerializer(serializers.ModelSerializer):
    TerminalKey = serializers.CharField(source="terminal_key")
    OrderId = serializers.IntegerField(source="order_id")
    Success = serializers.BooleanField(source="success")
    Status = serializers.CharField(source="status")
    PaymentId = serializers.IntegerField(source="payment_id")
    ErrorCode = serializers.CharField(source="error_code", required=False, allow_null=True)
    Amount = serializers.IntegerField(source="amount")
    RebillId = serializers.IntegerField(source="rebill_id", required=False, allow_null=True)
    CardId = serializers.CharField(source="card_id", required=False, allow_null=True, allow_blank=True)
    Pan = serializers.CharField(source="pan", required=False, allow_null=True)
    DATA = serializers.CharField(source="data", required=False, allow_null=True)
    Token = serializers.CharField(source="token")
    ExpDate = serializers.CharField(source="exp_date", required=False, allow_null=True)

    class Meta:
        model = PaymentNotification
        fields = [
            "TerminalKey",
            "OrderId",
            "Success",
            "Status",
            "PaymentId",
            "ErrorCode",
            "Amount",
            "RebillId",
            "CardId",
            "Pan",
            "DATA",
            "Token",
            "ExpDate",
        ]

    def validate_Amount(self, validated_data):
        return validated_data / 100


class CreditNotificationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="order_id")
    created_at = serializers.DateTimeField(source="bank_created")
    middle_name = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = CreditNotification
        fields = [
            "id",
            "status",
            "created_at",
            "first_payment",
            "order_amount",
            "credit_amount",
            "product",
            "term",
            "monthly_payment",
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "loan_number",
            "email",
        ]


class DolyameNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DolyameNotification
        fields = [
            "order",
            "status",
            "amount",
            "demo",
            "residual_amount",
            "client_info",
            "payment_schedule",
        ]
