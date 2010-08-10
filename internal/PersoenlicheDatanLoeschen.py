#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

from internal.Sprache import *
from internal.Datastore import *

class PersoenlicheDatanLoeschen(webapp.RequestHandler):
    def get(self):
        # Den Usernamen erfahren
        username = users.get_current_user()

        # �berpr�fen, ob schon ein Eintrag dieses Benutzers vorhanden ist.
        aktivezone = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankAktiveZone WHERE user = :username_db", username_db=username)
        # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt und gel�scht
        results = aktivezone.fetch(100)
        for result in results:
          result.delete()

        # �berpr�fen, ob schon ein Eintrag dieses Benutzers vorhanden ist.
        sprache = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankSprache WHERE user = :username_db", username_db=username)
        # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt und gel�scht
        results = sprache.fetch(100)
        for result in results:
          result.delete()

        # �berpr�fen, ob schon ein Eintrag dieses Benutzers vorhanden ist.
        testen = db.GqlQuery("SELECT * FROM KoalaCloudDatenbank WHERE user = :username_db", username_db=username)
        # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt und gel�scht
        results = testen.fetch(100)
        for result in results:
          result.delete()

        # �berpr�fen, ob schon ein Eintrag dieses Benutzers vorhanden ist.
        testen = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankFavouritenAMIs WHERE user = :username_db", username_db=username)
        # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt und gel�scht
        results = testen.fetch(100)
        for result in results:
          result.delete()

        self.redirect('/')