import logging
from flask_appbuilder import IndexView
from flask_appbuilder.views import expose
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from app.models import Unit, PurchaseLot, DiscogsRelease
from flask import redirect
import bson
import re
import discogs_client
from flask import current_app
from app.util import add_discogs_release

logger = logging.getLogger()

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

    @expose('/syncdiscogs')
    def syncdiscogs(self):
        self.update_redirect()
        logger.info('Updating discogs...')
        d = discogs_client.Client(current_app.config['DISCOGS_SETTINGS']['USER_AGENT'], user_token=current_app.config['DISCOGS_SETTINGS']['USER_TOKEN'])
        me = d.identity()
        releases = me.collection_folders[0].releases
        local_releases = DiscogsRelease.objects()
        logger.info('Total releases: ' + str(len(releases)))
        logger.info('Total local releases: ' + str(len(local_releases)))
        for item in releases:
            logger.debug('Checking discogs: ' + str(item))
            if not DiscogsRelease.objects(instance_id=item.instance_id):
                logger.info('Adding ' + str(item))
                add_discogs_release(item)
                
        for item in local_releases:
            logger.debug('Checking local: ' + str(item))
            if not any(x.instance_id == item.instance_id for x in releases):
                logger.info('Removing ' + str(item))
                item.delete()
        
        return redirect('/discogsreleasemodelview/list/')
