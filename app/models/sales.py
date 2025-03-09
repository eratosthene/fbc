from flask import Markup
from mongoengine import (
    Document,
    FloatField,
    ReferenceField,
    StringField,
)

from app.models.discogs import DiscogsOrder
from app.models.ebay import eBayOrder


class SalesReceipt(Document):
    date = StringField(required=True)
    ebay_order = ReferenceField(eBayOrder)
    discogs_order = ReferenceField(DiscogsOrder)
    sold_price = FloatField()
    net_sold = FloatField()

    meta = {
        "auto_create_index": False,
        "index_background": True,
        "indexes": [
            "ebay_order",
            "discogs_order",
        ],
    }

    def __unicode__(self):
        ret = self.date
        if self.ebay_order:
            ret = ret + ": " + self.ebay_order.order_id
        if self.discogs_order:
            ret = ret + ": " + self.discogs_order.order_id
        ret = ret + " $" + f"{self.sold_price:.2f}" + "/$" + f"{self.net_sold:.2f}"
        return ret

    def __repr__(self):
        ret = self.date
        if self.ebay_order:
            ret = ret + ": " + self.ebay_order.order_id
        if self.discogs_order:
            ret = ret + ": " + self.discogs_order.order_id
        ret = ret + " $" + f"{self.sold_price:.2f}" + "/$" + f"{self.net_sold:.2f}"
        return ret

    def fmt_sold_price(self):
        return "$" + f"{self.sold_price:.2f}"

    def fmt_net_sold(self):
        return "$" + f"{self.net_sold:.2f}"

    def fmt_ebay_order(self, markup=True):
        ret = ""
        if self.ebay_order:
            ret = (
                '<a href="https://www.ebay.com/mesh/ord/details?orderid='
                + self.ebay_order.order_id
                + '">eBay:Order&nbsp;$'
                + f"{self.ebay_order.price:.2f}"
                + "</a>"
            )
        if markup:
            return Markup(ret)
        else:
            return ret

    def fmt_discogs_order(self, markup=True):
        ret = ""
        if self.discogs_order:
            ret = (
                '<a href="https://www.discogs.com/sell/order/'
                + self.discogs_order.order_id
                + '">Discogs:Order&nbsp;$'
                + f"{self.discogs_order.price:.2f}"
                + "</a>"
            )
        if markup:
            return Markup(ret)
        else:
            return ret

    def link_column(self, markup=True):
        ret = self.fmt_ebay_order(False) + self.fmt_discogs_order(False)
        if markup:
            return Markup(ret)
        else:
            return ret
