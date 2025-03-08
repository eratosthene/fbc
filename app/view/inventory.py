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

logger = logging.getLogger()


class UnitModelView(ModelView):
    datamodel = MongoEngineInterface(Unit)
    list_columns = [
        "name",
        "unit_type",
        "grading",
        "pressing",
        "fmt_retail_price",
        "sold",
        "purchase_lot",
        "storage_box",
        "link_column",
    ]
    label_columns = {"fmt_retail_price": "Retail Price", "link_column": "Links"}
    search_columns = [
        "name",
        "unit_type",
        "description",
        "discogs_release",
        "discogs_listing",
        "ebay_listing",
        "purchase_lot",
        "storage_box",
        "grading",
        "pressing",
        "matrix",
        "notes",
        "retail_price",
        "sold",
    ]


class PurchaseLotModelView(ModelView):
    datamodel = MongoEngineInterface(PurchaseLot)
    related_views = [UnitModelView]
    list_columns = [
        "name",
        "date",
        "purchase_price",
        "notes",
        "list_total",
        "list_sold",
        "list_profit",
        "list_breakeven",
    ]
    show_columns = ["name", "date", "purchase_price", "notes", "breakdown"]
    label_columns = {
        "breakdown": "Breakdown",
        "list_total": "Units",
        "list_sold": "Sold",
        "list_profit": "Profit",
        "list_breakeven": "B/E",
    }


class StorageBoxModelView(ModelView):
    datamodel = MongoEngineInterface(StorageBox)
    related_views = [UnitModelView]
