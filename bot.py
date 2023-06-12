import os

import openai
import logging

import config

from gpytranslate import Translator

from aiogram import Bot, Dispatcher, executor, types


previous_responses = {}

filename = "users.txt"

# log
logging.basicConfig(level=logging.INFO)

# init translator
t = Translator()

#init bot
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)

# init openai
openai.api_key = config.OPENAI_TOKEN

# a made handler to work with openai
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text

    if not os.path.exists(filename):
        with open(filename, "w") as f:
            pass

    try:
        with open(filename, "r+") as f:
            contents = f.read()
            if str(user_id) not in contents:
                f.seek(0, 2)
                f.write(str(user_id) + "\n")
    except IOError as e:
        print(f"An error occurred while accessing the file: {e}")

    # Save all history
    if user_id not in previous_responses:
        previous_responses[user_id] = []
    previous_responses[user_id].append(user_message)

    # Create a context from whole history
    context = " ".join(previous_responses[user_id])

    # Create an answer with OPEN AI
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{context}\n",
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        ).choices[0].text

        await message.answer("ChatGPT: Генерирую ответ ...")
        translated_result = await t.translate(response, targetlang="ru")
        await message.answer(translated_result.text)
    except Exception as e:
        print(f"Ошибка при генерации ответа: {e}")
        response = "Извините, возникла ошибка при генерации ответа."

    # Update answers history
    previous_responses[user_id].append(response)


# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
