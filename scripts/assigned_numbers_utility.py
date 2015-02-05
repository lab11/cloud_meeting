# this file is meant to be imported into other files to handle the mapping
# between Bluetooth assigned numbers and the names of what they stand for

# ex: import assigned_numbers_utility as anutil
# service_name = anutil.get_service_name(0x1811)

from BeautifulSoup import BeautifulSoup
import urllib2, re, csv, time

#### MAPPINGS ####

gap_map = {}
service_map = {}

#### UTILITIES ####

# assigned number can be a: 
#   dec/hex integer: 10/0x0A
#   a hex string: '0x0A'
#   a dec string: '10'
def get_gap_data_type_name(assigned_number):
   assigned_number = convert_to_int(assigned_number)
   return gap_map[assigned_number]

def get_gap_data_type_number(data_type_name):
   num = None     
   for (number, name) in gap_map.vals():
      if name == data_type_name:
         num = number
   return num

def get_service_name(assigned_number):
   assigned_number = convert_to_int(assigned_number)
   return service_map[assigned_number]

def get_service_number(service_name):
   num = None     
   for (number, name) in service_map.vals():
      if name == service_name:
         num = number
   return num

def convert_to_int(assigned_number):
   if type(assigned_number) == type(""):
      if len(assigned_number) > 2 and assigned_number[1] == 'x':
         assigned_number = int(assigned_number, 16)
      else:
         assigned_number = int(assigned_number)
   return assigned_number

#### INITIALIZATION ####

# read CSV files into memory. If they don't exist, create them.
def init():
   global gap_map, service_map

   # read in gap file, create with scraper if it doesn't exist
   try:
      csvfile = open('gap-data-types.csv')
   except:
      scrape_gap_data_types()
      csvfile = open('gap-data-types.csv')
   reader = csv.reader(csvfile, delimiter=',', quotechar='|')
   for row in reader:
      gap_map[int(row[1], 16)] = row[0]
   csvfile.close()

   # read in service file, create with scraper if it doesn't exist
   try:
      csvfile = open('services.csv')
   except:
      scrape_services()
      csvfile = open('services.csv')
   reader = csv.reader(csvfile, delimiter=',', quotechar='|')
   for row in reader:
      service_map[int(row[1], 16)] = row[0]
   csvfile.close()

   #print(gap_map)
   #print(service_map)

#### SCRAPERS ####

def scrape_gap_data_types():
   sig_url = 'https://www.bluetooth.org/en-us/specification/assigned-numbers/generic-access-profile'
   html_page = urllib2.urlopen(sig_url)
   soup = BeautifulSoup(html_page)
   gap_data_types = []

   filename = "gap-data-types.csv"
   pair = []
   for (i, cell) in enumerate(soup.findAll('td')):
       if i % 3 == 0:
           pair.append(str(cell.string.replace(u'\u200b', ""))) #assigned number
       elif i % 3 == 1:
           # the entry for "3D information data" has a formatting problem on the page
           if cell.string == None:
               name = str(cell.next.nextSibling.next.string[2:-1])
           else:
               name = str(cell.string[1:-1].replace(u'\u200b', "").replace(u'\xab', "").replace(u'&#160;', ' '))
           # related to the messed up formatting for "3D information data", weirdly
           if pair[0] == u'0x22':
               name = 'LE Secure Connections Confirmation Value'
           pair.append(name) #data type name
       else:
           gap_data_types.append(pair)
           pair = []
   with open(filename, 'wb') as csvfile:
       writer = csv.writer(csvfile)
       for (assigned_num, data_type) in gap_data_types:
             writer.writerow([data_type, assigned_num])

def scrape_services():
   sig_url = 'https://developer.bluetooth.org/gatt/services/Pages/ServicesHome.aspx'
   search_term = "/ServiceViewer.aspx"
   html_page = urllib2.urlopen(sig_url)
   soup = BeautifulSoup(html_page)
   services = []

   #filename = time.strftime("%Y-%b%d_SIG-services")+ ".csv"
   filename = "services.csv"
   for link in soup.findAll('a'):
       if link == None:
            continue
       elif search_term in link['href']:
            service_name = link.string 
            assigned_num = link.parent.nextSibling.nextSibling.string 
            services.append((service_name, assigned_num))
   with open(filename, 'wb') as csvfile:
       writer = csv.writer(csvfile)
       for (service_name, assigned_num) in services:
             writer.writerow([service_name, assigned_num])



#### INITIALIZE ON IMPORT ####

# runs init (reads csv maps into memory) when this file is imported
init()