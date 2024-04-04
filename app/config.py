import os
from dotenv import load_dotenv


def build_dotenv() -> None:
	dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
	if not os.path.exists(dotenv_path):
		raise FileNotFoundError("File '.env' not exists in config_ derectory!")

	load_dotenv(dotenv_path)

class Configuration:
	build_dotenv()
	TOKEN = os.environ.get('TOKEN')
	TOKEN_CONTRACT = os.environ.get('TOKEN_CONTRACT')
	ANIMATION_PATH = os.environ.get('ANIMATION_PATH')
