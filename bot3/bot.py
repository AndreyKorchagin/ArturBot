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
	# for user_id in session.query(Users.user_id).filter(Users.user_id == id):
	# 	print(user_id)
	count = session.query(Users.user_id).filter(Users.user_id == id).count()
	if count == 1:
		return True
	elif count == 0:
		return False
	else:
		print("Error")


def check_role(id, role):
	role = session.query(Users.user_id).filter(Users.role == role).count()
	if role == 1:
		return True
	elif role == 0:
		return False
	else:
		print("Error")

def send_admins():
	for row in session.query(Users):
		if row.role == "admin":
			return row.user_id
	return False

bot = Bot(token = TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def process_start_command(message):
	send_admins()
	if check_user(message.from_user.id):
		if check_role(message.from_user.id, "admin"):
			await bot.send_message(message.from_user.id, "Hello admin")
		elif check_role(message.from_user.id, "user"):
			await bot.send_message(message.from_user.id, "Hello user")
	else:
		await bot.send_message(message.from_user.id, "Вы не авторизованы.\nВаш запрос отправлен администратору!!!")
		await bot.send_message(send_admins(), text = u'Добавить пользователя "%s" (id:%d)?' % (message.from_user.first_name, message.from_user.id), reply_markup=kb.add_new_user(message.from_user.id, message.from_user.first_name))

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
	await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")
	#await bot.send_message(message.from_user.id, text = 'HHHHH', reply_markup=kb.hours)

@dp.message_handler(commands=['add'])
async def process_ssh_add_command(message: types.Message):
	await bot.send_message("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.message_handler(commands=['ssh_add'])
async def process_ssh_add_command(message: types.Message):
	await bot.send_message("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")
	#await bot.send_message(message.from_user.id, text = 'HHHHH', reply_markup=kb.hours)

@dp.callback_query_handler(lambda call: True)
async def process_callback_1hour(callback_query: types.CallbackQuery):
	#for item in callback_query:
	#	print(item)
	if callback_query.data.split(' ')[0] == 'add_approve':
		#ua.add_user(str(callback_query.data.split(' ')[1]), callback_query.data.split(' ')[2])
		test = Users(user_id = callback_query.data.split(' ')[1], firstname = callback_query.data.split(' ')[2], role = "user")
		session.add(test)
		session.commit()
		bot.send_message(callback_query.data.split(' ')[1], u'Доступ предоставлен!!!')
		bot.send_message(callback_query.from_user.id, u'Доступ предоставлен пользователю %s (id:%s)!!!' % (str(callback_query.data.split(' ')[1]), callback_query.data.split(' ')[2]))
	elif callback_query.data.split(' ')[0] == 'add_decline':
		bot.send_message(callback_query.data.split(' ')[1], u'Отказано в доступе!!!')


if __name__ == '__main__':
	executor.start_polling(dp)