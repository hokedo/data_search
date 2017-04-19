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

def get_args():
	argp = ArgumentParser(__doc__)
	argp.add_argument(
		"--address",
		help="Address to search apartments for",
		default="Marasti"
		)
	argp.add_argument(
		"--key",
		help="Google Directions API key"
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

def tomorrow_ms():
	# Create tomorrow's date for noon
	date = datetime.now()
	date = date.replace(hour=13, minute=0)
	date = date + timedelta(days=1)
	return int((date - datetime(1970, 1, 1)).total_seconds())
	

if __name__ == "__main__":
	args = get_args()
	
	logging.basicConfig()
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

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

	try:
		if args.get("key"):
			insert_poi_dist_query = "UPDATE data.poi_distance SET distance = %s, instructions = %s WHERE poi_id = %s AND address_id = %s"
			get_poi_query = "SELECT id, latitude, longitude FROM data.poi"
			get_adresses_query = "SELECT id, address, latitude, longitude FROM data.geocoded"
			directions_api = "https://maps.googleapis.com/maps/api/directions/json"
			url_parts = list(urlparse.urlparse(directions_api))

			direction_params = {
				"mode": "transit",
				"transit_mode": "bus",
				"key": args["key"],
				"departure_time": tomorrow_ms()
			}
			cursor.execute(get_poi_query)
			pois = [dict(poi) for poi in cursor.fetchall()]

			cursor.execute(get_adresses_query)
			for address in cursor.fetchall():
				address = dict(address)
				for poi in pois:
					direction_params["origin"] = "{},{}".format(address["latitude"], address["longitude"])
					direction_params["destination"] = "{},{}".format(poi["latitude"], poi["longitude"])

					url_parts[4] = urlencode(direction_params)
					request_url = urlparse.urlunparse(url_parts)
					logger.info(request_url)

					api_response = requests.get(request_url)
					api_data = json.loads(api_response.text)

					data = {
						"walking_time": 0,
						"walking_distance": 0,
						"bus_time": 0,
						"bus_distance": 0,
						"buses": []
					}

					route = api_data.get("routes", [{}])[0]
					distance = route.get("legs", [{}])[0]["distance"]["value"]

					for step in route.get("legs", [{}])[0].get("steps", []):

						if step["travel_mode"] == "WALKING":
							data["walking_time"] += step["duration"]["value"]
							data["walking_distance"] += step["distance"]["value"]

						elif step["travel_mode"] == "TRANSIT":
							data["buses"].append(step["transit_details"]["line"]["short_name"])
							data["bus_time"] += step["duration"]["value"]
							data["bus_distance"] += step["distance"]["value"]

					if any(data.values()):
						str_data = json.dumps(data)
						logger.info(str_data)
						logger.info(poi["id"])
						logger.info(address["id"])
						cursor.execute(insert_poi_dist_query, [distance, str_data, poi["id"], address["id"]])
						connection.commit()


		else:
			with open("get_addresss.sql") as get_addresss_query_path:
				get_addresss_query = get_addresss_query_path.read().strip()

			with open("get_top_5.sql") as get_top_query_path:
				get_top_5_query = get_top_query_path.read().strip()

			keyword = [args["address"]]

			cursor.execute(get_addresss_query, keyword)
			data = [dict(item) for item in cursor.fetchall()]

			for apartment in data:
				address_id = apartment["address_id"]
				cursor.execute(get_top_5_query, [address_id])
				top_5_schools = [dict(item) for item in cursor.fetchall()]
				apartment["top_5"] = top_5_schools

			print json.dumps(data)
	except Exception as e:
		traceback.print_exc(file=sys.stderr)
		print e
	finally:
		connection.close()


