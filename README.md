# Scraper CDRE

Scraper for http://cdre.ons.org.br/ website.

## Getting Started

### Prerequisites

* Python >=3.6.3
* Webdriver: [Gecko](https://github.com/mozilla/geckodriver/releases)

### Installing

It´s recommanded that project gets installed in virtualenv. The easiest way is probabbly via [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/). However it is not required.

Clone repo.

Install requirements.

```
pip install -r requirements.txt
```

Setup environment variables.

* **SCDRE_USR**             - Usrname to use on login.
* **SCDRE_PWD**             - Password to use on login.
* **SCDRE_URL**             - Absolute URL to website.
* **SCDRE_EMAIL_USR**       - Email username to send notification from & to.
* **SCDRE_EMAIL_PWD**       - Email password to use.
* **SCDRE_EMAIL_PORT**      - Email port to use.
* **SCDRE_EMAIL_HOST**      - Email host to use.
* **SCDRE_FIREFOX_PROFILE** - Absolute path to firefox profile folder.
* **SCDRE_INSTANCE_PATH**   - Application working folder.

Make sure your browser downloads are always saved into instance folder of this project.

Download files.

```
python scraper.py downlaod-files
```

Start checking for changes in web directory.

```
python scraper.py check-state
```

## Authors

Initial content for this project was provided by Matic Zagmajster. For more information please see ```AUTHORS``` file.

## License

See the ```LICENSE``` file for details.
