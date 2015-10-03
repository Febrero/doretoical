# -*- coding: utf-8 -*-

import pytz
import re
import requests
import sys
from urlparse import urljoin, urlparse
from os.path import basename
import datetime
import os
from icalendar import Calendar, Event
import datetime
import yaml
import bs4

_pdfs = list()
_json = list()
txt = re.compile("(Abri|Programa|programaci|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)", re.IGNORECASE)
pdf = re.compile(".*(Programa|PrograDore|programDore).*\\.pdf$", re.IGNORECASE)

cal = Calendar()
cal.add('version', '2.0')
cal.add('prodid', u'-//Cine Doré//github.com santos82 doredb//ES')
cal.add('X-WR-CALNAME','Cine Dore')
cal.add('x-wr-timezone', 'Europe/Madrid')
location='Calle de Santa Isabel, 3, 28012 Madrid, España'
madrid_tz = pytz.timezone("Europe/Madrid")


def _getPdfs(url):
	page = requests.get(url)
	soup = bs4.BeautifulSoup(page.text,"lxml")
	links = soup.select("#info a")
	for l in links:
		t = l.get_text().strip()
		if l is not None and txt.match(t) and l.attrs.get('href').endswith('.pdf'):
			u = urljoin(url, l.attrs.get('href'))
			n = basename(urlparse(u).path)
			if pdf.match(n):
				_pdfs.append(u)
	if len(_pdfs) == 0:
		raise Exception('Programas no encontrados')

# ar == -1 <- Último programa
# ar == 0 <- Todos los programas de la última hoja
# ar == 1 <- Todos los programas
# ar > 2000 <- Los programas del año pasado por parametro
def getPdfs(ar):
	if ar == -1 or ar == 0 or ar == 1:
		_getPdfs('http://www.mecd.gob.es/cultura-mecd/areas-cultura/cine/mc/fe/cine-dore/programacion.html')
		if ar == -1:
			del _pdfs[1:]
			return _pdfs

	p = "http://www.mecd.gob.es/cultura-mecd/areas-cultura/cine/mc/fe/cine-dore/programacion/%s.html"

	if ar == 1:
		y = 2005
		year = datetime.datetime.now().year
		while y <= year:
			u = p % (str(y))
			_getPdfs(u)
			y += 1
	if ar > 2000:
		u = p % (ar)
		_getPdfs(u)
	return _pdfs

def _fillCal(url):
	f = os.popen("curl -s \"" + url + "\" | pdftotext - - | awk -f dore.awk")
	docs = yaml.load_all(f)
	for o in docs:
		i=datetime.datetime.strptime(o['inicio'], "%Y-%m-%d %H:%M")
		event = Event()
		event.add('summary', o[u'título'])
		event.add('dtstart', i)
		event.add('location', location)
		event.add('uid',i.strftime("%y%m%d%M%H")+"_"+o['sala']+"_dore")
		if o[u'duración']:
			f=i + datetime.timedelta(minutes = int(o[u'duración']))
			event.add('dtend', f)
		if o['nota']:
			event.add('DESCRIPTION',"Sala " + o['sala'] + " - " + o['nota']+"\n\nFuente: "+url)

		cal.add_component(event)

def run(ar):
	getPdfs(ar)
	for pdf in _pdfs:
		_fillCal(pdf)

if __name__ == "__main__":
	ar = -1
	if len(sys.argv) <= 1:
		run(-1)
	else:
		if sys.argv[1].isdigit():
			run(sys.argv[1])
		else:
			_fillCal(sys.argv[1])
	f = open('dore.ics', 'wb')
	f.write(cal.to_ical())
	f.close()

