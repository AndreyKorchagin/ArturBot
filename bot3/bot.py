#import aiogram
#from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot
from aiogram import types
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select
import os
import re

from database import Base, Users
import keyboards as kb
from config import TOKEN

engine = create_engine(f'sqlite:///users.db')

if not os.path.isfile(f'./users.db'):
    Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

session = Session()
# test = Users(user_id = 139050906, firstname = "Andrey", role = "admin")
# session.add(test)
# session.commit()


# for instance in session.query(Users).order_by(Users.id): 
#     print (instance.id, instance.user_id, instance.firstname, instance.role)


def check_user(id):
	count = session.query(Users.user_id).filter(Users.user_id == id).count()
	if count == 1:
		return True
	elif count == 0:
		return False
	else:
		print("Error")


def check_role(id, role):
	role = session.query(Users).filter(Users.role == role, Users.user_id == id).count()
	if role == 1:
		return True
	elif role == 0:
		return False
	else:
		print("Error")

def get_admins_id():
	admins = session.query(Users).filter(Users.role == "admin")
	for i in admins:
		return(i.user_id)
	return False

def add_ssh_pub_to_tmp(key):
	f = open("/home/pi/ArturBot/bot3/ssh.tmp", "w+")
	f.write(key)
	f.close

def check_add_ssh_pub():
	return os.popen("/home/pi/ArturBot/bot3/check_add_ssh_pub.sh").read()

bot = Bot(token = TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def process_start_command(message):
	if check_user(message.from_user.id):
		if check_role(message.from_user.id, "admin"):
			await bot.send_message(message.from_user.id, "Hello admin")
		elif check_role(message.from_user.id, "user"):
			await bot.send_message(message.from_user.id, "Hello user")
	else:
		await bot.send_message(message.from_user.id, "Вы не авторизованы.\nВаш запрос отправлен администратору!!!")
		await bot.send_message(get_admins_id(), text = u'Добавить пользователя "%s" (id:%d)?' % (message.from_user.first_name, message.from_user.id), reply_markup=kb.add_new_user(message.from_user.id, message.from_user.first_name))

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
	await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")
	#await bot.send_message(message.from_user.id, text = 'HHHHH', reply_markup=kb.hours)

@dp.message_handler(commands=['add'])
async def process_ssh_add_command(message: types.Message):
	await bot.send_message("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.message_handler(commands=['ssh_add'])
async def process_ssh_add_command(message: types.Message):
	if check_user(message.from_user.id):
		await bot.send_message(message.from_user.id, text = u'Скопируйте ваш публичный ключ, затем вставьте сюда и поставьте вначале "/"')
	else:
		await bot.send_message(message.from_user.id, text = u'Вы не авторизованы!!!')


@dp.message_handler(commands=['ssh-rsa'])
async def process_ssh_rsa_command(message: types.Message):
	if check_user(message.from_user.id):
		key = re.split(r'\s{1,}', message.text)
		if len(key) == 3:
			await bot.send_message(get_admins_id(), text = u'Пользователь %s (id:%s) хочет добавить свой публичный ssh ключ!!!' % (message.from_user.first_name, message.from_user.id), reply_markup = kb.add_ssh(message.from_user.id, message.from_user.first_name))
			string = key[0]
			for i in range(1, 3):
				string = u'%s %s' % (string, key[i])
			string = u'%s\n' % (string[1:])
			print(string)
			add_ssh_pub_to_tmp(string)
	else:
		await bot.send_message(message.from_user.id, text = u'Вы не авторизованы!!!')


@dp.callback_query_handler(lambda call: True)
async def process_callback_1hour(callback_query: types.CallbackQuery):
	if callback_query.data.split(' ')[0] == 'add_approve':
		if not check_user(int(callback_query.data.split(' ')[1])):
			user = Users(user_id = callback_query.data.split(' ')[1], firstname = callback_query.data.split(' ')[2], role = "user")
			session.add(user)
			session.commit()
			await bot.send_message(callback_query.data.split(' ')[1], u'Доступ предоставлен!!!')
			await bot.send_message(callback_query.from_user.id, u'Доступ предоставлен пользователю %s (id:%s)!!!' % (str(callback_query.data.split(' ')[1]), callback_query.data.split(' ')[2]))
		else:
			await bot.send_message(callback_query.from_user.id, "Пользователь уже добавлен")
	elif callback_query.data.split(' ')[0] == 'add_decline':
		await bot.send_message(callback_query.data.split(' ')[1], u'Отказано в доступе!!!')

	elif callback_query.data.split(' ')[0] == 'ssh_approve':
			if check_add_ssh_pub() == 'True\n':
				await bot.send_message(get_admins_id(), u'SSH ключ пользователя %s (id:%s) добавлен' % (callback_query.data.split(' ')[2], callback_query.data.split(' ')[1]))
				await bot.send_message(callback_query.data.split(' ')[1], u'Ваш ключ добавлен и Вам предоставлен доступ')
			else:
				await bot.send_message(get_admins_id(), u'Ключ не верный')
				await bot.send_message(callback_query.data.split(' ')[1], u'Ключ не верный')
	elif callback_query.data.split(' ')[0] == 'ssh_decline':
		await bot.send_message(get_admins_id(), u'Пользователю %s (id:%s) отказано в добавлении SSH Ключа' % (callback_query.data.split(' ')[2], callback_query.data.split(' ')[1]))
		await bot.send_message(callback_query.data.split(' ')[1], u'Вам отказано в добавлении SSH Ключа')


if __name__ == '__main__':
	executor.start_polling(dp)