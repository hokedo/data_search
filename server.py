#!/usr/bin/env python

import os
import web
import urlparse

from utils import query_db
from utils import get_all_pois

urls = ('/.*', 'Server')
app = web.application(urls, globals())


class Server(object):
	def GET(self):
		output = ""
		web.ctx.status = "200"
		request_url = web.ctx.env.get("REQUEST_URI")
		url_parts = urlparse.urlparse(request_url)

		if not url_parts.query:
			if url_parts.path == "/":
				with open("index.html") as resource:
					output = resource.read().strip()
			elif os.path.isfile(url_parts.path.strip("/")):
				with open(url_parts.path.strip("/")) as resource:
					output = resource.read().strip()
			else:
				web.ctx.status = "404"
		else:
			query = dict(urlparse.parse_qsl(url_parts.query))
			if query.get("q"):
				q = query["q"] if query["q"] != "*" else ""
				limit = query.get("limit", 100)
				price_min = query.get("price_min", 0)
				price_max = query.get("price_max", 1000)
				interest_poi_id = int(query.get("poi_id", 0)) or None
				output = query_db(q, price_min, price_max, limit, interest_poi_id)
			elif query.get("all_pois"):
				output = get_all_pois()

		return output

	def POST(self):
		return "POST WORKING!"


if __name__ == '__main__':
	app.run()
