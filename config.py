import os

class Config:
    API_ID = os.environ.get('API_ID', 10471716)
    API_HASH = os.environ.get('API_HASH', 'f8a1b21a13af154596e2ff5bed164860')
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '6916875347:AAEVxR4cO_sIBB6V57ANA92pHKxzw9G3yX0')


class Telegram:
    AUTH_USER_ID = os.environ.get('AUTH_USER_ID', '6883997969')


class Ai:
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')

class Database:
    REDIS_URI = os.environ.get('REDIS_URI', 'redis-10487.c62.us-east-1-4.ec2.redns.redis-cloud.com:10487')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '1W4xupLZHETTtjpy6zpeBseMad5os1qo')
