def sum(* temp):
    s=0
    for i in temp:
        s+=i
    return s
def sub(* temp):
    s1=0
    for i in temp:
        s1-=i
    return s1
def mul(* temp):
    x=1
    for i in temp:
        x*=i
    return x

def div(a,b):
        if b<=0:
            raise Exception("Enter a correct num  must be positive and non zero")
        return a/b
def mode(a,b):
    if b<=0:
        raise Exception("Enter a correct num  must be positive and non zero")
    return a%b

if __name__=='__main__':

    print("sum",sum(25,23))
    print("subtract",sub(50,-25))
    print("multiply",mul(50,56))
    print("mode",mode(23,5))
  

    try:

        print("Divide",div(24,5))
    except Exception as e:
        print("Error in Division",e)


    
