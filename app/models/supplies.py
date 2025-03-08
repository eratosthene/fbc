from flask_appbuilder.models.decorators import renders
from mongoengine import (
    Document,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)


class PurchaseOrder(Document):
    date = StringField(required=True)
    price = FloatField(required=True)
    notes = StringField()
    link = StringField()

    @renders("price")
    def purchase_price(self):
        return "$" + f"{self.price:.2f}"

    def __unicode__(self):
        return self.date + ": " + self.notes + " $" + f"{self.price:.2f}"

    def __repr__(self):
        return self.date + ": " + self.notes + " $" + f"{self.price:.2f}"


class Supply(Document):
    name = StringField(required=True)
    quantity = IntField(required=True, default=0)
    purchase_order = ListField(ReferenceField("PurchaseOrder"))

    def __unicode__(self):
        return self.name + ": " + str(self.quantity)

    def __repr__(self):
        return self.name + ": " + str(self.quantity)
