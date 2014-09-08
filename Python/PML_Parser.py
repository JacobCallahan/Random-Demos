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
	 	inFile = open(fileLocation, "r")
	 	fileString = inFile.read()
	 	#use regex to split the file into html/pml chunks
	 	regex = re.compile("<pml>(.*?)</pml>",re.IGNORECASE|re.MULTILINE|re.DOTALL)	 	
	 	self.fileStrings.append(regex.split(fileString))
	 	#of course we close to be nice!
	 	inFile.close()
	 	return True

	 def writeFile(self, fileLocation):
	 	outFile = open(fileLocation, "w")
	 	for line in self.fileStrings:
	 		outFile.write(line)
	 	
	 	outFile.close()
	 	return True

	 def executePMLString(self, pmlString):
	 	return exec(pmlString, global_vars, local_vars)

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

	 	# return the new string by joining and adding line breaks
	 	return "".join(line + "\n" for line in newPMLString)

if __name__ == '__main__':
	main()
