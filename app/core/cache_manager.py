import pickle
import os
import asyncio
from datetime import timedelta

class CacheManager:
    def __init__(self, cache_file='db/transactions_cache.pkl'):
        self.cache_file = cache_file
        self.processed_transactions = self.load_cache()  # Загрузка кэша при инициализации
        self.cache_cleanup_interval = timedelta(hours=1)  # Интервал очистки кэша

    def load_cache(self):
        # Загрузка кэша из файла
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        return set()

    def save_cache(self):
        # Сохранение кэша в файл
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.processed_transactions, f)

    async def clear_cache(self):
        # Очистка кэша и его сохранение
        self.processed_transactions.clear()
        self.save_cache()
        print("Cache cleared.")

    async def start_cache_cleanup_loop(self):
        # Запуск цикла очистки кэша
        while True:
            await asyncio.sleep(self.cache_cleanup_interval.total_seconds())
            await self.clear_cache()
