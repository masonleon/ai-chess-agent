


# MONTE-CARLO-TREE-SEARCH

## AIMA4e
__function__ MONTE-CARLO-TREE-SEARCH(_state_) __returns__ an action  
&emsp;tree &larr; NODE(_state_)
&emsp;__while__ TIME\-REMAINING() __do__  
&emsp;&emsp;&emsp;__tree__ &larr; PLAYOUT(_tree_)  
&emsp;__return__ the _move_ in ACTIONS(_state_) with highest Q(_state_,_move_)  

---

__function__ PLAYOUT(_tree_) __returns__ _updated tree_  
&emsp;_node_ &larr; _tree_  
&emsp;__while__ _node_ is not terminal and was already in _tree_ __do__  
&emsp;&emsp;&emsp;_move_ &larr; SELECT(_node_)  
&emsp;&emsp;&emsp;_node_ &larr; FOLLOW\-LINK(_node_,_move_)  
&emsp;_outcome_ &larr; SIMULATION(_node_.STATE)  
&emsp;UPDATE(_node_,_outcome_)  
&emsp;__return__ _tree_  

---

__function__ SELECT(_node_) __returns__ _an action_  
&emsp;__return__ argmax<sub>m &isin; FEASIBLE\-ACTIONS(_node_)</sub> UCB(RESULT(_node_,_m_))  

---

__function__ UCB(_child_) __returns__ _a number_  
&emsp;__return__ _child_.VALUE + C &times; <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\sqrt{\frac{\log{child.PARENT.N}}{child.N}}" target="_blank"><img src="https://latex.codecogs.com/png.latex?\inline&space;\sqrt{\frac{\log{child.PARENT.N}}{child.N}}" title="\sqrt{\frac{\log{child.PARENT.N}}{child.N}}" /></a> 


---
__FIGURE ??__ The Monte Carlo tree search algorithm. A game tree, _tree_, is initialized, and then grows by one node with each call to PLAYOUT. The function SELECT chooses a move that best balances exploitation and exploration according to the UCB formula. FOLLOW-LINK traverses from the current node by making a move; this could be to a previously-seen node, or to a new node that is added to the tree. Once we have added a new node, we exit the __while__ loop and SIMULATION chooses moves (with a randomized policy that is designed to favor good moves but to compute quickly) until the game is over. Then, UPDATE updates all the nodes in the tree from node to the root, recording the fact that the path led to the final __outcome__.
