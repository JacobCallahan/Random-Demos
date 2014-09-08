import sys
from StringIO import StringIO
import re

class PML_Parser():
	""" This class will perform the legwork of our parsing
	    aside from handling the files and providing output,
	    it will also keep track of global and local variables
	"""

	def __init__(self):
		""" initialize our class variables """
		self.global_vars = {}
		self.local_vars = {}
		self.fileStrings = []

	def readFile(self, fileLocation):
		""" We will read the file, split it into our sections, and pass it on """
		inFile = open(str(fileLocation), "r")
		fileString = inFile.read()
		#use regex to split the file into html/pml chunks
		regex = re.compile("<pml>(.*?)</pml>",re.IGNORECASE|re.MULTILINE|re.DOTALL)	 	
		self.fileStrings.append(regex.split(fileString))
		#of course we close to be nice!
		inFile.close()

	def writeFile(self, fileLocation):
		""" Finally, we will write the file out """
		outFile = open(fileLocation, "w")
		for fileString in self.fileStrings:
			for line in fileString:
				outFile.write(str(line))
		
		outFile.close()

	def compilePML(self):
		""" This module will leave standard HTML intact and process PML"""
		newStringGroup = []
		newSubGroup = []
		#loop through our main groups
		for stringGroup in self.fileStrings:
			#and out individual sub groups
			inner = 0
			for subGroup in stringGroup:
				if inner % 2 != 0:
					#first we clean up the string
					subGroup = self.cleanPMLString(subGroup)
					#then we execute the pml string to get our HTML
					subGroup = self.executePMLString(subGroup)
				newSubGroup.append(subGroup)
				inner = inner + 1
			newStringGroup.append(newSubGroup)

		self.fileStrings = newStringGroup

	def executePMLString(self, pmlString):
		#we will temporarily hijack stdout 
		buffer = StringIO()
		stdoutSave = sys.stdout
		sys.stdout = buffer
		#execute out pml and capture any output
		exec (pmlString, self.global_vars, self.local_vars)

		#restore stdout
		sys.stdout = stdoutSave
		return buffer.getvalue()

	def cleanPMLString(self, pmlString):
		splitPMLString = pmlString.split("\n")
		# remove extra lines from the top, if needed
		while splitPMLString[0] == "":
			splitPMLString = splitPMLString[1:]

		# if we have extra indentation, remove them 
		newPMLString = []
		while splitPMLString[0][:4] == "    ":
			for line in splitPMLString:
				if len(line) > 3:
					newPMLString.append(line[4:])
			splitPMLString, newPMLString = newPMLString, []

		# return the new string by joining and adding line breaks
		return "".join(line + "\n" for line in splitPMLString)

def main():
	""" This main function prompts the user for input and acts on it """
	myPMLParser = PML_Parser()
	#prompt for the file location
	fileLocation = input("Please enter the location of the pml file (enclose in quotes): ")
	#then we read the file into our container
	myPMLParser.readFile(fileLocation)
	#next, we compile the PML
	myPMLParser.compilePML()
	#finally, we write the contents to a new HTML file with the same name
	newFileLocation = fileLocation[:-3] + "html"
	myPMLParser.writeFile(newFileLocation)
	print ("File succesfully compiled! Saved in ", newFileLocation)

if __name__ == '__main__':
	main()
