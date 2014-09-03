# super quick demo featuring recursion and list comprehensions to solve an easy task
# that I choked on recently.. - This is for you, S!

def fibo(num):
	# define our recursive fibbonaci number generator
	if num == 0:
		return 0
	if num == 1:
		return 1
	# after the base cases are handled, we recursively call our fibo function
	# to return the desired number
	else:
		return fibo(num-1) + fibo(num-2)

# then we run a list comprehension through our fibo function
myFiboList = [fibo(num) for num in range(20)]

# finally, print out the results
print(myFiboList)