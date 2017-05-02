#!/usr/bin/env python

import os
import sys
import json
import logging
import urlparse
import psycopg2
import requests
import traceback
import psycopg2.extras

from urllib import urlencode
from datetime import datetime
from datetime import timedelta
from operator import itemgetter
from math import cos, asin, sqrt
from argparse import ArgumentParser


def distance(lat1, lon1, lat2, lon2):
	p = 0.017453292519943295
	a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
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


def tomorrow_ms():
	# Create tomorrow's date for noon
	date = datetime.now()
	date = date.replace(hour=13, minute=0)
	date = date + timedelta(days=1)
	return int((date - datetime(1970, 1, 1)).total_seconds())


def get_connection_cursor():
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
	return connection, cursor


def query_db(keyword, price_min, price_max, limit=100, interest_poi_id=None):
	con, cursor = get_connection_cursor()
	data = []
	try:
		with open("src/sql/get_adverts.sql") as get_adverts_query_path:
			get_adverts_query = get_adverts_query_path.read().strip()

		with open("src/sql/get_top_5.sql") as get_top_query_path:
			get_top_5_query = get_top_query_path.read().strip()

		with open("src/sql/get_adverts_poi_bias.sql") as get_adverts_query_path:
			get_adverts_poi_bias_query = get_adverts_query_path.read().strip()

		if interest_poi_id and interest_poi_id > -1:
			cursor.execute(get_adverts_poi_bias_query, [keyword, price_min, price_max, interest_poi_id, limit])
		else:
			cursor.execute(get_adverts_query, [keyword, price_min, price_max, limit])

		data = [dict(item) for item in cursor.fetchall()]
		for apartment in data:
			address_id = apartment["address_id"]
			cursor.execute(get_top_5_query, [address_id])
			top_5_schools = [dict(item) for item in cursor.fetchall()]
			apartment["top_5"] = top_5_schools

	finally:
		con.close()

	return json.dumps(data)

def get_all_pois():
	con, cursor = get_connection_cursor()
	data = []
	try:
		with open("src/sql/get_all_poi.sql") as get_pois_query_path:
			get_pois_query = get_pois_query_path.read().strip()

		cursor.execute(get_pois_query)
		data = [dict(item) for item in cursor.fetchall()]

	finally:
		con.close()

	return json.dumps(data)
