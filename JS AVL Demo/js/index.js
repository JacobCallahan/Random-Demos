function btnNode(value) {
  //This object will store the values required for each binary tree node
  this.value = value;
  this.parentNode = this; //if we don't have a parent node, we will be our own parent
  this.leftChild = null;
  this.rightchild = null;
  
  this.setParent = setParent;
  function setParent(newParentNode) {
    this.parentNode = newParentNode;
  }

  this.setLeftChild = setLeftChild;
  function setLeftChild(newLeftChildNode) {
    this.leftChild = newLeftChildNode;
  }

  this.setRightChild = setRightChild;
  function setRightChild(newRightChildNode) {
    this.rightChild = newRightChildNode;
  }
  
  this.getValue = getValue;
  function getValue() {return this.value;}
  
  this.getParentNode = getParentNode;
  function getParentNode() {return this.parentNode;}
  
  this.getLeftChild = getLeftChild;
  function getLeftChild() {return this.leftChild;}
  
  this.getRightChild = getRightChild;
  function getRightChild() {return this.rightChild;}

  this.addChild = addChild;
  function addChild(newChildNode) {
    //this function will determine where the new child needs to be.
    if (newChildNode.getValue() < this.value) {
      //if we don't already have a left child
      console.log(newChildNode.getValue() + " is less than " + this.value);
      if (!this.leftChild) {
        this.leftChild = newChildNode; //add the new node as the left child
        newChildNode.setParent(this);
      } else {
        this.leftChild.addChild(newChildNode); //if not, then add the new child to our left child
      }
    } else if (newChildNode.getValue() > this.value) {
      console.log(newChildNode.getValue() + " is greater than " + this.value);
      if (!this.rightChild) {
        this.rightChild = newChildNode;
        newChildNode.setParent(this);
      } else {
        this.rightChild.addChild(newChildNode);
      }
    }
  } 
  
  this.printTree = printTree;
  function printTree() {
    //recursively prints out the tree
    var tempList = this.value;
    if (this.leftChild) {
      tempList = this.leftChild.printTree() + "," + tempList;
    }  
    if (this.rightChild) {
      tempList += "," + this.rightChild.printTree();
    }
    return tempList;
  }

  this.getHeight = getHeight;
  function getHeight() {
    //this function returns the depth of the nodes under it
    //and including itself
    var tempHeight = 0, lHeight = 0, rHeight = 0;
    if (this.leftChild) {
      lHeight = this.leftChild.getHeight();
    }  
    if (this.rightChild) {
      rHeight = this.rightChild.getHeight();
    }
    //get the highest height
    tempHeight = lHeight > rHeight ? lHeight : rHeight;
    return (tempHeight + 1);
  }
  
  this.swap = swap;
  function swap(otherNode) {
    //this function should only be called on a parent node
    //to swap with one of its children 
    if (this.parentNode !== this) { 
      otherNode.setParent(this.parentNode);
    } else {
      otherNode.setParent(otherNode); //if we are at the top, make the other node its own parent
    }

    if (this.leftChild === otherNode) {
      //swap the position of this node with the supplanting node
      if (this.parentNode !== this) {
        if (otherNode.getValue() > this.parentNode.getValue()) {
          this.parentNode.setRightChild(otherNode);
        } else {
          this.parentNode.setLeftChild(otherNode);              
        }
      }
      this.leftChild = otherNode.getRightChild();           //adopt its appropriate child
      otherNode.setRightChild(this);
      if (this.leftChild) {this.leftChild.setParent(this);} //notify the child of its new parent

    } else if (this.rightChild === otherNode) {
      if (this.parentNode !== this) {
        if (otherNode.getValue() < this.parentNode.getValue()) {
          this.parentNode.setLeftChild(otherNode);
        } else {
          this.parentNode.setRightChild(otherNode);              
        }
      }
      this.rightChild = otherNode.getLeftChild();
      otherNode.setLeftChild(this);
      if (this.rightchild) {this.rightChild.setParent(this);}
    }

    this.parentNode = otherNode; //finally make our old child into our parentNode. (weird!)
  }
  
  this.balance = balance;
  function balance() {
    //this function will determine if the node needs to be balanced
    //if so, then we will balance it
    var leftHeight = 0, rightHeight = 0;
    if (this.leftChild) {
      this.leftChild.balance();
      leftHeight = this.leftChild.getHeight();
    }  
    if (this.rightChild) {
      this.rightChild.balance();
      rightHeight = this.rightChild.getHeight();
    }
    //now that we have the Heights of each, we need to decide which side is unbalanced
    if (leftHeight > rightHeight + 1) {
      this.swap(this.leftChild);
    } else if (rightHeight > leftHeight + 1) {
      this.swap(this.rightChild);
    }
    return this.parentNode;
  }

  this.drawSelf = drawSelf;
  function drawSelf(posX, posY, widthRemaining, target) {
    //add the new node div to the body
    document.body.innerHTML += "<div class='node' style='left:" + posX + "px; top:" + posY + "px;'>" + this.value + "</div>";
    var theta; //the angle between this node and its children. used for the lines
    if (this.leftChild) {
      theta = Math.atan2(-60, widthRemaining) * 180 / Math.PI;
      //a bit hacky, would have to sit down and work out the trig for this section if this was real code
      document.body.innerHTML += "<div class='line' style='width:" + (Math.sqrt(3600 + widthRemaining* widthRemaining) - 30) + "px; left:" + (posX - widthRemaining + 25 + 1 * (theta / 10)) + "px; top:" + (posY + 45) + "px; transform: rotate(" + theta + "deg);'></div>";
      this.leftChild.drawSelf(posX - widthRemaining, posY + 60, widthRemaining / 2);
    }  
    if (this.rightChild) {  
      theta = Math.atan2(60, widthRemaining) * 180 / Math.PI;
      document.body.innerHTML += "<div class='line' style='width:" + (Math.sqrt(3600 + widthRemaining* widthRemaining) - 30) + "px; left:" + (posX + 24 - theta / 6) + "px; top:" + (posY + 45) + "px; transform: rotate(" + theta + "deg);'></div>";
      this.rightChild.drawSelf(posX + widthRemaining, posY + 60, widthRemaining / 2);
    }
  }
}

function BinaryTree() {
  this.rootNode = null;
  
  this.addNode = addNode;
  function addNode(value) {
    newNode = new btnNode(value);      //create a new binary tree node
    if (this.rootNode === null) {      //if we haven't set a root node
      this.rootNode = newNode;         //go ahead and do that now
    } else {
      this.rootNode.addChild(newNode); //if not, then add the new node to the tree
    }
  }
  
  this.addValue = addValue;
  function addValue() {
    //this function will prompt the user for a new value, then pass it on to be added
    var newValue = Number(prompt("Please enter an integer value"));
    this.addNode(newValue);
  }
  
  this.printTree = printTree;
  function printTree() {
    //returns a string with the numbers sorted
    return this.rootNode.printTree(); //it is just that easy!
  }
  
  this.balance = balance;
  function balance() {
    this.rootNode = this.rootNode.balance(); //and again, recursion takes over!
  }
  
  this.draw = draw;
  function draw() {
    //remove any previous elements
    $('div').remove();
    var center = screen.width / 2;
    var target = document.getElementById("drawButton");
    this.rootNode.drawSelf(center, 20, center / 2, target);
  }
}

function addToBTN() {
  myBTN.addValue();
  myBTN.draw();
}

function balanceBTN() {
  myBTN.balance();
  myBTN.draw();
}

myBTN = new BinaryTree();