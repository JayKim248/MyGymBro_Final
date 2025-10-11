def weird(num):
    digits = [int(d) for d in str(num)]
    add_on = 0
    for i in range(len(digits)):
        add_on += digits[i]
    if num % add_on == 0:
        return 1
    else:
        return 0

    


n = int(input())
result = 0
for i in range(1, n+1):
    result += weird(i)

print(result)


