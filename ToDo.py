import random
import datetime
import pickle
import requests

WEATHER_TYPES_URL = "https://api.ipma.pt/open-data/weather-type-classe.json"
URL = 'http://api.ipma.pt/open-data/forecast/meteorology/cities/daily/'
CITY = '1110600'

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

class task(object):
	def __init__(self, title, description, completed, deadline, id):
		self.title = title
		self.description = description
		self.completed = completed
		self.id = id
		self.deadline = deadline

	def printTask(self):
		print(self.id)
		print(self.title)
		print(self.description)
		print(self.deadline)
		print(self.completed)
		
		if self.deadline != None:
			today = datetime.datetime.now()
			delta = self.deadline.day - today.day

			if delta > 5 or delta < 0: #API gets the weather for today and the next 4 days
				return
			
			result = requests.get(URL+CITY).json()
			weather_id = int(result["data"][delta]['idWeatherType'])
			forecast = requests.get(WEATHER_TYPES_URL).json()['data']
			forecast.pop(0)
			forecast = forecast[weather_id]['descIdWeatherTypeEN']
			print(f"Forecast for {self.deadline.strftime('%d/%b/%Y')} is {forecast}")

class ToDo():
	def __init__(self, load):
		self.generator = UniqueIntegers(0, 10)
		self.tasks = []
		
		if load:
			self.load()
		
		self.tasks.sort(key= lambda x: x.completed)
	
	def addTask(self, title, description, deadline):
		newTask = task(title, description, False, deadline, self.generator.getInt())

		#When adding new task add at the beggining, its not completed
		self.tasks.insert(0, newTask)
	
	def printTasks(self):
		for task in self.tasks:
			task.printTask()
			print("------")
	
	def save(self):
		with open("savefile", "wb") as f:
			pickle.dump(self.tasks, f)

	def load(self):
		try:
			with open("savefile", "rb") as f:
				self.tasks = pickle.load(f)
		except:
			return
		#Add the ids of the generated tasks to the generator so it doesnt generates this again
		added = [task.id for task in self.tasks]
		# Same as this
		# added = []
		# for task in self.tasks:
		# 	added.append(task.id)
		
		self.generator.addGenerated(added)
	
	def setCompleted(self, id):
		for task in self.tasks:
			if task.id == id:
				task.completed = True
				break
		
		#sort so it goes to end
		self.tasks.sort(key= lambda x: x.completed)

	def setIncompleted(self, id):
		for task in self.tasks:
			if task.id == id:
				task.completed = False
				break
		
		#sort so it goes to beginning
		self.tasks.sort(key= lambda x: x.completed)
	
	def delTask(self, id):
		for task in self.tasks:
			if task.id == id:
				self.tasks.pop( self.tasks.index(task) )
				return
		
	#edits the parameters that are passed, the others stay the same
	def editTask(self, id, new_title=None, new_description=None, new_deadline=None):
		for task in self.tasks:
			if task.id == id:			
				#Edit the task in index idx_task
				if new_title != None:
					task.title = new_title
				
				if new_description != None:
					task.description = new_description
				
				if new_deadline != None:
					task.deadline = new_deadline
			
			return

	def getTasks(self):
		return self.tasks

	def getTask_byid(self, id):
		l = [x for x in self.tasks if x.id == id]
		if len(l) != 1:
			print("Error, more than 1 task with same id")
			exit()
		return l[0]
		# Same as this
		# for t in self.tasks:
		# 	if t.id == id:
		# 		return t


if __name__ == "__main__":
	if input("Load? (Y/N) ").lower() == 'y':
		app = ToDo(load=True)
		print("Data loaded!")
	else:
		app = ToDo(load=False)

	while 1:
		a = input("What do you want to do?? ")

		if a == 'add':
			try:
				title = input("T??tulo: ")
				description = input("Descri????o: ")

				deadline = None
				if input("Do you want to add a deadline? (Y/N) ").lower() == "y":
					data = input("Insert date in format DD/MM/AAAA HH:MM : ")

					data = data.split(" ")

					day, month, year  = data[0].split("/")
					hour, minute = data[1].split(":")

					deadline = datetime.datetime(int(year), int(month), int(day), 
						hour=int(hour), minute=int(minute))

				app.addTask(title, description, deadline)
				print("Added!!")
			except:
				print("Error, try again")
		elif a == 'print':
			app.printTasks()
		elif a == 'complete':
			id = int(input("ID of task to complete: "))
			app.setCompleted(id)
		elif a == 'incomplete':
			id = int(input("ID of task to incomplete: "))
			app.setIncompleted(id)
		elif a == 'edit':
			id = int(input("ID of task to edit: "))
			new_title = input("T??tulo: ")
			new_description = input("Descri????o: ")

			new_deadline = None
			if input("Do you want to add a deadline? (Y/N) ").lower() == "y":
				deadline = None
				if input("Do you want to add a deadline? (Y/N) ").lower() == "y":
					data = input("Insert date in format DD/MM/AAAA HH:MM : ")

					data = data.split(" ")

					day, month, year  = data[0].split("/")
					hour, minute = data[1].split(":")

					new_deadline = datetime.datetime(int(year), int(month), int(day), 
						hour=int(hour), minute=int(minute))

			app.editTask(id, new_title, new_description, new_deadline)
			print("Updated!!")
		elif a == 'delete':
			id = int(input("ID of task to delete: "))
			app.delTask(id)
		elif a == "save":
			app.save()
		elif a == 'exit':
			exit()
