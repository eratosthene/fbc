from flask import render_template
from flask_appbuilder import ModelView, BaseView, expose, has_access
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from flask_appbuilder.actions import action
from flask_appbuilder.models.generic.interface import GenericInterface
from app import appbuilder
from app.models import Unit, PurchaseLot, StorageBox, SalesReceipt
from app.models import DiscogsRelease, Artist, Genre, Style, Folder
from app.models import eBayModel, eBaySession
import logging
import ebaysdk
from ebaysdk.utils import getNodeText
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

logger = logging.getLogger()
ebay_session = eBaySession()

class UnitModelView(ModelView):
    datamodel = MongoEngineInterface(Unit)
    list_columns = [
        'name',
        'unit_type',
        'grading',
        'pressing',
        'fmt_retail_price',
        'sold',
        'link_column'
    ]
    label_columns = {
        'fmt_retail_price': 'Retail Price',
        'link_column': 'Links'
    }

class SalesReceiptModelView(ModelView):
    datamodel = MongoEngineInterface(SalesReceipt)
    related_views = [ UnitModelView ]
    list_columns = [
        'date',
        'ebay_order',
        'fmt_sold_price',
        'fmt_net_sold'
    ]
    label_columns = {
        'ebay_order': 'eBay:Order',
        'fmt_sold_price': 'Sold Price',
        'fmt_net_sold': 'Net Sold'
    }
    show_columns = [
        'date',
        'ebay_order',
        'sold_price',
        'net_sold'
    ]

class PurchaseLotModelView(ModelView):
    datamodel = MongoEngineInterface(PurchaseLot)
    related_views = [ UnitModelView ]
    list_columns = [
        'name', 
        'date', 
        'purchase_price', 
        'notes'
    ]

class StorageBoxModelView(ModelView):
    datamodel = MongoEngineInterface(StorageBox)
    related_views = [ UnitModelView ]

class DiscogsReleaseModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsRelease)
    related_views = [ UnitModelView ]
    list_columns = [
        'title',
        'artists',
        'year',
        'master_year',
        'genres',
        'styles',
        'link_column'
    ]
    label_columns = {
        'link_column': 'Links'
    }
    edit_columns = [
        'title',
        'artists',
        'year',
        'master_id',
        'master_year'        
    ]

class ArtistModelView(ModelView):
    datamodel = MongoEngineInterface(Artist)
    related_views = [ DiscogsReleaseModelView ]
    list_columns = [
        'name',
        'sort_name',
        'artist_id',
    ]
    related_views = [ DiscogsReleaseModelView ]

class GenreModelView(ModelView):
    datamodel = MongoEngineInterface(Genre)
    base_order = ('name', 'desc')
    related_views = [ DiscogsReleaseModelView ]

class StyleModelView(ModelView):
    datamodel = MongoEngineInterface(Style)
    base_order = ('name', 'desc')
    related_views = [ DiscogsReleaseModelView ]
    
class FolderModelView(ModelView):
    datamodel = MongoEngineInterface(Folder)
    list_columns = [
        'name',
        'folder_id'
    ]
    base_order = ('name', 'desc')
    related_views = [ DiscogsReleaseModelView ]

class eBayModelView(ModelView):
    datamodel = GenericInterface(eBayModel, ebay_session)
    base_permissions = ['can_list', 'can_show']
    list_columns = ['item_id', 'title', 'fmt_price', 'fmt_url']
    search_columns = ['item_id', 'title']
    label_columns = {
        'fmt_price': 'Price',
        'fmt_url': 'URL'
    }
    
appbuilder.add_view(UnitModelView, "Units", category="Inventory")
appbuilder.add_view(PurchaseLotModelView, "Purchase Lots", category="Inventory")
appbuilder.add_view(StorageBoxModelView, "Storage Boxes", category="Inventory")
appbuilder.add_view(DiscogsReleaseModelView, "Releases", category="Discogs")
appbuilder.add_view(ArtistModelView, "Artists", category="Discogs")
appbuilder.add_view(GenreModelView, "Genres", category="Discogs")
appbuilder.add_view(StyleModelView, "Styles", category="Discogs")
appbuilder.add_view(FolderModelView, "Folders", category="Discogs")
appbuilder.add_view(SalesReceiptModelView, "Sales Receipts", category="Sales")
appbuilder.add_view(eBayModelView, "eBay Listings", category="Sales")

"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

