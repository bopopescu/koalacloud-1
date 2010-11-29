#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api.urlfetch import DownloadError

from library import loginelb

class LoadBalancer_Instanz_Zuordnen(webapp.RequestHandler):
    def post(self):
        mobile = self.request.get('mobile')
        if mobile != "true":
            mobile = "false"
        # self.response.out.write('posted!')
        # Zu verkn�pfenden Load Balancer holen
        loadbalancer = self.request.get('loadbalancer')
        # Zu verkn�pfende Instanz holen
        instanz = self.request.get('instanzen')
        # Den Usernamen erfahren
        username = users.get_current_user()

        # Mit ELB verbinden
        conn_elb = loginelb(username)

        # Eine leere Liste f�r das IDs der Instanzen erzeugen
        list_of_instances = []
        # Die Instanz in Liste einf�gen
        list_of_instances.append(instanz)

        try:
          # Die Instanz verkn�pfen
          conn_elb.register_instances(loadbalancer, list_of_instances)
        except EC2ResponseError:
          # Wenn es nicht geklappt hat...
          fehlermeldung = "62"
          self.redirect('/loadbalanceraendern?mobile='+str(mobile)+'&name='+loadbalancer+'&message='+fehlermeldung)
        except DownloadError:
          # Diese Exception hilft gegen diese beiden Fehler:
          # DownloadError: ApplicationError: 2 timed out
          # DownloadError: ApplicationError: 5
          fehlermeldung = "8"
          self.redirect('/loadbalanceraendern?mobile='+str(mobile)+'&name='+loadbalancer+'&message='+fehlermeldung)
        else:
          # Wenn es geklappt hat...
          fehlermeldung = "61"
          self.redirect('/loadbalanceraendern?mobile='+str(mobile)+'&name='+loadbalancer+'&message='+fehlermeldung)
