import click

from cdrescraper import get_config, FileDownloader, ROOT_DIRS


@click.group()
def cli():
	pass


@click.command('download-files', help="Download files.")
def download_files():
	conf = get_config()
	o = FileDownloader(conf)
	o.login()
	for  d in ROOT_DIRS:
		o.list(d)

	o.statistics()



@click.command('check-state', help="Checlk for change in web directory.")
def check_state():
	pass


cli.add_command(download_files)
cli.add_command(check_state)

if __name__ == '__main__':
	cli()

