import eventlet
from eventlet.green import urllib2
from lxml import etree
from lxml.etree import tostring
from lxml.html.soupparser import fromstring
import os

url = "http://sodt.mobi/"

header_vina_1 = ["091", "094", "0123"]
current_stop = 0
current_start = 0
current_header_index = 0

#max_stop = 10000000
max_stop = 91

def fetch(url):
	print("fetching", url)
	try:
		response = urllib2.urlopen(url, timeout=60).read()
	except Exception:
		response = "<html></html>"
		print("Error")
	return response

#fo = open("test.txt", "wb")
fd = os.open("test.txt", os.O_CREAT | os.O_WRONLY | os.O_NONBLOCK)

while current_header_index < len(header_vina_1):

	while current_stop < max_stop:
		urls = set()

		current_stop = current_stop + 30

		if current_stop > max_stop:
			current_stop = current_stop - abs(max_stop - current_stop)


		for i in range(current_start, current_stop):
			urls.add(url+header_vina_1[current_header_index]+"-"+str(i).zfill(7)+".html")

		current_start = current_stop

		pool = eventlet.GreenPool()
		for body in pool.imap(fetch, urls):
			try: 
			    root = fromstring(body)
			    tree = etree.ElementTree(root)
			    name = tree.xpath("/html/body/main/div/div/div[1]/div[2]/div/h5/text()")
			    location = tree.xpath("/html/body/main/div/div/div[1]/div[2]/div/h6/text()")
			    mobile_number = tree.xpath("/html/body/main/div/div/div[1]/div[1]/div[1]/h1")
			    if len(name) > 0 and len(mobile_number) >0:
			    	if len(location) > 0:
			    		total = name[0] + "|" + location[0] + "|" + mobile_number[0].text	
			    	else:
			    		total = name[0] + "|" + "None" + "|" + mobile_number[0].text

			    	os.write(fd, (total+"\r\n").encode(encoding='UTF-8'))

			    	print((total+"\r\n").encode(encoding='UTF-8'))
			except Exception:
				print("Error")
		pool.waitall()
	print("Finished " + header_vina_1[current_header_index])

	current_stop = 0
	current_start = 0
	
	current_header_index = current_header_index + 1	    	

os.close(fd)

