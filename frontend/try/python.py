""" with open('file.txt' , 'r') as file:
     data = file.readline()
     print(data)



with open("newFile.txt" , "r") as file:
    lines = ["hello new world\n" ,"my name is abdelrahman"]
    data = file.read().split('\n')
    print(data)


lst = ['hello' , "new" , 'year' , 'facenews', 'shutdown']

backwords_lst = map(lambda x : x[::-1] , lst) 
for item in backwords_lst: 
     print(item) 




def reverse_string(str:str ):
     if len(str) == 0: 
          return str 
     else:
          return reverse_string(str[1:]) + str[0]

str  = "hello" 
print('***:', reverse_string(str)  )                 


numbers = [15, 30, 47, 82, 95]
def lesser(numbers):
   return numbers < 50

small = list(map(lesser, numbers))
print(small) """
import sys 
from math import pi
locations = sys.path
print(locations)
class MyClass:
     g =9 
     def __init__(self): 
          self.__a=  5 

     def hello (self): 
          print("hello , world" , self.g)  

instance = MyClass() 
print(instance.hello())

h = "Checking the length & structure of the sentence."
num = 9
class Car:
    num = 5
    bathrooms = 2

def cost_evaluation(num):
    num = 10
    return num

class Bike():
    num = 11

cost_evaluation(num)
car = Car()
bike = Bike()
car.num = 7
Car.num = 2
print(num)