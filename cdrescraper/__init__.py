from os import environ, listdir, makedirs
from os.path import isfile, abspath, dirname, exists
from shutil import move

from minsplinter import MinSplinter


ROOT_DIRS = [
	"https://cdre.ons.org.br/CDRE%20%20Processo%20Relatrio%20Dirio%20da%20Situao%20HidrulicoH/Forms/AllItems.aspx",
	"https://cdre.ons.org.br/CDRE%20%20Processo%20ACOMPH%20%20Acompanhamento%20Hidrolgico/Forms/AllItems.aspx"

]

def get_config():
	instance_path = abspath(dirname(__file__)) + '/../instance'
	instance_path = instance_path.replace('\\', '/')

	c = {
		'SCDRE_USR': environ['SCDRE_USR'],
		'SCDRE_PWD': environ['SCDRE_PWD'],
		'SCDRE_URL': environ['SCDRE_URL'],
		'SCDRE_FIREFOX_PROFILE': environ['SCDRE_FIREFOX_PROFILE'],
		'SCDRE_INSTANCE_PATH': instance_path,
	}
	return c


class FileDownloader(object):
	def __init__(self, c):
		self.config = dict(c)
		spobj_conf = {
			'DRIVER_NAME': 'firefox',
			'PROFILE': self.config['SCDRE_FIREFOX_PROFILE']
		}
		self.spobj = MinSplinter(spobj_conf)
		self._file = ''
		self._count = 0
		self._relevant_dir = ''

	def login(self):
		self.spobj.visit(self.config['SCDRE_URL'])
		self.spobj.wait()

		s = 'username'
		elist = self.spobj.find_elements('id', s)

		# User already loggged in.
		if not len(elist):
			return None

		elist[0].fill(self.config['SCDRE_USR'])

		s = 'password'
		elist = self.spobj.find_elements('id', s)
		elist[0].fill(self.config['SCDRE_PWD'])

		s = 'submit.Signin'
		elist = self.spobj.find_elements('name', s)
		elist[0].click()

		self.spobj.wait()

	def is_file(self, link):
		allowed_extensions = ['zip', 'xls', 'xlsx', 'rar']

		for e in allowed_extensions:
			if link.endswith(('.' + e)):
				return True

		return False

	def list(self, link, level):
		self.spobj.visit(link)
		self.spobj.wait()

		# Initial selector.
		s = '#onetidDoclibViewTbl0 > tbody > tr'
		el = self.spobj.find_elements('css', s)
		# print('el ', len(el))

		i = 0
		h = ''
		text = ''
		dirs = list()
		dir_names = list()
		next_page = True

		while next_page:
			# Get file link.
			s2 = 'td:nth-child(3) a'
			while i < len(el):
				el2 = self.spobj.find_elements('css', s2, el[i])
				try:
					text = el2[0].text
					h = el2[0]['href']
				except KeyError:
					text = ''
					h = ''
				finally:
					if self.is_file(h):
						el2[0].click()
						self._count += 1
					else:
						dirs.append(h)
						dir_names.append(text)
						
				# print('is_file ', self.is_file(h), ' --> ', text, ' --> ', h)
				i += 1

			# Check if next page exists.
			s3 = '#pagingWPQ2next > a'
			el3 = self.spobj.find_elements('css', s3)
			if len(el3):
				# Ensure that we trigger click.
				h = self.spobj.browser.html
				while h == self.spobj.browser.html:
					el3[0].click()
					el3[0].mouse_over()
					h = self.spobj.browser.html

		# print('dirs ', dir_names)
		# We need to create directories on first lavel for proper file grouping.
		if not level and len(dir_names):
			p = self.config['SCDRE_INSTANCE_PATH'] + '/' + dir_names[0]
			
			if not exists(p):
				makedirs(p)

			self._relevant_dir = dir_names[0]

		# Iterate over other directories.
		j = 0
		while j < len(dirs):
			level += 1
			self.list(dirs[j], level)
			j += 1 

	def move_files(self):
		# Forbidden files.
		f = ['__init__']
		d = self.config['SCDRE_INSTANCE_PATH'] + '/' + self._relevant_dir
		for file in listdir(self.config['SCDRE_INSTANCE_PATH']):
			# File must not be moved or already exists.
			if file in f or exists('/'.join([d, file])):
				continue

			p = self.config['SCDRE_INSTANCE_PATH'] + '/' + file
			if isfile(p):
				move(p, d)

	def statistics():
		print(self._count, ' files downloaded.')



