import logging

from flask import render_template, request
from flask_appbuilder import BaseView, ModelView, expose, has_access
from flask_appbuilder.actions import action
from flask_appbuilder.models.generic.interface import GenericInterface
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from flask_wtf import FlaskForm

from app import appbuilder
from app.models.discogs import (
    Artist,
    DiscogsListing,
    DiscogsOrder,
    DiscogsRelease,
    Folder,
    Genre,
    Style,
)
from app.models.ebay import eBayListing, eBayOrder
from app.models.inventory import PurchaseLot, StorageBox, Unit
from app.models.sales import SalesReceipt
from app.models.supplies import PurchaseOrder, Supply
from app.widgets import (
    DiscogsListingListWidget,
    DiscogsOrderListWidget,
    DiscogsReleaseListWidget,
    eBayListingListWidget,
    eBayOrderListWidget,
)
from app.view.inventory import UnitModelView

logger = logging.getLogger()


class DiscogsReleaseModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsRelease)
    list_widget = DiscogsReleaseListWidget
    related_views = [UnitModelView]
    list_columns = [
        "title",
        "artists",
        "year",
        "master_year",
        "genres",
        "styles",
        "purchase_lot",
        "link_column",
    ]
    label_columns = {"link_column": "Links"}
    edit_columns = [
        "title",
        "artists",
        "year",
        "master_id",
        "master_year",
        "genres",
        "styles",
        "instance_id",
        "released",
        "folder",
    ]


class ArtistModelView(ModelView):
    datamodel = MongoEngineInterface(Artist)
    related_views = [DiscogsReleaseModelView]
    list_columns = [
        "name",
        "sort_name",
        "artist_id",
    ]
    related_views = [DiscogsReleaseModelView]


class GenreModelView(ModelView):
    datamodel = MongoEngineInterface(Genre)
    base_order = ("name", "desc")
    related_views = [DiscogsReleaseModelView]


class StyleModelView(ModelView):
    datamodel = MongoEngineInterface(Style)
    base_order = ("name", "desc")
    related_views = [DiscogsReleaseModelView]


class FolderModelView(ModelView):
    datamodel = MongoEngineInterface(Folder)
    list_columns = ["name", "folder_id"]
    base_order = ("name", "desc")
    related_views = [DiscogsReleaseModelView]
