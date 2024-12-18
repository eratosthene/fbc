from flask import render_template
from flask_appbuilder import ModelView, CompactCRUDMixin
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from flask_appbuilder.actions import action
from app import appbuilder
from app.models import Unit, PurchaseLot, StorageBox, SalesReceipt
from app.models import DiscogsRelease, Artist, Genre, Style, Folder
from app.models import DiscogsListing, eBayListing

class SalesReceiptModelView(ModelView):
    datamodel = MongoEngineInterface(SalesReceipt)

class UnitModelView(ModelView):
    datamodel = MongoEngineInterface(Unit)
    related_views = [ SalesReceiptModelView ]
    list_columns = [
        'name',
        'unit_type',
        'grading',
        'pressing',
        'retail_price',
        'sold',
        'link_column'
    ]
    label_columns = {
        'link_column': 'Links'
    }

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

class DiscogsListingModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsListing)
    related_views = [ UnitModelView ]

class eBayListingModelView(ModelView):
    datamodel = MongoEngineInterface(eBayListing)
    related_views = [ UnitModelView ]

appbuilder.add_view(UnitModelView, "Units", category="Inventory")
appbuilder.add_view(PurchaseLotModelView, "Purchase Lots", category="Inventory")
appbuilder.add_view(StorageBoxModelView, "Storage Boxes", category="Inventory")
appbuilder.add_view(DiscogsReleaseModelView, "Releases", category="Discogs")
appbuilder.add_view(ArtistModelView, "Artists", category="Discogs")
appbuilder.add_view(GenreModelView, "Genres", category="Discogs")
appbuilder.add_view(StyleModelView, "Styles", category="Discogs")
appbuilder.add_view(FolderModelView, "Folders", category="Discogs")
appbuilder.add_view(SalesReceiptModelView, "Sales Receipts", category="Sales")
appbuilder.add_view(DiscogsListingModelView, "Discogs Listings", category="Sales")
appbuilder.add_view(eBayListingModelView, "eBay Listings", category="Sales")


"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404

