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

class VolumeausSnapshotErzeugen(webapp.RequestHandler):
    def get(self):
        mobile = self.request.get('mobile')
        if mobile != "true":
            mobile = "false"
        #self.response.out.write('posted!')
        # Den Usernamen erfahren
        username = users.get_current_user()
        if not username:
            self.redirect('/')
        snapshot = self.request.get('snapshot')   
        # Eventuell vorhande Fehlermeldung holen
        message = self.request.get('message')

        sprache = aktuelle_sprache(username)
        navigations_bar = navigations_bar_funktion(sprache,mobile)
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

        zonen_liste = zonen_liste_funktion(username,sprache,mobile)

        if sprache != "de":
            sprache = "en"

        input_error_message = error_messages.get(message, {}).get(sprache)

        # Wenn keine Fehlermeldung gefunden wird, ist das Ergebnis "None"
        if input_error_message == None:
            input_error_message = ""

        # Wenn die Nachricht rot formatiert werden soll...
        if message in ("8", "10", "16", "17", "25"):
          input_error_message = format_error_message_red(input_error_message)
        else:
          input_error_message = ""


        try:
            # Liste mit den Zonen
            liste_zonen = conn_region.get_all_zones()
        except EC2ResponseError:
            # Wenn es nicht geklappt hat...
            fehlermeldung = "10"
            self.redirect('/volumeaussnapshoterzeugen?mobile='+str(mobile)+'&message='+fehlermeldung)
        except DownloadError:
            # Diese Exception hilft gegen diese beiden Fehler:
            # DownloadError: ApplicationError: 2 timed out
            # DownloadError: ApplicationError: 5
            fehlermeldung = "8"
            self.redirect('/volumeaussnapshoterzeugen?mobile='+str(mobile)+'&message='+fehlermeldung)
        else:
            # Wenn es geklappt hat...
            # Anzahl der Elemente in der Liste
            laenge_liste_zonen = len(liste_zonen)


        volume_aus_snapshot_erzeugen_tabelle = ''
        volume_aus_snapshot_erzeugen_tabelle += '<form action="/volumeaussnapshoterzeugen_definiv" method="post" accept-charset="utf-8">\n'
        volume_aus_snapshot_erzeugen_tabelle += '<input type="hidden" name="mobile" value="'+mobile+'">'
        volume_aus_snapshot_erzeugen_tabelle += '<input type="hidden" name="snapshot" value="'+snapshot+'">'
        volume_aus_snapshot_erzeugen_tabelle += '<table border="0" cellspacing="0" cellpadding="5">'
        volume_aus_snapshot_erzeugen_tabelle += '<tr>\n'
        volume_aus_snapshot_erzeugen_tabelle += '<td align="right"><b>ID:</b></td>\n'      
        volume_aus_snapshot_erzeugen_tabelle += '<td>'+snapshot+'</td>\n'
        volume_aus_snapshot_erzeugen_tabelle += '</tr>\n'
        volume_aus_snapshot_erzeugen_tabelle += '<tr>\n'
        if sprache == "de":
            volume_aus_snapshot_erzeugen_tabelle += '<td align="right"><b>Zonen:</b></td>\n'
        else:
            volume_aus_snapshot_erzeugen_tabelle += '<td align="right"><b>Zones:</b></td>\n' 
        volume_aus_snapshot_erzeugen_tabelle += '<td>\n'
        for i in range(laenge_liste_zonen):
            volume_aus_snapshot_erzeugen_tabelle += '<input type="radio" name="zone" value="'+liste_zonen[i].name+'"> '+liste_zonen[i].name+'<BR>\n'
        volume_aus_snapshot_erzeugen_tabelle += '</td>\n'
        volume_aus_snapshot_erzeugen_tabelle += '</tr>\n'

        volume_aus_snapshot_erzeugen_tabelle += '<tr>\n'
        if sprache == "de":
            volume_aus_snapshot_erzeugen_tabelle += '<td align="right"><b>Gr&ouml;&szlig;e:</b></td>\n'
        else:
            volume_aus_snapshot_erzeugen_tabelle += '<td align="right"><b>Size:</b></td>\n' 
        volume_aus_snapshot_erzeugen_tabelle += '<td><input name="groesse" type="text" size="3" maxlength="3">\n'
        volume_aus_snapshot_erzeugen_tabelle += '&nbsp;\n'
        volume_aus_snapshot_erzeugen_tabelle += '<select name="GB_oder_TB" size="1">\n'
        volume_aus_snapshot_erzeugen_tabelle += '<option selected="selected">GB</option>\n'
        volume_aus_snapshot_erzeugen_tabelle += '<option>TB</option>\n'
        volume_aus_snapshot_erzeugen_tabelle += '</select>\n'
        volume_aus_snapshot_erzeugen_tabelle += '</td>\n'
        volume_aus_snapshot_erzeugen_tabelle += '</tr>\n'      
        volume_aus_snapshot_erzeugen_tabelle += '<tr>\n'
        if sprache == "de":
            volume_aus_snapshot_erzeugen_tabelle += '<td align="left" colspan="2"><input type="submit" value="Volume aus Snapshot erzeugen"></td>\n'
        else:
            volume_aus_snapshot_erzeugen_tabelle += '<td align="left" colspan="2"><input type="submit" value="create volume from snapshot"></td>\n'
        volume_aus_snapshot_erzeugen_tabelle += '</table>'
        volume_aus_snapshot_erzeugen_tabelle += '</form>'

        path = '&amp;path=volumeaussnapshoterzeugen&amp;snapshot='+snapshot
          
        template_values = {
        'navigations_bar': navigations_bar,
        'url': url,
        'url_linktext': url_linktext,
        'zone': regionname,
        'zone_amazon': zone_amazon,
        'volume_aus_snapshot_erzeugen_tabelle': volume_aus_snapshot_erzeugen_tabelle,
        'input_error_message': input_error_message,
        'zonen_liste': zonen_liste,
        'path': path,
        }

        if mobile == "true":
            path = os.path.join(os.path.dirname(__file__), "../templates/mobile", sprache, "volume_aus_snapshot_create.html")
        else:
            path = os.path.join(os.path.dirname(__file__), "../templates", sprache, "volume_aus_snapshot_create.html")
        self.response.out.write(template.render(path,template_values))
            