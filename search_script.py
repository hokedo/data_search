#!/usr/bin/env python

import os
import json
import psycopg2
import psycopg2.extras

from operator import itemgetter
from math import cos, asin, sqrt
from argparse import ArgumentParser

get_poi_query = "SELECT name, address, latitude, longitude, rating FROM data.poi"
get_adverts_query = "SELECT a.title, a.address, a.url, g.latitude, g.longitude FROM data.advert a JOIN data.geocoded g ON g.address = a.address WHERE a.address ~* %s"

def get_args():
	argp = ArgumentParser(__doc__)
	argp.add_argument(
		"--address",
		help="Address to search apartments for",
		default="Marasti"
		)

	args = vars(argp.parse_args())
	return args


def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))

def pgpass(h, username):
		"""
		Read the password, for the db connection, in the
		user's "pgpass" file located in the root of the
		home folder.
		"""
		pgpass_path = os.path.expanduser('~/.pgpass')
		with open(pgpass_path) as f:
			for line in f:
				host, port, _, user, passwd = line.split(':')
				if host == h and user == username:
					return passwd.strip()

		error_msg = "Could not find password for user {} is ~/.pgpass".format(username)
		raise ValueError(error_msg)

dbname = "auto_scraper"
user = "rw_user"
port = 5432
host = "localhost"
password = pgpass(host, user)
connection = psycopg2.connect(
							dbname=dbname,
							user=user,
							password=password,
							host=host,
							port=port
							)
cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

args = get_args()
keyword = [args["address"]]

cursor.execute(get_poi_query)
poi = [dict(item) for item in cursor.fetchall()]
cursor.execute(get_adverts_query, keyword)
data = [dict(item) for item in cursor.fetchall()]
connection.close()

for apartment in data:
	schools = []
	for school in poi:
		d = distance(
			apartment["latitude"],
			apartment["longitude"],
			school["latitude"],
			school["longitude"]
			)
		school["distance"] = d
		schools.append(school)
	# get top 5 nearest schools
	apartment["schools"] = sorted(
							schools,
							key=itemgetter("distance"),
							reverse=False
							)[:5]


print json.dumps(data)


