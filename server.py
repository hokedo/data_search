#!/usr/bin/env python

import os
import web
import urlparse

from utils import query_db

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
				with open("src/html/index.html") as resource:
					output = resource.read().strip()
			elif os.path.isfile(url_parts.path.strip("/")):
				with open(url_parts.path.strip("/")) as resource:
					output = resource.read().strip()
			else:
				web.ctx.status = "404"
		else:
			query = dict(urlparse.parse_qsl(url_parts.query))
			if query.get("q"):
				limit = query.get("limit", 100)
				output = query_db(query["q"], limit)

		return output

	def POST(self):
		return "POST WORKING!"


if __name__ == '__main__':
	app.run()
