from rest_framework import serializers

from mailing.tasks import send_mail
from products.models import Record
from studying import shipment_factory as factory
from studying.shipment.base import BaseShipment


class RecordTemplateContext(serializers.ModelSerializer):
    record_link = serializers.CharField(source="get_url")

    class Meta:
        model = Record
        fields = [
            "name_genitive",
            "record_link",
        ]


@factory.register(Record)
class RecordShipment(BaseShipment):
    template_id = "purchased-record"

    @property
    def record(self) -> Record:
        return self.stuff_to_ship

    def ship(self) -> None:
        self.send_record_link()

    def unship(self) -> None:
        """No need to unship records"""

    def get_template_context(self) -> dict:
        return RecordTemplateContext().to_representation(self.record)

    def send_record_link(self) -> None:
        """Send email, convinience method for subclasses

        The mail is not sent by default, you have to call it manualy!
        """
        send_mail.delay(
            to=self.user.email,
            template_id=self.get_template_id(),
            ctx=self.get_template_context(),
            disable_antispam=True,
        )

    def get_template_id(self) -> str:
        template_id = self.record.get_template_id()

        if template_id is not None:
            return template_id

        return self.template_id
