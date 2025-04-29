import logging

from mongoengine import DoesNotExist

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
from flask import request
from flask_wtf import FlaskForm

logger = logging.getLogger()


def fprice(num):
    return "$" + f"{num:.2f}"


def fpercent(num):
    np = num * 100.0
    return f"{np:.2f}" + "%"


def add_ebay_listing(item):
    item_id = item["ItemID"]
    title = item["Title"]
    price = float(item["BuyItNowPrice"]["value"])
    url = item["ListingDetails"]["ViewItemURL"]

    ebay_listing = eBayListing.objects(item_id=item_id).modify(
        upsert=True,
        new=True,
        set__item_id=item_id,
        set__price=price,
        set__title=title,
        set__url=url,
    )
    ebay_listing.save()
    logger.debug(ebay_listing)


def add_ebay_order(item):
    order_id = item["OrderID"]
    price = float(item["Subtotal"]["value"])
    buyer = item["BuyerUserID"]
    date = item["CreatedTime"][:10]
    title = item["TransactionArray"]["Transaction"][0]["Item"]["Title"]
    ebay_listing_id = item["TransactionArray"]["Transaction"][0]["Item"]["ItemID"]
    from app.models.ebay import eBayListing as ebl

    obj = ebl.objects(item_id=ebay_listing_id)
    if obj.count() == 0:
        logger.warn("No eBay listing in DB for " + str(ebay_listing_id))
        ebay_order = eBayOrder.objects(order_id=order_id).modify(
            upsert=True,
            new=True,
            set__order_id=order_id,
            set__price=price,
            set__buyer=buyer,
            set__date=date,
            set__title=title,
        )
    for ebay_listing in obj:
        logger.info("Found eBay listing " + str(ebay_listing))
        ebay_order = eBayOrder.objects(order_id=order_id).modify(
            upsert=True,
            new=True,
            set__order_id=order_id,
            set__price=price,
            set__buyer=buyer,
            set__date=date,
            set__title=title,
            set__ebay_listing=ebay_listing,
        )
    ebay_order.save()
    logger.debug(ebay_order)


def add_discogs_release(item):
    folder = Folder.objects().get(folder_id=item.folder_id)
    artists = []
    genres = []
    styles = []
    for artist in item.release.artists:
        try:
            adoc = Artist.objects().get(artist_id=artist.id)
        except DoesNotExist:
            sn = ""
            n = artist.name
            if n.startswith("The "):
                sn = n.removeprefix("The ") + ", The"
                logger.debug("Replacing /" + n + "/ with /" + sn + "/")
            adoc = Artist(artist_id=artist.id, name=artist.name, sort_name=sn)
            adoc.save()
            logger.info("Adding artist " + str(adoc))
        artists.append(adoc)
    for genre in item.release.genres:
        try:
            gdoc = Genre.objects().get(name=genre)
        except DoesNotExist:
            gdoc = Genre(name=genre)
            gdoc.save()
            logger.info("Adding genre " + str(gdoc))
        genres.append(gdoc)
    for style in item.release.styles:
        try:
            sdoc = Style.objects().get(name=style)
        except DoesNotExist:
            sdoc = Style(name=style)
            sdoc.save()
            logger.info("Adding style " + str(sdoc))
        styles.append(sdoc)
    master_id = 0
    master_year = item.release.year
    if item.release.master:
        master_id = item.release.master.id
        master_year = item.release.master.year
    discogs_release = DiscogsRelease.objects(release_id=item.release.id).modify(
        upsert=True,
        new=True,
        set__release_id=item.release.id,
        set__instance_id=item.instance_id,
        set__title=item.release.title,
        set__year=item.release.year,
        set__artists=artists,
        set__genres=genres,
        set__styles=styles,
        set__master_id=master_id,
        set__master_year=master_year,
        set__formats=item.release.formats,
        set__released=item.release.fetch("released"),
        set__folder=folder,
        set__notes=item.notes,
    )
    discogs_release.save()
    logger.debug(discogs_release)


def add_discogs_listing(item):
    item_id = str(item.id)
    price = float(item.price.value)
    url = item.url
    a = []
    for artist in item.release.artists:
        a.append(artist.name)
    d = []
    for f in item.release.formats:
        d.append(", ".join(f["descriptions"]))
    lbl = []
    for label in item.release.labels:
        lbl.append(label.name)
    title = (
        " / ".join(a)
        + " - "
        + str(item.release.title)
        + " ("
        + ", ".join(d)
        + ") ("
        + ", ".join(lbl)
        + ")"
    )

    discogs_listing = DiscogsListing.objects(item_id=item_id).modify(
        upsert=True,
        new=True,
        set__item_id=item_id,
        set__price=price,
        set__title=title,
        set__url=url,
    )
    discogs_listing.save()
    logger.info("Adding " + title)
    logger.debug(discogs_listing)


def add_discogs_order(order):
    order_id = str(order.id)
    price = float(order.data["total"]["value"])
    buyer = order.buyer.username
    date = str(order.created)[:10]
    a = []
    for artist in order.items[0].release.artists:
        a.append(artist.name)
    d = []
    for f in order.items[0].release.formats:
        d.append(", ".join(f["descriptions"]))
    lbl = []
    for label in order.items[0].release.labels:
        lbl.append(label.name)
    title = (
        " / ".join(a)
        + " - "
        + str(order.items[0].release.title)
        + " ("
        + ", ".join(d)
        + ") ("
        + ", ".join(lbl)
        + ")"
    )

    discogs_order = DiscogsOrder.objects(order_id=order_id).modify(
        upsert=True,
        new=True,
        set__order_id=order_id,
        set__price=price,
        set__buyer=buyer,
        set__date=date,
        set__title=title,
    )
    discogs_order.save()
    logger.info("Adding " + title)
    logger.debug(discogs_order)


class CustomForm(FlaskForm):
    """
    A custom FlaskForm which reads data from request params
    """

    @classmethod
    def refresh(cls, obj=None):
        kw = dict(obj=obj)
        if request.method == "GET":
            kw["formdata"] = request.args
            logger.info(request.args)
        form = cls(**kw)
        return form
