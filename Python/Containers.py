"""
    This is a collection of container classes i have created
    to generally make life easier
"""

#+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^
class trieNode:
    def __init__(self, value = True):
        self.Value = value
        self.Children = ""
        self.Child = []
        self.hasTrue = False

    def addChild(self, value):
        if value is not True:            
            if len(value) == 1:
                remainder = True
            else:
                remainder = value[1:]
                value = value[0]
                
            if self.Children.find(value) == -1:
                newChild = trieNode(value)
                self.Child.append(newChild)
                self.Children = self.Children + value
                newChild.addChild(remainder)
        else:
            self.hasTrue = True

    def findValue(self, value):
        if value == self.Value:
            return self.hasTrue
        elif self.Children.find(value[0]) > -1:
            return self.Child[self.Children.find(value[0])].findValue(value[1:])
        else:
            return False

    def getNumBelow(self):
        sum = 0
        for i in range(0,len(self.Children)):
            sum = sum + self.Child[i].getNumBelow()

        return sum + 1

#+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^+-*~^
class BinaryTreeNode:
    def __init__(self, value, parentNode='self', leftChild=None, rightChild=None):
        self.Value = value
        self.leftChild = leftChild
        self.rightChild = rightChild

        if parentNode == 'self':
            self.parent = self
        else:
            self.parent = parentNode

    def addChild(self, child):
        #add a child node. working
        if child.Value < self.Value:
            if self.leftChild is None:
                self.leftChild = child
                child.parent = self
            else:
                self.leftChild.addChild(child)
        elif child.Value > self.Value:
            if self.rightChild is None:
                self.rightChild = child
                child.parent = self
            else:
                self.rightChild.addChild(child)

    def findValue(self, value):
        #Performs a binary search for a specified value
        if value == self.Value:
            print("found!")
            print(self)
            return self
        elif value < self.Value:
            if self.leftChild is None:
                print('value not found')
            else:
                self.leftChild.findValue(value)
        elif value > self.Value:
            if self.rightChild is None:
                print('value not found')
            else:
                self.rightChild.findValue(value)

    def genList(self):
        #recursively generates a sorted list of child node values
        numList = []
        if self.leftChild is not None:
            numList.extend(self.leftChild.genList())  #error
        numList.extend([self.Value])
        if self.rightChild is not None:
            numList.extend(self.rightChild.genList()) #error
        return numList

    def getDepth(self):
        #recursively find the deepest node
        depth = 0
        lDepth = 0
        rDepth = 0
        if self.leftChild is not None:
            lDepth = self.leftChild.getDepth()
        if self.rightChild is not None:
            rDepth = self.rightChild.getDepth()
        #now compare all the values
        if lDepth == rDepth == 0: #if there is nothing lower
            return 1              #return ourselves
        elif lDepth > rDepth:
            return lDepth + 1
        else:
            return rDepth + 1

    def delSelf(self): #working
        #prepares the tree to have the node removed
        if self.leftChild == self.rightChild is None:
            """do nothing"""
            print('did nothing')
        elif self.rightChild is None:
            self.leftChild.parent = self.parent
            self.parent.leftChild = self.leftChild
            print('reassigned left child')
        elif self.leftChild is None:
            self.rightChild.parent = self.parent
            self.parent.rightChild = self.rightChild
            print('reassigned right child')
        else:
            replacement = self.findNextLargest()
            self.leftChild.parent = replacement
            self.rightChild.parent = replacement
            replacement.leftChild = self.leftChild
            replacement.rightChild = self.rightChild
            replacement.parent.leftChild = self
            swap = replacement.parent 
            replacement.parent = self.parent
            self.parent = swap
            print('reassigned left and right children')

    def findNextLargest(self): #working
        #find the next largest numbernode
        topNode = self.getAncestor()
        numList = topNode.genList()
        numPos = numList.index(self.Value)
        nextNum = numList[numPos + 1]
        return self.findValue(nextNum)        

    def getAncestor(self):
        #find the top node of the tree. working
        if self.parent == self:
            return self
        else:
            return self.parent.getAncestor()
    
