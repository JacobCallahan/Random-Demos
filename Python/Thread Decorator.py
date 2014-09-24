import threading
#quick demo of how to use a decorator to easily thread out a function

def easyThread(*args):
    def wrapper(func):
        def threadedFunction():
            """ This is the function returned by the decorator """
            for arg in args:
                print("Starting new thread with ", arg)
                thread = threading.Thread(target=func, args=(arg,))
                thread.start()
        return threadedFunction
    return wrapper

@easyThread(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
def printNumber(myNum):
    """ Simply print out numbers until you reach the max number times 10"""
    maxCount = myNum * 10
    # note, use xrange if not using python 3.x
    for i in range(maxCount):
        print ("Printing {0} from {1} thread".format(i, myNum))

# We do not need to send arguments because the function has already been overwritten
printNumber()
