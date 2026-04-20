from kasdb.functions import Json, MsgPack
import kasdb.config as config
import os
import asyncio
try:
  from colorama import Fore, init
  init()
except ImportError:
  # In case colorama is somehow missing, we don't try to install it at runtime anymore.
  # We just define a dummy Fore if it's really needed, or just skip it.
  class DummyFore:
    def __getattr__(self, name): return ""
  Fore = DummyFore()


def create(db_name: str, keys: list):
  data = { }
  for key in keys:
    data[key] = None
  try: 
    Json.get(f"{db_name}.json")
  except:
    Json.set(f"{db_name}.json", data)
    if config.debug:
      print(Fore.GREEN + f"база данных {db_name} создана с такими данными: {data}")

def if_get(db_name, condition, key="all"):
  if condition:
    if key=='all':
      return Json.get(f"{db_name}.json")
    else:
      return Json.get(f"{db_name}.json")[key]
  else: 
    if config.debug:
      return print(Fore.GREEN + "условие не выполнено данные не получены")
  if config.debug:
    print(Fore.GREEN + "получины данные с условием")
      
def where_get(db_name, key, where):
  data = Json.get(f"{db_name}.json")[key]
  if where in data:
    if config.debug:
      print(Fore.GREEN + "получины данные с условием")
    return data
  else: 

    if config.debug:

      return print(Fore.GREEN + "условие не выполнено данные не получены")

def get(db_name, key="all"):
  try:
    if key=="all":
      data = Json.get(f"{db_name}.json")
    else:
      data = Json.get(f"{db_name}.json")[key]
    if config.debug:
      print(Fore.GREEN + "данные успешно получены")
    if data == {}:
      print(Fore.YELLOW + "база данных пустая")
      return
    else:
       return data
    
  except KeyError or FileNotFoundError:
    print(Fore.RED + f"базы данных {db_name} не существует или же ключ {key} ненайден")

def set(db_name, data, key = None):
  try:
    data1=Json.get(f"{db_name}.json")
    if key != None:
      data1[key] = data
      Json.set(f"{db_name}.json", data1)
    else:
      Json.set(f"{db_name}.json", data)
    if config.debug:
      print(Fore.GREEN + "данные успешно обновлены")
    if data == None:
       print(Fore.YELLOW +"нечего добавлять.")
    else:
       return
  except FileNotFoundError:
    print(Fore.RED + f"базы данных {db_name} не существует ")

def delete(db_name):
  try:
    os.remove(f"{db_name}.json")
    if config.debug:
      print(Fore.GREEN + f"база данных {db_name} успешно удалена")
  except FileNotFoundError:
    print(Fore.RED + f"базы данных {db_name} не существует")


class DB:
  def __init__(self, filename, extension=".db", data=None):
    if extension:
      self.filename = filename + extension
    else:
      self.filename = filename + ".db"
    
    self.onGetData = None
    self.onSaveData = None

    if data is not None:
      MsgPack.set(self.filename, data)

  def on(self, event, func):
    if event == "getData": self.onGetData = func
    if event == "saveData": self.onSaveData = func

  def getData(self, key=None):
    decodedObject = MsgPack.get(self.filename)
    if key is not None:
      res = decodedObject.get(key)
      if self.onGetData:
        self.onGetData({
          "key": key,
          "data": res,
          "filename": self.filename
        })
      return res
    else:
      if self.onGetData:
        self.onGetData({
          "key": "[null]",
          "data": decodedObject,
          "filename": self.filename
        })
      return decodedObject

  def saveData(self, key, value):
    data = self.getData()
    data[key] = value
    MsgPack.set(self.filename, data)
    if self.onSaveData:
      self.onSaveData({
        "key": key,
        "value": value,
        "filename": self.filename
      })


class AsyncDB:
  def __init__(self, filename, extension=".db", data=None):
    if extension:
      self.filename = filename + extension
    else:
      self.filename = filename + ".db"

    self.onGetData = None
    self.onSaveData = None

    if data is not None:
      MsgPack.set(self.filename, data)

  def on(self, event, func):
    if event == "getData": self.onGetData = func
    if event == "saveData": self.onSaveData = func

  async def getData(self, key=None):
    loop = asyncio.get_running_loop()
    decodedObject = await loop.run_in_executor(None, MsgPack.get, self.filename)
    if key is not None:
      res = decodedObject.get(key)
      if self.onGetData:
        self.onGetData({
          "key": key,
          "data": res,
          "filename": self.filename
        })
      return res
    else:
      if self.onGetData:
        self.onGetData({
          "key": "[null]",
          "data": decodedObject,
          "filename": self.filename
        })
      return decodedObject

  async def saveData(self, key, value):
    data = await self.getData()
    data[key] = value
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, MsgPack.set, self.filename, data)
    if self.onSaveData:
      self.onSaveData({
        "key": key,
        "value": value,
        "filename": self.filename
      })