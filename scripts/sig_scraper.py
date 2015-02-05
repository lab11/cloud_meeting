#######################################
# run: python sig_scarper.py 
# output: ordered list of all standard 
#           profiles and services from
#           BLE SIG on Feb 4th, 2015
# filename: <date>.csv 
#######################################
from BeautifulSoup import BeautifulSoup
import urllib2, re, csv, time
#isig_url = 'https://developer.bluetooth.org/TechnologyOverview/Pages/Profiles.aspx#GATT'
sig_url = 'https://developer.bluetooth.org/gatt/services/Pages/ServicesHome.aspx'
search_term = "/ServiceViewer.aspx"
html_page = urllib2.urlopen(sig_url)
soup = BeautifulSoup(html_page)
services = []


#filename = time.strftime("%Y-%b%d_SIG-services")+ ".csv"
filename = "sig-services.csv"
for link in soup.findAll('a'):
    if link == None:
         continue
    if search_term in link['href']:
         service_name = link.string 
         assigned_num = link.parent.nextSibling.nextSibling.string 
	 services.append((service_name, assigned_num))
with open(filename, 'wb') as csvfile:
    fieldnames = ['Service Name', 'Assigned Number']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for (service_name, assigned_num) in services:
          writer.writerow({'Service Name': service_name, 'Assigned Number': assigned_num})
