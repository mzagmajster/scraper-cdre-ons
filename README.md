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
* **SCDRE_FIREFOX_PROFILE** - Absolute path to firefox profile folder.

Make sure your browser downloads are always saved into instance folder of this project.

Download files.

```
python scraper.py downlaod-files
```

## Authors

Initial content for this project was provided by Matic Zagmajster. For more information please see ```AUTHORS``` file.

## License

See the ```LICENSE.md``` file for details.
