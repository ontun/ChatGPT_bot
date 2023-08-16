import openai

import configparser
config = configparser.ConfigParser()


config.read('config.ini')
openai.api_key=config.get('Settings', 'API_key_gpt')

models = openai.Model.list()


async def create_chat_completion(mess):
    chat_completion = await  openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=[{"role": "user", "content": mess}])
    return chat_completion.choices[0].message.content