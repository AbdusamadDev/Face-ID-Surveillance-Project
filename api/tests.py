# # from typing import List
# #
# # #
# # #
# # # class Solution:
# # #     """
# # #     Give a list of integers that represent the solution for each target
# # #     and returns a list of integers that represent the solution for each
# # #     target and returns a list of integers that represent the solution
# # #     for each target and returns
# # #     """
# # #
# # #     def __init__(self, nums: List[int], target: int):
# # #         self.nums = nums
# # #         self.target = target
# # #         self.length = len(nums)
# # #         self.validate()
# # #
# # #     def validate(self):
# # #         assert 2 <= self.length <= 10 ** 4, ValueError("Length must be between 2 and 10**4")
# # #         for j in self.nums:
# # #             if not -10 ** 9 <= j <= 10 ** 9:
# # #                 raise ValueError("List contains improper amount of number(s)")
# # #         assert -10 ** 9 <= self.target <= 10 ** 9, ValueError("Target must be between 2 and 10**9")
# # #
# # #     def two_sum(self) -> List[int]:
# # #         lookup = {}  # This dictionary will store the numbers and their indices.
# # #         for i, num in enumerate(self.nums):
# # #             complement = self.target - num  # Calculate the number needed to add to 'num' to reach the target.
# # #             if complement in lookup:
# # #                 # If the complement is found in the dictionary, return the pair of indices.
# # #                 return [lookup[complement], i]
# # #             lookup[num] = i  # If not found, add the number and its index to the dictionary.
# # #         return []  # If no pair is found, which shouldn't happen as per problem definition, return an empty list.
# # #
# # #
# # # a = [2, 7, 11, 15]
# # # tg = 9
# # # solution = Solution(a, tg)
# # # print(solution.two_sum())
# #
# #
# # # class Solution:
# # #     def isPalindrome(self, x: int) -> bool:
# # #         return str(x)[:(len(str(x)) // 2)] == str(x)[(len(str(x)) // 2) + 1:][::-1] if len(str(x)) % 2 == 1 else str(x)[:(len(str(x)) // 2)] == str(x)[(len(str(x)) // 2):][::-1]
# # #
# # #
# # # sl = Solution()
# # # print(sl.isPalindrome(540845))
# # # print(sl.isPalindrome(55655))
# # # print(sl.isPalindrome(587767785))
# # #
# # #
# # # from itertools import zip_longest
# # # import logging
# # #
# # # logging.basicConfig(level=logging.INFO)
# # #
# # #
# # # class Solution:
# # #     def is_the_same(self, tpl: tuple):
# # #         return len(set(tpl)) == 1
# # #
# # #     def longestCommonPrefix(self, strs: List[str]) -> str:
# # #         if not strs:
# # #             return ""
# # #         if len(strs) == 1:
# # #             return strs[0]
# # #
# # #         result = ""
# # #         target = list(zip_longest(*(list(word) for word in strs)))
# # #         for word in target:
# # #             if self.is_the_same(word):
# # #                 result += word[0]
# # #             else:
# # #                 return result
# # #         return result
# # # #
# # #
# # # sl = Solution()
# # # logging.info(sl.longestCommonPrefix(["flower", "flower", "flower", "flower"]))
# # import time
# #
# #
# # # class Solution:
# # #         def isValid(self, s: str) -> bool:
# # #             while '()' in s or '[]' in s or '{}' in s:
# # #                 s = s.replace('()', '').replace('[]', '').replace('{}', '')
# # #             return False if len(s) != 0 else True
# #
# # # sl = Solution()
# # # print(sl.isValid("{[]{}{{{{}}}{}{}(()))}{}}"))
# # # print(sorted(""))
# #
# # # class Solution:
# # #     def removeDuplicates(self, nums: List[int]) -> int:
# # #         if len(nums) not in range(1, (3 * (10 ** 4))):
# # #             return 0
# # #         for i in nums:
# # #             if i not in range(-100, 100):
# # #                 return 0
# # #         sorted_nums = sorted(nums)
# # #         if sorted_nums != nums:
# # #             return 0
# # #         return len(nums) - len(list(set(nums)))
# # # #
# # #
# # # sl = Solution()
# # # # print(sl.removeDuplicates([1, 1, 2]))
# # #
# # # import re
# # #
# # #
# # # class Solution:
# # #     def lengthOfLastWord(self, s: str) -> int:
# # #         pattern = re.compile(r'^[a-zA-Z ]+$')
# # #
# # #         if not pattern.match(s):
# # #             return 0
# # #         if 1 >= len(s) or len(s) >= 10 ** 4:
# # #             return 0
# # #         if len(s.split(' ')) <= 0:
# # #             return 0
# # #         return len(s.strip().split()[-1])
# #
# #
# # # sl = Solution()
# # # print(sl.lengthOfLastWord("a"))
# # # class Solution:
# # #     def searchInsert(self, nums: List[int], target: int) -> int:
# # #         if len(nums) <= 0 or len(nums) >= 10 ** 4:
# # #             print("nums is not in range")
# # #             return 0
# # #         for vl in nums:
# # #             if vl <= -10 ** 4 or vl >= 10 ** 4:
# # #                 print("vl is not in range")
# # #                 return 0
# # #         if len(list(set(nums))) != len(nums) or nums != sorted(nums):
# # #             print("not distinct or not sorted")
# # #             return 0
# # #         if target <= -10 ** 4 or target >= 10 ** 4:
# # #             print("target is not in range")
# # #             return 0
# # #         if target in nums:
# # #             return nums.index(target)
# # #         else:
# # #             for index, num in enumerate(nums):
# # #                 if num <= target <= nums[index + 1]:
# # #                     return index + 1
# #
# #
# # # sl = Solution()
# # # print(sl.searchInsert([1, 3, 5, 6], 0))
# #
# # class Solution:
# #     def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
# #         sorted_nums = sorted(nums1 + nums2)
# #         if len(sorted_nums) % 2 == 1:
# #             return sorted_nums[len(sorted_nums) // 2]
# #         else:
# #             return sorted_nums[len(sorted_nums) // 2 - 1] + (sorted_nums[len(sorted_nums) // 2] - (
# #                 sorted_nums[len(sorted_nums) // 2 - 1])) / 2
# #
# # #
# # # sl = Solution()
# # # print(sl.findMedianSortedArrays([1, 2, 87, 5, 3], [3, -5, 7, 1, 2]))
# # importing all required libraries
# import os


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
