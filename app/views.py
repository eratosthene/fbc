from flask import render_template
from flask_appbuilder import ModelView, BaseView, expose, has_access
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from flask_appbuilder.actions import action
from flask_appbuilder.models.generic.interface import GenericInterface
from app import appbuilder
from app.models.inventory import Unit, PurchaseLot, StorageBox
from app.models.discogs import DiscogsRelease, Artist, Genre, Style, Folder, DiscogsListing, DiscogsOrder
from app.models.ebay import eBayListing, eBayOrder
from app.models.sales import SalesReceipt
from app.models.supplies import Supply, PurchaseOrder
import logging
from app.widgets import DiscogsReleaseListWidget, eBayListingListWidget, eBayOrderListWidget, DiscogsListingListWidget, DiscogsOrderListWidget

logger = logging.getLogger()

class UnitModelView(ModelView):
    datamodel = MongoEngineInterface(Unit)
    list_columns = [
        'name',
        'unit_type',
        'grading',
        'pressing',
        'fmt_retail_price',
        'sold',
        'purchase_lot',
        'storage_box',
        'link_column'
    ]
    label_columns = {
        'fmt_retail_price': 'Retail Price',
        'link_column': 'Links'
    }
    search_columns = [
        'name',
        'unit_type',
        'description',
        'discogs_release',
        'discogs_listing',
        'ebay_listing',
        'purchase_lot',
        'storage_box',
        'grading',
        'pressing',
        'matrix',
        'notes',
        'retail_price',
        'sold'
    ]

class SalesReceiptModelView(ModelView):
    datamodel = MongoEngineInterface(SalesReceipt)
    related_views = [ UnitModelView ]
    list_columns = [
        'date',
        'link_column',
        'fmt_sold_price',
        'fmt_net_sold'
    ]
    label_columns = {
        'link_column': 'Order Link',
        'fmt_sold_price': 'Sold Price',
        'fmt_net_sold': 'Net Sold'
    }
    show_columns = [
        'date',
        'ebay_order',
        'discogs_order',
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
        'notes',
        'list_total',
        'list_sold',
        'list_profit',
        'list_breakeven'
    ]
    show_columns = [
        'name', 
        'date', 
        'purchase_price', 
        'notes',
        'breakdown'
    ]
    label_columns = {
        'breakdown': 'Breakdown',
        'list_total': 'Units',
        'list_sold': 'Sold',
        'list_profit': 'Profit',
        'list_breakeven': 'B/E'
    }

class StorageBoxModelView(ModelView):
    datamodel = MongoEngineInterface(StorageBox)
    related_views = [ UnitModelView ]

class DiscogsReleaseModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsRelease)
    list_widget = DiscogsReleaseListWidget
    related_views = [ UnitModelView ]
    list_columns = [
        'title',
        'artists',
        'year',
        'master_year',
        'genres',
        'styles',
        'purchase_lot',
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
        'master_year',
        'genres',
        'styles',
        'instance_id',
        'released',
        'folder'
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

class eBayListingModelView(ModelView):
    datamodel = MongoEngineInterface(eBayListing)
    list_widget = eBayListingListWidget
    list_columns = ['item_id', 'title', 'fmt_price', 'fmt_url']
    search_columns = ['item_id', 'title']
    label_columns = {
        'fmt_price': 'Price',
        'fmt_url': 'URL'
    }

class eBayOrderModelView(ModelView):
    datamodel = MongoEngineInterface(eBayOrder)
    list_widget = eBayOrderListWidget
    list_columns = ['date', 'fmt_url', 'title', 'buyer', 'fmt_price']
    search_columns = ['order_id', 'title', 'buyer']
    label_columns = {
        'fmt_price': 'Price',
        'fmt_url': 'Order Id'
    }
    
class DiscogsListingModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsListing)
    list_widget = DiscogsListingListWidget
    list_columns = ['item_id', 'title', 'fmt_price', 'fmt_url']
    search_columns = ['item_id', 'title']
    label_columns = {
        'fmt_price': 'Price',
        'fmt_url': 'URL'
    }

class DiscogsOrderModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsOrder)
    list_widget = DiscogsOrderListWidget
    list_columns = ['date', 'fmt_url', 'title', 'buyer', 'fmt_price']
    search_columns = ['order_id', 'title', 'buyer']
    label_columns = {
        'fmt_price': 'Price',
        'fmt_url': 'Order Id'
    }
    
class SupplyModelView(ModelView):
    datamodel = MongoEngineInterface(Supply)
    list_columns = [
        'name',
        'quantity',
        'purchase_order'
    ]

class PurchaseOrderModelView(ModelView):
    datamodel = MongoEngineInterface(PurchaseOrder)
    list_columns = [
        'date',
        'purchase_price',
        'notes',
        'link'
    ]
    label_columns = {
        'purchase_price': 'Price'
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
appbuilder.add_view(eBayListingModelView, "eBay Listings", category="Sales")
appbuilder.add_view(eBayOrderModelView, "eBay Orders", category="Sales")
appbuilder.add_view(DiscogsListingModelView, "Discogs Listings", category="Sales")
appbuilder.add_view(DiscogsOrderModelView, "Discogs Orders", category="Sales")
appbuilder.add_view(SupplyModelView, "Supply List", category="Supplies")
appbuilder.add_view(PurchaseOrderModelView, "Purchase Orders", category="Supplies")

"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

