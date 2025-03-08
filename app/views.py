from app import appbuilder
from app.view.inventory import UnitModelView
from app.view.inventory import PurchaseLotModelView
from app.view.inventory import StorageBoxModelView
from app.view.discogs import DiscogsReleaseModelView
from app.view.discogs import ArtistModelView
from app.view.discogs import GenreModelView
from app.view.discogs import StyleModelView
from app.view.discogs import FolderModelView
from app.view.sales import SalesReceiptModelView
from app.view.sales import eBayListingModelView
from app.view.sales import eBayOrderModelView
from app.view.sales import DiscogsListingModelView
from app.view.sales import DiscogsOrderModelView
from app.view.supplies import SupplyModelView
from app.view.supplies import PurchaseOrderModelView


appbuilder.add_view(UnitModelView, "Units", category="Inventory")
appbuilder.add_view(PurchaseLotModelView, "Purchase Lots", category="Inventory")
appbuilder.add_view(StorageBoxModelView, "Storage Boxes", category="Inventory")
appbuilder.add_view(DiscogsReleaseModelView, "Releases", category="Discogs")
appbuilder.add_view(ArtistModelView, "Artists", category="Discogs")
appbuilder.add_view(GenreModelView, "Genres", category="Discogs")
appbuilder.add_view(StyleModelView, "Styles", category="Discogs")
appbuilder.add_view(FolderModelView, "Folders", category="Discogs")
appbuilder.add_view(SalesReceiptModelView, "Sales Receipts", category="Sales")
appbuilder.add_view(eBayListingModelView, "eBay Listings", category="Sales")
appbuilder.add_view(eBayOrderModelView, "eBay Orders", category="Sales")
appbuilder.add_view(DiscogsListingModelView, "Discogs Listings", category="Sales")
appbuilder.add_view(DiscogsOrderModelView, "Discogs Orders", category="Sales")
appbuilder.add_view(SupplyModelView, "Supply List", category="Supplies")
appbuilder.add_view(PurchaseOrderModelView, "Purchase Orders", category="Supplies")
