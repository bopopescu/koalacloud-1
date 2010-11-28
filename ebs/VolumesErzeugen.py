#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api.urlfetch import DownloadError

from library import login

from boto.ec2.connection import *

class VolumesErzeugen(webapp.RequestHandler):
    def post(self):
        #self.response.out.write('posted!')
        mobile = self.request.get('mobile')
        groesse = self.request.get('groesse')
        GB_oder_TB = self.request.get('GB_oder_TB')
        zone = self.request.get('zone')

        # Den Usernamen erfahren
        username = users.get_current_user()

        conn_region, regionname = login(username)

        if groesse == "":
          # Testen ob die Gr��e des neuen Volumes angegeben wurde
          # Wenn keine Gr��e angegeben wurde, kann kein Volume angelegt werden
          #fehlermeldung = "Sie haben keine Gr��e angegeben"
          fehlermeldung = "16"
          self.redirect('/volumes?mobile='+str(mobile)+'&message='+fehlermeldung) 
        elif groesse.isdigit() == False: 
          # Testen ob die Gr��e eine Zahl ist
          # Wenn nicht ausschlie�lich eine Zahl eingegeben wurde sondern evtl. Buchstaben oder Sonderzeichen
          #fehlermeldung = "Sie haben keine Zahl angegeben"
          fehlermeldung = "17"
          self.redirect('/volumes?mobile='+str(mobile)+'&message='+fehlermeldung)
        elif GB_oder_TB == "TB" and int(groesse) > 1:
          # Testen ob TB als Ma�einheit angegeben wurde und die Gr��e > 1 TB ist
          # fehlermeldung = "Amazon EBS erm�glicht die Erstellung von Datentr�gern
          # mit einer Speicherkapazit�t von 1 GB bis 1 TB"
          fehlermeldung = "25"
          self.redirect('/volumes?mobile='+str(mobile)+'&message='+fehlermeldung)
        else:
          # Die Eingabe in Integer umwandeln
          groesse = int(groesse)
          if GB_oder_TB == "TB":
            # Testen ob GB oder TB als Ma�einheit angegeben wurde
            # Bei TB wird die Zahl mit 1000 multipliziert
            groesse *= 1000
          # Volume erzeugen
          try:
            # Volume erzeugen
            neues_volume = conn_region.create_volume(groesse, zone, snapshot=None)
          except EC2ResponseError:
            # Wenn es nicht klappt...
            fehlermeldung = "18"
            self.redirect('/volumes?mobile='+str(mobile)+'&message='+fehlermeldung)
          except DownloadError:
            # Wenn es nicht klappt...
            # Diese Exception hilft gegen diese beiden Fehler:
            # DownloadError: ApplicationError: 2 timed out
            # DownloadError: ApplicationError: 5
            fehlermeldung = "8"
            self.redirect('/volumes?mobile='+str(mobile)+'&message='+fehlermeldung)
          else:
            # Wenn es geklappt hat...
            fehlermeldung = "15"
            self.redirect('/volumes?mobile='+str(mobile)+'&message='+fehlermeldung)
            