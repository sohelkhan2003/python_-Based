def sum(a,b):
    return a+b
def sub(a,b):
    return a-b
def  mul(a,b):
    return a*b
def  div(a,b):
    try :
        if b<0:
            raise Exception("Enter a positive num  ")
        return a/b
    except Exception as e:
        print(e)
        return None
def mode(a,b):
    return (a%b)
def power(a,b):
    return a**b
def flore(a,b):
    return a//b
def factor(n):
    s=0
    for i in range(1,n+1):
        if n%i==0:
            s=i
            return s

