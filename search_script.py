#!/usr/bin/env python

import os
import json
import psycopg2
import psycopg2.extras

from operator import itemgetter
from math import cos, asin, sqrt
from argparse import ArgumentParser

get_poi_query = "SELECT name, address, latitude, longitude, rating FROM data.poi"
with open("get_adverts.sql") as get_adverts_query_path:
	get_adverts_query = get_adverts_query_path.read().strip()

with open("get_top_5.sql") as get_top_query_path:
	get_top_5_query = get_top_query_path.read().strip()

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

cursor.execute(get_adverts_query, keyword)
data = [dict(item) for item in cursor.fetchall()]

for apartment in data:
	address_id = apartment["address_id"]
	cursor.execute(get_top_5_query, [address_id])
	top_5_schools = [dict(item) for item in cursor.fetchall()]
	apartment["top_5"] = top_5_schools

connection.close()

print json.dumps(data)


