def ssalary( salary):


    if salary<=500000:
       return ("Not intrest")
    elif salary<=1000000:
        return (salary-salary*0.05)
    else:
        return (500000*0+500000*0.5+(salary-1000000)*0.1)



# salary=int(input("Enter a salary :"))
# ans=ssalary(salary)
# print("Toral salary :",ans)
