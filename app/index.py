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
        lots=PurchaseLot.objects()
        lot_totals = {}
        totals = {
            'capital': 0,
            'gross': 0,
            'net': 0,
            'fees': 0,
            'feepc': 0,
            'profit': 0,
            'roi': 0
        }
        for l in lots:
            totals['capital'] += l.price
            lot_totals[l.id] = {}
            lot_totals[l.id]['gross'] = 0
            lot_totals[l.id]['net'] = 0
        for u in Unit.objects():
            if u.sales_receipt:
                lot_totals[u.purchase_lot.id]['gross'] += u.sales_receipt.sold_price 
                totals['gross'] += u.sales_receipt.sold_price
                lot_totals[u.purchase_lot.id]['net'] += u.sales_receipt.net_sold
                totals['net'] += u.sales_receipt.net_sold
        for l in lots:
            lot_totals[l.id]['fees'] = round(lot_totals[l.id]['gross'] - lot_totals[l.id]['net'], 2)
            totals['fees'] += lot_totals[l.id]['fees']
            if lot_totals[l.id]['gross'] > 0:
                lot_totals[l.id]['feepc'] = round(lot_totals[l.id]['fees'] / lot_totals[l.id]['gross'] * 100, 2)
            else:
                lot_totals[l.id]['feepc'] = 0.0
            lot_totals[l.id]['profit'] = round(lot_totals[l.id]['net'] - l.price, 2)
            totals['profit'] += lot_totals[l.id]['profit']
            if l.price > 0:
                lot_totals[l.id]['roi'] = round(lot_totals[l.id]['profit'] / l.price * 100, 2)
            else:
                lot_totals[l.id]['roi'] = 0.0
        if totals['gross'] > 0:
            totals['feepc'] = round(totals['fees'] / totals['gross'] * 100, 2)
        else:
            totals['feepc'] = 0.0
        if totals['capital'] > 0:
            totals['roi'] = round(totals['profit'] / totals['capital'] * 100, 2)
        return self.render_template(self.index_template,
                appbuilder=self.appbuilder,
                stock_total=stock_total,
                lots=lots,
                lot_totals=lot_totals,
                totals=totals
        )

