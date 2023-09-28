import time, pickle

def writelog(txt, obj = None):
  print(txt)
  with open("logs/log.json", "a") as file:
    file.write(time.strftime("[%d/%m/%y--%H:%M:%S]  ",time.gmtime())+txt+"\n")

  if obj:
    with open("logs/obj.dat", "ab") as file:
      print(obj)
      pickle.dump(obj, file)
    
def getlog():
  with open("log.json", "r") as file:
    return file.read()
