#######################################
# run: python sig_scarper.py 
# output: ordered list of all standard 
#           profiles and services from
#           BLE SIG on Feb 4th, 2015
# filename: <date>.csv 
#######################################
from BeautifulSoup import BeautifulSoup
import urllib2, re, csv, time
sig_url = 'https://developer.bluetooth.org/TechnologyOverview/Pages/Profiles.aspx#GATT'
search_term = "/TechnologyOverview/Pages/"
html_page = urllib2.urlopen(sig_url)
soup = BeautifulSoup(html_page)
count = 0
profiles = []

filename = time.strftime("%Y-%b%d_SIG-profiles")+ ".csv"
for link in soup.findAll('a'):
    cur_href = link.get('href')
    if cur_href == None:
         continue
    if search_term in cur_href and count % 2 == 0:
         profiles.append(cur_href.split("/")[-1][:-5])
    count += 1
profiles.sort()
with open(filename, 'wb') as csvfile:
    fieldnames = ['Profile Name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for profile in profiles:
          writer.writerow({'Profile Name': profile});
      
