import httpx
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal
import json


dt = datetime.utcnow().replace(microsecond=0) - timedelta(hours=10)


class Token:
	def __init__(self, contract):
		self.headers = {
		    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
		}
		self.contract = contract
		token_info = self.get_token_info()[0]
		self.metadata = token_info['metadata']
		self.supply = token_info['totalSupply']
		self.chart = f"https://crunchy.network/#/token/{contract}_0?duration=1d&legend=price"
		self.buy = f"https://quipuswap.com/swap/tez-{contract}_0"
		self.dex = "Quipuswap"


	async def get_last_transactions(self, datetime: datetime, sender='KT1J8Hr3BP8bpbfmgGpRPoC9nAMSYtStZG43'):
		try:
			transactions = f'https://api.tzkt.io/v1/tokens/transfers'

			transactions_params = {
				'type': 'transaction',
				'sender': sender,  # DEX contract
				'token.contract': self.contract,
				'type': 'transaction',
				'timestamp.gt': f'{datetime.isoformat()+"Z"}',
				'limit': 1000,
				"select": "transactionId,to,from,amount"
			}

			async with httpx.AsyncClient(headers=self.headers) as client:
				response = await client.get(transactions, params=transactions_params)
				response.raise_for_status()
				return response.json()
		except Exception as e:
			return []

	async def get_hesh(self, transacton_id):
		try:
			url = f'https://api.tzkt.io/v1/operations/transactions'

			filter_params = {
				'id': transacton_id,
				'status': 'applied',
				"select": "hash"
			}

			async with httpx.AsyncClient(headers=self.headers) as client:
				response = await client.get(url, params=filter_params)
				response.raise_for_status()

				url = f"https://api.tzkt.io/v1/operations/{response.json()[0]}"
				filter_params["select"] = "parameter"
				del filter_params["id"]
				operation_type = await client.get(url, params=filter_params)
				if operation_type.json()[0]["parameter"]["entrypoint"] != "swap":
					return []
				return response.json()
		except Exception as e:
			return []

	def get_token_info(self):
		try:
			token_info_url = 'https://api.tzkt.io/v1/tokens'

			token_params = {
				'contract': self.contract,
				'select': "metadata,totalSupply"
			}

			with httpx.Client(headers=self.headers) as client:
				response = client.get(token_info_url, params=token_params)
				response.raise_for_status()  # Проверяем, не вернул ли сервер ошибку
				return response.json()  # Возвращаем данные в формате JSON
		except Exception as e:
			return []  # Возвращаем пустой список в случае ошибки

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

	def get_cats_count(self, value, min_value_filter):
		maximum = 10
		cats = round(value / min_value_filter)
		if cats > maximum:
			return ('😺' * 10)
		else:
			return ('😺' * int(cats))

