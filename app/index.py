import logging
from flask_appbuilder import IndexView
from flask_appbuilder.views import expose
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from app.models import Unit, PurchaseLot
from flask import redirect
import bson
import re

class MyIndexView(IndexView):
    index_template = "index.html"

    @expose('/')
    def index(self):
        self.update_redirect()
        stock_total = Unit.objects(sold=False).count()
        return self.render_template(self.index_template,
                appbuilder=self.appbuilder,
                stock_total=stock_total,
                lots=PurchaseLot.objects()
        )

