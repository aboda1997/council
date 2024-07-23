class Employees(object): 
    def __init__(self,name ,age )->None:
        self.name = name 
        self.age = age 




class SuperVision(Employees):
    def __init__(self, name, age , password): 
        super().__init__( name ,  age) 
        self.password = password 


class Chefs(Employees):
    def leave_(self, days): 
        return "now after " + str (days) + " days" + "i leave the project"

emp = Employees("ahmed", 25) 
emp1 = SuperVision("abdelrahman", 25, "hello") 

print(emp1.name)
print(issubclass(SuperVision , Employees))
