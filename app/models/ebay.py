import logging

from flask import Markup, url_for
from flask_appbuilder.models.decorators import renders
from mongoengine import (
    BooleanField,
    DictField,
    Document,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)

logger = logging.getLogger()


class eBayListing(Document):
    item_id = StringField(required=True, primary_key=True)
    title = StringField()
    price = FloatField()
    url = StringField()

    def __unicode__(self):
        return self.item_id + ": " + self.title + " $" + f"{self.price:.2f}"

    def __repr__(self):
        return self.item_id + ": " + self.title + " $" + f"{self.price:.2f}"

    def fmt_price(self):
        return "$" + f"{self.price:.2f}"

    def fmt_url(self):
        return Markup('<a href="' + self.url + '">' + self.url + "</a>")


class eBayOrder(Document):
    order_id = StringField(required=True, primary_key=True)
    date = StringField()
    buyer = StringField()
    price = FloatField()
    title = StringField()

    def __unicode__(self):
        if self.title:
            return (
                self.date
                + " "
                + self.order_id
                + " ["
                + self.title[:45]
                + "]: "
                + self.buyer
                + " $"
                + f"{self.price:.2f}"
            )
        else:
            return (
                self.date
                + " "
                + self.order_id
                + ": "
                + self.buyer
                + " $"
                + f"{self.price:.2f}"
            )

    def __repr__(self):
        if self.title:
            return (
                self.date
                + " "
                + self.order_id
                + " ["
                + self.title[:45]
                + "]: "
                + self.buyer
                + " $"
                + f"{self.price:.2f}"
            )
        else:
            return (
                self.date
                + " "
                + self.order_id
                + ": "
                + self.buyer
                + " $"
                + f"{self.price:.2f}"
            )

    def fmt_price(self):
        return "$" + f"{self.price:.2f}"

    def fmt_url(self):
        return Markup(
            '<a href="https://www.ebay.com/mesh/ord/details?orderid='
            + self.order_id
            + '">'
            + self.order_id
            + "</a>"
        )

    def add_sr(self):
        return Markup(
            '<a href="'
            + url_for(
                "SalesReceiptModelView.add",
                sold_price=self.price,
                ebay_order=self.order_id,
                date=self.date,
            )
            + '">Add SR</a>'
        )
