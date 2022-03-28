import tkinter as tk
from tkinter import ttk as ttk
from tkinter import messagebox
import tkcalendar

from PIL import ImageTk, Image

import requests
import datetime
from functools import partial

from ToDo import ToDo, task

WEATHER_TYPES_URL = "https://api.ipma.pt/open-data/weather-type-classe.json"
URL = 'http://api.ipma.pt/open-data/forecast/meteorology/cities/daily/'
CITY = '1110600'

class ScrollableFrame():
	"""
		Frames dont have a scrolling capability, but canvas do, put all the buttons and stuff inside a 
		frame thats inside a canvas: Frame(canvas with scroll(frame with everything) )

		To get the frame where you place everything use the method getObjectsFrame
	"""
	def __init__(self, parent):
		"""	
		Parameters:
			parent: parent widget
			
		Returns: ScrollableFrame object
		"""

		self.canvas = tk.Canvas(parent)
		self.canvas.pack(side = tk.LEFT, fill=tk.BOTH, expand=True)
		self.scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.canvas.yview) 
		self.scroll.pack(side = tk.RIGHT, fill=tk.Y)

		self.canvas.configure(yscrollcommand=self.scroll.set)
		self.canvas.bind("<Configure>",self.onCanvasConfigure )
		
		self.canvas.bind("<Enter>", self.bind_mouse)
		self.canvas.bind("<Leave>", self.unbind_mouse)

		self.canvas.bind_all("<MouseWheel>", self.on_mousewheel )
		
		self.ObjectsFrame = tk.Frame(self.canvas)
		self.ObjectsFrame.bind("<Configure>", self.updateScroll)
		self.canvas.create_window((0,0), window=self.ObjectsFrame, anchor='nw', tags="frame")

	def updateScroll(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))

	def bind_mouse(self, event=None):
		#The binding is made to MouseWheel (mouse wheel scroll in windows)
		# But also to <4> and <5> (mouse wheel scroll on linux)
		self.canvas.bind_all("<4>", self.on_mousewheel)
		self.canvas.bind_all("<5>", self.on_mousewheel)
		self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

	def unbind_mouse(self, event=None):
		#Same as bind_mouse
		self.canvas.unbind_all("<4>")
		self.canvas.unbind_all("<5>")
		self.canvas.unbind_all("<MouseWheel>")

	def getObjectsFrame(self):
		"""	
		Parameters: Nothing
			
		Returns: Frame where the widgets must be placed
		"""
		return self.ObjectsFrame
	
	def onCanvasConfigure(self, event=None):
		#To make the frame resize with the canvas
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
		self.canvas.itemconfig('frame', width=self.canvas.winfo_width() )

	def on_mousewheel(self, event):
		#Linux uses event.num; Windows and Mac uses event.delta
		if event.num == 4 or event.delta > 0:
			self.canvas.yview_scroll(-1, "units" )
		elif event.num == 5 or event.delta < 0:
			self.canvas.yview_scroll(1, "units" )

class Wizard(tk.Toplevel):
	"""
		Implements a wizard with at least one page
	"""

	def __init__(self, parent, finishFunc, onePage = False, firstNext = None, nextfunc = None, geometry=None):
		"""	
		Parameters:
			parent: parent widget
			finishFunc: Function to be executed when "Finish" button is pressed
		
		Optional Parameters:
			onePage: Bool value indicating if the wizard will only have one page
			firstNext:
			nextfunc:
			geometry: 

		Returns: CheckList object
		"""
		super().__init__(parent)
		self.resizable(0,0)
		if geometry != None:
			self.geometry(geometry)

		self.attributes('-topmost', 'true')
		self.columnconfigure(0, weight=2)

		self.onePage = False
		self.pages = []

		self.current = 0

		if callable(nextfunc): #Function to run every time the next button is pressed
			self.nextfunc = nextfunc
		else:
			self.nextfunc = None

		if callable(firstNext): #Function to run the 1st time next button is pressed
			self.firstNext = firstNext
		else:
			self.firstNext = None

		#empty label acting as spacer
		tk.Label(self, text=" ").grid(row=1, columnspan=3, sticky="we")

		if onePage:
			self.onePage = True
			self.finishButton = ttk.Button(self, text="Finish", command=partial(self.finish, finishFunc))
			self.finishButton.grid(row=2, column=2, padx=2, sticky="e")

			self.nextButton = ttk.Button(self, text="Next", state="disabled")
			self.nextButton.grid(row=2, column=1, padx=2, sticky="e")
		else:
			self.finishButton = ttk.Button(self, text="Finish", state="disabled", command=partial(self.finish, finishFunc))
			self.finishButton.grid(row=2, column=2, padx=2, sticky="e")

			self.nextButton = ttk.Button(self, text="Next", command=self.nextPage)
			self.nextButton.grid(row=2, column=1, padx=2, sticky="e")

	def isLastPage(self):
		"""	
		Parameters: Nothing

		Returns: True if current page is last, False otherwise
		"""

		if self.pages[self.current] == self.pages[-1]:
			return True
		else:
			return False

	def firstPage(self, firstPage):
		"""	
		Parameters: 
			firstPage: Frame to add to the Wizard as the 1st page

		Returns: Nothing
		"""

		firstPage.grid(row=0, column=0, columnspan=3, sticky="nswe")
		self.pages.append(firstPage)

	def nextPage(self):
		"""	
		Advances to the next page
		"""

		if self.nextfunc != None and self.current != 0:
			#nextfunc must return true to go to the next page
			#the wizard will provide the funtion the current page number
			#The current page is self.current -1 because page 0 is the first page
			# For the user of this class the first page (page 0) 
			# is the first page that the user added 
			retValue = self.nextfunc(self.current-1)
			if retValue != True:
				messagebox.showerror("Error :((", f"You have errors in the previous fields!\nCorrect those errors before going to the next page! :)")
				return

		self.current+=1

		if self.current == 1:
			if self.firstNext != None:
				self.firstNext()

		self.pages[self.current].tkraise()

		if self.isLastPage():
			self.finishButton.configure(state="normal")
			self.nextButton.configure(state="disabled")

	def addPage(self, frame):
		"""	
		Adds one more page to the Wizard

		Parameters:
			frame: Tkinter frame with the page to add
		"""

		if self.onePage:
			print("ERROR: You cant have more pages, wizard initialized as with only one page")
			return

		if not isinstance(frame, tk.Frame):
			print(f"Error, argument is not frame, is {type(frame)}")
			return

		frame.grid(row=0, column=0, columnspan=3, sticky="nswe")
		self.pages.append(frame)
		self.pages[self.current].tkraise()

	def finish(self, finishFunc):
		"""	
		Function that executes when finish button is pressed, calls the function the user defined and
		then destroys the window

		Parameters:
			finishFunc: Function to be executed
		"""

		if self.nextfunc != None:
			#same loginc as in nextPage()
			retValue = self.nextfunc(self.current-1)
			if retValue != True:
				messagebox.showerror("Error :((", f"You have errors in the previous fields!\nCorrect those errors before going to the next page! :)")
				return

		retValue = finishFunc()
		if retValue == True:
			self.destroy()

#inherits from ttk frame
#just adds a variable tag
class TaggedLabelFrame(ttk.Labelframe):
	def __init__(self, parent, tag, *args, **kwargs):
		super(TaggedLabelFrame, self).__init__(parent, *args, **kwargs)

		self.tag = tag

class Root(tk.Tk):    
	def __init__(self):
		super(Root, self).__init__()

		self.app = ToDo(load=True)

		self.weather_types = requests.get(WEATHER_TYPES_URL).json()['data']
		self.weather_types.pop(0)
		
		self.onScreenTasks = []
		self.displayedTasks = []

		self.title('To Do')
		self.geometry("600x800")
		# self.resizable(0,0)

		#delete icon
		self.del_img = ImageTk.PhotoImage(Image.open("delete.png").resize((25, 25), Image.ANTIALIAS) )
		self.edit_img = ImageTk.PhotoImage(Image.open("edit.png").resize((25, 25), Image.ANTIALIAS) )
		
		tk.Label(self, text="Your Tasks:").pack()

		self.top = tk.Frame(self)

		self.scrollable = ScrollableFrame(self.top)
		self.tasksFrame = self.scrollable.getObjectsFrame()
		# self.tasksFrame = tk.Frame(self, background='red')
		# self.tasksFrame.pack(fill='both', expand='true')
		self.tasksFrame.columnconfigure(0, weight=2)
		# self.tasksFrame.columnconfigure(1, weight=0)

		self.top.pack(fill='both', expand='True')
		
		self.Tasksrow = 0

		self.buttonsFrame = tk.Frame(self, background='yellow')
		self.buttonsFrame.pack(side='bottom')

		self.addBtn = ttk.Button(self.buttonsFrame, text="Add New Task", command=self.NewTask)		
		self.addBtn.grid(row= 0, column=0)

		# self.clearBtn = ttk.Button(self.buttonsFrame, text="Clear Tasks", command=self.NewTask)		
		# self.clearBtn.grid(row= 0, column=2)

		self.saveBtn = ttk.Button(self.buttonsFrame, text="Save", command=self.Save)		
		self.saveBtn.grid(row= 0, column=1)

		self.drawTasks()

	def Save(self):
		self.app.save()
		messagebox.showinfo("Saved!", "Data was sucessfully saved!")

	def NewTask(self):
		def finish():
			#Save the stuff to the app 
			try:
				h = int(hourEntry.get()) 
				m = int(minEntry.get())
				if (not 0<=h<24) and (not 0<=m<60):
					raise
			except:
				messagebox.showerror("Error :((", "You must provide a valid hour and minute!\nPlease try again! :)")
				return False

			date = dateEntry.get_date()						

			deadline = datetime.datetime(date.year, date.month, date.day,
										int(hourEntry.get()), int(minEntry.get()))

			self.app.addTask(titleEntry.get(), descriptionEntry.get(), deadline)

			# before drawing the new task we must take from screen the completed ones, so this 
			# doesnt go to the end

			#so delete all the completed ones
			for frame in self.tasksFrame.winfo_children():
				task = self.app.getTask_byid(frame.tag)

				if task.completed: #then delete from screen
					frame.grid_forget()
					frame.destroy()

					# and delete from displayed
					index = -1
					for idx, t in enumerate(self.displayedTasks):
						if t == task.id:
							index=idx
							break
					
					if index==-1:
						print("Erro")
						return
					else:
						self.displayedTasks.pop(index)

			#and redraw
			self.drawTasks()
			return True

		newWizard = Wizard(self, finish, onePage=True)
		
		# Build the page to add to the wizard
		page = ttk.Frame(newWizard)
		row = 0

		tk.Label(page, text="New Task").grid(row=row, column=0, sticky="e")
		row += 1

		tk.Label(page, text="Title:").grid(row=row, column=0, sticky="e")
		titleEntry = ttk.Entry(page)
		titleEntry.grid(row=row, column=1, sticky="we")
		row += 1

		tk.Label(page, text="Description:").grid(row=row, column=0, sticky="e")
		descriptionEntry = ttk.Entry(page)
		descriptionEntry.grid(row=row, column=1, sticky="we")
		row += 1

		### DEADLINE ###
		tk.Label(page, text="Deadline:").grid(row=row, column=0, sticky="e")
		dateEntry = tkcalendar.DateEntry(page, width=14)
		dateEntry.grid(row=row, column=1)

		row += 1
		timeFrame = tk.Frame(page)
		
		hourEntry = ttk.Spinbox(timeFrame, width=3, from_=1, to=24, wrap=True)
		hourEntry.pack(side=tk.LEFT)

		tk.Label(timeFrame, text="h:").pack(side=tk.LEFT)

		minEntry = ttk.Spinbox(timeFrame, width=3, from_=1, to=59, wrap=True)
		minEntry.pack(side=tk.LEFT)

		tk.Label(timeFrame, text="m").pack(side=tk.RIGHT)

		timeFrame.grid(row=row, column=1)

		# Add to wizard
		newWizard.firstPage(page)

	def setCompleted(self, tid, frame, var):
		if not var.get(): #if button is not seleced
			#set in the self.app as completed
			self.app.setIncompleted(tid)
			return

		#set in the self.app as completed
		self.app.setCompleted(tid)
		
		#Delete from displayed
		index = -1
		for idx, t in enumerate(self.displayedTasks):
			if t == tid:
				index=idx
				break
		
		if index==-1:
			print("Erro")
			return
		else:
			self.displayedTasks.pop(index)

		#delete from screen
		frame.grid_forget()
		#Must destroy because they need to be redrawn in another place
		frame.destroy()

		#call draw tasks again, to draw it at the end
		self.drawTasks()

	def delTask(self, tid, frame):
		#Delete from array
		self.app.delTask(tid)

		#Delete from displayed
		index = -1
		for idx, t in enumerate(self.displayedTasks):
			if t == tid:
				index=idx
				break
		
		if index==-1:
			print("Erro")
			return
		else:
			self.displayedTasks.pop(index)

		#delete from screen
		frame.grid_forget()
		frame.destroy()

	def drawTasks(self, new=False):
		def draw(t):
			def drawWeather():
				if t.deadline == None:
					return

				today = datetime.datetime.now()
				delta = t.deadline.day - today.day

				result = "ola"
				if delta > 5 or delta < 0: #API gets the weather for today and the next 4 days
					forecast = "No forecast available.. :("
				else:
					result = requests.get(URL+CITY).json()
					weather_id = int(result["data"][delta]['idWeatherType'])
					forecast = self.weather_types[weather_id]['descIdWeatherTypeEN']

				tk.Label(f, text=forecast).grid(row=0, column=2, rowspan=4, sticky="ns")

			def editTask(tid):
				def finish():
					#Update the stuff on the app 
					try:
						h = int(editHourEntry.get()) 
						m = int(editMinEntry.get())
						if (not 0<=h<24) and (not 0<=m<60):
							raise
					except:
						messagebox.showerror("Error :((", "You must provide a valid hour and minute!\nPlease try again! :)")
						return False

					titleLabel['text'] = editTitleEntry.get()

					descriptionLabel['text'] = editDescriptionEntry.get()

					date = editDateEntry.get_date()

					deadline = datetime.datetime(date.year, date.month, date.day,
										int(editHourEntry.get()), int(editMinEntry.get()))

					deadlineLabel['text'] = deadline.strftime("%d/%b/%Y, %Hh:%M")
					
					self.app.editTask(tid, titleLabel['text'], descriptionLabel['text'], deadline)

					#We dont edit the comnpleted field, there is a function to do that

					return True

				newWizard = Wizard(self, finish, onePage=True)
				
				# Build the page to add to the wizard
				page = ttk.Frame(newWizard)
				row = 0

				tk.Label(page, text=f"Task {tid}").grid(row=row, column=0, sticky="e")
				row += 1

				tk.Label(page, text="Title:").grid(row=row, column=0, sticky="e")
				editTitleEntry = ttk.Entry(page)
				editTitleEntry.insert(0, t.title)
				editTitleEntry.grid(row=row, column=1, sticky="we")
				row += 1

				tk.Label(page, text="Description:").grid(row=row, column=0, sticky="e")
				editDescriptionEntry = ttk.Entry(page)
				editDescriptionEntry.insert(0, t.description)
				editDescriptionEntry.grid(row=row, column=1, sticky="we")
				row += 1

				### DEADLINE ###
				tk.Label(page, text="Deadline:").grid(row=row, column=0, sticky="e")
				editDateEntry = tkcalendar.DateEntry(page, width=14, year=2000)
				editDateEntry.set_date(t.deadline)
				editDateEntry.grid(row=row, column=1)
				
				row += 1
				timeFrame = tk.Frame(page)
				
				editHourEntry = ttk.Spinbox(timeFrame, width=3, from_=1, to=24, wrap=True)
				
				if t.deadline != None:
					editHourEntry.insert(0, t.deadline.hour)
				
				editHourEntry.pack(side=tk.LEFT)

				tk.Label(timeFrame, text="h:").pack(side=tk.LEFT)

				editMinEntry = ttk.Spinbox(timeFrame, width=3, from_=1, to=59, wrap=True)
				
				if t.deadline != None:
					editMinEntry.insert(0, t.deadline.minute)

				editMinEntry.pack(side=tk.LEFT)

				tk.Label(timeFrame, text="m").pack(side=tk.RIGHT)

				timeFrame.grid(row=row, column=1)

				# Add to wizard
				newWizard.firstPage(page)
			
			########################################

			f = TaggedLabelFrame(self.tasksFrame, t.id, text=f"Task {t.id}")
			f.columnconfigure(1, weight=2)
			f.columnconfigure(2, weight=2)

			tk.Label(f, text="Title:").grid(row=0, column=0, sticky="e", pady=2)
			titleLabel = tk.Label(f, text=t.title)
			titleLabel.grid(row =0, column=1, sticky="w")

			tk.Label(f, text="Description:").grid(row = 1, column=0, sticky="e", pady=2)
			descriptionLabel = tk.Label(f, text=t.description)
			descriptionLabel.grid(row =1, column=1, sticky="w")

			if t.deadline != None:
				tk.Label(f, text="Deadline:").grid(row = 2, column=0, sticky="e", pady=2)
				deadlineLabel = tk.Label(f, text=t.deadline.strftime("%d/%b/%Y, %Hh:%M"))
				deadlineLabel.grid(row =2, column=1, sticky="w")

			var=tk.IntVar()
			tk.Label(f, text="Completed:").grid(row = 4, column=0, sticky="e", pady=2)
			check = ttk.Checkbutton(f, variable=var, command=partial(self.setCompleted, tid=t.id, frame=f, var=var))
			check.grid(row=4, column=1, sticky="w", padx=1)
			if t.completed:
				var.set(1)
			
			drawWeather()

			tk.Button(f, image=self.del_img, relief=tk.FLAT, command=partial(self.delTask, tid=t.id, frame=f)).grid(row=0, column=3, sticky="e")

			tk.Button(f, image=self.edit_img, relief=tk.FLAT, command=partial(editTask, tid=t.id)).grid(row=1, column=3, sticky="e")

			f.grid(row = self.Tasksrow, column=0, sticky='we', pady=2)

			self.Tasksrow +=1
		########################################

		#Draw boxes for each task in self.tasksFrame
		
		# Tasks are sorted so it will start from not completed tasks 
		for t in self.app.getTasks():
			if (t.id in self.displayedTasks):
				continue

			#if not, add it
			self.displayedTasks.append(t.id)
			draw(t)

if __name__ == '__main__':	
	root = Root()
	root.mainloop()