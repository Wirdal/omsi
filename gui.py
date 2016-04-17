#Testing tkinter
from Tkinter import *
import tkMessageBox
import tkFileDialog
import tkSimpleDialog
import pdb
import os




class Example(Frame):

	def __init__(self,master):
		Frame.__init__(self,master)
		self.parent = master
		self.lastqNum = -1
		self.widgets()

	def donothing(self):
		filewin = Toplevel(self.parent)
		button = Button(filewin, text = "Do nothing button")
		button.pack()

	def onOpen(self):
		ftypes = [('Python files','*.py'),('All files','*')]
		dlg = tkFileDialog.Open(self,filetypes=ftypes)
		fl = dlg.show()
		if fl != '':
			f = open(fl,"r")
			text = f.read()
			self.txt.insert(END,text)

	def helloCallback(self):
		s = "This size is {0}".format(self.parent.winfo_height())
		tkMessageBox.showinfo("Hello Python", s)

	def updateQuestionBox(self,qNum = None):
		# pdb.set_trace()
		
		if self.lastqNum == qNum:
			return
		self.question.delete("1.0",END)
		self.question.insert(END,self.QuestionsArr[qNum])

	def updateAnswerBox(self,qNum = None):
		#qNum 0 refers to the description
		if qNum == self.lastqNum:
			return

		if self.lastqNum > 0:
			self.answersArr[self.lastqNum-1] = self.txt.get("1.0",END)

		self.txt.delete("1.0",END)
		if not qNum == None and qNum > 0:
			self.txt.insert(END,self.answersArr[qNum-1])
		self.lastqNum = qNum

	def listboxSelected(self,evt):
		w = evt.widget
		index = int(w.curselection()[0])
		value = w.get(index)
		self.updateQuestionBox(index-1)
		self.updateAnswerBox(index-1)

	def enteredServerInfo(self):
		if not self.validate():
			self.hostEntry.focus_set()
			return

		self.dBox.withdraw()
		self.dBox.update_idletasks()

		self.cancel()

	def cancel(self,event=None):
		self.parent.focus_set()
		self.dBox.destroy()


	#Makes a dialog window pop up asking for host port and email
	def getConnectionInfo(self):
		self.dBox = Toplevel(self.parent)
		self.dBox.transient(self.parent)

		body = Frame(self.dBox)

		Label(body,text="Host:").grid(row = 0)
		Label(body,text="Port:").grid(row = 1)
		Label(body,text="Student email:").grid(row=2)

		self.hostEntry = Entry(body)
		self.portEntry = Entry(body)
		self.emailEntry = Entry(body)

		self.hostEntry.grid(row=0,column=1)
		self.portEntry.grid(row=1,column=1)
		self.emailEntry.grid(row=2,column=1)

		self.hostEntry.focus_set()
		body.pack()

		buttonBox = Frame(self.dBox)
		ok = Button(buttonBox, text="Enter",width=10,command=self.enteredServerInfo,default=ACTIVE)
		ok.pack(side=LEFT,padx=5,pady=5)
		cancel = Button(buttonBox,text="Cancel",width = 10,command=self.cancel)
		cancel.pack(side=RIGHT,padx=5,pady=5)
		
		#Bind enter and escape to respective methods
		self.dBox.bind("<Return>",self.enteredServerInfo)
		self.dBox.bind("<Escape>",self.cancel)
		buttonBox.pack()

		self.dBox.grab_set()

		#Makes the X button call the cancel method
		self.dBox.protocol("WM_DELETE_WINDOW",self.cancel)

		#This blocks until the dialog box is closed
		self.dBox.wait_window(self.dBox)
		self.connectToServer()
		self.getQuestions()

	def connectToServer(self):
		import Client
		import ClientGlobals
		ClientGlobals.gHost = self.host
		ClientGlobals.gPort = self.port
		ClientGlobals.gStudentEmail = self.email
		Client.main()

	def validate(self):
		try:
			self.host = self.hostEntry.get()
			self.port = int(self.portEntry.get())
			self.email = self.emailEntry.get()
			if not self.host or not self.port or not self.email:
				raise ValueError
			return 1
		except ValueError:
			tkMessageBox.showwarning(
				"Bad input", "Enter host, post and email!"
			)
			return 0

	def getQuestions(self):
		import utility
		self.QuestionsArr = utility.ParseQuestions("ExamQuestions.txt")
		self.lb.delete(1)
		self.lb.insert(1,"Description")
		self.answersArr = []
		for i in range(1,len(self.QuestionsArr)):
			self.lb.insert(i+1,"Question {0}".format(i))
			self.answersArr.append("Put your answer for question {0} here.".format(i))



	def widgets(self):
		self.parent.title("GUI Testing")
		self.parent.grid_columnconfigure(0,weight =1)
		self.parent.grid_columnconfigure(1,weight = 6)
		self.parent.grid_rowconfigure(0,weight=1)
		menubar = Menu(self.parent)
		filemenu = Menu(menubar, tearoff = 0)
		filemenu.add_command(label="New",command = self.donothing)
		filemenu.add_command(label="Open", command = self.onOpen)
		filemenu.add_command(label="Connect",command = self.getConnectionInfo)
		filemenu.add_command(label="Save", command=self.donothing)
		filemenu.add_command(label="Save as...", command=self.donothing)
		filemenu.add_command(label="Close", command=self.donothing)

		filemenu.add_separator()

		filemenu.add_command(label="Exit",command = self.parent.quit)
		menubar.add_cascade(label="File",menu=filemenu)

		editmenu = Menu(menubar, tearoff=0)
		editmenu.add_command(label="Undo", command = self.donothing)

		editmenu.add_separator()

		editmenu.add_command(label="Cut", command=self.donothing)
		editmenu.add_command(label="Copy", command=self.donothing)
		editmenu.add_command(label="Paste", command=self.donothing)
		editmenu.add_command(label="Delete", command=self.donothing)
		editmenu.add_command(label="Select All", command=self.donothing)

		menubar.add_cascade(label="Edit",menu=editmenu)

		self.parent.config(menu=menubar)
		
		
		self.questionFrame = Frame(self.parent,bg="yellow")
		self.questionFrame.grid(row = 0,column=0,sticky="nswe")

		# btn = Button(self.questionFrame,text="hi",command=self.helloCalself.lback)
		# btn.pack()
		print "Parent height = {0}".format(self.parent.winfo_height())
		self.lb = Listbox(self.questionFrame,width=20)
		self.lb.insert(1,"Connect to server to get quesions...")
		self.lb.bind('<<ListboxSelect>>',self.listboxSelected)

		self.lb.pack(fill=BOTH,expand=1,padx=5,pady=5)
		# pdb.set_trace()

		#Frame for the question and answer text boxes
		self.textFrame = Frame(self.parent)
		self.textFrame.grid(row=0,column=1,sticky="nswe")
		self.textFrame.grid_rowconfigure(0,weight=1)
		self.textFrame.grid_rowconfigure(1,weight=6)
		self.textFrame.grid_columnconfigure(0,weight=1)

		#Question text box
		self.question = Text(self.textFrame,bg="red")
		self.question.grid(row=0,sticky="nswe",padx=5,pady =5)

		#Answer text box
		self.txt = Text(self.textFrame,bg="orange")
		self.txt.grid(row=1,sticky="nswe",padx=5,pady=5)



def main():
	top = Tk()
	top.geometry("{0}x{1}".format(top.winfo_screenwidth(),top.winfo_screenheight()))
	top.update()
	top.minsize(top.winfo_width(),top.winfo_height())
	app  =  Example(top)
	
	top.mainloop()

if __name__ == '__main__':
	main()