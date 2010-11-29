#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

class ZugangEntfernen(webapp.RequestHandler):
    def get(self):
        mobile = self.request.get('mobile')
        if mobile != "true":
            mobile = "false"
        region = self.request.get('region')
        endpointurl = self.request.get('endpointurl')
        accesskey = self.request.get('accesskey')
        # Den Usernamen erfahren
        username = users.get_current_user()

        #anfrage = db.GqlQuery("SELECT * FROM KoalaCloudDatenbank WHERE user = :username_db AND regionname = :regionname_db AND endpointurl = :endpointurl_db AND accesskey = accesskey_db", username_db=username, regionname_db=region, endpointurl_db=endpointurl, accesskey_db=accesskey)
        testen = db.GqlQuery("SELECT * FROM KoalaCloudDatenbank WHERE user = :username_db AND regionname = :regionname_db AND endpointurl = :endpointurl_db AND accesskey = :accesskey_db", username_db=username, regionname_db=region, endpointurl_db=endpointurl, accesskey_db=accesskey)
        # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt und gel�scht
        results = testen.fetch(100)
        for result in results:
          result.delete()

        testen = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankAktiveZone WHERE user = :username_db", username_db=username)
        # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt und gel�scht
        results = testen.fetch(100)
        for result in results:
          result.delete()

        self.redirect('/regionen?mobile='+str(mobile))
        