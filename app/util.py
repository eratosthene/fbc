from app.models.discogs import Artist, Folder, Genre, Style, DiscogsRelease
from app.models.ebay import eBayListing, eBayOrder
from mongoengine import DoesNotExist
import logging
from flask import current_app
import ebaysdk
from ebaysdk.exception import ConnectionError
from ebaysdk.trading import Connection as Trading

logger = logging.getLogger()

def add_ebay_listing(item):
    item_id = item['ItemID']
    title = item['Title']
    price = float(item['BuyItNowPrice']['value'])
    url = item['ListingDetails']['ViewItemURL']
    
    ebay_listing = eBayListing.objects(item_id=item_id).modify(
            upsert = True,
            new = True,
            set__item_id = item_id,
            set__price = price,
            set__title = title,
            set__url = url,
            )
    ebay_listing.save()
    logger.debug(ebay_listing)
    
def add_ebay_order(item):
    order_id = item['OrderID']
    price = float(item['Subtotal']['value'])
    buyer = item['BuyerUserID']
    date = item['CreatedTime'][:10]
    title = item['TransactionArray']['Transaction'][0]['Item']['Title']
    
    ebay_order = eBayOrder.objects(order_id=order_id).modify(
            upsert = True,
            new = True,
            set__order_id = order_id,
            set__price = price,
            set__buyer = buyer,
            set__date = date,
            set__title = title
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
            n=artist.name
            if n.startswith("The "):
                sn = n.removeprefix("The ") + ", The"
                logger.debug("Replacing /"+n+"/ with /"+sn+"/")
            adoc = Artist(
                    artist_id = artist.id,
                    name = artist.name,
                    sort_name = sn
                    )
            adoc.save()
            logger.info('Adding artist ' + str(adoc))
        artists.append(adoc)
    for genre in item.release.genres:
        try:
            gdoc = Genre.objects().get(name=genre)
        except DoesNotExist:
            gdoc = Genre(name = genre)
            gdoc.save()
            logger.info('Adding genre ' + str(gdoc))
        genres.append(gdoc)
    for style in item.release.styles:
        try:
            sdoc = Style.objects().get(name=style)
        except DoesNotExist:
            sdoc = Style(name = style)
            sdoc.save()
            logger.info('Adding style ' + str(sdoc))
        styles.append(sdoc)
    master_id = 0
    master_year = item.release.year
    if item.release.master:
        master_id = item.release.master.id
        master_year = item.release.master.year
    discogs_release = DiscogsRelease.objects(release_id=item.release.id).modify(
            upsert = True,
            new = True,
            set__release_id = item.release.id,
            set__instance_id = item.instance_id,
            set__title = item.release.title,
            set__year = item.release.year,
            set__artists = artists,
            set__genres = genres,
            set__styles = styles,
            set__master_id = master_id,
            set__master_year = master_year,
            set__formats = item.release.formats,
            set__released = item.release.fetch('released'),
            set__folder = folder,
            set__notes = item.notes
            )
    discogs_release.save()
    logger.debug(discogs_release)