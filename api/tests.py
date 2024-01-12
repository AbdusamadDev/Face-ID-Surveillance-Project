import os

<<<<<<< HEAD
os.system('python3 test.py')
=======

# # importing all required libraries
# # import logging
# # from aiogram import Bot, Dispatcher, types
# # from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# # from aiogram.contrib.middlewares.logging import LoggingMiddleware
# #
# # API_TOKEN = '6195275934:AAEngBypgfNw3SwcV9uV_jdatZtMvojF9cs'
# # logging.basicConfig(level=logging.INFO)
# #
# # bot = Bot(token=API_TOKEN)
# # dp = Dispatcher(bot)
# # dp.middleware.setup(LoggingMiddleware())
# #
# #
# # @dp.message_handler(commands=['start', 'help'])
# # async def send_welcome(message: types.Message):
# #     keyboard = InlineKeyboardMarkup(row_width=2)
# #     view_button = InlineKeyboardButton("View service addresses", callback_data='view_addresses')
# #     suggest_button = InlineKeyboardButton("Suggest service", callback_data='suggest_service')
# #     keyboard.add(view_button, suggest_button)
# #
# #     welcome_text = "Welcome to the car service chat!\n\nHow can I help you today?"
# #     await message.reply(welcome_text, reply_markup=keyboard)
# #
# #
# # @dp.callback_query_handler(lambda c: c.data == 'view_addresses')
# # async def view_addresses(callback_query: types.CallbackQuery):
# #     # Logic to retrieve service addresses and show on Google Maps
# #     await bot.send_message(callback_query.from_user.id, "Viewing service addresses on Google Maps...")
# #
# #
# # @dp.callback_query_handler(lambda c: c.data == 'suggest_service')
# # async def suggest_service(callback_query: types.CallbackQuery):
# #     welcome_text = "Welcome to the car service chat!\n\nPlease provide details about the service you want to suggest."
# #     await bot.send_message(callback_query.from_user.id, welcome_text)

# #
# # if __name__ == '__main__':
# #     from aiogram import executor
# #     executor.start_polling(dp, skip_updates=True)
# # from typing import List
# #
# #
# # class Solution:
# #     def singleNumber(self, nums: List[int]) -> int:
# #         while True:
# #             target = nums[0]
# #             nums.remove(target)
# #             if target not in nums:
# #                 return target
# #             else:
# #                 nums = [k for k in nums if k != target]
# #
# # sl = Solution()
# # print(sl.singleNumber([10, 1, 10, 5, 1, 2, 2, 5, 7, 7, 7, 6, 88, 5, 6, 5]))
# # import re
# #
# #
# # class Solution:
# #     def isPalindrome(self, s: str) -> bool:
# #         string = re.sub('[^a-zA-Z0-9]', '', s).lower()
# #         return string == string[::-1]
# #
# # sl = Solution()
# # print(sl.isPalindrome("A man, a plan, a canal: Panama"))


# # class Solution:
# #     def strStr(self, haystack: str, needle: str) -> int:
# #         haystack = haystack.lower()
# #         for index, i in enumerate(haystack):
# #             if needle == haystack[index:index + len(needle)]:
# #                 return index
# #         return -1
# #
# #
# # sl = Solution()
# # print(sl.strStr("A man, a plan, a canal", "a"))
# # class Solution:
# #     def reverse(self, x: int) -> int:
# #         result = - int(str(x)[::-1][:-1]) if x < 0 else int(str(x)[::-1])
# #         if -2 ** 31 >= result or result >= 2 ** 31 - 1:
# #             return 0
# #         return result


# # sl = Solution()
# # print((2 ** 31 - 1) > 9646324351)
# # print(sl.reverse(1534236469))
# import random
# from string import ascii_letters

# example = {
#     "one": {"longitude": 7864234234, "latitude": 123422},
#     "two": {"longitude": 7823464, "latitude": 122342},
#     "three": {"longitude": 7862344, "latitude": 234122},
# }

# clients = list(example.values())
# print(clients)
# {
#     "Content-Length": "",
#     "Content-Type": "text/plain",
#     "Host": "localhost:8000",
#     "User-Agent": "python-requests/2.25.1",
#     "Accept-Encoding": "gzip, deflate",
#     "Accept": "*/*",
#     "Connection": "keep-alive",
#     "Longitude": "19",
#     "Latitude": "72",
# }
import time

index = 0
while True:
    index += 1
    print("Elapsed time: ", index)
    time.sleep(1)
>>>>>>> parent of 3a9a2f7 (Autostart using nginx)
