from mongoengine import Document
from mongoengine import IntField, StringField, ListField, ReferenceField, BooleanField, DictField, FloatField
from flask import Markup
from flask_appbuilder.models.decorators import renders

class Unit(Document):
    name = StringField(required=True)
    unit_type = StringField()
    description = StringField()
    discogs_release = ReferenceField('DiscogsRelease')
    discogs_instance = ReferenceField('DiscogsInstance')
    discogs_listing = ReferenceField('DiscogsListing')
    ebay_listing = ReferenceField('eBayListing')
    purchase_lot = ReferenceField('PurchaseLot')
    storage_box = ReferenceField('StorageBox')
    grading = StringField()
    pressing = StringField()
    matrix = StringField()
    notes = StringField()
    retail_price = FloatField()
    sold = BooleanField()
    
    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

class DiscogsRelease(Document):
    release_id = IntField(required=True, unique=True)
    artists     = ListField(ReferenceField('Artist'), required=True)
    genres      = ListField(ReferenceField('Genre'))
    styles      = ListField(ReferenceField('Style'))
    title       = StringField(required=True)
    year        = IntField()
    master_id   = IntField()
    master_year = IntField()
    formats     = ListField(DictField())
    released    = StringField()
    
    def __unicode__(self):
        return self.title

    def __repr__(self):
        return self.title

    def release_show(self):
        return Markup(
            '<a href="https://www.discogs.com/release/' + str(self.release_id) + '">' + str(self.release_id) + '</a>'
        )
    
    def master_show(self):
        return Markup(
            '<a href="https://www.discogs.com/master/' + str(self.master_id) + '">' + str(self.master_id) + '</a>'
        )
        
class DiscogsInstance(Document):
    instance_id = IntField(required=True, unique=True)
    notes       = ListField(DictField())
    folder      = ReferenceField('Folder')

class DiscogsListing(Document):
    discogs_listing_id = IntField(required=True, unique=True)
        
    def discogs_show(self):
        return Markup(
            '<a href="https://www.discogs.com/sell/item/' + str(self.discogs_listing_id) + '">' + str(self.discogs_listing_id) + '</a>'
        )

class eBayListing(Document):
    ebay_listing_id = IntField(required=True, unique=True)
            
    def ebay_show(self):
        return Markup(
            '<a href="https://www.ebay.com/itm/' + str(self.ebay_listing_id) + '">' + str(self.ebay_listing_id) + '</a>'
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

class SalesReceipt(Document):
    date = StringField(required=True)
    ebay_listing = ReferenceField('eBayListing')
    discogs_listing = ReferenceField('DiscogsListing')
    sold_price = FloatField()
    net_sold = FloatField()
    units = ListField(ReferenceField('Unit'))
    