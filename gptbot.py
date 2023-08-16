import asyncio
import logging
from datetime import datetime
from aiohttp import ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import configparser
import openai
import Base as b
import main as m


config = configparser.ConfigParser()
config.read('config.ini')
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")



logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.get('Settings', 'API_key_bot'))
dp = Dispatcher(bot)
loop = asyncio.get_event_loop()


async def d_pay():
    scheduler.add_job(send_pay, "cron", day_of_week="mon-sun", hour="4", minute="10")


async def send_pay():
    b.new_all_kol_req(0)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not b.av_in_db(message.chat.id):
        date_end = '2038-01-01'
        date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        b.new_user(message.chat.id, message.chat.username, 0, date_end)
        if b.date_p_s(message.chat.id).date() >= date_end:
            kol = 100
        else:
            kol = 250
        await message.reply(f'Чтобы получить ответ на интересующий вопрос, '
                            f'просто отправьте сообщение боту')
    else:
        dt = '2038-01-01'
        dt = datetime.strptime(dt, '%Y-%m-%d').date()
        if b.date_p_s(message.chat.id).date() >= dt:
            kol = 100
        else:
            kol = 250
        await message.reply(f'Чтобы получить ответ на интересующий вопрос, '
                            f'просто отправьте сообщение боту\nКоличество запросов в день: <b>{kol}</b>',
                            parse_mode='HTML')


@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    dt = '2038-01-01'
    dt = datetime.strptime(dt, '%Y-%m-%d').date()
    kolr = b.kol_req_r(message.chat.id)
    if b.date_p_s(message.chat.id).date() >= dt:
        kol = 100
    else:
        kol = 250
    await bot.send_message(message.chat.id, f'Отправьте интересующий вас вопрос сообщением боту\n'
                                            f'Количество запросов использованных за день: <b>{kolr}/{kol}</b>',
                           parse_mode='HTML')


@dp.message_handler(content_types=['text', ])
async def GPT_otvet(message: types.Message):
    try:
        dt = '2038-01-01'
        dt = datetime.strptime(dt, '%Y-%m-%d').date()
        if b.date_p_s(message.chat.id).date() >= dt:
            kol_m = 100
        else:
            kol_m = 250

        if b.kol_req_r(message.chat.id) <= kol_m:
            datam = message.text
            kol = b.kol_req_r(message.chat.id) + 1
            b.new_kol_req(message.chat.id, message.chat.username, kol)
            del_s = await bot.send_message(message.chat.id, f'Пожалуйста, подождите ответа бота...')
            openai.aiosession.set(ClientSession())
            otvet = await m.create_chat_completion(datam)
            await openai.aiosession.get().close()
            await bot.delete_message(message.chat.id, del_s.message_id)
            if otvet:
                if len(otvet) <= 4096:
                    await bot.send_message(message.chat.id, otvet)
                else:
                    for k in range(0, len(otvet), 4096):
                        await bot.send_message(message.chat.id, otvet[k:k + 4096])
            else:
                await bot.send_message(message.chat.id, 'ChatGpt не смог ответить на данный вопрос, '
                                                        'попробуйте поставить вопрос по-другому или задать еще раз')

        else:
            await bot.send_message(message.chat.id, 'Достигнут лимит запросов')

    except:
        await bot.delete_message(message.chat.id, del_s.message_id)
        await bot.send_message(message.chat.id, 'ChatGpt не смог ответить на данный вопрос, '
                                                'попробуйте поставить вопрос по-другому или задать еще раз')


async def start_task():
    scheduler.start()
    await d_pay()


if __name__ == "__main__":
    loop.create_task(start_task())
    executor.start_polling(dp, skip_updates=True)
