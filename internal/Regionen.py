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

class Regionen(webapp.RequestHandler):
    def get(self):
        message = self.request.get('message')
        neuerzugang = self.request.get('neuerzugang')
        # Den Usernamen erfahren
        # Get the username
        username = users.get_current_user()
        # self.response.out.write('posted!')

        # Wir m�ssen das so machen, weil wir sonst nicht weiterkommen,
        # wenn ein Benutzer noch keinen Zugang eingerichtet hat.
        if users.get_current_user():
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
            if message in ("89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99"):
              # wird sie hier, in der Hilfsfunktion rot formatiert
              input_error_message = format_error_message_red(input_error_message)
            else:
              input_error_message = ""


            # Erst �berpr�fen, ob schon ein Eintrag dieses Benutzers vorhanden ist.
            testen = db.GqlQuery("SELECT * FROM KoalaCloudDatenbank WHERE user = :username_db", username_db=username)
            # Wenn Eintr�ge vorhanden sind, werden sie aus der DB geholt und gel�scht
            # Wie viele Eintr�ge des Benutzers sind schon vorhanden?
            anzahl = testen.count()     
            # Alle Eintr�ge des Benutzers holen?
            results = testen.fetch(100) 

            if anzahl:
              # wenn schon Eintr�ge f�r den Benutzer vorhanden sind...
              tabelle_logins = ''
              tabelle_logins = tabelle_logins + '<table border="3" cellspacing="0" cellpadding="5">'
              tabelle_logins = tabelle_logins + '<tr>'
              tabelle_logins = tabelle_logins + '<th>&nbsp;</th>'
              if sprache == "de":
                tabelle_logins = tabelle_logins + '<th align="center">Art der Region</th>'
              else:
                tabelle_logins = tabelle_logins + '<th align="center">Sort of Region</th>'
              tabelle_logins = tabelle_logins + '<th align="center">Endpoint URL</th>'
              tabelle_logins = tabelle_logins + '<th align="center">Access Key</th>'
              if sprache == "de":
                tabelle_logins = tabelle_logins + '<th align="center">Name/Beschreibung</th>'
              else:
                tabelle_logins = tabelle_logins + '<th align="center">Name/Description</th>'
              tabelle_logins = tabelle_logins + '</tr>'
              for test in results:
                tabelle_logins = tabelle_logins + '<tr>'
                tabelle_logins = tabelle_logins + '<td>'
                tabelle_logins = tabelle_logins + '<a href="/zugangentfernen?region='
                tabelle_logins = tabelle_logins + str(test.regionname)
                tabelle_logins = tabelle_logins + '&amp;endpointurl='
                tabelle_logins = tabelle_logins + str(test.endpointurl)
                tabelle_logins = tabelle_logins + '&amp;accesskey='
                tabelle_logins = tabelle_logins + str(test.accesskey)
                if sprache == "de":
                  tabelle_logins = tabelle_logins + '" title="Zugang l&ouml;schen'
                else:
                  tabelle_logins = tabelle_logins + '" title="erase credentials'
                tabelle_logins = tabelle_logins + '"><img src="bilder/delete.png" width="16" height="16" border="0"'
                if sprache == "de":
                  tabelle_logins = tabelle_logins + ' alt="Zugang l&ouml;schen"></a>'
                else:
                  tabelle_logins = tabelle_logins + ' alt="erase credentials"></a>'
                tabelle_logins = tabelle_logins + '</td>'
                tabelle_logins = tabelle_logins + '<td align="center">'
                tabelle_logins = tabelle_logins + str(test.zugangstyp)
                tabelle_logins = tabelle_logins + '</td>'
                tabelle_logins = tabelle_logins + '<td align="center">'
                tabelle_logins = tabelle_logins + str(test.endpointurl)
                tabelle_logins = tabelle_logins + '</td>'
                tabelle_logins = tabelle_logins + '<td align="left">'
                tabelle_logins = tabelle_logins + str(test.accesskey)
                tabelle_logins = tabelle_logins + '</td>'
                tabelle_logins = tabelle_logins + '<td align="left">'
                tabelle_logins = tabelle_logins + test.eucalyptusname
                tabelle_logins = tabelle_logins + '</td>'
                tabelle_logins = tabelle_logins + '</tr>'
              tabelle_logins = tabelle_logins + '</table>'
            else:
              # wenn noch keine Eintr�ge f�r den Benutzer vorhanden sind...
              if sprache == "de":
                tabelle_logins = 'Sie haben noch keine Login-Daten eingegeben'
              else:
                tabelle_logins = 'No credentials available'
              tabelle_logins = tabelle_logins + '<p>&nbsp;</p>'

            if neuerzugang == "eucalyptus":
              eingabefelder = '<p>&nbsp;</p>'
              eingabefelder = eingabefelder + '<form action="/zugangeinrichten" method="post" accept-charset="utf-8">'
              eingabefelder = eingabefelder + '<input type="hidden" name="typ" value="eucalyptus">'
              eingabefelder = eingabefelder + '<table border="0" cellspacing="5" cellpadding="5">'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Der Name ist nur zur Unterscheidung</font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Choose one you like</font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Name:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="nameregion" value="">'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Nur die IP oder DNS ohne <tt>/services/Eucalyptus</tt></font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Just the IP or DNS without <tt>/services/Eucalyptus</tt></font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Endpoint URL:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="endpointurl" value="">'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Google App Engine akzeptiert nur diese Ports</font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Google App Engine accepts only these ports</font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Port:</td>'
              #eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="5" maxlength="5" name="port" value=""></td>'
              eingabefelder = eingabefelder + '    <td colspan="2">'
              eingabefelder = eingabefelder + '      <select name="port" size="1">'
              eingabefelder = eingabefelder + '        <option>80</option>'
              eingabefelder = eingabefelder + '        <option>443</option>'
              eingabefelder = eingabefelder + '        <option>4443</option>'
              eingabefelder = eingabefelder + '        <option>8080</option>'
              eingabefelder = eingabefelder + '        <option>8081</option>'
              eingabefelder = eingabefelder + '        <option>8082</option>'
              eingabefelder = eingabefelder + '        <option>8083</option>'
              eingabefelder = eingabefelder + '        <option>8084</option>'
              eingabefelder = eingabefelder + '        <option>8085</option>'
              eingabefelder = eingabefelder + '        <option>8086</option>'
              eingabefelder = eingabefelder + '        <option>8087</option>'
              eingabefelder = eingabefelder + '        <option>8088</option>'
              eingabefelder = eingabefelder + '        <option>8089</option>'
              eingabefelder = eingabefelder + '        <option selected="selected">8188</option>'
#              eingabefelder = eingabefelder + '        <option>8442</option>' ####### weg damit!!! ###
              eingabefelder = eingabefelder + '        <option>8444</option>'
              eingabefelder = eingabefelder + '        <option>8990</option>'
              eingabefelder = eingabefelder + '      </select>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="accesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Secret Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="secretaccesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td>&nbsp;</td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="Zugang einrichten"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="L&ouml;schen"></td>'
              else:
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="send"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="erase"></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '</table>'
              eingabefelder = eingabefelder + '</form>'
            elif neuerzugang == "ec2":
              eingabefelder = '<p>&nbsp;</p>'
              eingabefelder = eingabefelder + '<form action="/zugangeinrichten" method="post" accept-charset="utf-8">'
              eingabefelder = eingabefelder + '<input type="hidden" name="typ" value="ec2">'
              eingabefelder = eingabefelder + '<table border="0" cellspacing="5" cellpadding="5">'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="accesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Secret Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="secretaccesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td>&nbsp;</td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="Zugang einrichten"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="L&ouml;schen"></td>'
              else:
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="send"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="erase"></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '</table>'
              eingabefelder = eingabefelder + '</form>'
            elif neuerzugang == "GoogleStorage":
              eingabefelder = '<p>&nbsp;</p>'
              eingabefelder = eingabefelder + '<form action="/zugangeinrichten" method="post" accept-charset="utf-8">'
              eingabefelder = eingabefelder + '<input type="hidden" name="typ" value="GoogleStorage">'
              eingabefelder = eingabefelder + '<table border="0" cellspacing="5" cellpadding="5">'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="accesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Secret Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="secretaccesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td>&nbsp;</td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="Zugang einrichten"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="L&ouml;schen"></td>'
              else:
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="send"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="erase"></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '</table>'
              eingabefelder = eingabefelder + '</form>'
            elif neuerzugang == "nimbus":
              eingabefelder = '<p>&nbsp;</p>'
              eingabefelder = eingabefelder + '<form action="/zugangeinrichten" method="post" accept-charset="utf-8">'
              eingabefelder = eingabefelder + '<input type="hidden" name="typ" value="nimbus">'
              eingabefelder = eingabefelder + '<table border="0" cellspacing="5" cellpadding="5">'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Der Name ist nur zur Unterscheidung</font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Choose one you like</font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Name:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="nameregion" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Nur die IP oder DNS</font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Just the IP or DNS</font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Endpoint URL:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="endpointurl" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Google App Engine akzeptiert nur diese Ports</font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Google App Engine accepts only these ports</font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Port:</td>'
              #eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="5" maxlength="5" name="port" value=""></td>'
              eingabefelder = eingabefelder + '    <td colspan="2">'
              eingabefelder = eingabefelder + '      <select name="port" size="1">'
              eingabefelder = eingabefelder + '        <option>80</option>'
              eingabefelder = eingabefelder + '        <option>443</option>'
              eingabefelder = eingabefelder + '        <option>4443</option>'
              eingabefelder = eingabefelder + '        <option>8080</option>'
              eingabefelder = eingabefelder + '        <option>8081</option>'
              eingabefelder = eingabefelder + '        <option>8082</option>'
              eingabefelder = eingabefelder + '        <option>8083</option>'
              eingabefelder = eingabefelder + '        <option>8084</option>'
              eingabefelder = eingabefelder + '        <option>8085</option>'
              eingabefelder = eingabefelder + '        <option>8086</option>'
              eingabefelder = eingabefelder + '        <option>8087</option>'
              eingabefelder = eingabefelder + '        <option>8088</option>'
              eingabefelder = eingabefelder + '        <option>8089</option>'
              eingabefelder = eingabefelder + '        <option selected="selected">8188</option>'
              #eingabefelder = eingabefelder + '        <option>8442</option>' ####### weg damit!!! ###
              eingabefelder = eingabefelder + '        <option>8444</option>'
              eingabefelder = eingabefelder + '        <option>8990</option>'
              eingabefelder = eingabefelder + '      </select>'
              eingabefelder = eingabefelder + '    </td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="accesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Secret Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="secretaccesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td>&nbsp;</td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="Zugang einrichten"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="L&ouml;schen"></td>'
              else:
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="send"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="erase"></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '</table>'
              eingabefelder = eingabefelder + '</form>'
            elif neuerzugang == "opennebula":
#              eingabefelder = '<p>&nbsp;</p>'
#              if sprache == "de":
#                eingabefelder = eingabefelder + '<font color="green">Unterst&uuml;tung f&uuml;r OpenNebula ist noch nicht implementiert</font>'
#              else:
#                eingabefelder = eingabefelder + '<font color="green">The support of OpenNebula is not yet finished</font>'

              eingabefelder = '<p>&nbsp;</p>'
              eingabefelder = eingabefelder + '<form action="/zugangeinrichten" method="post" accept-charset="utf-8">'
              eingabefelder = eingabefelder + '<input type="hidden" name="typ" value="opennebula">'
              eingabefelder = eingabefelder + '<table border="0" cellspacing="5" cellpadding="5">'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Der Name ist nur zur Unterscheidung</font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Choose one you like</font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Name:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="nameregion" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Nur die IP oder DNS</font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Just the IP or DNS</font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Endpoint URL:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="endpointurl" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '  <td></td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td><font color="green">Google App Engine akzeptiert nur diese Ports</font></td>'
              else:
                eingabefelder = eingabefelder + '    <td><font color="green">Google App Engine accepts only these ports</font></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Port:</td>'
              #eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="5" maxlength="5" name="port" value=""></td>'
              eingabefelder = eingabefelder + '    <td colspan="2">'
              eingabefelder = eingabefelder + '      <select name="port" size="1">'
              eingabefelder = eingabefelder + '        <option>80</option>'
              eingabefelder = eingabefelder + '        <option>443</option>'
              eingabefelder = eingabefelder + '        <option>4443</option>'
              #eingabefelder = eingabefelder + '        <option>4567</option>'  ### Nichte f�r die Produktion!!!
              eingabefelder = eingabefelder + '        <option>8080</option>'
              eingabefelder = eingabefelder + '        <option>8081</option>'
              eingabefelder = eingabefelder + '        <option>8082</option>'
              eingabefelder = eingabefelder + '        <option>8083</option>'
              eingabefelder = eingabefelder + '        <option>8084</option>'
              eingabefelder = eingabefelder + '        <option>8085</option>'
              eingabefelder = eingabefelder + '        <option>8086</option>'
              eingabefelder = eingabefelder + '        <option>8087</option>'
              eingabefelder = eingabefelder + '        <option>8088</option>'
              eingabefelder = eingabefelder + '        <option>8089</option>'
              eingabefelder = eingabefelder + '        <option selected="selected">8188</option>'
              #eingabefelder = eingabefelder + '        <option>8442</option>' ####### weg damit!!! ###
              eingabefelder = eingabefelder + '        <option>8444</option>'
              eingabefelder = eingabefelder + '        <option>8990</option>'
              eingabefelder = eingabefelder + '      </select>'
              eingabefelder = eingabefelder + '    </td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="accesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td align="right">Secret Access Key:</td>'
              eingabefelder = eingabefelder + '    <td colspan="2"><input type="text" size="40" name="secretaccesskey" value=""></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '  <tr>'
              eingabefelder = eingabefelder + '    <td>&nbsp;</td>'
              if sprache == "de":
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="Zugang einrichten"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="L&ouml;schen"></td>'
              else:
                eingabefelder = eingabefelder + '    <td align="center"><input type="submit" value="send"></td>'
                eingabefelder = eingabefelder + '    <td align="center"><input type="reset" value="erase"></td>'
              eingabefelder = eingabefelder + '  </tr>'
              eingabefelder = eingabefelder + '</table>'
              eingabefelder = eingabefelder + '</form>'
            elif neuerzugang == "tashi":
              eingabefelder = '<p>&nbsp;</p>'
              if sprache == "de":
                eingabefelder = eingabefelder + '<font color="green">Unterst&uuml;tung f&uuml;r Tashi ist noch nicht implementiert</font>'
              else:
                eingabefelder = eingabefelder + '<font color="green">The support of Tashi is not yet finished</font>'
            else:
              eingabefelder = ''

            if neuerzugang == "eucalyptus":
              version_warnung = '<p>&nbsp;</p>'
              if sprache == "de":
                version_warnung = version_warnung + '<p><font color="red">KOALA unterst&uuml;tzt ausschlie&szlig;lich Eucalyptus 1.6.2.<br> '
                version_warnung = version_warnung + 'Fr&uuml;here Versionen haben Fehler, die zu Problemen f&uuml;hren k&ouml;nnen.<br>'
                version_warnung = version_warnung + 'Ein Update von Eucalyptus auf die aktuelle Version wird daher empfohlen.</font></p>'
              else:
                version_warnung = version_warnung + '<p><font color="red">KOALA supports only Eucalyptus 1.6.2.<br> '
                version_warnung = version_warnung + 'Prior versions have some bugs that can cause some problems.<br>'
                version_warnung = version_warnung + 'Updating Eucalyptus to the latest version should be considered.</font></p>'
            else:
              version_warnung = ''

            if neuerzugang == "eucalyptus":
              port_warnung = '<p>&nbsp;</p>\n'
              if sprache == "de":
                port_warnung = port_warnung + 'Die Google App Engine akzeptiert nur wenige Ports. '
                port_warnung = port_warnung + 'Leider ist der Standard-Port von Eucalyputs (8773) nicht dabei. '
                port_warnung = port_warnung + 'Es empfiehlt sich darum, einen anderen Port auf den Eucalyptus-Port umzuleiten. '
                port_warnung = port_warnung + 'Ein Beispiel:<br> \n'
                port_warnung = port_warnung + '<tt>iptables -I INPUT -p tcp --dport 8188 -j ACCEPT</tt><br>\n '
                port_warnung = port_warnung + '<tt>iptables -I PREROUTING -t nat -i eth0 -p tcp --dport 8188 -j REDIRECT --to-port 8773</tt> '
              else:
                port_warnung = port_warnung + 'The Google App Engine accepts only a few number of ports '
                port_warnung = port_warnung + 'and the default port of Eucalyptus (8773) is not included. '
                port_warnung = port_warnung + 'Because of this fact, you have to route another port to the Eucayptus port. '
                port_warnung = port_warnung + 'For example:<br> \n'
                port_warnung = port_warnung + '<tt>iptables -I INPUT -p tcp --dport 8188 -j ACCEPT</tt><br>\n '
                port_warnung = port_warnung + '<tt>iptables -I PREROUTING -t nat -i eth0 -p tcp --dport 8188 -j REDIRECT --to-port 8773</tt> '
            elif neuerzugang == "nimbus":
              port_warnung = '<p>&nbsp;</p>\n'
              if sprache == "de":
                port_warnung = port_warnung + 'Die Google App Engine akzeptiert nur wenige Ports. '
                port_warnung = port_warnung + 'Wenn die Nimbus-Infrastruktur, die Sie verwenden m&ouml;chten, keinen unterst&uuml;tzten Port (z.B. 8442) verwendet, '
                port_warnung = port_warnung + 'empfiehlt es sich, einen unterst&uuml;tzten Port auf den Port der Nimbus-Infrastruktur umzuleiten. '
                port_warnung = port_warnung + 'Ein Beispiel:<br> \n'
                port_warnung = port_warnung + '<tt>iptables -I INPUT -p tcp --dport 8188 -j ACCEPT</tt><br>\n '
                port_warnung = port_warnung + '<tt>iptables -I PREROUTING -t nat -i eth0 -p tcp --dport 8188 -j REDIRECT --to-port 8442</tt> '
              else:
                port_warnung = port_warnung + 'The Google App Engine accepts only a few number of ports. '
                port_warnung = port_warnung + 'If the Nimbus infrastructure you want to access, has a non accepted port (e.g. 8442), you have to route an accepted port to the port of the Nimbus infrastructure. '
                port_warnung = port_warnung + 'For example:<br> \n'
                port_warnung = port_warnung + '<tt>iptables -I INPUT -p tcp --dport 8188 -j ACCEPT</tt><br>\n '
                port_warnung = port_warnung + '<tt>iptables -I PREROUTING -t nat -i eth0 -p tcp --dport 8188 -j REDIRECT --to-port 8442</tt> '
            elif neuerzugang == "opennebula":
              port_warnung = '<p>&nbsp;</p>\n'
              if sprache == "de":
                port_warnung = port_warnung + 'Die Google App Engine akzeptiert nur wenige Ports. '
                port_warnung = port_warnung + 'Leider ist der Standard-Port von OpenNebula (4567) nicht dabei. '
                port_warnung = port_warnung + 'Es ist darum notwendig, den econe Server auf einen anderen, unterst&uuml;tzten Port umzuleiten. '
                port_warnung = port_warnung + 'Die Einstellung erfolgt in der Datei <tt>econe.conf</tt>'
              else:
                port_warnung = port_warnung + 'The Google App Engine accepts only a few number of ports '
                port_warnung = port_warnung + 'and the default port of OpenNebula (4567) is not included. '
                port_warnung = port_warnung + 'Because of this fact, you have to route the econe server to another, supported port. '
                port_warnung = port_warnung + 'The port configuration of the econe server is done inside <tt>econe.conf</tt>'
            else:
              port_warnung = '<p>&nbsp;</p>'


            template_values = {
            'navigations_bar': navigations_bar,
            'url': url,
            'url_linktext': url_linktext,
            'zone': regionname,
            'zone_amazon': zone_amazon,
            'eingabefelder': eingabefelder,
            'input_error_message': input_error_message,
            'tabelle_logins': tabelle_logins,
            'zonen_liste': zonen_liste,
            'port_warnung': port_warnung,
            'version_warnung': version_warnung,
            }

            path = os.path.join(os.path.dirname(__file__), "../templates", sprache, "index.html")
            self.response.out.write(template.render(path,template_values))
        else:
            self.redirect('/')

