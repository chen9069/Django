from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.simple import direct_to_template
from django.utils import feedgenerator
from django.shortcuts import render

from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import users

from src.models import *
from google.appengine.api import mail

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import os
import urllib
import datetime
import re

# generate rss for each question
def index(request, id):
    question = Question.get_by_id(long(id), parent=ndb.Key('User', 'root'))
    answers = Answer.query(ancestor=question.key).order(-Answer.votes, Answer.date_create)
    context = {}
        # create a feed generator having a channel with following title, link and description
    feed = feedgenerator.Rss201rev2Feed(
                                        title=u"OpenSource",
                                        link=u"http://chenji-opensource.appspot.com",
                                        description=u"Final Project",
                                        language=u"en",
            )
    feed.add_item(title=question.title,
                  link='http://chenji-opensource.appspot.com/question/' + id,
                  description=question.content,
                  )
    for answer in answers:
        feed.add_item(title="Answer of " + question.title,
                  link='http://chenji-opensource.appspot.com/question/' + id,
                  description=answer.content,)

    return HttpResponse(feed.writeString('UTF-8'), mimetype='application/rss+xml')


def admin_page(request):
    questions = Question.query(ancestor=ndb.Key('User', 'root'))
    return direct_to_template(request, 'opensource/admin_page.html', {'usr': users.get_current_user().email(), 'questions': questions})

def delete_page(request):
    if request.method == 'POST':
        list=request.POST.getlist('key')
        for key in list:
            ndb.delete_multi(
                             Answer.query(ancestor=ndb.Key(urlsafe=key)).fetch(keys_only=True)
                             )
            ndb.delete_multi(
                            Question.query(ancestor=ndb.Key(urlsafe=key)).fetch(keys_only=True)
                           )
        return HttpResponseRedirect('/admin/')
    return HttpResponseRedirect('/')


# display and sort all questions
def main_page(request, tag=''):
    
    #ndb.delete_multi( Question.query().fetch(keys_only=True) )
    
    _order = request.GET.get('sort', DEFAULT_ORDER)
    _search = request.GET.get('q', '')
    _page = request.GET.get('page', DEFAULT_PAGE)
    _curs = Cursor(urlsafe=request.GET.get('cursor'))

    if (tag == '' and _search == ''):
        tagged_query = Question.query(ancestor=ndb.Key('User', 'root'))
    elif (tag):
        tagged_query = Question.query(Question.tags==tag, ancestor=ndb.Key('User', 'root'))
    elif (_search):
        tagged_query = Question.query(Question.tags.IN([x.strip() for x in re.split(';| ', _search)]), ancestor=ndb.Key('User', 'root'))
    else:
        tagged_query = Question.query(ancestor=ndb.Key('User', 'root'))

    if (_order == 'newest'):
        ordered_query = tagged_query.order(-Question.date_create, Question.key)
    elif (_order == 'votes'):
        ordered_query = tagged_query.order(-Question.votes, Question.key)
    elif (_order == 'answers'):
        ordered_query = tagged_query.order(-Question.answers, Question.key)
    else:
        ordered_query = tagged_query.order(-Question.views, Question.key)

    count = ordered_query.count()
    
    questions, next_curs, more = ordered_query.fetch_page(10, start_cursor=_curs)
#questions, next_curs, more = Question.query(ancestor=ndb.Key('User', 'root', 'Post', 4744598832283648)).fetch_page(10, start_cursor=_curs)

    template_values = {
        'questions': questions,
        'page': _page,
        'pages': ((count-1) if count > 0 else count)/10 + 1,
        'order': _order,
        _order: 'select',
        'search': _search,
    }

    if more and next_curs:
        template_values['next'] = int(_page) + 1
        template_values['cursor'] = next_curs.urlsafe(),

    cur_user = users.get_current_user()
    if cur_user:
        url = users.create_logout_url(request.get_full_path())
        url_linktext = 'Logout'
        if users.is_current_user_admin():
            template_values.update({'admin': '/admin',})
        template_values.update({
            'usr': cur_user.email(),
            'usr_name': cur_user.email().partition('@')[0],
            'usr_id': cur_user.user_id(),
            })
    else:
        url = users.create_login_url(request.get_full_path())
        url_linktext = 'Login'

    template_values.update({
        'url': url,
        'url_linktext': url_linktext,
        })

    return direct_to_template(request, 'opensource/main_page.html', template_values)

# display the ask-questoin page
def ask_page(request):
    template_values = {}
    cur_user = users.get_current_user()
    if cur_user:
        url = users.create_logout_url(request.get_full_path())
        upload_url = blobstore.create_upload_url('/upload')
        template_values.update({
                               'usr': cur_user.email(),
                               'usr_name': cur_user.email().partition('@')[0],
                               'usr_id': cur_user.user_id(),
                               'default_title': "What's your question?",
                               'upload_url': upload_url,
                               'your_upload': request.GET.get('upload_key'),
                               })
        url_linktext = 'Logout'
        template_page = 'opensource/form_page.html'
    else:
        url = users.create_login_url(request.get_full_path())
        url_linktext = 'Login'
        template_values.update({
            'error_msg': "You must be logged in to ask a question"
            })
        template_page = 'opensource/error_page.html'

    template_values.update({
        'url': url,
        'url_linktext': url_linktext,
        })
    return direct_to_template(request, template_page, template_values)

# handle the form post request in ask-question page
def question_post(request):
    if request.method == 'POST':
        _title_post_ = request.POST.get('title')
        _content_post_ = request.POST.get('text')
        _tags_post_ = request.POST.get('tags')
        cur_user = users.get_current_user()
        if cur_user:
            question = Question(parent=ndb.Key('User', 'root'),
                                author=cur_user,
                                content=_content_post_,
                                title=_title_post_,
                                tags=list(set([x.strip() for x in re.split(';| ', _tags_post_) if x.strip()])),
                                )
            question.put()
        else:
            url = users.create_login_url(request.get_full_path())
            url_linktext = 'Login'
            template_values = {
                'url': url,
                'url_linktext': url_linktext,
                'error_msg': "You must be logged in to ask a question",
            }
            return direct_to_template(request, 'opensource/error_page.html', template_values)
    return HttpResponseRedirect('/')


# display the question page, including question content and all its answers, provide a answer question form at bottom
def question_page(request, id):
    question = Question.get_by_id(long(id), parent=ndb.Key('User', 'root'))
    answers = Answer.query(ancestor=question.key).order(-Answer.votes, Answer.date_create)
    votes = Vote_question.query(ancestor=question.key)
    vote_up = votes.filter(Vote_question.up=='+').count()
    vote_down = votes.filter(Vote_question.down=='-').count()
    question.answers = answers.count()
    question.votes = vote_up - vote_down
    question.views = question.views + 1
    question.put()

    for answer in answers:
        votes = Vote_answer.query(ancestor=answer.key)
        vote_up = votes.filter(Vote_answer.up=='+').count()
        vote_down = votes.filter(Vote_answer.down=='-').count()
        answer.votes = vote_up - vote_down
        answer.put()
    
    template_values = {
        'question': question,
        'answers': answers,
        'ans_count': answers.count(),
    }
    cur_user = users.get_current_user()
    if cur_user:
        url = users.create_logout_url(request.get_full_path())
        url_linktext = 'Logout'
        upload_url = blobstore.create_upload_url('/upload')
        template_values.update({
                               'usr': cur_user.email(),
                               'usr_name': cur_user.email().partition('@')[0],
                               'usr_id': cur_user.user_id(),
                               'upload_url': upload_url,
                               'your_upload': request.GET.get('upload_key'),
                               })

    else:
        url = users.create_login_url(request.get_full_path())
        url_linktext = 'Login'
    template_values.update({
                           'url': url,
                           'url_linktext': url_linktext,
                           })

    return direct_to_template(request, 'opensource/question_page.html', template_values)

# display the edit-quesiont and edit-answer page, forms are pre-filled
def edit_page(request):
    _qkey_ = request.GET.get('qkey')
    _akey_ = request.GET.get('akey')
    if _qkey_:
        # edit question
        template_values = {}
        cur_user = users.get_current_user()
        if cur_user:
            url = users.create_logout_url(request.get_full_path())
            upload_url = blobstore.create_upload_url('/upload')
            template_values.update({
                'usr': cur_user.email(),
                'usr_name': cur_user.email().partition('@')[0],
                'usr_id': cur_user.user_id(),
                'upload_url': upload_url,
                'your_upload': request.GET.get('upload_key'),
                })
            url_linktext = 'Logout'
            question = Question.query(ancestor=ndb.Key(urlsafe=_qkey_)).get()
            if cur_user == question.author:
                template_values.update({
                                       'question': question,
                                       })
                template_page = 'opensource/form_page.html'
            else:
                template_values.update({
                                       'error_msg': "Only author can edit questions"
                                       })
                template_page = 'opensource/error_page.html'
        else:
            url = users.create_login_url(request.get_full_path())
            url_linktext = 'Login'
            template_values.update({
                'error_msg': "You must be logged in to edit a question"
                })
            template_page = 'opensource/error_page.html'
        template_values.update({
                       'url': url,
                       'url_linktext': url_linktext,
                       })
        return direct_to_template(request, template_page, template_values)

    elif _akey_:
        # edit answer
        template_values = {}
        cur_user = users.get_current_user()
        if cur_user:
            url = users.create_logout_url(request.get_full_path())
            upload_url = blobstore.create_upload_url('/upload')
            template_values.update({
                                   'usr': cur_user.email(),
                                   'usr_name': cur_user.email().partition('@')[0],
                                   'usr_id': cur_user.user_id(),
                                   'upload_url': upload_url,
                                   'your_upload': request.GET.get('upload_key'),
                                   })
            url_linktext = 'Logout'
            question = Question.query(ancestor=ndb.Key(urlsafe=_akey_).parent()).get()
            answer = Answer.query(ancestor=ndb.Key(urlsafe=_akey_)).get()
            if cur_user == answer.author:
                template_values.update({
                        'question': question,
                        'answer': answer,
                        })
                template_page = 'opensource/edit_answer.html'
            else:
                template_values.update({
                                       'error_msg': "Only author can edit answers"
                                       })
                template_page = 'opensource/error_page.html'
        else:
            url = users.create_login_url(request.get_full_path())
            url_linktext = 'Login'
            template_values.update({
                       'error_msg': "You must be logged in to edit an answer"
                       })
            template_page = 'opensource/error_page.html'
        template_values.update({
                               'url': url,
                               'url_linktext': url_linktext,
                               })
        return direct_to_template(request, template_page, template_values)
    else:
        return HttpResponseRedirect('/')

# submit the form of editting quesiont & answer
def edit_submit(request):
    if request.method == 'POST':
        if request.POST.get('title'):
            # edit question
            _id_ = request.POST.get('id')
            template_values = {}
            cur_user = users.get_current_user()
            if cur_user:
                url = users.create_logout_url(request.get_full_path())
                template_values.update({
                    'usr': cur_user.email(),
                    'usr_name': cur_user.email().partition('@')[0],
                    'usr_id': cur_user.user_id(),
                    })
                url_linktext = 'Logout'
                question = Question.get_by_id(long(_id_), parent=ndb.Key('User', 'root'))
                if cur_user == question.author:
                    question.title = request.POST.get('title')
                    question.content = request.POST.get('text')
                    question.tags = [x.strip() for x in re.split(';| ', request.POST.get('tags')) if x.strip()]
                    question.date_modify = datetime.datetime.now()
                    question.put()
                    return HttpResponseRedirect('/question/' + str(question.key.id()))
                else:
                    template_values.update({
                                           'error_msg': "Only author can edit questions"
                                            })
            else:
                url = users.create_login_url(request.get_full_path())
                url_linktext = 'Login'
                template_values.update({
                       'error_msg': "You must be logged in to edit a question"
                        })
            template_values.update({
                                   'url': url,
                                   'url_linktext': url_linktext,
                                   })
            return direct_to_template(request, 'opensource/error_page.html', template_values)
        else:
            # edit answer
            template_values = {}
            cur_user = users.get_current_user()
            if cur_user:
                url = users.create_logout_url(request.get_full_path())
                template_values.update({
                                       'usr': cur_user.email(),
                                       'usr_name': cur_user.email().partition('@')[0],
                                       'usr_id': cur_user.user_id(),
                                       })
                url_linktext = 'Logout'
                answer = Answer.query(ancestor=ndb.Key(urlsafe=request.POST.get('key'))).get()
                if cur_user == answer.author:
                    answer.content = request.POST.get('text')
                    answer.date_modify = datetime.datetime.now()
                    answer.put()
                    return HttpResponseRedirect('/question/' + request.POST.get('qid'))
                else:
                    template_values.update({
                        'error_msg': "Only author can edit answers"
                    })
            else:
                url = users.create_login_url(request.get_full_path())
                url_linktext = 'Login'
                template_values.update({
                    'error_msg': "You must be logged in to edit an answer"
                     })
                template_values.update({
                    'url': url,
                    'url_linktext': url_linktext,
                    })
            return direct_to_template(request, 'opensource/error_page.html', template_values)
    return HttpResponseRedirect('/')

# handle the request of post answer form
def answer_post(request):
    if request.method == 'POST':
        _qid_ = request.POST.get('qid')
        _content_post_ = request.POST.get('text')
        cur_user = users.get_current_user()
        if cur_user:
            answer = Answer(parent=ndb.Key('User', 'root', 'Post', long(_qid_)),
                            author=cur_user,
                            content=_content_post_,
                            )
            answer.put()
            return HttpResponseRedirect('/question/' + _qid_)
        else:
            url = users.create_login_url(request.get_full_path())
            url_linktext = 'Login'
            template_values = {
                'url': url,
                'url_linktext': url_linktext,
                'error_msg': "You must be logged in to answer a question",
            }
            return direct_to_template(request, 'opensource/error_page.html', template_values)
    return HttpResponseRedirect('/')

# handle the request of vote
def vote_post(request):
    if request.method == 'POST':
        _qid_ = request.POST.get('qid')
        _key_ = request.POST.get('key')
        _vote_ = request.POST.get('vote')
        cur_user = users.get_current_user()
        parent_key = ndb.Key(urlsafe=_key_)
        if cur_user:
            if request.POST.get('aid'):
                # vote answer
                vote = Vote_answer.query(Vote_answer.author==cur_user, ancestor=parent_key).get()
                if not vote:
                    vote = Vote_answer(parent=parent_key,
                                author=cur_user,
                                )
            else:
                # vote question
                vote = Vote_question.query(Vote_question.author==cur_user, ancestor=parent_key).get()
                if not vote:
                    vote = Vote_question(parent=parent_key,
                                author=cur_user,
                                )
            if _vote_ == '+':
                vote.up = '+'
                vote.down = ''
            else:
                vote.up = ''
                vote.down = '-'
            vote.put()
            return HttpResponseRedirect('/question/' + _qid_)
        else:
            url = users.create_login_url(request.get_full_path())
            url_linktext = 'Login'
            template_values = {
                'url': url,
                'url_linktext': url_linktext,
                'error_msg': "You must be logged in to answer a question",
            }
            return direct_to_template(request, 'opensource/error_page.html', template_values)
#
#        template_values = {
#            'url': '',
#            'url_linktext': '',
#            'error_msg': _key_ + ":" + str(ndb.Key(urlsafe=_key_)),
#            }
#        return direct_to_template(request, 'opensource/error_page.html', template_values)
#
    return HttpResponseRedirect('/')
