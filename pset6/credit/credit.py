import sys
# get credit card number
n = input("Number: ")
# check it's the right length
if len(n) not in [13, 15, 16]:
    print("INVALID")
    sys.exit(1)
# Apply Luhn's algorithm in stages
# Multiply every other digit by 2 and store
a = []
for i in n[-2::-2]:
    a.append(str(int(i * 2)))
# if number in list double digits, separate out
c = []
for i in a:
    if int(i) >= 10:
        c.append(i[0])
        c.append(i[1])
    else:
        c.append(i)
# make numbers and add together
print(c)
odd = 0
for i in c:
    odd += int(i)
# add together other set of digit
b = []
for i in n[::-2]:
    b.append(i)
# make numbers and add together
print(b)
even = 0
for i in b:
    even += int(i)
# last digit needs to be 0 to be valid
print(odd,even)
if (odd + even) % 10 != 0:
    print("INVALID")
    sys.exit(1)
#match numbers to cards
if n[0:1] in ["34", "37"]:
    print("AMEX")
elif n[0:1] in ["51", "52", "53", "54", "55"]:
    print("MASTERCARD")
elif n[0] == "4":
    print("VISA")
else:
    print("INVALID")
    sys.exit(1)












"""


All American Express numbers start with 34 or 37; most MasterCard numbers start with 51, 52, 53, 54, or 55
 and all Visa numbers start with 4.

Multiply every other digit by 2, starting with the number’s second-to-last digit, and then add those products’ digits together.
Add the sum to the sum of the digits that weren’t multiplied by 2.
If the total’s last digit is 0 (or, put more formally, if the total modulo 10 is congruent to 0), the number is valid!
"""