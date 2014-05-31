#!/usr/bin/env python
'''
	Script for automated downloading subtitles for video files from opensubtitles.

	Author:		Stanislav Nechutny
	License:	GPLv2

	Revision:	1
	Repository:	https://github.com/nechutny/subs
	Created:	2014-05-31 20:13
	Modified:	2014-05-31 20:13
	
	

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




def subtitlesByLink(url):
	try:
		http = urllib2.urlopen(url);
	except urllib2.URLError:
		print >> sys.stderr, "Can't connect to server. "
		sys.exit(1);
	data = http.read();

	res = [];
	try:
		dom = minidom.parseString(data);
	except xml.parsers.expat.ExpatError:
		print >> sys.stderr, "Readed invalid XML. "
		sys.exit(1);
	results = dom.getElementsByTagName('subtitle');
	for result in results:
		if len(result.getElementsByTagName("MovieName")) > 0:
			return result.getElementsByTagName("IDSubtitle")[0].getAttribute("LinkDownload");

	return res;

def downloadSubtitle(link,fhash):
	subs = urllib2.urlopen(link);
	if subs.headers.get("Content-type") == "text/html":
		print >> sys.stderr, "Limit reached - can't download."
		sys.exit(1);

	output = open("/tmp/"+fhash+".zip",'wb');
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
		return "IOError"

def unzip(fhash,filename):
	(prefix, sep, suffix) = filename.rpartition('.')

	try:
		with zipfile.ZipFile("/tmp/"+fhash+".zip") as zf:
			for member in zf.infolist():
				words = member.filename.split('/')
				path = "./"
				for word in words[:-1]:
					drive, word = os.path.splitdrive(word);
					head, word = os.path.split(word);
					if word in (os.curdir, os.pardir, ''): continue
					path = os.path.join(path, word);

				if re.match(r".*[.](srt|sub)$",words[0]) != None:
					zf.extract(member, "/tmp/");
					shutil.move("/tmp/"+words[0], prefix+"."+(re.findall(r".*[.](srt|sub)$",words[0])[0]));
						
	except zipfile.BadZipfile:
		print  >> sys.stderr, "Can't extract subtitles from downloaded file.";



if len(sys.argv) < 2:
	print "Try run with "+sys.argv[0]+" [-l eng] filename"
	sys.exit(1)
elif len(sys.argv) == 4 and sys.argv[1] == "-l":
	lang = sys.argv[2]
	filename = sys.argv[3]
elif len(sys.argv) == 2:
	lang = "eng"
	filename = sys.argv[1]
else:
	print "Try run with "+sys.argv[0]+" [-l eng] filename"
	sys.exit(1)
	
fhash = hashFile(filename)

url = "http://www.opensubtitles.org/en/search/sublanguageid-"+lang+"/moviehash-"+fhash+"/xml"

url = subtitlesByLink(url)

downloadSubtitle(url,fhash)

unzip(fhash, filename)

os.unlink("/tmp/"+fhash+".zip");
