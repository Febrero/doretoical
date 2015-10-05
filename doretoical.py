# -*- coding: utf-8 -*-
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
import os.path
import glob
import sys
import traceback
import httplib

_prog = list()
_pdfs = list()
_docs = list()
txt = re.compile("(Abri|Programa|programaci|enero|febrero|marzo|abril|mayo|Mayoe|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)", re.IGNORECASE)
pdf = re.compile(".*(Programa|PrograDore|programDore).*\\.(pdf|doc)$", re.IGNORECASE)

FULL='dore.ics'
CALDIR='ics/'
YMLDIR='yaml/'
LOCATION='Calle de Santa Isabel, 3, 28012 Madrid, España'

def exists(url):
	try:
		u=urlparse(url)
		conn = httplib.HTTPConnection(u.netloc)
		conn.request('HEAD', u.path)
		response = conn.getresponse()
		conn.close()
		if response.status in (200, 301, 302):
			return True
		sys.stderr.write("NOT CONNECT (" +str(response.status) + ") "+ url+"\n")
	except Exception,e:
		sys.stderr.write("NOT CONNECT ("+str(e)+") "+ url+"\n")

	return False

def create(programa):
	_cal = Calendar()
	_cal.add('version', '2.0')
	_cal.add('prodid', u'-//Cine Doré//github.com santos82 doredb//ES')
	_cal.add('X-WR-CALNAME','Cine Dore')
	_cal.add('x-wr-timezone', 'Europe/Madrid')
	return _cal

def _collect(url):
	ct=0;
	page = requests.get(url)
	soup = bs4.BeautifulSoup(page.text,"lxml")
	links = soup.select("#info a")
	for l in links:
		t = l.get_text().strip()
		if l is not None and txt.match(t) and l.attrs.get('href'):
			u = urljoin(url, l.attrs.get('href'))
			n = basename(urlparse(u).path)
			if pdf.match(n):
				ct=ct+1
				if n.endswith('.pdf'):
					_pdfs.append(u)
				elif n.endswith('.doc') or n.endswith('.docx'):
					_docs.append(u)
	if ct == 0:
		sys.stderr.write("DATA NOT FOUND in "+ url+"\n")

# ar == -1 <- Último programa
# ar == 0 <- Todos los programas de la última hoja
# ar == 1 <- Todos los programas
# ar > 2000 <- Los programas del año pasado por parametro
def collect(ar):
	if ar == -1 or ar == 0 or ar == 1:
		_collect('http://www.mecd.gob.es/cultura-mecd/areas-cultura/cine/mc/fe/cine-dore/programacion.html')
		if ar == -1:
			del _pdfs[1:]
			return

	p = "http://www.mecd.gob.es/cultura-mecd/areas-cultura/cine/mc/fe/cine-dore/programacion/%s.html"

	if ar == 1:
		y = 2005
		year = datetime.datetime.now().year
		while y <= year:
			u = p % (str(y))
			_collect(u)
			y += 1
	if ar > 2000:
		u = p % (ar)
		_collect(u)
	
def _getYaml(url,_chance=1):
	if not exists(url):
		return (None, None, None)
	bash=''
	cmd=''
	s_yaml=''
	try:
		if url.endswith('.pdf'):
			cmd='pdftotext'
			bash="curl -L -s \"" + url + "\" | pdftotext -htmlmeta - - | awk -f dore.awk -v url=\"" + url + "\""
		elif url.endswith('.docx'):
			cmd='abiword'
			bash="curl -L -s \"" + url + "\" | abiword --to=txt --to-name=fd://1 fd://0 | sed -e 's/\s\+/ /g' -e 's/^ | $//g' | awk -f dore.awk -v url=\"" + url + "\""
		elif url.endswith('.doc'):
			if _chance==1:
				cmd='catdoc'
				#bash="curl -L -s \"" + url + "\" | catdoc | iconv -c -f utf-8 -t ascii | strings | awk -f dore.awk"
				bash="curl -L -s \"" + url + "\" | catdoc | sed -e 's/\s\+/ /g' -e 's/^ | $//g' | awk -f dore.awk -v url=\"" + url + "\""
			elif _chance==2:
				cmd='abiword'
				bash="curl -L -s \"" + url + "\" | abiword --to=txt --to-name=fd://1 fd://0 | sed -e 's/\s\+/ /g' -e 's/^ | $//g' | awk -f dore.awk -v url=\"" + url + "\""
			elif _chance==3:
				cmd='antiword'
				bash="curl -L -s \"" + url + "\" | antiword - | sed -e 's/^\s*\||\|\s*$//g' -e 's/\s\+/ /g' -e 's/^ | $//g' | awk -f dore.awk -v url=\"" + url + "\""
		f = os.popen(bash)
		s_yaml=f.read()
		f.close()
	except Exception,e:
		if url.endswith('.doc') and _chance<3:
			return _getYaml(url,_chance+1)
		sys.stderr.write("Error with curl/"+cmd+" "+ url+"\n")
		sys.stderr.write("\t"+bash+"\n")
		sys.stderr.write("\t"+str(e)+"\n")
		return (None, None, None)
	try:
		docs = yaml.load_all(s_yaml)
		pr=next(docs)
		if not pr:
			sys.stderr.write("Error with yaml - None "+ url+"\n")
			return (None, None, None)
		if ('error' in pr):
			sys.stderr.write(pr['error']+" "+ url+"\n")
			return (None, None, None)
		if not ('programa' in pr) or not pr['programa']:
			sys.stderr.write("Error with yaml format 'programa' "+ url+"\n")
			sys.stderr.write("\t"+bash+"\n")
			return (None, None, None)
		return (docs,pr['programa'],s_yaml)
	except Exception,e:
		if url.endswith('.doc') and _chance<3:
			return _getYaml(url,_chance+1)
		sys.stderr.write("Error with yaml "+ url+"\n")
		sys.stderr.write("\t"+bash+"\n")
		sys.stderr.write("\t"+str(e)+"\n")
		return (None, None, None)

def _fillCal(url):
	docs, programa, s_yaml = _getYaml(url)
	if not docs or not programa or programa in _prog:
		return None
	try:
		ct=0
		cal=create(programa)
		for o in docs:
			ct=ct+1
			i=datetime.datetime.strptime(o['inicio'], "%Y-%m-%d %H:%M")
			event = Event()
			event.add('summary', o[u'título'])
			event.add('dtstart', i)
			event.add('location', LOCATION)
			event.add('uid',i.strftime("%y%m%d%M%H")+"_"+o['sala']+"_dore")
			if o[u'duración']:
				f=i + datetime.timedelta(minutes = int(o[u'duración']))
				event.add('dtend', f)
			if o['nota']:
				event.add('DESCRIPTION',"Sala " + o['sala'] + " - " + o['nota']+"\n\nFuente: "+url)

			cal.add_component(event)
		if ct==0:
			sys.stderr.write("NOT EVENTS in ("+programa+") "+ url+"\n")
		else:
			f = open(CALDIR + programa + '.ics', 'wb')
			f.write(cal.to_ical())
			f.close()
			f = open(YMLDIR + programa + '.yaml', 'wb')
			f.write(s_yaml)
			f.close()
			_prog.append(programa)
	except Exception,e:
		sys.stderr.write("Error in ("+str(programa)+") "+ url+"\n")
		sys.stderr.write("\t"+str(e)+"\n")
		if o:
			print str(o)
		raise e

def run(ar):
	collect(ar)
	if len(_pdfs) == 0 and len(_docs)==0:
		raise Exception('NOTHING TO DO\n')
	for pdf in _pdfs:
		_fillCal(pdf)
	for doc in _docs:
		_fillCal(doc)

def join():
	full=create(FULL)
	for s in glob.glob(CALDIR + '*.ics'):
		f = open(s,'rb')
		cal = Calendar.from_ical(f.read())
		for component in cal.subcomponents:
			if component.name == 'VEVENT':
				full.add_component(component)
		f.close()
	f = open(FULL, 'wb')
	f.write(full.to_ical())
	f.close()

if __name__ == "__main__":
	ar = -1
	if len(sys.argv) <= 1:
		run(-1)
	else:
		if sys.argv[1].isdigit():
			run(int(sys.argv[1]))
		else:
			_fillCal(sys.argv[1])
	#join()

