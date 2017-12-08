from os import environ, listdir, makedirs
from os.path import isfile, abspath, dirname, exists
from shutil import move
from datetime import datetime

import requests
from mailer import Mailer, Message

from minsplinter import MinSplinter

# Files to download.
ROOT_DIRS = [
	"https://cdre.ons.org.br/CDRE%20%20Processo%20Relatrio%20Dirio%20da%20Situao%20HidrulicoH/Forms/AllItems.aspx",
	"https://cdre.ons.org.br/CDRE%20%20Processo%20ACOMPH%20%20Acompanhamento%20Hidrolgico/Forms/AllItems.aspx"
]

# URL to watch (send notification on detected change).
URL_TO_WATCH = 'https://agentes.ons.org.br/publicacao/PrevisaoVazoes/preliminar/'

# List of application files. 
APPLICATION_FILES = [
	'__init__',
	'web-dirs',
	'notification.html'
]

# User agents to use (currently script chooses the first user-agent in list but that could be easily changed in WebDirectoryLister class).
USER_AGENTS = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"
]


MONTHS = [
	'JANEIRO',
	'FEVEREIRO',
	'MARCO',
	'ABRIL',
	'MAIO',
	'JUNHO',
	'JULHO',
	'AGOSTO',
	'SETEMBRO',
	'OUTUBRO',
	'NOVEMBRO',
	'DEZEMBRO'
]


def get_config():
	"""dict: Get config.
		Load configuration
	"""
	instance_path = abspath(dirname(__file__)) + '/../instance'
	instance_path = instance_path.replace('\\', '/')

	c = {
		'SCDRE_USR': environ['SCDRE_USR'],
		'SCDRE_PWD': environ['SCDRE_PWD'],
		'SCDRE_URL': environ['SCDRE_URL'],
		'SCDRE_EMAIL_USR': environ['SCDRE_EMAIL_USR'],
		'SCDRE_EMAIL_PWD': environ['SCDRE_EMAIL_PWD'],
		'SCDRE_EMAIL_PORT': int(environ['SCDRE_EMAIL_PORT']),
		'SCDRE_EMAIL_HOST': environ['SCDRE_EMAIL_HOST'],
		'SCDRE_FIREFOX_PROFILE': environ['SCDRE_FIREFOX_PROFILE'],
		'SCDRE_INSTANCE_PATH': instance_path
	}
	return c


def send_notification(mail_config):
	"""None: Send notification
		Notify about chagne in web directory for current month via email.
	"""
	message = Message(
		From=mail_config['SCDRE_EMAIL_USR'],
		To=mail_config['SCDRE_EMAIL_USR'],
		charset="utf-8"
	)
	message.Subject = "Web directory has changed"

	content = ''
	p = mail_config['SCDRE_INSTANCE_PATH'] + '/' + 'notification.html'
	with open(p, 'r') as fp:
		content = fp.read()

	message.Html = content

	use_ssl = False
	use_tls = False

	if mail_config['SCDRE_EMAIL_PORT'] == 587:
		use_tls = True
	elif mail_config['SCDRE_EMAIL_PORT'] == 465:
		use_ssl = True

	sender = Mailer(
		mail_config['SCDRE_EMAIL_HOST'],
		mail_config['SCDRE_EMAIL_PORT'],
		usr=mail_config['SCDRE_EMAIL_USR'],
		pwd=mail_config['SCDRE_EMAIL_PWD'],
		use_ssl=use_ssl,
		use_tls=use_tls
	)

	sender.send(message)


class FileDownloader(object):
	def __init__(self, c):
		"""Initializer"""
		self.config = dict(c)
		spobj_conf = {
			'DRIVER_NAME': 'firefox',
			'PROFILE': self.config['SCDRE_FIREFOX_PROFILE'],
			'USER_AGENT': USER_AGENTS[0]
		}
		self.spobj = MinSplinter(spobj_conf)
		self._file = ''
		self._count = 0
		self._relevant_dir = ''

	def login(self):
		"""None: Login
			Login to webstie to access resources.
		"""
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

	def get_cookies(self):
		"""dict: Get cookies
			Get browser cookies so we can use them with requests package.
		"""
		return self.spobj.browser.cookies.all()

	def is_file(self, link):
		"""bool: Is file
			Naive but useful way of determinig  if specific link points to file or not,

			Rwturns:
				bool: True if given link is file, False otherwise.
		"""
		allowed_extensions = ['zip', 'xls', 'xlsx', 'rar']

		for e in allowed_extensions:
			if link.endswith(('.' + e)):
				return True

		return False

	def list(self, link, level):
		"""None: List
			List all items in directory and all subdirectories.
		 """
		self.spobj.visit(link)
		self.spobj.wait()

		# Initial selector.
		s = '#onetidDoclibViewTbl0 > tbody > tr'
		el = self.spobj.find_elements('css', s)

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
			else:
				next_page = False

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
		"""None: Move files
			Move local files to correct sub-directory to prevent trubles because of same names on diffrent files.
		"""

		# Forbidden files.
		f = APPLICATION_FILES
		d = self.config['SCDRE_INSTANCE_PATH'] + '/' + self._relevant_dir
		for file in listdir(self.config['SCDRE_INSTANCE_PATH']):
			# File must not be moved or already exists.
			if file in f or exists('/'.join([d, file])):
				continue

			p = self.config['SCDRE_INSTANCE_PATH'] + '/' + file
			if isfile(p):
				move(p, d)

	def statistics():
		"""None: Statistics"""
		print(self._count, ' files downloaded.')


class WebDirectoryLister(object):
	def _get_web_dir_file(self):
		"""str: Get web dir file.
			Get absolute path of 'web-dirs' file.
		 """
		return '/'.join([self.config['SCDRE_INSTANCE_PATH'], self._web_dirs_file])

	def __init__(self, c):
		"""Initializer"""
		self.config = dict(c)
		self._web_dirs_file = 'web-dirs'
		self._text = ''

	def read(self):
		"""int: Read content of web directory.
			
			Returns:
				int: On usccessful read 0 is returned, 1 is returned otherwise.
		"""
		# Get into proper subfolder.
		d = datetime.now()
		y = str(d.year)
		m = str(d.month)
		if len(m) < 2:
			m = '0' + m
		nm = m + '_' + MONTHS[d.month - 1]
		url = self.config['_URL_TO_WATCH'] + '{0}/{1}/'.format(y, nm)

		h = {'user-agent': USER_AGENTS[0]}
		r = requests.get(url, headers=h, cookies=self.config['_COOKIES'])
		if r.status_code != 200:
			return 1

		r.encoding = 'UTF-8'
		self._text = r.text
		return 0

	def compare(self):
		"""int: Compare.
			Compare fresh content form web with content from local file.

			Rwturns:
				int: If chagne has been detected 1 is returned, otherwise 0 is returned.
		 """
		if not exists(self._get_web_dir_file()):
			self.save()

		with open(self._get_web_dir_file(), 'r', encoding='utf8') as fp:
			prev_text = fp.read()
			if len(prev_text) != len(self._text):
				return 1
		return 0

	def save(self):
		"""None: Save
			Save content from web to local file.
		"""
		fp = open(self._get_web_dir_file(), 'w')
		fp.write(self._text)
		fp.close()


