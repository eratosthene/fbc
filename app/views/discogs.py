from flask_appbuilder import ModelView
from flask_appbuilder.models.mongoengine.interface import MongoEngineInterface

from app.models.discogs import (
    Artist,
    DiscogsRelease,
    Folder,
    Genre,
    Style,
)
from app.widgets import (
    DiscogsReleaseListWidget,
)
from app.views.inventory import UnitModelView


class DiscogsReleaseModelView(ModelView):
    datamodel = MongoEngineInterface(DiscogsRelease)
    list_widget = DiscogsReleaseListWidget
    related_views = [UnitModelView]
    list_columns = [
        "title",
        "artists",
        "year",
        "master_year",
        "genres",
        "styles",
        "purchase_lot",
        "link_column",
    ]
    label_columns = {"link_column": "Links"}
    edit_columns = [
        "title",
        "artists",
        "year",
        "master_id",
        "master_year",
        "genres",
        "styles",
        "instance_id",
        "released",
        "folder",
    ]


class ArtistModelView(ModelView):
    datamodel = MongoEngineInterface(Artist)
    related_views = [DiscogsReleaseModelView]
    list_columns = [
        "name",
        "sort_name",
        "artist_id",
    ]
    related_views = [DiscogsReleaseModelView]


class GenreModelView(ModelView):
    datamodel = MongoEngineInterface(Genre)
    base_order = ("name", "desc")
    related_views = [DiscogsReleaseModelView]


class StyleModelView(ModelView):
    datamodel = MongoEngineInterface(Style)
    base_order = ("name", "desc")
    related_views = [DiscogsReleaseModelView]


class FolderModelView(ModelView):
    datamodel = MongoEngineInterface(Folder)
    list_columns = ["name", "folder_id"]
    base_order = ("name", "desc")
    related_views = [DiscogsReleaseModelView]
