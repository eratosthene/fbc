from mongoengine import Document
from mongoengine import IntField, StringField, ListField, ReferenceField, BooleanField, DictField, FloatField
from flask import Markup, url_for

class DiscogsRelease(Document):
    release_id = IntField(required=True, unique=True)
    title       = StringField(required=True)
    artists     = ListField(ReferenceField('Artist'), required=True)
    year        = IntField()
    genres      = ListField(ReferenceField('Genre'))
    styles      = ListField(ReferenceField('Style'))
    master_id   = IntField()
    master_year = IntField()
    formats     = ListField(DictField())
    released    = StringField()
    instance_id = IntField()
    notes       = ListField(DictField())
    folder      = ReferenceField('Folder')
    
    def artist_rep(self):
        num = 0
        ret = ''
        for artist in self.artists:
            if num:
                ret = ret + ' / '
            ret = ret + str(artist)
            num = num + 1
        return ret
        
    def __unicode__(self):
        return self.artist_rep() + ' - ' + self.title + ' (' + str(self.year) + ')'

    def __repr__(self):
        return self.artist_rep() + ' - ' + self.title + ' (' + str(self.year) + ')'

    def release_show(self, markup=True):
        s = '<a href="https://www.discogs.com/release/' + str(self.release_id) + '">D:Release</a>'
        if markup:
            return Markup(s)
        else:
            return s
    
    def master_show(self, markup=True):
        s = '<a href="https://www.discogs.com/master/' + str(self.master_id) + '">D:Master</a>'
        if markup:
            return Markup(s)
        else:
            return s
        
    def unit_list(self, markup=True):
        s = '<a href="' + url_for('UnitModelView.list',_flt_0_discogs_release=str(self.id)) + '">ListUnits</a>'
        if markup:
            return Markup(s)
        else:
            return s
        
    def link_column(self):
        return Markup(
            '<ul><li>' + self.release_show(False) + '</li><li>' + self.master_show(False) + '</li><li>' + self.unit_list(False) + '</li></ul>'
        )
        
class Artist(Document):
    artist_id   = IntField(required=True, unique=True)
    name        = StringField(required=True)
    sort_name   = StringField()

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
    name        = StringField(required=True, unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

class Style(Document):
    name        = StringField(required=True, unique=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

class Folder(Document):
    folder_id   = IntField(required=True, unique=True)
    name        = StringField(required=True)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name

