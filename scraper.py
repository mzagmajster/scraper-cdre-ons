from time import sleep
import click

from cdrescraper import get_config, FileDownloader, ROOT_DIRS, send_notification, WebDirectoryLister, URL_TO_WATCH


@click.group()
def cli():
	pass


@click.command('download-files', help="Download files.")
def download_files():
	conf = get_config()
	o = FileDownloader(conf)
	o.login()
	for  d in ROOT_DIRS:
		o.list(d, 0)
		# Wait for downloading process to complete.
		print('Waiting for downloads to complete.')
		sleep(7)
		self.move_files()

	o.statistics()



@click.command('check-state', help="Check for change in web directory.")
def check_state():
	conf = get_config()
	# More configuration.
	conf['_URL_TO_WATCH'] = URL_TO_WATCH

	# Get browser cookies so we can login when we are using requests package.
	lo = FileDownloader(conf)
	lo.login()
	conf['_COOKIES'] = lo.get_cookies()

	o = WebDirectoryLister(conf)
	quit = False
	print('Press CTRL + C to quit.')
	while not quit:
		try:
			o.read()
			if o.compare() == 1:
				# Update & notify.
				o.save()
				send_notification(conf)
			sleep(3)  # Do we really need to update so frequently?
		except KeyboardInterrupt:
			quit = True

	lo.spobj.quit()

@click.command('test')
def test():
	conf = get_config()
	send_notification(conf)


cli.add_command(download_files)
cli.add_command(check_state)
cli.add_command(test)

if __name__ == '__main__':
	cli()

