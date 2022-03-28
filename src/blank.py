#Imports here
import random

class UniqueIntegers():
	def __init__(self, min=0, max=999999):
		self.min = min
		self.max = max
		self.generated = []
	
	def getInt(self):
		if len(self.generated) == self.max-self.min+1:
			print("Full :(")
			raise ValueError("Full generator :(")

		while True:
			n = random.randint(self.min, self.max)
			if n not in self.generated:
				self.generated.append(n)
				return n
	
	def addGenerated(self, toAdd):
		if isinstance(toAdd, list):
			self.generated += toAdd
		elif isinstance(toAdd, int):
			self.generated.append(toAdd)	

	def deleteInt(self, n):
		try:
			self.generated.remove(n)
		except:
			print(f"ERROR: {n} was not generated")

## Implement class task here

## Implement class Todo here

if __name__ == "__main__":
    print("Hello, welcome to Python WS!! :)")
    
	## Implement terminal interface here