from time import sleep
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
		o.list(d, 0)
		# Wait for downloading process to complete.
		print('Waiting for downloads to complete.')
		sleep(7)
		self.move_files()

	o.statistics()



@click.command('check-state', help="Checlk for change in web directory.")
def check_state():
	pass


@click.command('test')
def test():
	conf = get_config()
	print(conf)
	"""o = FileDownloader(conf)
	o.login()
	d = 'https://cdre.ons.org.br/CDRE%20%20Processo%20Relatrio%20Dirio%20da%20Situao%20HidrulicoH/Forms/AllItems.aspx?RootFolder=%2FCDRE%20%20Processo%20Relatrio%20Dirio%20da%20Situao%20HidrulicoH%2FRDH%5F2014%2F01%5FJaneiro&FolderCTID=0x0120000A691184EC3EB3468DDF9C6B199E5B58&View=%7BDCD6C8DB%2DC1DB%2D4BF7%2DB375%2D39FA66E4AB70%7D'
	o.list(d, 0)
	o.statistics()"""



cli.add_command(download_files)
cli.add_command(check_state)
cli.add_command(test)

if __name__ == '__main__':
	cli()

