#!/usr/bin/env python

import psycopg2
import psycopg2.extras

from math import cos, asin, sqrt

get_poi_query = "SELECT name, address, latitude, longitude, rating FROM data.poi"
get_adverts_query = "SELECT a.title, a.address, g.latitude, g.longitude FROM data.advert a JOIN data.geocoded g ON g.address = a.address WHERE a.address ~* %s"


def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))

def pgpass(host, user):
		"""
		Read the password, for the db connection, in the
		user's "pgpass" file located in the root of the
		home folder.
		"""
		pgpass_path = os.path.expanduser('~/.pgpass')
		with open(pgpass_path) as f:
			for line in f:
				host, port, _, user, passwd = line.split(':')
				if host == self.host and user == self.username:
					return passwd.strip()

		error_msg = "Could not find password for user {} is ~/.pgpass".format(self.username)
		raise ValueError(error_msg)

dbname = "auto_scraper"
user = "rw_ser"
port = 5432
host = "localhost"
passsword = pgpass(host, user)
connection = psycopg2.connect(
							dbname=dbname,
							user=user,
							password=password,
							host=host,
							port=port
							)
cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
self.connection.close()