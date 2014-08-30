import threading

def easyThread(*args):
	def wrapper(func):
		def threadedFunction():
			for arg in args:
				print("Starting new thread with ", arg)
				thread = threading.Thread(target=func, args=(arg,))
				thread.start()
		return threadedFunction
	return wrapper

@easyThread(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
def printNumber(myNum):
	maxCount = myNum * 10
	for i in range(maxCount):
		print("Printing ", i, " from ", myNum, " thread")

printNumber()