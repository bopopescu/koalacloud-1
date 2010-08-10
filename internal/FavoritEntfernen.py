#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

class FavoritEntfernen(webapp.RequestHandler):
    def get(self):
        # AMI des zu l�schenden Favoriten holen
        ami = self.request.get('ami')
        # Zone des zu l�schenden Favoriten holen
        zone = self.request.get('zone')
        # Den Usernamen erfahren
        username = users.get_current_user()

        ami = str(ami)

        testen = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankFavouritenAMIs WHERE user = :username_db AND ami = :ami_db AND zone = :zone_db", username_db=username, ami_db=ami, zone_db=zone)
        # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt
        results = testen.fetch(100)
        for result in results:
          try:
            result.delete()
            # Versuchen den Favorit zu l�schen
          except:
            # Wenn es nicht klappt...
            self.redirect('/images')
          else:
            # Wenn es geklappt hat...
            self.redirect('/images')

        # Wenn es keine Eintr�ge im Datastore gab...
        self.redirect('/images')