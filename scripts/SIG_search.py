#####################################
# Call search(name, adr) and get json 
####################################
import sys, json, os, getopt
script_dir = os.path.dirname(__file__) 

beenInit = False
json_num = dict()
json_name = dict()

def read_to_mem(path):
   global json_name, json_num
   file_path = os.path.join(script_dir, path)
   with open(file_path) as f:
      pre_json = f.read().replace('\n', '')
      json_file = json.loads(pre_json)
      for json_obj in json_file:
         json_name[json_obj['SpecificationName.desc']] = json_obj
         if 'AssignedNumber' in json_obj: #profiles dont have nums
            json_num[json_obj['AssignedNumber']] = json_obj

def init():
   read_to_mem("json/characteristics_json")
   read_to_mem("json/services_json")
   read_to_mem("json/profiles_json")

def search(name, adr):
   global beenInit, json_name, json_num
   if beenInit == False:
      init()
      beenInit = True
   if name in json_name:
      print json_name[name]
   if adr in json_num:
      print json_num[adr]
   else:
      return -1


def main(argv): 
   name = ''
   adr = ''
   try:
      opts, args = getopt.getopt(argv,"hn:a:",["nfile=","afile="])
   except getopt.GetoptError:
      print 'SIG_search.py -n <peripheral_name> -a <peripheral_assigned_num>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'SIG_search.py -n <peripheral_name> -a <peripheral_assigned_num>'
         sys.exit()
      elif opt in ("-n", "--nfile"):
         name = arg
      elif opt in ("-a", "--afile"):
         adr = arg
         if (adr[:2] != "0x"):
            adr = "0x" + adr.upper()
         else:
            adr = adr[2:]
            adr = "0x" + adr.upper()
   search(name, adr)

if __name__ == "__main__":
   main(sys.argv[1:])
