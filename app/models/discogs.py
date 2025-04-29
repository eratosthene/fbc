import logging
import re

from flask import Markup, url_for
from mongoengine import (
    DictField,
    Document,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)

logger = logging.getLogger()


class DiscogsRelease(Document):
    release_id = IntField(required=True, unique=True)
    title = StringField(required=True)
    artists = ListField(ReferenceField("Artist"), required=True)
    year = IntField()
    genres = ListField(ReferenceField("Genre"))
    styles = ListField(ReferenceField("Style"))
    master_id = IntField()
    master_year = IntField()
    formats = ListField(DictField())
    released = StringField()
    instance_id = IntField()
    notes = ListField(DictField())
    folder = ReferenceField("Folder")

    meta = {
        "auto_create_index": False,
        "index_background": True,
        "indexes": [
            "title",
            "artists",
            "genres",
            "styles",
            "folder",
        ],
    }

    def artist_rep(self):
        num = 0
        ret = ""
        for artist in self.artists:
            if num:
                ret = ret + " / "
            ret = ret + str(artist)
            num = num + 1
        return ret

    def __unicode__(self):
        return self.artist_rep() + " - " + self.title + " (" + str(self.year) + ")"

    def __repr__(self):
        return self.artist_rep() + " - " + self.title + " (" + str(self.year) + ")"

    def release_show(self, markup=True):
        s = (
            '<a href="https://www.discogs.com/release/'
            + str(self.release_id)
            + '">D:Release</a>'
        )
        if markup:
            return Markup(s)
        else:
            return s

    def master_show(self, markup=True):
        s = (
            '<a href="https://www.discogs.com/master/'
            + str(self.master_id)
            + '">D:Master</a>'
        )
        if markup:
            return Markup(s)
        else:
            return s

    def unit_list(self, markup=True):
        s = (
            '<a href="'
            + url_for("UnitModelView.list", _flt_0_discogs_release=str(self.id))
            + '">ListUnits</a>'
        )
        if markup:
            return Markup(s)
        else:
            return s

    def unit_add(self, markup=True):
        grading = ""
        for d in self.notes:
            if d["field_id"] == 1:
                m = re.search(".*\((.*)\)", d["value"])
                if m:
                    grading = grading + m.group(1)
            elif d["field_id"] == 2:
                m = re.search(".*\((.*)\)", d["value"])
                if m:
                    grading = grading + "/" + m.group(1)
        s = (
            '<a href="'
            + url_for(
                "UnitModelView.add",
                name=str(self),
                unit_type='12" LP"',
                grading=grading,
                discogs_release=self.pk,
            )
            + '">AddUnit</a>'
        )
        if markup:
            return Markup(s)
        else:
            return s

    def link_column(self):
        return Markup(
            self.release_show(False)
            + "<br>"
            + self.master_show(False)
            + "<br>"
            + self.unit_list(False)
            + "<br>"
            + self.unit_add(False)
            + "<br>"
        )

    def purchase_lot(self):
        from app.models.inventory import Unit

        ret = ""
        try:
            unit = Unit.objects().get(discogs_release=self)
            if unit:
                ret = unit.purchase_lot.name
        except Exception as e:
            logger.error(self.title)
            logger.error(e)
        return Markup(ret)


class Artist(Document):
    artist_id = IntField(required=True, unique=True)
    name = StringField(required=True)
    sort_name = StringField()

    def __unicode__(self):
        if self.sort_name:
            return self.sort_name
        else:
            return self.name

    def __repr__(self):
        if self.sort_name:
            return self.sort_name
        else:
            return self.name


class Genre(Document):
    name = StringField(required=True, unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name


class Style(Document):
    name = StringField(required=True, unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name


class Folder(Document):
    folder_id = IntField(required=True, unique=True)
    name = StringField(required=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name


class DiscogsListing(Document):
    item_id = StringField(required=True, primary_key=True)
    title = StringField()
    price = FloatField()
    url = StringField()

    def __unicode__(self):
        return self.item_id + ": " + self.title + " $" + f"{self.price:.2f}"

    def __repr__(self):
        return self.item_id + ": " + self.title + " $" + f"{self.price:.2f}"

    def fmt_price(self):
        return "$" + f"{self.price:.2f}"

    def fmt_url(self):
        return Markup('<a href="' + self.url + '">' + self.url + "</a>")


class DiscogsOrder(Document):
    order_id = StringField(required=True, primary_key=True)
    date = StringField()
    buyer = StringField()
    price = FloatField()
    title = StringField()

    def __unicode__(self):
        if self.title:
            return (
                self.date
                + " "
                + self.order_id
                + " ["
                + self.title[:45]
                + "]: "
                + self.buyer
                + " $"
                + f"{self.price:.2f}"
            )
        else:
            return (
                self.date
                + " "
                + self.order_id
                + ": "
                + self.buyer
                + " $"
                + f"{self.price:.2f}"
            )

    def __repr__(self):
        if self.title:
            return (
                self.date
                + " "
                + self.order_id
                + " ["
                + self.title[:45]
                + "]: "
                + self.buyer
                + " $"
                + f"{self.price:.2f}"
            )
        else:
            return (
                self.date
                + " "
                + self.order_id
                + ": "
                + self.buyer
                + " $"
                + f"{self.price:.2f}"
            )

    def fmt_price(self):
        return "$" + f"{self.price:.2f}"

    def fmt_url(self):
        return Markup(
            '<a href="https://www.ebay.com/mesh/ord/details?orderid='
            + self.order_id
            + '">'
            + self.order_id
            + "</a>"
        )

    def add_sr(self):
        return Markup(
            '<a href="'
            + url_for(
                "SalesReceiptModelView.add",
                sold_price=self.price,
                discogs_order=self.order_id,
                date=self.date,
            )
            + '">Add SR</a>'
        )
