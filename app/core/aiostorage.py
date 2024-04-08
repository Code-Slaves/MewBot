import json
import aiofiles

class ChatStorage():
    def __init__(self, path):
        self.path = path

    async def add_data(self, key, value):
        data = {}  # Используем словарь для хранения данных по ключам
        try:
            async with aiofiles.open(self.path, "r") as file:
                content = await file.read()
                if content:
                    data = json.loads(content)
        except FileNotFoundError:
            pass

        if key not in data:
            data[key] = []

        if value not in data[key]:
            data[key].append(value)
            async with aiofiles.open(self.path, "w") as file:
                await file.write(json.dumps(data))

    async def remove_data(self, key, value):
        try:
            async with aiofiles.open(self.path, "r") as file:
                data = json.loads(await file.read())
            if key in data and value in data[key]:
                data[key].remove(value)
                async with aiofiles.open(self.path, "w") as file:
                    await file.write(json.dumps(data))
        except (FileNotFoundError, ValueError):
            pass

    async def get_all_data(self, key):
        try:
            async with aiofiles.open(self.path, "r") as file:
                data = json.loads(await file.read())
                if isinstance(data, dict):  # Убедимся, что data является словарем
                    return data.get(key, [])
                else:
                    return []  # Возвращает пустой список, если data не словарь
        except (FileNotFoundError, json.JSONDecodeError):
            return []  # Возвращает пустой список, если файл не найден или пуст
