import datetime
import logging
import pprint
import re

import bson
import discogs_client
import ebaysdk
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading
from ebaysdk.utils import getNodeText
from flask import current_app, redirect, request
from flask_appbuilder import IndexView
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface
from flask_appbuilder.views import expose

from app.models.discogs import DiscogsRelease
from app.models.ebay import eBayListing, eBayOrder
from app.models.inventory import PurchaseLot, StorageBox, Unit
from app.models.supplies import PurchaseOrder
from app.util import *

logger = logging.getLogger()


class MyIndexView(IndexView):
    index_template = "index.html"

    @expose("/")
    def index(self):
        self.update_redirect()
        stock_total = Unit.objects(sold=False).count()
        unit_total = Unit.objects().count()
        lots = PurchaseLot.objects()
        boxes = StorageBox.objects()
        lot_totals = {}
        box_totals = {}
        pos = PurchaseOrder.objects()
        supply_total = 0
        totals = {
            "capital": 0,
            "gross": 0,
            "net": 0,
            "fees": 0,
            "feepc": 0,
            "profit": 0,
            "roi": 0,
        }
        for b in boxes:
            box_totals[b.id] = {}
            box_totals[b.id]["name"] = b.name
            box_totals[b.id]["instock"] = Unit.objects(
                storage_box=b, sold=False
            ).count()
            box_totals[b.id]["capital"] = 0.0
            box_totals[b.id]["gross"] = 0.0
            box_totals[b.id]["net"] = 0.0
        box_totals[0] = {}
        box_totals[0]["name"] = "No Box Assigned"
        box_totals[0]["instock"] = Unit.objects(storage_box=b, sold=False).count()
        box_totals[0]["capital"] = 0.0
        box_totals[0]["gross"] = 0.0
        box_totals[0]["net"] = 0.0
        for l in lots:
            totals["capital"] += l.price
            lot_totals[l.id] = {}
            lot_totals[l.id]["gross"] = 0
            lot_totals[l.id]["net"] = 0
            lot_totals[l.id]["perunit"] = round(
                l.price / Unit.objects(purchase_lot=l).count(), 2
            )
        for po in pos:
            supply_total += po.price
        for u in Unit.objects():
            if u.sales_receipt:
                if u.storage_box:
                    box_totals[u.storage_box.id]["gross"] += u.sales_receipt.sold_price
                    box_totals[u.storage_box.id]["net"] += u.sales_receipt.net_sold
                else:
                    box_totals[0]["gross"] += u.sales_receipt.sold_price
                    box_totals[0]["net"] += u.sales_receipt.net_sold
                lot_totals[u.purchase_lot.id]["gross"] += u.sales_receipt.sold_price
                totals["gross"] += u.sales_receipt.sold_price
                lot_totals[u.purchase_lot.id]["net"] += u.sales_receipt.net_sold
                totals["net"] += u.sales_receipt.net_sold
            if u.storage_box:
                box_totals[u.storage_box.id]["capital"] += lot_totals[
                    u.purchase_lot.id
                ]["perunit"]
            else:
                box_totals[0]["capital"] += lot_totals[u.purchase_lot.id]["perunit"]
        for l in lots:
            lot_totals[l.id]["fees"] = round(
                lot_totals[l.id]["gross"] - lot_totals[l.id]["net"], 2
            )
            totals["fees"] += lot_totals[l.id]["fees"]
            if lot_totals[l.id]["gross"] > 0:
                lot_totals[l.id]["feepc"] = round(
                    lot_totals[l.id]["fees"] / lot_totals[l.id]["gross"] * 100, 2
                )
            else:
                lot_totals[l.id]["feepc"] = 0.0
            lot_totals[l.id]["profit"] = round(lot_totals[l.id]["net"] - l.price, 2)
            totals["profit"] += lot_totals[l.id]["profit"]
            if l.price > 0:
                lot_totals[l.id]["roi"] = round(
                    lot_totals[l.id]["profit"] / l.price * 100, 2
                )
            else:
                lot_totals[l.id]["roi"] = 0.0
        for b in boxes:
            box_totals[b.id]["fees"] = round(
                box_totals[b.id]["gross"] - box_totals[b.id]["net"], 2
            )
            if box_totals[b.id]["gross"] > 0:
                box_totals[b.id]["feepc"] = round(
                    box_totals[b.id]["fees"] / box_totals[b.id]["gross"] * 100, 2
                )
            else:
                box_totals[b.id]["feepc"] = 0.0
            box_totals[b.id]["profit"] = round(
                box_totals[b.id]["net"] - box_totals[b.id]["capital"], 2
            )
            if box_totals[b.id]["capital"] > 0:
                box_totals[b.id]["roi"] = round(
                    box_totals[b.id]["profit"] / box_totals[b.id]["capital"] * 100, 2
                )
            else:
                box_totals[b.id]["roi"] = 0.0
        box_totals[0]["fees"] = round(box_totals[0]["gross"] - box_totals[0]["net"], 2)
        if box_totals[0]["gross"] > 0:
            box_totals[0]["feepc"] = round(
                box_totals[0]["fees"] / box_totals[0]["gross"] * 100, 2
            )
        else:
            box_totals[0]["feepc"] = 0.0
        box_totals[0]["profit"] = round(
            box_totals[0]["net"] - box_totals[0]["capital"], 2
        )
        if box_totals[0]["capital"] > 0:
            box_totals[0]["roi"] = round(
                box_totals[0]["profit"] / box_totals[0]["capital"] * 100, 2
            )
        else:
            box_totals[0]["roi"] = 0.0
        if totals["gross"] > 0:
            totals["feepc"] = round(totals["fees"] / totals["gross"] * 100, 2)
        else:
            totals["feepc"] = 0.0
        if totals["capital"] > 0:
            totals["roi"] = round(totals["profit"] / totals["capital"] * 100, 2)
        total_net_profit = totals["profit"] - supply_total
        for l in lots:
            lot_totals[l.id]["instock"] = Unit.objects(
                purchase_lot=l, sold=False
            ).count()
        return self.render_template(
            self.index_template,
            appbuilder=self.appbuilder,
            stock_total=stock_total,
            lots=lots,
            lot_totals=lot_totals,
            totals=totals,
            supply_total=supply_total,
            total_net_profit=total_net_profit,
            unit_total=unit_total,
            box_totals=box_totals,
        )

    @expose("/syncdiscogs")
    def syncdiscogs(self):
        self.update_redirect()
        logger.info("Updating discogs...")
        d = discogs_client.Client(
            current_app.config["DISCOGS_SETTINGS"]["USER_AGENT"],
            user_token=current_app.config["DISCOGS_SETTINGS"]["USER_TOKEN"],
        )
        me = d.identity()
        releases = me.collection_folders[0].releases
        local_releases = DiscogsRelease.objects()
        logger.info("Total releases: " + str(len(releases)))
        logger.info("Total local releases: " + str(len(local_releases)))
        for item in releases:
            logger.debug("Checking discogs: " + str(item))
            if not DiscogsRelease.objects(instance_id=item.instance_id):
                logger.info("Adding " + str(item))
                add_discogs_release(item)

        for item in local_releases:
            logger.debug("Checking local: " + str(item))
            if not any(x.instance_id == item.instance_id for x in releases):
                o = Unit.objects().get(discogs_release=item)
                if isinstance(o, Unit):
                    logger.info("Updating " + str(o))
                    del o.discogs_release
                    o.save()
                else:
                    for unit in o:
                        logger.info("Updating " + str(unit))
                        del unit.discogs_release
                        unit.save()
                logger.info("Removing " + str(item))
                item.delete()

        ref = request.referrer
        if ref:
            return redirect(ref)
        else:
            return redirect("/discogsreleasemodelview/list/")

    @expose("/syncebaylistings")
    def syncebaylistings(self):
        self.update_redirect()
        logger.info("Updating eBay listings...")
        ebayconfig = current_app.config["EBAY_SETTINGS"]
        try:
            api = Trading(
                debug=False,
                config_file=None,
                appid=ebayconfig["APP_ID"],
                domain="api.ebay.com",
                certid=ebayconfig["CERT_ID"],
                devid=ebayconfig["DEV_ID"],
                token=ebayconfig["USER_TOKEN"],
            )

            response = api.execute(
                "GetMyeBaySelling",
                {
                    "ActiveList": {
                        "Include": True,
                        "Sort": "StartTime",
                        "Pagination": {"EntriesPerPage": 200, "PageNumber": 1},
                    }
                },
            )
            logging.info("eBay response: " + api.response_status())
            resp = response.dict()
            listings = resp["ActiveList"]["ItemArray"]["Item"]
            local_listings = eBayListing.objects()
            logger.info("Total listings: " + str(len(listings)))
            logger.info("Total local listings: " + str(len(local_listings)))
            for item in listings:
                # logger.info(item)
                logger.debug("Checking ebay: " + str(item["ItemID"]))
                if not eBayListing.objects(item_id=item["ItemID"]):
                    logger.info("Adding " + str(item["ItemID"]))
                    add_ebay_listing(item)
        except ConnectionError as e:
            logging.error(e)
            logging.error(e.response.dict())
        ref = request.referrer
        if ref:
            return redirect(ref)
        else:
            return redirect("/ebaylistingmodelview/list/")

    def doebaysync(self, api, response):
        logging.info("eBay response: " + api.response_status())
        resp = response.dict()
        orders = resp["OrderArray"]["Order"]
        local_orders = eBayOrder.objects()
        logger.info("Total orders: " + str(len(orders)))
        logger.info("Total local orders: " + str(len(local_orders)))
        for item in orders:
            # logger.info(item)
            logger.debug("Checking ebay: " + str(item["OrderID"]))
            if not eBayOrder.objects(order_id=item["OrderID"]):
                logger.info("Adding " + str(item["OrderID"]))
                add_ebay_order(item)

    @expose("/syncebayorders")
    def syncebayorders(self):
        self.update_redirect()
        logger.info("Updating eBay orders...")
        ebayconfig = current_app.config["EBAY_SETTINGS"]
        try:
            currentTime = datetime.datetime.now() + datetime.timedelta(days=1)
            startTime = currentTime + datetime.timedelta(days=-10)
            api = Trading(
                debug=False,
                config_file=None,
                appid=ebayconfig["APP_ID"],
                domain="api.ebay.com",
                certid=ebayconfig["CERT_ID"],
                devid=ebayconfig["DEV_ID"],
                token=ebayconfig["USER_TOKEN"],
            )

            response = api.execute(
                "GetOrders",
                {
                    "CreateTimeFrom": str(startTime)[0:19],
                    "CreateTimeTo": str(currentTime)[0:19],
                    "OrderStatus": "Completed",
                },
            )
            self.doebaysync(api, response)
        except ConnectionError as e:
            logging.error(e)
            logging.error(e.response.dict())
        ref = request.referrer
        if ref:
            return redirect(ref)
        else:
            return redirect("/ebayordermodelview/list/")

    @expose("/syncebayordersdeep")
    def syncebayordersdeep(self):
        self.update_redirect()
        logger.info("Deep updating eBay orders...")
        ebayconfig = current_app.config["EBAY_SETTINGS"]
        try:
            currentTime = datetime.datetime.now() + datetime.timedelta(days=1)
            startTime = currentTime + datetime.timedelta(days=-88)
            api = Trading(
                debug=False,
                config_file=None,
                appid=ebayconfig["APP_ID"],
                domain="api.ebay.com",
                certid=ebayconfig["CERT_ID"],
                devid=ebayconfig["DEV_ID"],
                token=ebayconfig["USER_TOKEN"],
            )

            response = api.execute(
                "GetOrders",
                {
                    "CreateTimeFrom": str(startTime)[0:19],
                    "CreateTimeTo": str(currentTime)[0:19],
                    "OrderStatus": "Completed",
                },
            )
            self.doebaysync(api, response)
        except ConnectionError as e:
            logging.error(e)
            logging.error(e.response.dict())
        ref = request.referrer
        if ref:
            return redirect(ref)
        else:
            return redirect("/ebayordermodelview/list/")

    @expose("/syncdiscogslistings")
    def syncdiscogslistings(self):
        self.update_redirect()
        logger.info("Updating Discogs listings...")
        d = discogs_client.Client(
            current_app.config["DISCOGS_SETTINGS"]["USER_AGENT"],
            user_token=current_app.config["DISCOGS_SETTINGS"]["USER_TOKEN"],
        )
        me = d.identity()
        inventory = me.inventory
        for item in inventory:
            add_discogs_listing(item)
        ref = request.referrer
        if ref:
            return redirect(ref)
        else:
            return redirect("/discogslistingmodelview/list/")

    @expose("/syncdiscogsorders")
    def syncdiscogsorders(self):
        self.update_redirect()
        logger.info("Updating Discogs orders...")
        d = discogs_client.Client(
            current_app.config["DISCOGS_SETTINGS"]["USER_AGENT"],
            user_token=current_app.config["DISCOGS_SETTINGS"]["USER_TOKEN"],
        )
        me = d.identity()
        orders = me.orders
        for order in orders:
            add_discogs_order(order)
        ref = request.referrer
        if ref:
            return redirect(ref)
        else:
            return redirect("/ebaydiscogsmodelview/list/")
