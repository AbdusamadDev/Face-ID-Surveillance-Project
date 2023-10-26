# def check_power(num):
#     """Checks if number is power of four"""
#     return int(str(num)[-1]) in (4, 6)

# a = 4 ** 25
# b = 5 ** 25
# c = 8 ** 2
# print(check_power(a))
# print(check_power(b))
# print(check_power(c))
# ___________________________________________________________________________
# sentence = "Django bu web sahifalar ishlab chiqish uchun web Framework hisoblanadi"
# sentence_list = sentence.split(" ")
# reverse = sentence_list[::-1]
# reversed_sentence = ""
# for word in reverse:
#     capitalized = word.capitalize()
#     reversed_sentence += capitalized
#     reversed_sentence += " "
# reversed_sentence = reversed_sentence.strip()
# print(reversed_sentence)
# ___________________________________________________________________________
# password = "$enterpassword$"
# encrypted_password = ""
# for letter in password:
#     encryption = chr(ord(letter) + 5)
#     encrypted_password += encryption

# print(encrypted_password)
# ___________________________________________________________________________
# word = "Dastur uchun matn"

# unli = ["a", "e", "i", "o", "u", "o'"]
# new_word = ""
# for i in word:
#     if i in unli:
#         new_word += "$"
#     else:
#         new_word += i

# print(new_word)
# ___________________________________________________________________________
# passwd = "$enterpassword$"
# percentage = 0
# score = 0
# lowest = [
#     "a", "b", "c", "d", "e", "f", "g", "h", "i",
#     "j", "k", "l", "m", "n", "o", "p", "q", "r",
#     "s", "t", "u", "v", "w", "x", "y", "z",
# ]


# low = [
#     'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
#     'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
#     'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
# ]
# high = [
#     "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"
# ]
# highest = [
#     "!", "@", "#", "$", "%", "^", "&", "*", "(",
#     ")", ".", "_", "+", "-", "*", "/"
# ]
# length = set()
# for letter in passwd:
#     if letter in lowest:
#         length.add("lst")
#     elif letter in low:
#         length.add("l")
#     elif letter in high:
#         length.add("h")
#     elif letter in highest:
#         length.add("hst")
# index = len(length)
# label = [
#     "Juda kuchsiz - 25 %",
#     "Qoniqarli - 50 %",
#     "Kuchli - 75 %",
#     "Juda kuchli va havfsiz - 100 %"
# ]
# daraja =  label[index - 1]
# print(daraja)
# ___________________________________________________________________________
