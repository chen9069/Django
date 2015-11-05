from django.conf.urls.defaults import *
from src.views import *

urlpatterns = patterns('',
    (r'^admin/$', admin_page),
    (r'^admin/delete/$', delete_page),
    (r'^$', main_page),
    (r'^tagged/(?P<tag>.+)$', main_page),
    (r'^search/$', main_page),
    (r'^ask/$', ask_page),
    (r'^question/(?P<id>\d+)$', question_page),
    (r'^ask/submit/$', question_post),
    (r'^ans/submit/$', answer_post),
    (r'^vote/$', vote_post),
    (r'^edit/$', edit_page),
    (r'^edit/submit/$', edit_submit),
    (r'^rss/(?P<id>\d+)$', index),
)
