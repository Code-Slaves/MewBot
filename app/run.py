from aiogram import executor
from app import dp
import asyncio
from hendlers import register_all_handlers
from core import Token
from aiogram import types
from datetime import datetime, timedelta
from core import CacheManager
from config import Configuration
from decimal import Decimal
from hendlers import storage
from aiogram.types import ParseMode



Token =Token(Configuration.TOKEN_CONTRACT)
cache = CacheManager()



def create_kb(view_tx_url, chart_url, buy_url):
    inline_kb = types.InlineKeyboardMarkup(row_width=3)  

    # Создание кнопок с проверкой на наличие URL
    buttons = []

    view_tx_button = types.InlineKeyboardButton('VIEW TX', url=view_tx_url)
    buttons.append(view_tx_button)

    chart_button = types.InlineKeyboardButton('CHART', url=chart_url)
    buttons.append(chart_button)

    buy_button = types.InlineKeyboardButton('BUY', url=buy_url)
    buttons.append(buy_button)

    # Добавление кнопок в клавиатуру, если они были созданы

    inline_kb.add(*buttons)
    
    return inline_kb


def transactions_by_price_filter(transactions, tezos_price: float, decimals: int):
    if transactions:
        gap = []
        for i in transactions:
            value = (int(i['parameter']['value'][0]['txs'][0]['amount'])/ 10**decimals)*tezos_price 
            if value >= 2 and i["hash"] not in cache.processed_transactions:
                gap.append(i)
                cache.processed_transactions.add(i["hash"])
                i["tezos_value"] = value

        cache.save_cache()
        return gap

    return []


def message_constructor(received_mew, spent_xtz, cats, xtz_usd_price, price_in_xtz, supply, volume_24h):
    message_template = f"""
*MEW BUY*\n
{cats}\n

Spent: *{round(spent_xtz, 2)} XTZ (${round((spent_xtz * xtz_usd_price), 2)})*\n
Received: *{round(received_mew, 2)} MEW*\n
Price: *{price_in_xtz:.10f} XTZ*\n
DEX: *Quipuswap*\n

Marketcap: *{round((price_in_xtz*supply), 2)} XTZ*\n
Traiding Volume 24h: *{round(float(volume_24h), 2)} XTZ*
    """

    return message_template.strip()



async def new_buy_message(dp):
    while True:
        try:
            await asyncio.sleep(60)
            chats = await storage.get_all_data("chat_ids")
            dt = datetime.utcnow().replace(microsecond=0) - timedelta(hours=1)

            token_info = await Token.get_token_info(Token.contract)
            last_transactions = await Token.get_last_transactions(dt)
            market = await Token.get_token_chronic('1d')
            if not (market and token_info):
                continue

            token_info = token_info[0]
            market= market[0]["quotes"][0]['buckets'][-1]
            metadata = token_info["metadata"]
            close_price = float(market["close"])


            transactions = transactions_by_price_filter(last_transactions, close_price, int(metadata["decimals"]))

            if transactions and chats:
                xtz_usd_price = await Token.get_xtz_price()

                for chat_id in chats:
                    for transaction in transactions:
                        received_mew = int(transaction['parameter']['value'][0]['txs'][0]['amount'])/ 10**int(metadata["decimals"])
                        cats = Token.get_cats_count(float(transaction["tezos_value"]))
                        supply = int(token_info["totalMinted"])/10**int(metadata["decimals"])
                        view_tx_url = f"https://tzkt.io/{transaction['hash']}"


                        message_text = message_constructor(received_mew, float(transaction["tezos_value"]), cats, xtz_usd_price, close_price, supply, market["quoteVolume"])


                        _kb = create_kb(view_tx_url, Token.chart, Token.buy)


                        await dp.bot.send_animation(chat_id=chat_id, caption=message_text, animation=Configuration.ANIMATION_PATH, reply_markup=_kb, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            pass

                
        



async def on_startup(dp):
    asyncio.create_task(cache.start_cache_cleanup_loop())
    asyncio.create_task(new_buy_message(dp))

if __name__ == '__main__':    
    register_all_handlers(dp)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)