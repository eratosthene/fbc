from flask import Markup, url_for
from flask_appbuilder.models.decorators import renders
from mongoengine import (
    BooleanField,
    Document,
    FloatField,
    ReferenceField,
    StringField,
)

from app.util import fpercent, fprice


class Unit(Document):
    name = StringField(required=True)
    unit_type = StringField()
    description = StringField()
    discogs_release = ReferenceField("DiscogsRelease")
    discogs_listing = ReferenceField("DiscogsListing")
    ebay_listing = ReferenceField("eBayListing")
    ebay_draft_url = StringField()
    purchase_lot = ReferenceField("PurchaseLot")
    storage_box = ReferenceField("StorageBox")
    grading = StringField()
    pressing = StringField()
    matrix = StringField()
    notes = StringField()
    retail_price = FloatField()
    sold = BooleanField()
    sales_receipt = ReferenceField("SalesReceipt")

    def __unicode__(self):
        return (
            self.name + " " + self.unit_type + " " + self.pressing + " " + self.grading
        )

    def __repr__(self):
        return (
            self.name + " " + self.unit_type + " " + self.pressing + " " + self.grading
        )

    def fmt_retail_price(self):
        if self.retail_price:
            return "$" + f"{self.retail_price:.2f}"
        else:
            return None

    def link_column(self):
        ret = ""
        if self.discogs_release:
            ret = (
                ret
                + self.discogs_release.release_show(False)
                + "<br/>"
                + self.discogs_release.master_show(False)
                + "<br/>"
            )
        if self.ebay_listing:
            ret = (
                ret
                + '<a href="'
                + self.ebay_listing.url
                + '">eBay:Listing&nbsp;$'
                + f"{self.ebay_listing.price:.2f}"
                "</a><br/>"
            )
        if self.ebay_draft_url:
            ret = ret + '<a href="' + self.ebay_draft_url + '">eBay:Draft</a><br/>'
        if self.discogs_listing:
            ret = (
                ret
                + '<a href="'
                + self.discogs_listing.url
                + '">D:Listing&nbsp;$'
                + f"{self.discogs_listing.price:.2f}"
                "</a><br/>"
            )
        if self.sales_receipt:
            ret = (
                ret
                + '<a href="'
                + url_for("SalesReceiptModelView.show", pk=str(self.sales_receipt.id))
                + '">SalesReceipt&nbsp$'
                + f"{self.sales_receipt.net_sold:.2f}"
                + "</a><br/>"
            )
            if self.sales_receipt.ebay_order:
                ret = ret + self.sales_receipt.fmt_ebay_order(False)
        return Markup(ret)


class PurchaseLot(Document):
    name = StringField(required=True)
    date = StringField(required=True)
    price = FloatField(required=True)
    notes = StringField()

    @renders("price")
    def purchase_price(self):
        return fprice(self.price)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

    def compute_profit(self):
        ret = {}
        ret["gross"] = 0.0
        ret["net"] = 0.0
        for unit in Unit.objects(purchase_lot=self):
            if unit.sales_receipt:
                ret["gross"] += unit.sales_receipt.sold_price
                ret["net"] += unit.sales_receipt.net_sold
        ret["fees"] = round(ret["gross"] - ret["net"], 2)
        if ret["gross"] > 0:
            ret["feepc"] = round(ret["fees"] / ret["gross"], 2)
        else:
            ret["feepc"] = 0.0
        ret["profit"] = round(ret["net"] - self.price, 2)
        ret["roi"] = round(ret["profit"] / self.price, 2)
        return ret

    def compute_units(self):
        ret = {}
        ret["total"] = Unit.objects(purchase_lot=self).count()
        ret["sold"] = Unit.objects(purchase_lot=self, sold=True).count()
        ret["left"] = ret["total"] - ret["sold"]
        return ret

    def compute_forecast(self, t, u):
        ret = {}
        if u["total"] > 0:
            ret["breakeven"] = self.price / u["total"] / (1 - t["feepc"])
        else:
            ret["breakeven"] = 0
        total_price = 0.0
        total_sold_price = 0.0
        total_num_sold = 0
        for unit in Unit.objects(purchase_lot=self):
            if unit.retail_price:
                total_price += unit.retail_price
            if unit.sold and unit.sales_receipt:
                total_num_sold += 1
                total_sold_price += unit.sales_receipt.sold_price
        ret["pprofit"] = total_price - (total_price * t["feepc"]) - self.price
        if total_num_sold > 0:
            ret["avgsoldprice"] = total_sold_price / total_num_sold
        else:
            ret["avgsoldprice"] = 0
        ret["avgppu"] = ret["avgsoldprice"] - ret["breakeven"]
        ret["lprofit"] = u["total"] * ret["avgppu"]
        return ret

    def breakdown(self):
        t = self.compute_profit()
        u = self.compute_units()
        c = self.compute_forecast(t, u)
        ret = '<table class="table table-bordered table-condensed table-hover" style="width: auto">'
        ret = (
            ret
            + "<tr><th>Capital</th><th>Sold For</th><th>Fees</th><th>Fee %</th><th>Net Sold</th><th>Profit</th><th>ROI</th></tr>"
        )
        ret = ret + "<tr>"
        ret = ret + "<td>" + fprice(self.price) + "</td>"
        ret = ret + "<td>" + fprice(t["gross"]) + "</td>"
        ret = ret + "<td>" + fprice(t["fees"]) + "</td>"
        ret = ret + "<td>" + fpercent(t["feepc"]) + "</td>"
        ret = ret + "<td>" + fprice(t["net"]) + "</td>"
        ret = ret + "<td>" + fprice(t["profit"]) + "</td>"
        ret = ret + "<td>" + fpercent(t["roi"]) + "</td>"
        ret = ret + "</tr></table>"
        ret = (
            ret
            + '<table class="table table-bordered table-condensed table-hover" style="width: auto">'
        )
        ret = (
            ret + "<tr><th>Total Units</th><th>Sold Units</th><th>Units Left</th></tr>"
        )
        ret = ret + "<tr>"
        ret = ret + "<td>" + str(u["total"]) + "</td>"
        ret = ret + "<td>" + str(u["sold"]) + "</td>"
        ret = ret + "<td>" + str(u["left"]) + "</td>"
        ret = ret + "</tr></table>"
        ret = (
            ret
            + '<table class="table table-bordered table-condensed table-hover" style="width: auto">'
        )
        ret = (
            ret
            + "<tr><th>Breakeven Price</th><th>Potential Profit</th><th>Avg. Sold Price</th><th>Avg. Profit/Unit</th><th>Likely Profit</th></tr>"
        )
        ret = ret + "<tr>"
        ret = ret + "<td>" + fprice(c["breakeven"]) + "</td>"
        ret = ret + "<td>" + fprice(c["pprofit"]) + "</td>"
        ret = ret + "<td>" + fprice(c["avgsoldprice"]) + "</td>"
        ret = ret + "<td>" + fprice(c["avgppu"]) + "</td>"
        ret = ret + "<td>" + fprice(c["lprofit"]) + "</td>"
        ret = ret + "</tr></table>"
        return Markup(ret)

    def list_sold(self):
        u = self.compute_units()
        return u["sold"]

    def list_total(self):
        u = self.compute_units()
        return u["total"]

    def list_profit(self):
        t = self.compute_profit()
        return fprice(t["profit"])

    def list_breakeven(self):
        t = self.compute_profit()
        u = self.compute_units()
        c = self.compute_forecast(t, u)
        return fprice(c["breakeven"])


class StorageBox(Document):
    name = StringField(required=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name
