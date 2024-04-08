from aiogram import Dispatcher, Bot
from config import Configuration
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from AiogramStorages.storages import SQLiteStorage
from aiogram.types import ParseMode
import logging

# Configure logging
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',level=logging.INFO)

bot = Bot(token=Configuration.TOKEN, parse_mode=ParseMode.HTML)

dp = Dispatcher(bot=bot)

dp.middleware.setup(LoggingMiddleware())