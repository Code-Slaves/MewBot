from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types, Dispatcher
from app import dp
from core import ChatStorage

storage = ChatStorage("db/storage.json")


async def send_welcome(message: types.Message):
	bot = message.bot

	keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(
			"Click here to add to a group.",
			url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true"
		))

	if message.chat.type == "private":
		# Отправляем сообщение с кнопкой
		await message.answer("👇 Ready to get started? Add a bot to your group now!", reply_markup=keyboard)


async def chat_member_updated(update: types.ChatMemberUpdated):
	bot = update.bot
	chat_id = update.chat.id
	new_status = update.new_chat_member.status

	if new_status in ["member", "administrator"]:
		# Проверка на канал и администратора
		if update.chat.type == "channel" and new_status == "administrator":
			if update.new_chat_member.can_post_messages:
				await storage.add_data('chat_ids', chat_id)
				await bot.send_message(chat_id, "🤖 The bot has been successfully connected!")
		elif update.chat.type in ["group", "supergroup"]:
			await storage.add_data('chat_ids', chat_id)
			await bot.send_message(chat_id, "🤖 The bot has been successfully connected!")

	elif new_status in ["left", "kicked"]:
		# Удален из группы или канала
		await storage.remove_data("chat_ids", chat_id)



def register_all_handlers(dp : Dispatcher):
	dp.register_message_handler(send_welcome, commands=['start'])
	dp.register_my_chat_member_handler(chat_member_updated)


