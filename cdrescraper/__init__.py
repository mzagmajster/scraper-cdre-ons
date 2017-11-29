from os import environ

from minsplinter import MinSplinter


ROOT_DIRS = [
	"https://cdre.ons.org.br/CDRE%20%20Processo%20ACOMPH%20%20Acompanhamento%20Hidrolgico/Forms/AllItems.aspx",
	"https://cdre.ons.org.br/CDRE%20%20Processo%20Relatrio%20Dirio%20da%20Situao%20HidrulicoH/Forms/AllItems.aspx"

]

def get_config():
	c = {
		'SCDRE_USR': environ['SCDRE_USR'],
		'SCDRE_PWD': environ['SCDRE_PWD'],
		'SCDRE_URL': environ['SCDRE_URL'],
		'SCDRE_FIREFOX_PROFILE': environ['SCDRE_FIREFOX_PROFILE']
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
		self.fdobj = MinSplinter(spobj_conf)
		self._file = ''
		self._count = 0

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


	def list(self, link):
		self.spobj.visit(link)
		self.spobj.wait()

		# Initial selector.
		s = '#onetidDoclibViewTbl0 > tbody > tr'
		el = self.spobj.find_elements('css', s)
		print('el ', len(el))

		i = 0
		h = ''
		text = ''
		dirs = list()

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
			# print('is_file ', self.is_file(h), ' --> ', text, ' --> ', h)
			i += 1

		# print('dirs ', dirs)
		# Iterate over other directories.
		for d in dirs:
			self.list(d)

	def statistics():
		print(self._count, ' files downloaded.')



