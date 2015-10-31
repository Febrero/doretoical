from icalendar import Calendar, Event
import datetime
import os.path
import shutil

CALDIR='ics/'
YMLDIR='yaml/'
last='last'

ahora=datetime.datetime.now()
actual=str(ahora.year)+"-"+str(ahora.month)
siguiente=str(ahora.year)+"-"+str(ahora.month+1)

if os.path.isfile(CALDIR+actual+".ics"):
	if not os.path.isfile(CALDIR+siguiente+".ics"):
		shutil.copy(CALDIR+actual+".ics", CALDIR+last+".ics")
	else:
		shutil.copy(CALDIR+siguiente+".ics", CALDIR+last+".ics")
		catlast = open(CALDIR+last+".ics",'rb')
		l = Calendar.from_ical(catlast.read())
		catactual = open(CALDIR+actual+".ics",'rb')
		a = Calendar.from_ical(catactual.read())
        for c in a.subcomponents:
            if c.name == 'VEVENT':
                l.add_component(c)
        catlast.close()

if os.path.isfile(YMLDIR+actual+".yaml"):
	if not os.path.isfile(YMLDIR+siguiente+".yaml"):
		shutil.copy(YMLDIR+actual+".yaml", YMLDIR+last+".yaml")
	else:
		d = open(YMLDIR+last+".yaml", 'wb')
		shutil.copyfileobj(open(YMLDIR+actual+".yaml", 'rb'), d)
		shutil.copyfileobj(open(YMLDIR+siguiente+".yaml", 'rb'), d)
		d.close()
