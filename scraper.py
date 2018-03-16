from time import sleep
from pyvirtualdisplay import Display
import click

from cdrescraper import get_config, FileDownloader, ROOT_DIRS, send_notification, WebDirectoryLister, URL_TO_WATCH

from os import makedirs

@click.group()
def cli():
	pass


@click.command('download-files', help="Download files.")
def download_files():
	display = Display(visible=0, size=(1680, 1050))
	display.start()
	conf = get_config()

	if not len(conf.keys()):
		print('Please make sure file "settings.json" exists and it is properly configured.')
		return None

	o = FileDownloader(conf)
	o.login()
	for  d in ROOT_DIRS:
		o.list(d, 0)
		# Wait for downloading process to complete.
		print('Waiting for downloads to complete.')
		sleep(7)
		o.move_files()

	o.statistics()
	display.stop()


@click.command('check-state', help="Check for change in web directory.")
def check_state():
	conf = get_config()

	if not len(conf.keys()):
		print('Please make sure file "settings.json" exists and it is properly configured.')
		return None

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


@click.command('download-watch')
def download_watch():
	display = Display(visible=0, size=(1680, 1050))
	display.start()
	conf = get_config()

	if not len(conf.keys()):
		print('Please make sure file "settings.json" exists and it is properly configured.')
		return None

	conf['_URL_TO_WATCH'] = URL_TO_WATCH

	# Authenticate,
	lo = FileDownloader(conf)
	lo.login()

	# Now create web lister to download stuff.
	wl = WebDirectoryLister(conf, lo.spobj)

	dirs = wl.list()
	for link in dirs:
		base_dir = wl.list(link)
		print('Downloaded the files.')
		wl.move_files(base_dir)
		print('Moved the files to ' + base_dir)

	wl.spobj.quit()
	display.stop()


@click.command('test')
def test():
	conf = get_config()

	if not len(conf.keys()):
		print('Please make sure file "settings.json" exists and it is properly configured.')
		return None

	send_notification(conf)


@click.command('test2')
def test2():
	pass

cli.add_command(download_files)
cli.add_command(check_state)
cli.add_command(download_watch)
cli.add_command(test)
cli.add_command(test2)

if __name__ == '__main__':
	cli()

