#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import re

from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import memcache

from library import login

from boto.ec2.connection import *

class KeyErzeugen(webapp.RequestHandler):
    def post(self):
        #self.response.out.write('posted!')
        neuerkeyname = self.request.get('keyname')

        # Den Usernamen erfahren
        username = users.get_current_user()

        conn_region, regionname = login(username)

        if neuerkeyname == "":
          # Testen ob ein Name f�r den neuen key angegeben wurde
          # Wenn kein Name angegeben wurde, kann kein Key angelegt werden
          #fehlermeldung = "Sie haben keine Namen angegeben"
          fehlermeldung = "92"
          self.redirect('/schluessel?message='+fehlermeldung)
        elif re.search(r'[^\-_a-zA-Z0-9]', neuerkeyname) != None:
          # Testen ob der Name f�r den neuen key nicht erlaubte Zeichen enth�lt
          fehlermeldung = "100"
          self.redirect('/schluessel?message='+fehlermeldung)
        else:

          liste_key_pairs = conn_region.get_all_key_pairs()
          # Anzahl der Elemente in der Liste
          laenge_liste_keys = len(liste_key_pairs)
          # Variable erzeugen zum Erfassen, ob der neue Schl�ssel schon existiert
          schon_vorhanden = 0

          for i in range(laenge_liste_keys):
            # Vergleichen
            if str(liste_key_pairs[i].name) == neuerkeyname:
              # Schl�ssel existiert schon!
              schon_vorhanden = 1
              neu = "nein"
              fehlermeldung = "102"
              self.redirect('/schluessel?message='+fehlermeldung)

          # Wenn der Schl�ssel noch nicht existiert...
          if schon_vorhanden == 0:
            try:
              # Schl�sselpaar erzeugen
              neuer_key = conn_region.create_key_pair(neuerkeyname)
            except EC2ResponseError:
              fehlermeldung = "101"
              self.redirect('/schluessel?message='+fehlermeldung)
            except DownloadError:
              # Diese Exception hilft gegen diese beiden Fehler:
              # DownloadError: ApplicationError: 2 timed out
              # DownloadError: ApplicationError: 5
              fehlermeldung = "8"
              self.redirect('/schluessel?message='+fehlermeldung)
            else:
              neu = "ja"
              secretkey = neuer_key.material
              keyname = str(neuerkeyname)
              keyname = keyname + "_"
              keyname = keyname + regionname
              keyname = keyname + "_"
              keyname = keyname + str(username)
              # der Secret Key wird f�r 10 Minuten im Memcache gespeichert
              memcache.add(key=keyname, value=secretkey, time=600)
              fehlermeldung = "99"
              self.redirect('/schluessel?message='+fehlermeldung+'&neu='+neu+'&neuerkeyname='+neuerkeyname+'&secretkey='+keyname)
