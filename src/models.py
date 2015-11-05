from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

import re

DEFAULT_ORDER = 'newest'
DEFAULT_PAGE = '1'

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

class Post(polymodel.PolyModel):
    '''Models an individual Post entry.'''
    author = ndb.UserProperty()
    date_create = ndb.DateTimeProperty(auto_now_add=True)
    date_modify = ndb.DateTimeProperty()
    content = ndb.TextProperty()
    views = ndb.IntegerProperty(default=0)
    votes = ndb.IntegerProperty(default=0)

class Question(Post):
    '''Models an individual Question entry.'''
    title = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    def tags_to_string(self):
        return "; ".join(self.tags)
    answers = ndb.IntegerProperty(default=0)

class Answer(Post):
    '''Models an individual Answer entry.'''

class Vote_question(ndb.Model):
    '''Models an individual Vote entry.'''
    author = ndb.UserProperty()
    up = ndb.StringProperty()
    down = ndb.StringProperty()

class Vote_answer(ndb.Model):
    '''Models an individual Vote entry.'''
    author = ndb.UserProperty()
    up = ndb.StringProperty()
    down = ndb.StringProperty()
