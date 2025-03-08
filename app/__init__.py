import logging

from flask import Flask
from flask import render_template
from flask_appbuilder import AppBuilder
from flask_appbuilder.security.mongoengine.manager import SecurityManager
from flask_mongoengine import MongoEngine

from app.index import MyIndexView
from app.views.inventory import UnitModelView, PurchaseLotModelView, StorageBoxModelView
from app.views.discogs import (
    DiscogsReleaseModelView,
    ArtistModelView,
    GenreModelView,
    StyleModelView,
    FolderModelView,
)
from app.views.sales import (
    SalesReceiptModelView,
    eBayListingModelView,
    eBayOrderModelView,
    DiscogsListingModelView,
    DiscogsOrderModelView,
)
from app.views.supplies import SupplyModelView, PurchaseOrderModelView

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_envvar("FBC_SETTINGS")
db = MongoEngine(app)
appbuilder = AppBuilder(
    app, security_manager_class=SecurityManager, indexview=MyIndexView
)


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


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
