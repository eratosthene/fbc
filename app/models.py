from mongoengine import Document
from mongoengine import IntField, StringField, ListField, ReferenceField, BooleanField, DictField, FloatField
from flask import Markup, url_for
from flask_appbuilder.models.decorators import renders
from flask_appbuilder.models.generic import GenericModel, GenericSession, GenericColumn
from flask_appbuilder.models.generic.interface import GenericInterface
import ebaysdk
from ebaysdk.utils import getNodeText
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
import logging
from flask import current_app
import pprint
import datetime

logger = logging.getLogger()

class eBayModel(GenericModel):
    item_id = GenericColumn(str, primary_key=True)
    title = GenericColumn(str)
    price = GenericColumn(float)
    url = GenericColumn(str)

    def __unicode__(self):
        return self.item_id + ': ' + self.title + ' $' + f"{self.price:.2f}"

    def __repr__(self):
        return self.item_id + ': ' + self.title + ' $' + f"{self.price:.2f}"
        
    def fmt_price(self):
        return '$' + f"{self.price:.2f}"
        
    def fmt_url(self):
        return Markup(
            '<a href="' + self.url + '">' + self.url + '</a>'
        )

class eBaySession(GenericSession):
    def do_query(self, endpoint=str, options=dict):
        ebayconfig = current_app.config['EBAY_SETTINGS']
        try:
            api = Trading(debug=False, config_file=None, appid=ebayconfig['APP_ID'], domain='api.ebay.com',
                          certid=ebayconfig['CERT_ID'], devid=ebayconfig['DEV_ID'], token=ebayconfig['USER_TOKEN'])

            response = api.execute(endpoint, options)
            logging.info('eBay response: ' + api.response_status())
            return response.dict()
        except ConnectionError as e:
            logging.error(e)
            logging.error(e.response.dict())
            
    def _add_object(self, obj):
        model = eBayModel()
        model.item_id = obj['ItemID']
        model.title = obj['Title']
        model.price = float(obj['BuyItNowPrice']['value'])
        model.url = obj['ListingDetails']['ViewItemURL']
        self.add(model)
    
    def get(self, pk):
        resp = self.do_query('GetItem',{'ItemID':pk})
        try:
            listing = resp['Item']
            logger.debug(pprint.pformat(listing))
            model = eBayModel()
            model.item_id = listing['ItemID']
            model.title = listing['Title']
            model.price = float(listing['ListingDetails']['ConvertedStartPrice']['value'])
            model.url = listing['ListingDetails']['ViewItemURL']
            logger.debug(model)
            return model
        except Exception as e:
            logging.error(e)
            return None
        
    def all(self):
        self.delete_all(eBayModel())
        resp = self.do_query('GetMyeBaySelling', {
            'ActiveList': {
                'Include': True,
                'Sort': 'StartTime',
                'Pagination': {
                    'EntriesPerPage':200,
                    'PageNumber':1
                }
            }
        })
        listings = resp['ActiveList']['ItemArray']['Item']
        for listing in listings:
            self._add_object(listing)
        return super(eBaySession, self).all()

class eBayOrderModel(GenericModel):
    order_id = GenericColumn(str, primary_key=True)
    date = GenericColumn(str)
    buyer = GenericColumn(str)
    price = GenericColumn(float)

    def __unicode__(self):
        return self.order_id + ': ' + self.buyer + ' $' + f"{self.price:.2f}"

    def __repr__(self):
        return self.order_id + ': ' + self.buyer + ' $' + f"{self.price:.2f}"
        
    def fmt_price(self):
        return '$' + f"{self.price:.2f}"
        
    def fmt_url(self):
        return Markup(
            '<a href="https://www.ebay.com/mesh/ord/details?orderid=' + self.order_id + '">' + self.order_id + '</a>'
        )
class eBayOrderSession(GenericSession):
    def do_query(self, endpoint=str, options=dict):
        ebayconfig = current_app.config['EBAY_SETTINGS']
        try:
            api = Trading(debug=False, config_file=None, appid=ebayconfig['APP_ID'], domain='api.ebay.com',
                          certid=ebayconfig['CERT_ID'], devid=ebayconfig['DEV_ID'], token=ebayconfig['USER_TOKEN'])

            response = api.execute(endpoint, options)
            logging.info('eBay response: ' + api.response_status())
            return response.dict()
        except ConnectionError as e:
            logging.error(e)
            logging.error(e.response.dict())
            
    def _add_object(self, obj):
        model = eBayOrderModel()
        model.order_id = obj['OrderID']
        model.price = float(obj['Subtotal']['value'])
        model.buyer = obj['BuyerUserID']
        model.date = obj['CreatedTime'][:10]
        self.add(model)
    
    def get(self, pk):
        resp = self.do_query('GetOrders',{'OrderIDArray':[{'OrderID':pk}]})
        try:
            order = resp['OrderArray']['Order'][0]
            logger.debug(pprint.pformat(order))
            model = eBayOrderModel()
            model.order_id = order['OrderID']
            model.price = float(order['Subtotal']['value'])
            model.buyer = order['BuyerUserID']
            model.date = order['CreatedTime'][:10]
            logger.debug(model)
            return model
        except Exception as e:
            logging.error(e)
            return None
        
    def all(self):
        self.delete_all(eBayOrderModel())
        # currentTime = datetime.datetime.now()+datetime.timedelta(hours = 5)
        # startTime = currentTime + datetime.timedelta(days = -89)
        resp = self.do_query('GetOrders', {
            # 'CreateTimeFrom': str(startTime)[0:19],
            # 'CreateTimeTo': str(currentTime)[0:19],
            'NumberOfDays': 30,
            'OrderStatus': 'Completed'
        })
        with open('log.txt', 'w') as out:
            out.write(pprint.pformat(resp))
        orders = resp['OrderArray']['Order']
        for order in orders:
            self._add_object(order)
        return super(eBayOrderSession, self).all()

class SalesReceipt(Document):
    date = StringField(required=True)
    ebay_order_id = StringField()
    sold_price = FloatField()
    net_sold = FloatField()

    def __unicode__(self):
        return self.date + ': ' + self.ebay_order_id + ' $' + f"{self.sold_price:.2f}" + '/$' + f"{self.net_sold:.2f}"

    def __repr__(self):
        return self.date + ': ' + self.ebay_order_id + ' $' + f"{self.sold_price:.2f}" + '/$' + f"{self.net_sold:.2f}"

    def fmt_sold_price(self):
        return '$' + f"{self.sold_price:.2f}"
        
    def fmt_net_sold(self):
        return '$' + f"{self.net_sold:.2f}"
        
    def ebay_order(self, markup=True):
        ret = ''
        if self.ebay_order_id:
            ret = '<a href="https://www.ebay.com/mesh/ord/details?orderid=' + self.ebay_order_id + '">eBay:Order'
            ebay_order_session = eBayOrderSession()
            ebay_order = GenericInterface(eBayOrderModel, ebay_order_session)
            l = ebay_order.get(self.ebay_order_id)
            if l:
                ret = ret + '&nbsp;$' + f"{l.price:.2f}"
            ret = ret + '</a>'
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
        ebay_session = eBaySession()
        ebay = GenericInterface(eBayModel, ebay_session)
        ret = ''
        if self.discogs_release:
            ret = ret + self.discogs_release.release_show(False) + '<br/>' + self.discogs_release.master_show(False) + '<br/>'
        if self.ebay_listing_id:
            ret = ret + '<a href="https://www.ebay.com/itm/' + str(self.ebay_listing_id) + '">eBay:Listing'
            l = ebay.get(self.ebay_listing_id)
            if l:
                ret = ret + '&nbsp;$' + f"{l.price:.2f}"
            ret = ret + '</a><br/>'
        if self.ebay_draft_url:
            ret = ret + '<a href="' + self.ebay_draft_url + '">eBay:Draft</a><br/>'
        if self.discogs_listing_id:
            ret = ret + '<a href="https://www.discogs.com/sell/item/' + str(self.discogs_listing_id) + '">D:Listing</a><br/>'
        if self.sales_receipt:
            ret = ret + '<a href="' + url_for('SalesReceiptModelView.show',pk=str(self.sales_receipt.id)) + '">SalesReceipt&nbsp$' + f"{self.sales_receipt.net_sold:.2f}" + '</a><br/>'
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
        s = '<a href="https://www.discogs.com/release/' + str(self.release_id) + '">D:Release</a>'
        if markup:
            return Markup(s)
        else:
            return s
    
    def master_show(self, markup=True):
        s = '<a href="https://www.discogs.com/master/' + str(self.master_id) + '">D:Master</a>'
        if markup:
            return Markup(s)
        else:
            return s
        
    def unit_list(self, markup=True):
        s = '<a href="' + url_for('UnitModelView.list',_flt_0_discogs_release=str(self.id)) + '">ListUnits</a>'
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

class PurchaseOrder(Document):
    date  = StringField(required=True)
    price = FloatField(required=True)
    notes = StringField()
    link = StringField()
    
    @renders('price')
    def purchase_price(self):
        return '$' + f"{self.price:.2f}"
    
    def __unicode__(self):
        return self.date + ': ' + self.notes + ' $' + f"{self.price:.2f}"

    def __repr__(self):
        return self.date + ': ' + self.notes + ' $' + f"{self.price:.2f}"

    
class Supply(Document):
    name = StringField(required=True)
    quantity = IntField(required=True, default=0)
    purchase_order = ListField(ReferenceField('PurchaseOrder'))

    def __unicode__(self):
        return self.name + ': ' + str(self.quantity)

    def __repr__(self):
        return self.name + ': ' + str(self.quantity)

