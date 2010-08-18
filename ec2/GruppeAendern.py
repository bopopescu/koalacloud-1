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

from dateutil.parser import *

from error_messages import error_messages

from boto.ec2.connection import *

class GruppeAendern(webapp.RequestHandler):
    def get(self):
        # Eventuell vorhande Fehlermeldung holen
        message = self.request.get('message')
        # Den Namen der zu l�schenden Gruppe holen
        gruppe = self.request.get('gruppe')
        # Den Usernamen erfahren
        username = users.get_current_user()
        if not username:
            self.redirect('/')

        sprache = aktuelle_sprache(username)
        navigations_bar = navigations_bar_funktion(sprache)
        # Nachsehen, ob eine Region/Zone ausgew�hlte wurde
        aktivezone = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankAktiveZone WHERE user = :username_db", username_db=username)
        results = aktivezone.fetch(100)

        if not results:
          regionname = '---'
          zone_amazon = ""
        else:
          conn_region, regionname = login(username)
          zone_amazon = amazon_region(username)

        url = users.create_logout_url(self.request.uri).replace('&', '&amp;').replace('&amp;amp;', '&amp;')
        url_linktext = 'Logout'

        zonen_liste = zonen_liste_funktion(username,sprache)

        if sprache != "de":
          sprache = "en"

        input_error_message = error_messages.get(message, {}).get(sprache)

        # Wenn keine Fehlermeldung gefunden wird, ist das Ergebnis "None"
        if input_error_message == None:
          input_error_message = ""

        # Wenn die Nachricht gr�n formatiert werden soll...
        if message in ("28", "37"):
          # wird sie hier, in der Hilfsfunktion gr�n formatiert
          input_error_message = format_error_message_green(input_error_message)
        # Ansonsten wird die Nachricht rot formatiert
        elif message in ("8", "29", "30", "31", "32", "33", "34", "35", "36", "38", "39"):
          input_error_message = format_error_message_red(input_error_message)
        else:
          input_error_message = ""

        try:
          # Liste mit den Security Groups
          # Man kann nicht direkt versuchen mit get_all_security_groups(gruppen_liste)
          # die anzulegende Gruppe zu erzeugen. Wenn die Gruppe noch nicht existiert,
          # gibt es eine Fehlermeldung
          liste_security_groups = conn_region.get_all_security_groups()
        except EC2ResponseError:
          # Wenn es nicht klappt...
          fehlermeldung = "7"
          self.redirect('/securitygroups?message='+fehlermeldung)
        except DownloadError:
          # Diese Exception hilft gegen diese beiden Fehler:
          # DownloadError: ApplicationError: 2 timed out
          # DownloadError: ApplicationError: 5
          fehlermeldung = "7"
          self.redirect('/securitygroups?message='+fehlermeldung)
        else:
          # Wenn es geklappt hat und die Liste geholt wurde...

          # Anzahl der Elemente in der Liste
          laenge_liste_security_groups = len(liste_security_groups)


          for i in range(laenge_liste_security_groups):
            # Vergleichen
            if liste_security_groups[i].name == gruppe:
              # Liste mit den Regeln der Security Group holen
              liste_regeln = liste_security_groups[i].rules
              # Anzahl der Elemente in der Liste mit den Regeln
              laenge_liste_regeln = len(liste_regeln)
              if laenge_liste_regeln == 0:
                if sprache == "de":
                  regelntabelle = 'Es sind noch keine Regeln in der  Sicherheitsgruppe '+gruppe+' vorhanden'
                else:
                  regelntabelle = 'Still no rules exist inside the security group '+gruppe
              else:
                for i in range(laenge_liste_regeln):

                  regelntabelle = ''
                  regelntabelle = regelntabelle + '<table border="3" cellspacing="0" cellpadding="5">'
                  regelntabelle = regelntabelle + '<tr>'
                  regelntabelle = regelntabelle + '<th>&nbsp;</th>'
                  if sprache == "de":
                    regelntabelle = regelntabelle + '<th align="center">Protokoll</th>'
                  else:
                    regelntabelle = regelntabelle + '<th align="center">Protocol</th>'
                  regelntabelle = regelntabelle + '<th align="center">From Port</th>'
                  regelntabelle = regelntabelle + '<th align="center">To Port</th>'
                  regelntabelle = regelntabelle + '</tr>'
                  for i in range(laenge_liste_regeln):
                      regelntabelle = regelntabelle + '<tr>'
                      regelntabelle = regelntabelle + '<td>'
                      regelntabelle = regelntabelle + '<a href="/grupperegelentfernen?regel='
                      regelntabelle = regelntabelle + str(liste_regeln[i])
                      regelntabelle = regelntabelle + '&amp;gruppe='
                      regelntabelle = regelntabelle + gruppe
                      regelntabelle = regelntabelle + '" title="Regel l&ouml;schen"><img src="bilder/delete.png" width="16" height="16" border="0" alt="Regel l&ouml;schen"></a>'
                      regelntabelle = regelntabelle + '</td>'
                      regelntabelle = regelntabelle + '<td>'
                      if str(liste_regeln[i].ip_protocol) == "tcp":
                        regelntabelle = regelntabelle + 'TCP'
                      if str(liste_regeln[i].ip_protocol) == "udp":
                        regelntabelle = regelntabelle + 'UDP'
                      if str(liste_regeln[i].ip_protocol) == "icmp":
                        regelntabelle = regelntabelle + 'ICMP'
                      regelntabelle = regelntabelle + '</td>'
                      regelntabelle = regelntabelle + '<td>'
                      regelntabelle = regelntabelle + str(liste_regeln[i].from_port)
                      regelntabelle = regelntabelle + '</td>'
                      regelntabelle = regelntabelle + '<td>'
                      regelntabelle = regelntabelle + str(liste_regeln[i].to_port)
                      regelntabelle = regelntabelle + '</td>'
                      regelntabelle = regelntabelle + '</tr>'
                  regelntabelle = regelntabelle + '</table>'

          template_values = {
          'navigations_bar': navigations_bar,
          'url': url,
          'url_linktext': url_linktext,
          'zone': regionname,
          'zone_amazon': zone_amazon,
          'gruppe': gruppe,
          'regelntabelle': regelntabelle,
          'input_error_message': input_error_message,
          'zonen_liste': zonen_liste,
          }

          #if sprache == "de": naechse_seite = "securitygrouprules_de.html"
          #else:               naechse_seite = "securitygrouprules_en.html"
          #path = os.path.join(os.path.dirname(__file__), naechse_seite)
          path = os.path.join(os.path.dirname(__file__), "../templates", sprache, "securitygrouprules.html")
          self.response.out.write(template.render(path,template_values))
