import db, config
import random
config.debug = True #логи в консоли о действиях дб можно убрать.

db.create("t", ["kay1", "kay2"]) #создать базу данных под названием t с начальными ключами

data = db.get("t", "kay1") #получаем то что у нас в базе

print(data)#выводим базу
f = ["you gay!", "you not gay!"] #список хрени
db.set("t", random.choice(f), "you gay?")#записуем новые данные

print(db.get("t"))#выводим результат добавления данных

db.delete("t")#удаляем базу данных t