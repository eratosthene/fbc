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


class SupplyModelView(ModelView):
    datamodel = MongoEngineInterface(Supply)
    list_columns = ["name", "quantity", "purchase_order"]


class PurchaseOrderModelView(ModelView):
    datamodel = MongoEngineInterface(PurchaseOrder)
    list_columns = ["date", "purchase_price", "notes", "link"]
    label_columns = {"purchase_price": "Price"}
