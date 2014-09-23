#!/usr/bin/env python
'''
	Script for automated downloading subtitles for video files from opensubtitles.

	Author:		Stanislav Nechutny
	License:	GPLv2

	Revision:	4
	Repository:	https://github.com/nechutny/subs
	Created:	2014-05-31 20:13
	Modified:	2014-09-10 20:24
	
	

'''
import sys;
import os;
import re;
import urllib2;
import zipfile
from xml.dom import minidom
import xml.parsers.expat
import struct
import shutil
import tempfile
import locale
import getopt



def subtitlesByLink(url):
	try:
		http = urllib2.urlopen(url);
	except urllib2.URLError:
		print >> sys.stderr, "Can't connect to server. "
		sys.exit(1);
	data = http.read();

	try:
		dom = minidom.parseString(data);
	except xml.parsers.expat.ExpatError:
		print >> sys.stderr, "Readed invalid XML. "
		sys.exit(1);
	results = dom.getElementsByTagName('subtitle');
	for result in results:
		if len(result.getElementsByTagName("MovieName")) > 0:
			return result.getElementsByTagName("IDSubtitle")[0].getAttribute("LinkDownload");

	print  >> sys.stderr, "Subtitles not found.";
	sys.exit(1);

def downloadSubtitle(link,fhash):
	subs = urllib2.urlopen(link);
	if subs.headers.get("Content-type") == "text/html":
		print >> sys.stderr, "Limit reached - can't download."
		sys.exit(1);

	output = open(tempfile.gettempdir()+"/"+fhash+".zip",'wb');
	output.write(subs.read());
	output.close();

# googled function for calculating movie hash
# http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes#Python
def hashFile(name):
	try:
		longlongformat = 'q'  # long long
		bytesize = struct.calcsize(longlongformat)
		
		f = open(name, "rb") 

		filesize = os.path.getsize(name)
		hash = filesize

		if filesize < 65536 * 2:
			return "SizeError"

		for x in range(65536/bytesize):
			buffer = f.read(bytesize)
			(l_value,)= struct.unpack(longlongformat, buffer)
			hash += l_value
			hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number

		f.seek(max(0,filesize-65536),0)
		for x in range(65536/bytesize):
			buffer = f.read(bytesize)
			(l_value,)= struct.unpack(longlongformat, buffer)
			hash += l_value
			hash = hash & 0xFFFFFFFFFFFFFFFF

		f.close()
		returnedhash =  "%016x" % hash
		return returnedhash

	except(IOError):
		print  >> sys.stderr, "Can't open file.";
		sys.exit(1);

def unzip(fhash,filename):
	(prefix, sep, suffix) = filename.rpartition('.')
	if remove_directory:
		prefix = directory+"/"+os.path.basename(prefix);
	found = 0;
	try:
		with zipfile.ZipFile(tempfile.gettempdir()+"/"+fhash+".zip") as zf:
			for member in zf.infolist():
				words = member.filename.split('/')
				path = "./"
				
				for word in words[:-1]:
					drive, word = os.path.splitdrive(word);
					head, word = os.path.split(word);
					if word in (os.curdir, os.pardir, ''): continue
					path = os.path.join(path, word);

				if re.match(r".*[.](srt|sub)$",words[0]) != None:
					zf.extract(member, tempfile.gettempdir()+"/");
					shutil.move(tempfile.gettempdir()+"/"+words[0], prefix+"."+(re.findall(r".*[.](srt|sub)$",words[0])[0]));
					found += 1;
						
	except zipfile.BadZipfile:
		print  >> sys.stderr, "Can't extract subtitles from downloaded file.";
		os.unlink(tempfile.gettempdir()+"/"+fhash+".zip");
		sys.exit(1);

	if found == 0:
		print  >> sys.stderr, "Subtitle file not found in archive.";
		os.unlink(tempfile.gettempdir()+"/"+fhash+".zip");
		sys.exit(1);

def defaultLang():
	lang = {"ab":"abk","aa":"aar","af":"afr","sq":"sqi","am":"amh","ar":"ara","hy":"hye","as":"asm","ay":"aym","az":"aze","ba":"bak","eu":"eus","bn":"ben","bh":"bih","bi":"bis","be":"bre","bg":"bul","my":"mya","be":"bel","ca":"cat","zh":"zho","co":"cos","cs":"cze","da":"dan","nl":"nla","dz":"dzo","en":"eng","eo":"epo","et":"est","fo":"fao","fj":"fij","fi":"fin","fr":"fre","fy":"fry","gd":"gdh","gl":"glg","ka":"kat","de":"ger","el":"gre","kl":"kal","gn":"grn","gu":"guj","ha":"hau","he":"heb","hi":"hin","hu":"hun","is":"isl","id":"ind","ia":"ina","- ":"ine","iu":"iku","ik":"ipk","ga":"gai","it":"ita","ja":"jpn","jv":"jav","jw":"jaw","kn":"kan","ks":"kas","kk":"kaz","km":"khm","rw":"kin","ky":"kir","ko":"kor","ku":"kur","oc":"oci","lo":"lao","la":"lat","lv":"lav","ln":"lin","lt":"lit","mk":"mak","mg":"mlg","ms":"/ms","ml":"mlt","mi":"mri","mr":"mar","mo":"mol","mn":"mon","na":"nau","ne":"nep","no":"nor","or":"ori","om":"orm","pa":"pan","fa":"fas","pl":"pol","pt":"por","ps":"pus","qu":"que","rm":"roh","ro":"ron","rn":"run","ru":"rus","sm":"smo","sg":"sag","sa":"san","sh":"scr","sn":"sna","sd":"snd","si":"sin","- ":"sit","ss":"ssw","sk":"slo","sl":"slv","so":"som","st":"sot","es":"esl","su":"sun","sw":"swa","sv":"swe","tl":"tgl","tg":"tgk","ta":"tam","tt":"tat","te":"tel","th":"tha","bo":"bod","ti":"tir","to":"tog","ts":"tso","tn":"tsn","tr":"tur","tk":"tuk","tw":"twi","ug":"uig","uk":"ukr","ur":"urd","uz":"uzb","vi":"vie","vo":"vol","cy":"cym","wo":"wol","xh":"xho","yi":"yid","yo":"yor","za":"zha","zu":"zul"};
	try:
		return lang[ locale.getdefaultlocale()[0][0:2] ];
	except KeyError:
		return "eng"

lang = defaultLang();
directory = -1;

def removeFromListByValue(where, search):
	for i in range(0, len(where)):
		if where[i] == search:
			del where[i];
			del where[i];
			return where;
	return where;

remove_lang = False;
remove_directory = False;

try:
	opts, args = getopt.getopt(sys.argv[1:],"hl:d:")
except getopt.GetoptError:
	print "Try run with "+sys.argv[0]+" [-l eng] [-d directory] filename(s)"
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print "Try run with "+sys.argv[0]+" [-l eng] [-d directory] filename(s)"
		sys.exit()
	elif opt == '-l':
		lang = arg
		remove_lang = True;
	elif opt == '-d':
		directory = arg
		remove_directory = True;

del sys.argv[0];
if remove_directory:
	sys.argv = removeFromListByValue(sys.argv,"-d");
if remove_lang:
	sys.argv = removeFromListByValue(sys.argv,"-l");


for filename in sys.argv:
	fhash = hashFile(filename)
	url = "http://www.opensubtitles.org/en/search/sublanguageid-"+lang+"/moviehash-"+fhash+"/xml"
	url = subtitlesByLink(url)
	downloadSubtitle(url,fhash)
	unzip(fhash, filename)
	os.unlink(tempfile.gettempdir()+"/"+fhash+".zip");
	print "Downloaded "+lang+" subtitles for "+filename; 
