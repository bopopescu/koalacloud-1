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

class ImageStarten(webapp.RequestHandler):
    def get(self):
        # Den Usernamen erfahren
        username = users.get_current_user()
        if not username:
            self.redirect('/')
        # Die ID des zu startenden Images holen
        image = self.request.get('image')
        # Die Architektur des zu startenden Images holen
        arch = self.request.get('arch')

        sprache = aktuelle_sprache(username)
        navigations_bar = navigations_bar_funktion(sprache)
        # Nachsehen, ob eine Region/Zone ausgewählte wurde
        aktivezone = db.GqlQuery("SELECT * FROM KoalaCloudDatenbankAktiveZone WHERE user = :username_db", username_db=username)
        results = aktivezone.fetch(100)

        if not results:
          regionname = 'keine'
          zone_amazon = ""
        else:
          conn_region, regionname = login(username)
          zone_amazon = amazon_region(username)

        # So wird der HTML-Code korrekt
        url = users.create_logout_url(self.request.uri).replace('&', '&amp;').replace('&amp;amp;', '&amp;')
        #url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        zonen_liste = zonen_liste_funktion(username,sprache)

        for result in results:
          if result.zugangstyp == "Amazon":
            imageliste = [image]
            # Liste mit den Images
            liste_images = conn_region.get_all_images(image_ids=imageliste)  
            # Anzahl der Images in der Liste
            laenge_liste_images = len(liste_images)
            for i in range(laenge_liste_images):
              if liste_images[i].id == image:
                manifest = str(liste_images[i].location)
          else:
            # Liste mit den Images
            liste_images = conn_region.get_all_images()
            # Anzahl der Images in der Liste
            laenge_liste_images = len(liste_images)
            for i in range(laenge_liste_images):
              if liste_images[i].id == image:
                manifest = str(liste_images[i].location)


        if result.zugangstyp == "Nimbus":

          imagetextfeld = '<input name="image_id" type="text" size="70" maxlength="70" value="'
          imagetextfeld = imagetextfeld + image
          imagetextfeld = imagetextfeld + '" readonly>'

          manifesttextfeld = '<input name="image_manifest" type="text" size="70" maxlength="70" value="'
          manifesttextfeld = manifesttextfeld + manifest
          manifesttextfeld = manifesttextfeld + '" readonly>'

          if sprache == "de": number_instances_min_anfang = "Instanzen (min):"
          else:               number_instances_min_anfang = "Instances (min):"

          if sprache == "de": number_instances_max_anfang = "Instanzen (max):"
          else:               number_instances_max_anfang = "Instances (max):"

          if sprache == "de": image_starten_ueberschrift_anfang = "Image starten: "
          else:               image_starten_ueberschrift_anfang = "Start image: "

          if sprache == "de": value_button_image_starten = "Image starten"
          else:               value_button_image_starten = "start image"

          template_values = {
          'navigations_bar': navigations_bar,
          'url': url,
          'url_linktext': url_linktext,
          'zone': regionname,
          'zone_amazon': zone_amazon,
          'image': imagetextfeld,
          'manifest': manifesttextfeld,
          'zonen_liste': zonen_liste,
          'number_instances_max_anfang': number_instances_max_anfang,
          'number_instances_min_anfang': number_instances_min_anfang,
          'image_starten_ueberschrift_anfang': image_starten_ueberschrift_anfang,
          'value_button_image_starten': value_button_image_starten,
          }

          #path = os.path.join(os.path.dirname(__file__), 'image_starten_nimbus.html')
          path = os.path.join(os.path.dirname(__file__), "../templates", sprache, "image_starten_nimbus.html")
          self.response.out.write(template.render(path,template_values))

        else: # Wenn es nicht Nimbus ist


          # Wenn es Amazon EC2 ist
          if result.zugangstyp == "Amazon":
            if arch == "i386":
              # Liste mit den Instanz-Typen wenn es ein 32-Bit Image ist
              liste_instanztypen_eucalyptus = ["m1.small", "c1.medium"]
            else:
              # Liste mit den Instanz-Typen wenn es ein 64-Bit Image ist
              liste_instanztypen_eucalyptus = ["m1.large", "m1.xlarge", "m2.xlarge", "m2.2xlarge", "m2.4xlarge", "c1.xlarge"]
            # Anzahl der Elemente in der Liste
            laenge_liste_instanztypen_eucalyptus = len(liste_instanztypen_eucalyptus)

            instance_types_liste = ""
            for i in range(laenge_liste_instanztypen_eucalyptus):
                if i == 0:
                  instance_types_liste = instance_types_liste + '<option selected="selected">'
                else:
                  instance_types_liste = instance_types_liste + "<option>"
                instance_types_liste = instance_types_liste + liste_instanztypen_eucalyptus[i]
                instance_types_liste = instance_types_liste + "</option>"

            instance_types_liste_laenge = laenge_liste_instanztypen_eucalyptus
          elif result.zugangstyp == "Nimbus":
            # Wenn es Nimbus ist
            instance_types_liste_laenge = 0
            liste_instanztypen_eucalyptus = []
            laenge_liste_instanztypen_eucalyptus = 0
            instance_types_liste = []
          else:
            # Wenn es Eucalyptus ist
            liste_instanztypen_eucalyptus = ["m1.small", "c1.medium", "m1.large", "m1.xlarge", "c1.xlarge"] 
            # Anzahl der Elemente in der Liste mit den Instanz-Typen
            laenge_liste_instanztypen_eucalyptus = len(liste_instanztypen_eucalyptus) 

            instance_types_liste = ""
            for i in range(laenge_liste_instanztypen_eucalyptus):
                if i == 0:
                  instance_types_liste = instance_types_liste + '<option selected="selected">'
                else:
                  instance_types_liste = instance_types_liste + "<option>"
                instance_types_liste = instance_types_liste + liste_instanztypen_eucalyptus[i]
                instance_types_liste = instance_types_liste + "</option>"

            instance_types_liste_laenge = laenge_liste_instanztypen_eucalyptus

          # Liste mit den Zonen
          liste_zonen = conn_region.get_all_zones()
          # Anzahl der Elemente in der Liste
          laenge_liste_zonen = len(liste_zonen)

          # Hier wird die Auswahlliste der Zonen erzeugt
          # Diese Auswahlliste ist zum Erzeugen neuer Volumes notwendig
          zonen_in_der_region = ''
          for i in range(laenge_liste_zonen):
              zonen_in_der_region = zonen_in_der_region + "<option>"
              zonen_in_der_region = zonen_in_der_region + liste_zonen[i].name
              zonen_in_der_region = zonen_in_der_region + "</option>"

          # Liste mit den Schlüsseln
          liste_key_pairs = conn_region.get_all_key_pairs()
          # Anzahl der Elemente in der Liste
          laenge_liste_keys = len(liste_key_pairs)

          keys_liste = ''
          if laenge_liste_keys == 0:
            if sprache == "de":
              keys_liste = '<font color="red">Es sind keine Schl&uuml in der Zone vorhanden</font>'
            else:
              keys_liste = '<font color="red">No keypairs exist inside this security zone</font>'
          elif laenge_liste_keys == 1:
            keys_liste = '<input name="keys_liste" type="text" size="70" maxlength="70" value="'
            keys_liste = keys_liste + liste_key_pairs[0].name
            keys_liste = keys_liste + '" readonly>'
          else:
            keys_liste = keys_liste + '<select name="keys_liste" size="'
            keys_liste = keys_liste + str(laenge_liste_keys)
            keys_liste = keys_liste + '">'
            for i in range(laenge_liste_keys):
              if i == 0:
                keys_liste = keys_liste + '<option selected="selected">'
              else:
                keys_liste = keys_liste + '<option>'
              keys_liste = keys_liste + liste_key_pairs[i].name
              keys_liste = keys_liste + '</option>'
            keys_liste = keys_liste + '</select>'

          if sprache == "de": keys_liste_anfang = "Schl&uuml;ssel"
          else:               keys_liste_anfang = "Keypair"

          if sprache == "de": number_instances_min_anfang = "Instanzen (min):"
          else:               number_instances_min_anfang = "Instances (min):"

          if sprache == "de": number_instances_max_anfang = "Instanzen (max):"
          else:               number_instances_max_anfang = "Instances (max):"

          if sprache == "de": typ_anfang = "Typ: "
          else:               typ_anfang = "Type: "

          if sprache == "de": image_starten_ueberschrift_anfang = "Image starten:"
          else:               image_starten_ueberschrift_anfang = "Start image:"

          if sprache == "de": value_button_image_starten = "Image starten"
          else:               value_button_image_starten = "start image"

          if sprache == "de": nicht_zwingend_notwendig = "Nicht zwingend notwendig"
          else:               nicht_zwingend_notwendig = "Not essential"

          if sprache == "de": zonen_anfang = "Verf&uuml;gbarkeitszone:"
          else:               zonen_anfang = "Availability Zone:"

          # Liste mit den Security Groups
          liste_security_groups = conn_region.get_all_security_groups()
          # Anzahl der Elemente in der Liste
          laenge_liste_security_groups = len(liste_security_groups)

          gruppen_liste = ''
          if laenge_liste_security_groups == 0:
            if sprache == "de":
              gruppen_liste = '<font color="red">Es sind keine Sicherheitsgruppen in der Zone vorhanden</font>'
            else:
              gruppen_liste = '<font color="red">No Security Groups exist inside this security zone</font>'
          elif laenge_liste_security_groups == 1:
            gruppen_liste = liste_security_groups[0].name
          else:
            gruppen_liste = gruppen_liste + '<select name="gruppen_liste" size="'
            gruppen_liste = gruppen_liste + str(laenge_liste_security_groups)
            gruppen_liste = gruppen_liste + '">'
            for i in range(laenge_liste_security_groups):
              if i == 0:
                gruppen_liste = gruppen_liste + '<option selected="selected">'
              else:
                gruppen_liste = gruppen_liste + '<option>'
              gruppen_liste = gruppen_liste + liste_security_groups[i].name
              #gruppen_liste = gruppen_liste + ' ('
              #gruppen_liste = gruppen_liste + liste_security_groups[i].owner_id
              #gruppen_liste = gruppen_liste + ')'
              gruppen_liste = gruppen_liste + '</option>'
            gruppen_liste = gruppen_liste + '</select>'

          imagetextfeld = '<input name="image_id" type="text" size="70" maxlength="70" value="'
          imagetextfeld = imagetextfeld + image
          imagetextfeld = imagetextfeld + '" readonly>'

          manifesttextfeld = '<input name="image_manifest" type="text" size="70" maxlength="70" value="'
          manifesttextfeld = manifesttextfeld + manifest
          manifesttextfeld = manifesttextfeld + '" readonly>'

          # Wenn es Amazon EC2 ist
          if result.aktivezone == "us-east-1" or result.aktivezone == "eu-west-1" or result.aktivezone == "us-west-1":
            if arch == "i386": # 32-Bit Image
              tabelle_ec2_instanztypen = '<table border="3" cellspacing="0" cellpadding="5">'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              if sprache == "de": # Wenn die Sprache Deutsch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Instanztyp</th>'
              else:               # Wenn die Sprache Englisch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Type</th>'
              if sprache == "de": # Wenn die Sprache Deutsch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Architektur</th>'
              else:               # Wenn die Sprache Englisch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Architecture</th>'
              if sprache == "de": # Wenn die Sprache Deutsch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Virtuelle Cores</th>'
              else:               # Wenn die Sprache Englisch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Virtual Cores</th>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>EC2 Compute Units</th>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td><tt>m1.small</tt></td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">32-Bit</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">1</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">1</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td><tt>c1.medium</tt></td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">32-Bit</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">2</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">5</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</table'
            elif arch == "x86_64": # 64-Bit Image
              tabelle_ec2_instanztypen = '<table border="3" cellspacing="0" cellpadding="5">'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              if sprache == "de": # Wenn die Sprache Deutsch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Instanztyp</th>'
              else:               # Wenn die Sprache Englisch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Type</th>'
              if sprache == "de": # Wenn die Sprache Deutsch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Architektur</th>'
              else:               # Wenn die Sprache Englisch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Architecture</th>'
              if sprache == "de": # Wenn die Sprache Deutsch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Virtuelle Cores</th>'
              else:               # Wenn die Sprache Englisch ist...
                tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>Virtual Cores</th>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<th>EC2 Compute Units</th>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td><tt>m1.large</tt></td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">64-Bit</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">2</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">4</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td><tt>m1.xlarge</tt></td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">64-Bit</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">4</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">8</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td><tt>m2.xlarge</tt></td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">64-Bit</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">2</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">6.5</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td><tt>m2.2xlarge</tt></td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">64-Bit</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">4</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">13</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td><tt>m2.4xlarge</tt></td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">64-Bit</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">8</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">26</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td><tt>c1.xlarge</tt></td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">64-Bit</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">8</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '<td align="center">20</td>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</tr>'
              tabelle_ec2_instanztypen = tabelle_ec2_instanztypen + '</table'
            else:
              # Wenn es etwas ganz anderes ist...?
              tabelle_ec2_instanztypen = ''
          else:
            # wenn es Eucalyptus ist
            tabelle_ec2_instanztypen = ''

          template_values = {
          'navigations_bar': navigations_bar,
          'url': url,
          'url_linktext': url_linktext,
          'zone': regionname,
          'zone_amazon': zone_amazon,
          'image': imagetextfeld,
          'manifest': manifesttextfeld,
          'instance_types_liste': instance_types_liste,
          'instance_types_liste_laenge': instance_types_liste_laenge,
          'keys_liste': keys_liste,
          'keys_liste_anfang': keys_liste_anfang,
          'gruppen_liste': gruppen_liste,
          'zonen_liste': zonen_liste,
          'number_instances_max_anfang': number_instances_max_anfang,
          'number_instances_min_anfang': number_instances_min_anfang,
          'typ_anfang': typ_anfang,
          'image_starten_ueberschrift_anfang': image_starten_ueberschrift_anfang,
          'value_button_image_starten': value_button_image_starten,
          'nicht_zwingend_notwendig': nicht_zwingend_notwendig,
          'tabelle_ec2_instanztypen':tabelle_ec2_instanztypen,
          'zonen_in_der_region': zonen_in_der_region,
          'laenge_liste_zonen': laenge_liste_zonen,
          'zonen_anfang': zonen_anfang,
          }

          path = os.path.join(os.path.dirname(__file__), "../templates", sprache, "image_starten.html")
          self.response.out.write(template.render(path,template_values))

