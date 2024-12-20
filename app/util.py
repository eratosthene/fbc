from app.models import *
from mongoengine import DoesNotExist
import logging

def add_discogs_release(item):
    logger = logging.getLogger()
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
    print(discogs_release)