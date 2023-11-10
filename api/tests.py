from typing import List

#
#
# class Solution:
#     """
#     Give a list of integers that represent the solution for each target
#     and returns a list of integers that represent the solution for each
#     target and returns a list of integers that represent the solution
#     for each target and returns
#     """
#
#     def __init__(self, nums: List[int], target: int):
#         self.nums = nums
#         self.target = target
#         self.length = len(nums)
#         self.validate()
#
#     def validate(self):
#         assert 2 <= self.length <= 10 ** 4, ValueError("Length must be between 2 and 10**4")
#         for j in self.nums:
#             if not -10 ** 9 <= j <= 10 ** 9:
#                 raise ValueError("List contains improper amount of number(s)")
#         assert -10 ** 9 <= self.target <= 10 ** 9, ValueError("Target must be between 2 and 10**9")
#
#     def two_sum(self) -> List[int]:
#         lookup = {}  # This dictionary will store the numbers and their indices.
#         for i, num in enumerate(self.nums):
#             complement = self.target - num  # Calculate the number needed to add to 'num' to reach the target.
#             if complement in lookup:
#                 # If the complement is found in the dictionary, return the pair of indices.
#                 return [lookup[complement], i]
#             lookup[num] = i  # If not found, add the number and its index to the dictionary.
#         return []  # If no pair is found, which shouldn't happen as per problem definition, return an empty list.
#
#
# a = [2, 7, 11, 15]
# tg = 9
# solution = Solution(a, tg)
# print(solution.two_sum())


# class Solution:
#     def isPalindrome(self, x: int) -> bool:
#         return str(x)[:(len(str(x)) // 2)] == str(x)[(len(str(x)) // 2) + 1:][::-1] if len(str(x)) % 2 == 1 else str(x)[:(len(str(x)) // 2)] == str(x)[(len(str(x)) // 2):][::-1]
#
#
# sl = Solution()
# print(sl.isPalindrome(540845))
# print(sl.isPalindrome(55655))
# print(sl.isPalindrome(587767785))
#
#
# from itertools import zip_longest
# import logging
#
# logging.basicConfig(level=logging.INFO)
#
#
# class Solution:
#     def is_the_same(self, tpl: tuple):
#         return len(set(tpl)) == 1
#
#     def longestCommonPrefix(self, strs: List[str]) -> str:
#         if not strs:
#             return ""
#         if len(strs) == 1:
#             return strs[0]
#
#         result = ""
#         target = list(zip_longest(*(list(word) for word in strs)))
#         for word in target:
#             if self.is_the_same(word):
#                 result += word[0]
#             else:
#                 return result
#         return result
#
#
# sl = Solution()
# logging.info(sl.longestCommonPrefix(["flower", "flower", "flower", "flower"]))
import time


# class Solution:
#         def isValid(self, s: str) -> bool:
#             while '()' in s or '[]' in s or '{}' in s:
#                 s = s.replace('()', '').replace('[]', '').replace('{}', '')
#             return False if len(s) != 0 else True
#
# sl = Solution()
# print(sl.isValid("{[]{}{{{{}}}{}{}(()))}{}}"))
# print(sorted(""))

class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        if len(nums) not in range(1, (3 * (10 ** 4))):
            return 0
        for i in nums:
            if i not in range(-100, 100):
                print(i)
                return 0
        sorted_nums = nums.sort()
        if sorted_nums != nums:
            print(sorted_nums)
            print(nums)
            return 0
        return len(nums) - len(list(set(nums)))


sl = Solution()
print(sl.removeDuplicates([5, 5, 5, 5, 7, 9, 10, 11]))
