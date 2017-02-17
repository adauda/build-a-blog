#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import cgi

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def render_front(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC ")
        self.render("front.html", title=title, art=art, error=error, arts = arts)

    def get(self):
        #self.write("asciichan!")
        #self.render("front.html")
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art)
            a.put()
            #self.redirect("/")
            self.redirect("/blogs")
        else:
            error = "we need both subject and post!"
            self.render_front(title, art, error)

class BlogsHandler(Handler):
    def render_blogs(self, title="", art=""):
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC LIMIT 5 ")
        self.render("blogs.html", title=title, art=art, arts = arts)

    def get(self):
        #self.write("asciichan!")
        #self.render("front.html")
        self.render_blogs()

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Art.get_by_id(int(id))

        if post:
            self.response.write("<center> <strong> <br><br><a href='/'>New Post</a>&nbsp;&nbsp;&nbsp;<a href='/blogs'>Main Page</a><br><br> </strong> </center>")
            self.response.write("<br><p style='font-size:30px'><strong>" + cgi.escape(post.title)+ "</strong></p><br><br>" +cgi.escape(post.art)+ "<br><br>")
        else:
            self.response.write("Not a valid blog id")

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/blogs', BlogsHandler),
                               webapp2.Route('/blog/<id:\d+>', ViewPostHandler)], debug=True)
