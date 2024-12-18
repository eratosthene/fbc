from mongoengine import Document
from mongoengine import IntField, StringField, ListField, ReferenceField, BooleanField, DictField, FloatField
from flask import Markup, url_for
from flask_appbuilder.models.decorators import renders

class Unit(Document):
    name = StringField(required=True)
    unit_type = StringField()
    description = StringField()
    discogs_release = ReferenceField('DiscogsRelease')
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

    def link_column(self):
        if self.discogs_release:
            return Markup(
                '<ul><li>' + self.discogs_release.release_show(False) + '</li><li>' + self.discogs_release.master_show(False) + '</li></ul>'
            )
        else:
            return Markup('')
        
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
    