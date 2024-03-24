import time, pickle

def writelog(txt, obj = None, mode = "normal"):
  print(txt)
  filename = "logs/log.json"
  if mode == "community":
    filename = "logs/community_log.json"
  with open(filename, "a") as file:
    file.write(time.strftime("[%d/%m/%y--%H:%M:%S]  ",time.gmtime())+txt+"\n")

  if obj:
    with open("logs/obj.dat", "ab") as file:
      print(obj)
      pickle.dump(obj, file)
    
def getlog(mode = "normal"):
  filename = "logs/log.json"
  if mode == "community":
    filename = "logs/community_log.json"
  with open(filename, "r") as file:
    return file.read()
