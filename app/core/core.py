import httpx
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal


dt = datetime.utcnow().replace(microsecond=0) - timedelta(hours=10)


class Token:
	def __init__(self, contract):
		self.headers = {
		    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
		}
		self.contract = contract
		self.chart = f"https://crunchy.network/#/token/{contract}_0?duration=1d&legend=price"
		self.buy = f"https://quipuswap.com/swap/tez-{contract}_0"
		self.dex = "Quipuswap"
		self.token_info = None
		self.valume_24h = None
		self.marketcap = None
		self.price = None
		self.metadata = None


	async def get_last_transactions(self, datetime: datetime, sender='KT1J8Hr3BP8bpbfmgGpRPoC9nAMSYtStZG43'):
		try:
			transactions = f'https://api.tzkt.io/v1/accounts/{self.contract}/operations'

			transactions_params = {
				'sender': sender,  # DEX contract
				'type': 'transaction',
				'timestamp.gt': f'{datetime.isoformat()+"Z"}'
			}

			async with httpx.AsyncClient(headers=self.headers) as client:
				response = await client.get(transactions, params=transactions_params)
				response.raise_for_status()
				return response.json()
		except Exception as e:
			return []

	async def get_token_info(self, address):
		try:
			token_info = f'https://api.tzkt.io/v1/tokens'

			token_params = {
				'contract': f'{address}'
			}

			async with httpx.AsyncClient(headers=self.headers) as client:
				response = await client.get(token_info, params=token_params)
				response.raise_for_status()
				return response.json()
		except Exception as e:
			print(e)
			return []

	async def get_token_chronic(self, deadline: str):
		try:
			token_chronic = f"https://api.crunchy.network/v1/tokens/{self.contract}/0/quotes/{deadline}"

			async with httpx.AsyncClient(headers=self.headers) as client:
				response = await client.get(token_chronic)
				response.raise_for_status()
				return response.json()
		except Exception as e:
			print(e)
			return []

	async def get_xtz_price(self):
		url = "https://api.coingecko.com/api/v3/simple/price?ids=tezos&vs_currencies=usd"
		try:
			async with httpx.AsyncClient(headers=self.headers) as client:
				response = await client.get(url)
				response.raise_for_status()
				data = response.json()
				price = data.get("tezos", {}).get("usd")
				return float(price)
		except Exception as e:
			return []

	def get_cats_count(self, value):
		cats = round(value / 2)
		return ('😺' * int(cats)).strip()

	def __str__(self):
		return f"Contract: {self.contract}\n" \
			f"Chart URL: {self.chart}\n" \
			f"Buy URL: {self.buy}\n" \
			f"DEX: {self.dex}\n" \
			f"Token Info: {self.token_info}\n" \
			f"Volume: {self.valume_24h}\n" \
			f"Market Cap: {self.marketcap}" \
			f"Price: {self.price}" 
