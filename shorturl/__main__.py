import gunicorn.app.wsgiapp
import os, sys
from shorturl.utils.config import server_conf

class SiteManager:

	def run_server(self) -> None:
		"""Prepare and run the web server."""

		print("Starting server.")

		port = server_conf.port

		# Patch the arguments for gunicorn
		sys.argv = [
			"gunicorn",
			"--preload",
			"-b", f"{server_conf.hostname}:{port}",
			"shorturl.server.wsgi:application",
			"--threads", f"{server_conf.threads}",
			"-w", f"{server_conf.workers}",
			"--max-requests", "1000",
			"--max-requests-jitter", "50",
		]

		# Run gunicorn for the production server.
		gunicorn.app.wsgiapp.run()


def main() -> None:
    SiteManager().run_server()


if __name__ == '__main__':
    main()