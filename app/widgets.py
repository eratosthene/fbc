from flask_appbuilder.widgets import ListWidget

class DiscogsReleaseListWidget(ListWidget):
     template = 'widgets/d_r_list.html'

class eBayListingListWidget(ListWidget):
     template = 'widgets/e_l_list.html'

class eBayOrderListWidget(ListWidget):
     template = 'widgets/e_o_list.html'

class DiscogsListingListWidget(ListWidget):
     template = 'widgets/d_l_list.html'

class DiscogsOrderListWidget(ListWidget):
     template = 'widgets/d_o_list.html'
