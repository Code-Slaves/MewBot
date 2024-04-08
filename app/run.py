from aiogram import executor
from app import dp
import asyncio
from handlers import register_all_handlers
from core import Token
from aiogram import types
from datetime import datetime, timedelta
from core import CacheManager
from config import Configuration
from decimal import Decimal
from handlers import storage
from aiogram.types import ParseMode
import surrogates



Token =Token(Configuration.TOKEN_CONTRACT)
cache = CacheManager()



def create_kb(view_tx_url, chart_url, buy_url):
    inline_kb = types.InlineKeyboardMarkup()  

    # Создание первой строки с кнопками "VIEW TX" и "CHART"
    first_row_buttons = []

    view_tx_button = types.InlineKeyboardButton('VIEW TX', url=view_tx_url)
    first_row_buttons.append(view_tx_button)

    chart_button = types.InlineKeyboardButton('CHART', url=chart_url)
    first_row_buttons.append(chart_button)

    inline_kb.row(*first_row_buttons)

    # Создание второй строки с кнопкой "BUY", занимающей всю ширину
    buy_button = types.InlineKeyboardButton('BUY', url=buy_url)
    inline_kb.add(buy_button)

    return inline_kb



def transactions_by_price_filter(transactions, tezos_price: float, decimals: int):
    if transactions:
        gap = []
        for i in transactions:
            value = (int(i['amount'])/ 10**decimals)*tezos_price 
            if value >= Configuration.MIN_TOKEN_VALUE_FILTER and i["transactionId"] not in cache.processed_transactions:
                gap.append(i)
                cache.last.add(i["transactionId"])
                i["tezos_value"] = value

        return gap

    return []


def message_constructor(received_mew, spent_xtz, cats, xtz_usd_price, price_in_xtz, supply, volume_24h):
    message_template = f"""
*MEW BUY! MEW BUY!*
{cats}\n
{surrogates.decode("🔀")} Spent: *${round((spent_xtz * xtz_usd_price), 2)}  ({round(spent_xtz, 2)} XTZ)*
{surrogates.decode("🔀")} Got: *{int(received_mew)} MEW*
{surrogates.decode("🪙")} Dex *Quipuswap*
Price: *{price_in_xtz:.10f} XTZ*
{surrogates.decode("💸")} Market Cap: *${round(((price_in_xtz*supply)*xtz_usd_price), 2)}*
{surrogates.decode("📈")} 24H Volume: *${round((float(volume_24h)*xtz_usd_price), 2)}*
    """

    return message_template.strip()



async def new_buy_message(dp):
    while True:
        try:
            await asyncio.sleep(70)
            chats = await storage.get_all_data("chat_ids")
            dt = datetime.utcnow().replace(microsecond=0) - timedelta(hours=1)

            last_transactions = await Token.get_last_transactions(dt)

            market = await Token.get_token_chronic('1d')

            if not (market and chats):
                continue

            market= market[0]["quotes"][0]['buckets'][-1]
            
            close_price = float(market["close"])


            transactions = transactions_by_price_filter(last_transactions, close_price, int(Token.metadata["decimals"]))

            if transactions:

                xtz_usd_price = await Token.get_xtz_price()

                for chat_id in chats:
                    for transaction in transactions:
                        hash_ = await Token.get_hesh(transaction["transactionId"])
                        if not hash_:
                            continue
                        received_mew = int(transaction['amount'])/ 10**int(Token.metadata["decimals"])
                        cats = Token.get_cats_count(float(transaction["tezos_value"]), Configuration.MIN_TOKEN_VALUE_FILTER)
                        supply = int(Token.supply)/10**int(Token.metadata["decimals"])
                        view_tx_url = f"https://tzkt.io/{hash_[0]}"


                        message_text = message_constructor(received_mew, float(transaction["tezos_value"]), cats, xtz_usd_price, close_price, supply, market["quoteVolume"])


                        _kb = create_kb(view_tx_url, Token.chart, Token.buy)

                        cache.save_cache()
                        await dp.bot.send_animation(chat_id=chat_id, caption=message_text, animation=Configuration.ANIMATION_PATH, reply_markup=_kb, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(e)

                
        



async def on_startup(dp):
    asyncio.create_task(cache.start_cache_cleanup_loop())
    asyncio.create_task(new_buy_message(dp))

if __name__ == '__main__':    
    register_all_handlers(dp)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)