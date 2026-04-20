import json
import msgpack

class Json:
  @staticmethod
  def get(filename):
    with open(filename, encoding="utf-8") as infile:
      return json.load(infile)


  @staticmethod
  def set(filename, content):
    with open(filename, "w") as outfile:
      json.dump(content, outfile, ensure_ascii=True, indent=2)

class MsgPack:
  @staticmethod
  def get(filename):
    with open(filename, "rb") as infile:
      return msgpack.unpack(infile)

  @staticmethod
  def set(filename, content):
    with open(filename, "wb") as outfile:
      msgpack.pack(content, outfile)