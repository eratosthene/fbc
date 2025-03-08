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


class eBayListingModelView(ModelView):
    datamodel = MongoEngineInterface(eBayListing)
    list_widget = eBayListingListWidget
    list_columns = ["item_id", "title", "fmt_price", "fmt_url"]
    search_columns = ["item_id", "title"]
    label_columns = {"fmt_price": "Price", "fmt_url": "URL"}


class eBayOrderModelView(ModelView):
    datamodel = MongoEngineInterface(eBayOrder)
    list_widget = eBayOrderListWidget
    list_columns = ["date", "fmt_url", "title", "buyer", "fmt_price", "add_sr"]
    search_columns = ["order_id", "title", "buyer"]
    label_columns = {"fmt_price": "Price", "fmt_url": "Order Id", "add_sr": "Add SR"}


class DiscogsListingModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsListing)
    list_widget = DiscogsListingListWidget
    list_columns = ["item_id", "title", "fmt_price", "fmt_url"]
    search_columns = ["item_id", "title"]
    label_columns = {"fmt_price": "Price", "fmt_url": "URL"}


class DiscogsOrderModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsOrder)
    list_widget = DiscogsOrderListWidget
    list_columns = ["date", "fmt_url", "title", "buyer", "fmt_price", "add_sr"]
    search_columns = ["order_id", "title", "buyer"]
    label_columns = {"fmt_price": "Price", "fmt_url": "Order Id", "add_sr": "Add SR"}


class CustomForm(FlaskForm):
    """
    A custom FlaskForm which reads data from request params
    """

    @classmethod
    def refresh(cls, obj=None):
        kw = dict(obj=obj)
        if request.method == "GET":
            kw["formdata"] = request.args
        form = cls(**kw)
        return form


class SalesReceiptModelView(ModelView):
    datamodel = MongoEngineInterface(SalesReceipt)
    related_views = [UnitModelView]
    list_columns = ["date", "link_column", "fmt_sold_price", "fmt_net_sold"]
    label_columns = {
        "link_column": "Order Link",
        "fmt_sold_price": "Sold Price",
        "fmt_net_sold": "Net Sold",
    }
    show_columns = ["date", "ebay_order", "discogs_order", "sold_price", "net_sold"]

    def _init_forms(self):
        super(ModelView, self)._init_forms()
        self.add_form = type("CustomForm", (CustomForm, self.add_form), {})
