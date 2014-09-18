import sys, pygame, random, time
from pygame import *
    
class BTNPlus:
    def __init__(self, value, X=0, Y=0, width=0, height=0, parentNode='self', leftChild=None, rightChild=None):
        self.Value = value
        self.leftChild = leftChild
        self.rightChild = rightChild
        self.X = X
        self.Y = Y
        self.Width = width
        self.Height = height

        if parentNode == 'self':
            self.parent = self
        else:
            self.parent = parentNode

    def drawTree(self):
        #this will create a screen and draw a tree
        pygame.init()
        
        screen = pygame.display.set_mode((1050, 650))
        #screen.fill((255,255,255))
        
        self.drawSelf(screen, 1)
        pygame.display.update()
        pygame.image.save(screen, "BTNShot.png")
        time.wait(5000)
        pygame.display.quit()
        

    def drawSelf(self, screen, level):
        #This will draw a line representation of the current node.
        #up to 10 levels
        if level > 10:
            return
        if self.leftChild is not None:
            self.leftChild.drawSelf(screen, level + 1)
            pygame.draw.line(screen, (0,0,255), (self.X, self.Y), (self.leftChild.X, self.leftChild.Y))
            pygame.display.update()
            time.wait(50)
        if self.rightChild is not None:
            self.rightChild.drawSelf(screen, level + 1)
            pygame.draw.line(screen, (255,0,0), (self.X, self.Y), (self.rightChild.X, self.rightChild.Y))
            pygame.display.update()
            time.wait(50)
        pygame.draw.rect(screen, (0,255,0), (self.X,self.Y,3,3))

    def addChild(self, child):
        #add a child node. working
        if child.Value < self.Value:
            if self.leftChild is None:
                self.leftChild = child
                self.leftChild.Width = int(self.Width / 2)
                self.leftChild.X = self.X - self.leftChild.Width
                self.leftChild.Y = self.Y + self.Height
                self.leftChild.Height = self.Height
                child.parent = self
            else:
                self.leftChild.addChild(child)
        elif child.Value > self.Value:
            if self.rightChild is None:
                self.rightChild = child
                self.rightChild.Width = int(self.Width / 2)
                self.rightChild.X = self.X + self.rightChild.Width
                self.rightChild.Y = self.Y + self.Height
                self.rightChild.Height = self.Height
                child.parent = self
            else:
                self.rightChild.addChild(child)

    def genList(self):
        #recursively generates a sorted list of child node values
        numList = []
        if self.leftChild is not None:
            numList.extend(self.leftChild.genList())  #make the left node generate its list
        numList.extend([self.Value])
        if self.rightChild is not None:
            numList.extend(self.rightChild.genList()) #make the right node generate its list
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
        #no compare all the values
        if lDepth == rDepth == 0: #if there is nothing lower
            return 1              #return ourselves
        elif lDepth > rDepth:
            return lDepth + 1
        else:
            return rDepth + 1

X = 500
Y = 25
width = 500
height = 60
root = BTNPlus(500, X, Y, width, height)

i = 0
for i in range(0, 500):
    num = random.randint(1, 1000)
    # insert values
    node = BTNPlus(num)
    root.addChild(node)
    
root.drawTree()
