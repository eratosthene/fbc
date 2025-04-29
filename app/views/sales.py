from flask_appbuilder import ModelView
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface

from app.models.discogs import (
    DiscogsListing,
    DiscogsOrder,
)
from app.models.ebay import eBayListing, eBayOrder
from app.models.sales import SalesReceipt
from app.widgets import (
    DiscogsListingListWidget,
    DiscogsOrderListWidget,
    eBayListingListWidget,
    eBayOrderListWidget,
)
from app.views.inventory import UnitModelView
from app.util import CustomForm


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


class eBayListingModelView(ModelView):
    datamodel = MongoEngineInterface(eBayListing)
    list_widget = eBayListingListWidget
    list_columns = ["item_id", "title", "fmt_price", "fmt_url"]
    search_columns = ["item_id", "price", "title"]
    label_columns = {"fmt_price": "Price", "fmt_url": "URL"}
    related_views = [UnitModelView]


class eBayOrderModelView(ModelView):
    datamodel = MongoEngineInterface(eBayOrder)
    list_widget = eBayOrderListWidget
    list_columns = ["date", "fmt_url", "title", "buyer", "fmt_price", "links"]
    search_columns = ["order_id", "price", "title", "buyer"]
    label_columns = {"fmt_price": "Price", "fmt_url": "Order Id", "links": "Links"}
    related_views = [SalesReceiptModelView]


class DiscogsListingModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsListing)
    list_widget = DiscogsListingListWidget
    list_columns = ["item_id", "title", "fmt_price", "fmt_url"]
    search_columns = ["item_id", "price", "title"]
    label_columns = {"fmt_price": "Price", "fmt_url": "URL"}
    related_views = [UnitModelView]


class DiscogsOrderModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsOrder)
    list_widget = DiscogsOrderListWidget
    list_columns = ["date", "fmt_url", "title", "buyer", "fmt_price", "add_sr"]
    search_columns = ["order_id", "price", "title", "buyer"]
    label_columns = {"fmt_price": "Price", "fmt_url": "Order Id", "add_sr": "Add SR"}
    related_views = [SalesReceiptModelView]
