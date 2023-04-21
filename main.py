from aiogram import Bot, executor, types, Dispatcher


import sqlite3

TOKEN_API = "6127202910:AAFj_01hnVbpWZxyCTMW2Kh70wTJj1e_vtI"

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

owner_id = '716470590'

async def on_startup(_):
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_info (id INTEGER)''')

    conn.commit()
    conn.close()
    print("Bot was startet!")


conn = sqlite3.connect('user_info.db')
cursor = conn.cursor()

cursor.execute('SELECT id FROM user_info')

results = cursor.fetchall()


@dp.message_handler(content_types=['new_chat_members'])
async def on_user_join_chat(message: types.Message):
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    user_id = message.new_chat_members[0].id
    cursor.execute("INSERT INTO user_info (id) VALUES (?)", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

@dp.message_handler(commands=['leave'])
async def leave_handler(message: types.Message):

    user_id = message.from_user.id

    cursor.execute(f"DELETE FROM user_info WHERE id={user_id}")
    conn.commit()

    if cursor.rowcount == 0:
        await message.reply("Вашого id не знайдено")
    else:
        await message.reply("Ви були успішно видалені з бази даних")


@dp.message_handler(commands='join')
async def join_handler(message: types.Message):

    user_id = message.from_user.id

    cursor.execute(f"SELECT * FROM user_info WHERE id={user_id}")
    if cursor.fetchone() is not None:
        await message.reply("Ви вже є в базі Даних!")
        return

    cursor.execute(f"INSERT INTO user_info (id) VALUES ({user_id})")
    conn.commit()

    await message.reply("Ви успішно додані до бази даних")


@dp.message_handler(content_types=['photo'])
async def photo(message: types.Message):
    for user_id in results:
        if message.photo and str(message.from_user.id) == owner_id:
            caption = message.caption or ""
            if message.caption is not None and message.caption[0:5] == "/news":
                photo_id = message.photo[-1].file_id

                await bot.send_photo(chat_id=user_id[0], photo=photo_id, caption=caption[5:])
                print(f"я надіслав фото {user_id}")
            elif message.caption is None:
                print("я не надіслав фото")
                break

@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    for user_id in results:
        if message.text[0:5] == "/send" and str(message.from_user.id) == owner_id:
            await bot.send_message(text=message.text[5:], chat_id=user_id[0])
        elif message.text[0:5] == "/send":
            await message.reply(text="ви не є власником")


if __name__ == '__main__':
     executor.start_polling(dp, on_startup=on_startup)


