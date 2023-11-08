# from typing import List
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
class Solution:
    def romanToInt(self, s: str) -> int:
        lookup = {
            "I": 1,
            "V": 5,
            "X": 10,
            "L": 50,
            "C": 100,
            "D": 500,
            "M": 1000,
        }
        result = 0
        for i in s:
            result += lookup[i]
        return result


num = "MMCMXCIX"

sl = Solution()
print(sl.romanToInt(num))
