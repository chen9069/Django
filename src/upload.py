import os
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class MainHandler(webapp.RequestHandler):
    def get(self):
        for b in blobstore.BlobInfo.all():
            self.response.out.write('<li><img src="/serve/%s' % str(b.key()) + '">' + "/serve/" + str(b.filename) + '.psg</img></li>')

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.response.out.write('<img src="/serve/%s' % str(blob_info.key()) + '">' + "/serve/" + str(blob_info.key()) + '.psg</img>')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key = str(urllib.unquote(blob_key))
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blobstore.BlobInfo.get(blob_key), save_as=True)

application = webapp.WSGIApplication(
                                     [
                                      ('/upload', UploadHandler),
                                      ('/upload/imgs', MainHandler),
                                      ('/serve/([^/]+)?', ServeHandler),
                                      ], debug=True)
