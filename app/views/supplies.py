import logging

from flask_appbuilder import ModelView
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface

from app.models.supplies import PurchaseOrder, Supply

logger = logging.getLogger()


class SupplyModelView(ModelView):
    datamodel = MongoEngineInterface(Supply)
    list_columns = ["name", "quantity", "purchase_order"]


class PurchaseOrderModelView(ModelView):
    datamodel = MongoEngineInterface(PurchaseOrder)
    list_columns = ["date", "purchase_price", "notes", "link"]
    label_columns = {"purchase_price": "Price"}
