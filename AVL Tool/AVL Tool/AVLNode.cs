using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace AVL_Tool {
    class AVLNode {
        int value;
        AVLNode parentNode;
        AVLNode leftChild;
        AVLNode rightChild;
        System.Windows.Forms.Label myLabel;

        public AVLNode(int nodeValue) {
            //the simple constructor will take in an integer value
            //and sets ourself as the parent node
            this.value = nodeValue;
            this.parentNode = this;
            this.leftChild = null;
            this.rightChild = null;
            this.myLabel = null;
        }

        public AVLNode(int nodeValue, AVLNode ParentNode) {
            //the preferred constructor will take in an integer value
            //and also take in a ParentNode
            this.value = nodeValue;
            this.parentNode = ParentNode;
            this.leftChild = null;
            this.rightChild = null;
        }
        //start our get set functions
        public int Value {
            get { return this.value; }
            set { this.value = Value; }
        }

        public AVLNode ParentNode {
            get { return this.parentNode; }
            set { this.parentNode = ParentNode; }
        }

        public AVLNode LeftChild {
            get { return this.leftChild; }
            set { this.leftChild = LeftChild; }
        }

        public AVLNode RightChild {
            get { return this.rightChild; }
            set { this.rightChild = RightChild; }
        }

        public void addChild(AVLNode newChild) {
            //This function will put a new child node into the tree
            if (newChild.value <= this.value) {
                //check to see of we have an empty slot in the left child position
                if (this.leftChild == null) {
                    //if so, fill it
                    newChild.parentNode = this;
                    this.leftChild = newChild;
                } else {
                    //if not, then pass the new node on to it
                    this.leftChild.addChild(newChild);
                }
            } else {
                if (this.rightChild == null) {
                    newChild.parentNode = this;
                    this.rightChild = newChild;
                } else {
                    this.rightChild.addChild(newChild);
                }
            }
        }

        public List<int> printTree() {
            //this function will return a sorted list of all the values
            //below and including this node
            List<int> tempList = new List<int>();
            if (this.leftChild != null) {
                //if we have a left child add its list to our list first
                tempList.AddRange(this.leftChild.printTree());
            }
            //add our value no matter what
            tempList.Add(this.value);
            if (this.rightChild != null) {
                //if we have a right child add its list to our list last
                tempList.AddRange(this.rightChild.printTree());
            }
            return tempList;
        }

        public String printTreeString() {
            //this function will return a sorted list of all the values
            //below and including this node
            String tempString = "";
            if (this.leftChild != null) {
                //if we have a left child add its list to our list first
                tempString = string.Concat(this.leftChild.printTreeString(),", ");
            }
            //add our value no matter what
            tempString = string.Concat(tempString, Convert.ToString(this.value));
            if (this.rightChild != null) {
                //if we have a right child add its list to our list last
                tempString = string.Concat(tempString, ", ", this.rightChild.printTreeString());
            }
            return tempString;
        }

        public int getDepth() {
            int thisDepth = 0;
            if (this.leftChild != null) {
                //if we have a left child set its depth as the current value
                thisDepth = this.leftChild.getDepth();
            }
            if (this.rightChild != null) {
                //if we have a right child, see if its depth is greater than our left
                int tempDepth = this.rightChild.getDepth();
                //if so, set this depth equal to our right child's depth
                if (tempDepth > thisDepth) { thisDepth = tempDepth; }
            }
            return thisDepth + 1; //finally add 1 to account for ourselves.
        }

        public void swap(AVLNode replacementNode) {
            //this function is the brunt of the balancing movement
            //this function should only be called on a parent node
            //to swap with one of its children 
            if (this.parentNode != this) { 
                replacementNode.ParentNode = this.parentNode;
            } else {
                //if we are at the top, make the other node its own parent
                replacementNode.ParentNode = replacementNode; 
            }

            if (this.leftChild == replacementNode) {
                //swap the position of this node with the supplanting node
                if (this.parentNode != this) {
                    if (replacementNode.Value > this.parentNode.Value) {
                        this.parentNode.RightChild = replacementNode;
                    } else {
                        this.parentNode.LeftChild = replacementNode;              
                    }
                }
                this.leftChild = replacementNode.RightChild;           //adopt its appropriate child
                replacementNode.RightChild = replacementNode;
                if (this.leftChild != null) {this.leftChild.ParentNode = this;} //notify the child of its new parent

            } else if (this.rightChild == replacementNode) {
                if (this.parentNode != this) {
                    if (replacementNode.Value < this.parentNode.Value) {
                        this.parentNode.LeftChild = replacementNode;
                } else {
                    this.parentNode.RightChild = replacementNode;              
                }
                }
                this.rightChild = replacementNode.LeftChild;
                replacementNode.LeftChild = this;
                if (this.rightChild != null) { this.rightChild.ParentNode = this; }
            }
            //finally make our old child into our parentNode. (weird!)
            this.parentNode = replacementNode; 
        }

        public AVLNode balance() {
            //this function will balance the sides under this node
            int leftWeight = 0, rightWeight = 0;
            if (this.leftChild != null) {
                //first balance the child
                this.leftChild.balance();
                //then pull its weight value in
                leftWeight = this.leftChild.getDepth();
            }
            if (this.rightChild != null) {
                this.rightChild.balance();
                rightWeight = this.rightChild.getDepth();
            }
            //now we make our comparisons to determine if swaps need to be made
            if (leftWeight > rightWeight + 1) {
                //if one side significantly outweighs the other, make the swap
                this.swap(this.leftChild);
            } else if (rightWeight > leftWeight + 1) {
                this.swap(this.rightChild);
            }
            //finally return the current parent node for reference
            return this.parentNode; 
        }

        public void drawSelf(frmAVL currentForm) {
            this.myLabel = new System.Windows.Forms.Label();
            
            currentForm.label1.AutoSize = true;
            currentForm.label1.Location = new System.Drawing.Point(235, 9);
            currentForm.label1.Name = "label1";
            currentForm.label1.Size = new System.Drawing.Size(39, 13);
            currentForm.label1.TabIndex = 3;
            currentForm.label1.Text = "Depth:";
        }
    }
}
