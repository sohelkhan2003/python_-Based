import calculator1 

print("Welcome to the calculator")
n = int(input("Enter a number: "))
ans = n

while True:
    o = input("Enter an operator ('+','-','*','/','%','**','//') or '=' to finish: ")

    if o == '=':
        break
    else:
        s = int(input("Enter another number: "))
        if o == '+':
            ans = calculator1.sum(ans, s)
        elif o == '-':
            ans = calculator1.sub(ans, s)
        elif o == '*':
            ans = calculator1.mul(ans, s)
        elif o == '/':
            ans = calculator1.div(ans, s)
        elif o == '%':
            ans = calculator1.mode(ans, s)
        elif o == '**':
            ans = calculator1.power(ans, s)
        elif o == '//':
            ans = calculator1.floordiv(ans, s)
        else:
            print("Wrong input. Try again.")

print("Ans:", ans)


