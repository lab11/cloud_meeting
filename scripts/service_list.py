import csv

class ServiceList(object):
   def __init__(self):
      self.map = {}
      try:
            csvfile = open('sig-services.csv')
      except:
         import sig_scraper
         csvfile = open('sig-services.csv')
      reader = csv.reader(csvfile, delimiter=',', quotechar='|')
      for row in reader:
         self.map[row[1]] = row[0]
      csvfile.close()

   def get_service_name(self, assigned_number):
      return self.map[assigned_number]

   def get_assigned_number(self, service_name):
      num = None     
      for (number, name) in self.map.vals():
         if name == service_name:
            num = number
      return num
          

ServiceList()
