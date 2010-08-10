#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api.urlfetch import DownloadError

from library import login
from library import aktuelle_sprache
from library import navigations_bar_funktion
from library import amazon_region
from library import zonen_liste_funktion
from library import format_error_message_green
from library import format_error_message_red

from boto.ec2.connection import *

class AlleInstanzenBeendenFrage(webapp.RequestHandler):
    def get(self):
        # Den Usernamen erfahren
        username = users.get_current_user()
        if not username:
            self.redirect('/')

        # Nachsehen, ob eine Region/Zone ausgew�hlte wurde
        aktivezone = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankAktiveZone WHERE user = :username_db", username_db=username)
        results = aktivezone.fetch(100)

        if results:
          sprache = aktuelle_sprache(username)
          navigations_bar = navigations_bar_funktion(sprache)
          url = users.create_logout_url(self.request.uri).replace('&', '&amp;').replace('&amp;amp;', '&amp;')
          url_linktext = 'Logout'

          conn_region, regionname = login(username)
          zone_amazon = amazon_region(username)

          zonen_liste = zonen_liste_funktion(username,sprache)

          template_values = {
          'navigations_bar': navigations_bar,
          'url': url,
          'url_linktext': url_linktext,
          'zone': regionname,
          'zone_amazon': zone_amazon,
          'zonen_liste': zonen_liste,
          }

          #if sprache == "de": naechse_seite = "alle_images_beenden_frage_de.html"
          #else:               naechse_seite = "alle_images_beenden_frage_en.html"
          #path = os.path.join(os.path.dirname(__file__), naechse_seite)
          path = os.path.join(os.path.dirname(__file__), "../templates", sprache, "alle_images_beenden_frage.html")
          self.response.out.write(template.render(path,template_values))
