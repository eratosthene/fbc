from mongoengine import Document
from mongoengine import IntField, StringField, ListField, ReferenceField, BooleanField, DictField, FloatField
from flask import Markup, url_for
from app.models.ebay import eBayOrder

class SalesReceipt(Document):
    date = StringField(required=True)
    ebay_order = ReferenceField(eBayOrder)
    sold_price = FloatField()
    net_sold = FloatField()

    def __unicode__(self):
        ret = self.date
        if self.ebay_order:
            ret = ret + ': ' + self.ebay_order.order_id
        ret = ret + ' $' + f"{self.sold_price:.2f}" + '/$' + f"{self.net_sold:.2f}"
        return ret

    def __repr__(self):
        ret = self.date
        if self.ebay_order:
            ret = ret + ': ' + self.ebay_order.order_id
        ret = ret + ' $' + f"{self.sold_price:.2f}" + '/$' + f"{self.net_sold:.2f}"
        return ret

    def fmt_sold_price(self):
        return '$' + f"{self.sold_price:.2f}"
        
    def fmt_net_sold(self):
        return '$' + f"{self.net_sold:.2f}"
        
    def fmt_ebay_order(self, markup=True):
        ret = ''
        if self.ebay_order:
            ret = '<a href="https://www.ebay.com/mesh/ord/details?orderid=' + self.ebay_order.order_id + '">eBay:Order&nbsp;$' + f"{self.ebay_order.price:.2f}" + '</a>'
        if markup:
            return Markup(ret)
        else:
            return ret
