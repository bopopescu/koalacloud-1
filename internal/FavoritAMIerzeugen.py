#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import re

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

from library import login

from internal.Datastore import *

from boto.ec2.connection import *
from boto.s3.connection import *

class FavoritAMIerzeugen(webapp.RequestHandler):
    def post(self):
        mobile = self.request.get('mobile')
        if mobile != "true":
            mobile = "false"
        #self.response.out.write('posted!')
        ami = self.request.get('ami')
        zone = self.request.get('zone')
        # Den Usernamen erfahren
        username = users.get_current_user()

        if ami == "":
          # Testen ob die AMI-Bezeichnung angegeben wurde
          # Wenn keine AMI-Bezeichnung angegeben wurde, kann kein Favorit angelegt werden
          #fehlermeldung = "Sie haben keine AMI-Bezeichnung angegeben"
          fehlermeldung = "84"
          self.redirect('/images?mobile='+str(mobile)+'&message='+fehlermeldung)
        else:
          if re.match('ami-*', ami) == None:  
            # Erst �berpr�fen, ob die Eingabe mit "ami-" ang�ngt
            fehlermeldung = "85"
            self.redirect('/images?mobile='+str(mobile)+'&message='+fehlermeldung)
          elif len(ami) != 12:
            # �berpr�fen, ob die Eingabe 12 Zeichen lang ist
            fehlermeldung = "86"
            self.redirect('/images?mobile='+str(mobile)+'&message='+fehlermeldung)
          elif re.search(r'[^\-a-zA-Z0-9]', ami) != None:
            # �berpr�fen, ob die Eingabe nur erlaubte Zeichen enth�lt
            # Die Zeichen - und a-zA-Z0-9 sind erlaubt. Alle anderen nicht. Darum das ^
            fehlermeldung = "87"
            self.redirect('/images?mobile='+str(mobile)+'&message='+fehlermeldung)
          else:
            # Erst �berpr�fen, ob schon ein AMI-Eintrag dieses Benutzers in der Zone vorhanden ist.
            testen = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankFavouritenAMIs WHERE user = :username_db AND ami = :ami_db AND zone = :zone_db", username_db=username, ami_db=ami, zone_db=zone)
            # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt und gel�scht
            results = testen.fetch(100)
            for result in results:
              result.delete()

            # Erst testen, ob es dieses AMI �berhaupt gibt.
            # Eine leere Liste f�r das AMI erzeugen
            ami_liste = []
            # Das AMIs in die Liste einf�gen
            ami_liste.append(ami)

            conn_region, regionname = login(username)
            try:
              liste_favoriten_ami_images = conn_region.get_all_images(image_ids=ami_liste)
            except EC2ResponseError:
              fehlermeldung = "88"
              self.redirect('/images?mobile='+str(mobile)+'&message='+fehlermeldung)
            else:
              # Favorit erzeugen
              # Festlegen, was in den Datastore geschrieben werden soll
              favorit = KoalaCloudDatenbankFavouritenAMIs(ami=ami,
                                                          zone=zone,
                                                          user=username)
              # In den Datastore schreiben
              favorit.put()

              fehlermeldung = "83"
              self.redirect('/images?mobile='+str(mobile)+'&message='+fehlermeldung)

