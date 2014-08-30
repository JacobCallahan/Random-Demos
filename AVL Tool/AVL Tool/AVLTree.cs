using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace AVL_Tool {
    class AVLTree {
        AVLNode rootNode;
        public AVLTree() {
            //the default constructor does some simple initialization
            this.rootNode = null;
        }

        public void addValue(int newValue) {
            //create a new node with the new value
            AVLNode newNode = new AVLNode(newValue);
            if (this.rootNode == null) {
                //if we don't currently have a root node, make it the new node
                this.rootNode = newNode;
            } else {
                //if we do have a root node, pass the new node down to it for processing
                this.rootNode.addChild(newNode);
            }
        }

        public String getTreeString() {
            //this function will return a sorted list consisting of the
            //values currently in the tree
            String returnString = "";
            if (this.rootNode != null) {
                returnString = this.rootNode.printTreeString();
            }
            return returnString;
        }

        public int getDepth() {
            //this function will simply return out the max dept of the current tree
            if (this.rootNode != null) {
                int myDepth = this.rootNode.getDepth();
                return myDepth;
            } else {
                return 0;
            }
        }

        public void balance() {
            //balance the tree and get the new rootNode, if it changes
            this.rootNode = this.rootNode.balance();
        }
    }
}
