class ListItem:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

class LinkedList:
    def __init__(self, values=None):
        self.head = None
        self.tail = None
        if values:
            for value in values:
                self.add(value)

    def add(self, value):
        if not self.head:
            self.head = self.tail = ListItem(value)
        else:
            self.tail.right = ListItem(value, self.tail)
            self.tail = self.tail.right

    def to_list(self):
        if not (curr := self.head):
            return []        
        outlist = [curr.value]
        while (curr := curr.right):
            outlist.append(curr.value)
        return outlist

