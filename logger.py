import time

def writelog(txt):
  print(txt)
  with open("log.json", "a") as file:
    file.write(time.strftime("[%d/%m/%y--%H:%M:%S]  ",time.gmtime())+txt+"\n")

def getlog():
  with open("log.json", "r") as file:
    return file.read()
