from lxml import html, etree
import re
import requests
import sys
from urlparse import urljoin, urlparse
from os.path import basename
import datetime
import json
import os

_pdfs = list()
_json = list()
txt = re.compile("(Abri|Programa|programaci|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)", re.IGNORECASE)
pdf = re.compile(".*(Programa|PrograDore|programDore).*\\.pdf$", re.IGNORECASE)


def _getPdfs(url):
    try:
        page = requests.get(url)
        tree = html.fromstring(page.text)
        links = tree.xpath('//div[@id="info"]//a[contains(@href,".pdf")]')
        for l in links:
            etree.strip_tags(l, "*")
            if l.text is not None:
                t = l.text.strip()
                if txt.match(t):
                    u = urljoin(url, l.get("href"))
                    n = basename(urlparse(u).path)
                    if pdf.match(n):
                        _pdfs.append(u)
        if len(_pdfs) == 0:
            raise Exception('Programas no encontrados')
    except:
#        sys.stderr.write(url);
#        sys.stderr.write(sys.exc_info()[0])
        print url
#        print sys.exc_info()[0]
        raise
        return None


def getPdfs(ar):
    del _pdfs[:]
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


def _getJson(url):
    f = os.popen("curl -s \"" + url + "\" | pdftotext - - | awk -f dore.awk")
    keys = ['inicio', 'duracion', 'sala', 'titulo', 'descripcion']
    obj = {}
    ct = 0
    for i in f.readlines():
        i = i.strip()
        if len(i) == 0:
            _json.append(obj)
            obj = {}
            ct = 0
            continue
        if ct < len(keys):
            obj[keys[ct]] = i
        else:
            k = keys[-1]
            obj[k] = obj[k] + "\n" + i
        ct += 1
    return _json


def getJson(flag=-1):
    getPdfs(flag)
    del _json[:]
    for pdf in _pdfs:
        _getJson(pdf)
    return _json


if __name__ == "__main__":
    ar = -1
    if len(sys.argv) > 1:
        ar = int(sys.argv[1])
    getJson(ar)
    print json.dumps(_json)


