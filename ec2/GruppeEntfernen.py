#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api.urlfetch import DownloadError

from library import login

from boto.ec2.connection import *

class GruppeEntfernen(webapp.RequestHandler):
    def get(self):
        # Den Namen der zu l�schenden Gruppe holen
        gruppe = self.request.get('gruppe')
        # Den Usernamen erfahren
        username = users.get_current_user()

        conn_region, regionname = login(username)

        try:
            # Security Gruppe l�schen
            conn_region.delete_security_group(gruppe)
        except EC2ResponseError:
            # Wenn es nicht geklappt hat...
            fehlermeldung = "49"
            self.redirect('/securitygroups?message='+fehlermeldung)
        except DownloadError:
            # Diese Exception hilft gegen diese beiden Fehler:
            # DownloadError: ApplicationError: 2 timed out
            # DownloadError: ApplicationError: 5
            fehlermeldung = "8"
            self.redirect('/securitygroups?message='+fehlermeldung)
        else:
            # Wenn es geklappt hat...
            fehlermeldung = "48"
            self.redirect('/securitygroups?message='+fehlermeldung)
            