from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.environ.get('HOST')
PORT = int(os.environ.get('PORT'))
