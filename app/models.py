from mongoengine import Document
from mongoengine import IntField, StringField, ListField, ReferenceField, BooleanField, DictField, FloatField
from flask import Markup, url_for
from flask_appbuilder.models.decorators import renders

class SalesReceipt(Document):
    date = StringField(required=True)
    ebay_order_id = StringField()
    sold_price = FloatField()
    net_sold = FloatField()

    def __unicode__(self):
        return self.date + ': ' + self.ebay_order_id + ' $' + f"{self.sold_price:.2f}" + '/$' + f"{self.net_sold:.2f}"

    def __repr__(self):
        return self.date + ': ' + self.ebay_order_id + ' $' + f"{self.sold_price:.2f}" + '/$' + f"{self.net_sold:.2f}"

    def ebay_order(self, markup=True):
        ret = ''
        if self.ebay_order_id:
            ret = '<a href="https://www.ebay.com/mesh/ord/details?orderid=' + self.ebay_order_id + '">eBay Order</a>'
        if markup:
            return Markup(ret)
        else:
            return ret

class Unit(Document):
    name = StringField(required=True)
    unit_type = StringField()
    description = StringField()
    discogs_release = ReferenceField('DiscogsRelease')
    discogs_listing_id = StringField()
    ebay_listing_id = StringField()
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

    def link_column(self):
        ret = ''
        if self.discogs_release:
            ret = ret + self.discogs_release.release_show(False) + '<br/>' + self.discogs_release.master_show(False) + '<br/>'
        if self.ebay_listing_id:
            ret = ret + '<a href="https://www.ebay.com/itm/' + str(self.ebay_listing_id) + '">' + str(self.ebay_listing_id) + '</a><br/>'
        if self.discogs_listing_id:
            ret = ret + '<a href="https://www.discogs.com/sell/item/' + str(self.discogs_listing_id) + '">' + str(self.discogs_listing_id) + '</a><br/>'
        if self.sales_receipt:
            ret = ret + '<a href="' + url_for('SalesReceiptModelView.show',pk=str(self.sales_receipt.id)) + '">Sales Receipt</a><br/>'
            if self.sales_receipt.ebay_order_id:
                ret = ret + self.sales_receipt.ebay_order(False)
        return Markup(ret)
            
class DiscogsRelease(Document):
    release_id = IntField(required=True, unique=True)
    title       = StringField(required=True)
    artists     = ListField(ReferenceField('Artist'), required=True)
    year        = IntField()
    genres      = ListField(ReferenceField('Genre'))
    styles      = ListField(ReferenceField('Style'))
    master_id   = IntField()
    master_year = IntField()
    formats     = ListField(DictField())
    released    = StringField()
    instance_id = IntField()
    notes       = ListField(DictField())
    folder      = ReferenceField('Folder')
    
    def artist_rep(self):
        num = 0
        ret = ''
        for artist in self.artists:
            if num:
                ret = ret + ' / '
            ret = ret + str(artist)
            num = num + 1
        return ret
        
    def __unicode__(self):
        return self.artist_rep() + ' - ' + self.title + ' (' + str(self.year) + ')'

    def __repr__(self):
        return self.artist_rep() + ' - ' + self.title + ' (' + str(self.year) + ')'

    def release_show(self, markup=True):
        s = '<a href="https://www.discogs.com/release/' + str(self.release_id) + '">Release ' + str(self.release_id) + '</a>'
        if markup:
            return Markup(s)
        else:
            return s
    
    def master_show(self, markup=True):
        s = '<a href="https://www.discogs.com/master/' + str(self.master_id) + '">Master ' + str(self.master_id) + '</a>'
        if markup:
            return Markup(s)
        else:
            return s
        
    def unit_list(self, markup=True):
        s = '<a href="' + url_for('UnitModelView.list',_flt_0_discogs_release=str(self.id)) + '">Search Units</a>'
        if markup:
            return Markup(s)
        else:
            return s
        
    def link_column(self):
        return Markup(
            '<ul><li>' + self.release_show(False) + '</li><li>' + self.master_show(False) + '</li><li>' + self.unit_list(False) + '</li></ul>'
        )
        
class Artist(Document):
    artist_id   = IntField(required=True, unique=True)
    name        = StringField(required=True)
    sort_name   = StringField()

    def __unicode__(self):
        if self.sort_name:
            return self.sort_name
        else:
            return self.name

    def __repr__(self):
        if self.sort_name:
            return self.sort_name
        else:
            return self.name

class Genre(Document):
    name        = StringField(required=True, unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

class Style(Document):
    name        = StringField(required=True, unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

class Folder(Document):
    folder_id   = IntField(required=True, unique=True)
    name        = StringField(required=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

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
