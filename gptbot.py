import aiogram
from loguru import logger
from telebot import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import Base as b
from datetime import datetime
import main as m
import configparser
from apscheduler.schedulers.asyncio import AsyncIOScheduler



config = configparser.ConfigParser()
config.read('config.ini')
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")




class nw_mess(StatesGroup):
    mess = State()
    summ = State()



logger.add('debug.log', format='{time} {level} {message}',
        level='DEBUG', rotation='10 MB', compression='zip'
        )

bot = aiogram.Bot(config.get('Settings', 'API_key_bot'))
dp = aiogram.Dispatcher(bot,storage=MemoryStorage())






async def d_pay():
    scheduler.add_job(send_pay,  "cron", day_of_week="mon-sun", hour = "4", minute="10")

async def send_pay():
    b.new_all_kol_req(0)
            






@logger.catch
@dp.message_handler(commands=['start'],state='*')
async def start(message: aiogram.types.Message,state: FSMContext):
    await state.finish()
    if not(b.av_in_db(message.chat.id)):
        date_end='2038-01-01'
        date_end=datetime.strptime(date_end, '%Y-%m-%d')
        date_end=date_end.date()
        b.new_user(message.chat.id,message.chat.username,0,date_end)
        if (b.date_p_s(message.chat.id).date()>=date_end):
            kol=100
        else:
            kol=250
        await bot.send_message(message.chat.id,text=f'Чтобы получить ответ на интересующий вопрос, просто отправьте сообщение боту',parse_mode=types.ParseMode.MARKDOWN)
        if (b.kol_req_r(message.chat.id)<=kol):   
            await nw_mess.mess.set()
        else: 
            await bot.send_message(message.chat.id,text=f'Достигнут лимит запросов',parse_mode=types.ParseMode.MARKDOWN)
    else:
        dt='2038-01-01'
        dt=datetime.strptime(dt, '%Y-%m-%d')
        dt=dt.date()
        if (b.date_p_s(message.chat.id).date()>=dt):
            kol=100
        else:
            kol=250
        await bot.send_message(message.chat.id,text=f'Чтобы получить ответ на интересующий вопрос, просто отправьте сообщение боту\nКоличество запросов в день: {kol}')
        if (b.kol_req_r(message.chat.id)<=kol):   
            await nw_mess.mess.set()
        else: 
            await bot.send_message(message.chat.id,text=f'Достигнут лимит запросов',parse_mode=types.ParseMode.MARKDOWN)
       


@logger.catch
@dp.message_handler(commands=['menu'],state='*')
async def menu(message: aiogram.types.Message,state: FSMContext):
    await state.finish()
    dt='2038-01-01'
    dt=datetime.strptime(dt, '%Y-%m-%d')
    dt=dt.date()
    kolr=b.kol_req_r(message.chat.id)
    if (b.date_p_s(message.chat.id).date()>=dt):
        kol=100
    else:
        kol=250
    await bot.send_message(message.chat.id,text=f'Отправьте интересующий вас вопрос сообщением боту\nКоличество запросов использованных за день: *{kolr}*/*{kol}*', parse_mode=types.ParseMode.MARKDOWN)
    if (b.kol_req_r(message.chat.id)<=kol):   
        await nw_mess.mess.set()
    else: 
        await bot.send_message(message.chat.id,text=f'Достигнут лимит запросов',parse_mode=types.ParseMode.MARKDOWN)

@logger.catch
@dp.message_handler(commands=['GPT'],state='*')
async def GPT(message: aiogram.types.Message,state: FSMContext):
    await state.finish()
    dt='2038-01-01'
    dt=datetime.strptime(dt, '%Y-%m-%d')
    dt=dt.date()
    if (b.date_p_s(message.chat.id).date()>=dt):
        kol_m=15
    else:
        kol_m=100
    if (b.kol_req_r(message.chat.id)<=kol_m):   
        await nw_mess.mess.set()
    else: 
        await bot.send_message(message.chat.id,text=f'Достигнут лимит запросов',parse_mode=types.ParseMode.MARKDOWN)



@logger.catch
@dp.message_handler(state=nw_mess.mess)
async def GPT_otvet(message: aiogram.types.Message, state: FSMContext):
    try:
        await state.update_data(mess=message.text)
        datam = await state.get_data()
        kol=b.kol_req_r(message.chat.id)+1
        b.new_kol_req(message.chat.id,message.chat.username,kol)
        del_s=await bot.send_message(message.chat.id,text=f'Пожалуйста, подождите ответа бота...')
        del_s=del_s.message_id
        otvet= await m.create_chat_completion(str(datam['mess']))
        await bot.delete_message(message.chat.id,del_s)
        if otvet is not None:
            if len(otvet)<=4096:
                await bot.send_message(message.chat.id,text=f'{otvet}')
            else:
                for k in range(0, len(otvet), 4096):
                    await bot.send_message(message.chat.id, text=f'{otvet[k:k+4096]}')
        else:
            await bot.send_message(message.chat.id,text=f'ChatGpt не смог ответить на данный вопрос, попробуйте поставить вопрос по-другому или задать еще раз')
        
        await state.finish()
        await GPT(message,state)
    except:
        await state.finish()
        await bot.delete_message(message.chat.id,del_s)
        await bot.send_message(message.chat.id,text=f'ChatGpt не смог ответить на данный вопрос, попробуйте поставить вопрос по-другому или задать еще раз')
        await GPT(message,state)



async def start_task(dp):
    scheduler.start()
    await d_pay()




if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False,on_startup=start_task)
    

