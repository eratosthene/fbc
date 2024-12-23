from app.models.discogs import DiscogsRelease
from app.models.sales import SalesReceipt
from app.models.ebay import eBayListing
from mongoengine import Document
from mongoengine import IntField, StringField, ListField, ReferenceField, BooleanField, DictField, FloatField
from flask import Markup, url_for
from flask_appbuilder.models.decorators import renders

class Unit(Document):
    name = StringField(required=True)
    unit_type = StringField()
    description = StringField()
    discogs_release = ReferenceField('DiscogsRelease')
    discogs_listing_id = StringField()
    ebay_listing = ReferenceField('eBayListing')
    ebay_draft_url = StringField()
    purchase_lot = ReferenceField('PurchaseLot')
    storage_box = ReferenceField('StorageBox')
    grading = StringField()
    pressing = StringField()
    matrix = StringField()
    notes = StringField()
    retail_price = FloatField()
    sold = BooleanField()
    sales_receipt = ReferenceField('SalesReceipt')
    
    def __unicode__(self):
        return self.name + ' ' + self.unit_type + ' ' + self.pressing + ' ' + self.grading

    def __repr__(self):
        return self.name + ' ' + self.unit_type + ' ' + self.pressing + ' ' + self.grading

    def fmt_retail_price(self):
        if self.retail_price:
            return '$' + f"{self.retail_price:.2f}"
        else:
            return None
        
    def link_column(self):
        ret = ''
        if self.discogs_release:
            ret = ret + self.discogs_release.release_show(False) + '<br/>' + self.discogs_release.master_show(False) + '<br/>'
        if self.ebay_listing:
            ret = ret + '<a href="https://www.ebay.com/itm/' + str(self.ebay_listing.item_id) + '">eBay:Listing&nbsp;$' + f"{self.ebay_listing.price:.2f}"'</a><br/>'
        if self.ebay_draft_url:
            ret = ret + '<a href="' + self.ebay_draft_url + '">eBay:Draft</a><br/>'
        if self.discogs_listing_id:
            ret = ret + '<a href="https://www.discogs.com/sell/item/' + str(self.discogs_listing_id) + '">D:Listing</a><br/>'
        if self.sales_receipt:
            ret = ret + '<a href="' + url_for('SalesReceiptModelView.show',pk=str(self.sales_receipt.id)) + '">SalesReceipt&nbsp$' + f"{self.sales_receipt.net_sold:.2f}" + '</a><br/>'
            if self.sales_receipt.ebay_order:
                ret = ret + self.sales_receipt.fmt_ebay_order(False)
        return Markup(ret)
            
class PurchaseLot(Document):
    name  = StringField(required=True)
    date  = StringField(required=True)
    price = FloatField(required=True)
    notes = StringField()
    
    @renders('price')
    def purchase_price(self):
        return '$' + f"{self.price:.2f}"
    
    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

class StorageBox(Document):
    name = StringField(required=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

