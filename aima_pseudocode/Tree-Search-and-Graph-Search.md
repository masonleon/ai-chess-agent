# GRAPH-SEARCH

## AIMA4e


__function__ GRAPH-SEARCH(_problem_) __returns__ a solution, or failure  
&emsp;_frontier_ &larr; a queue initially containing one path, for the _problem_'s initial state  
&emsp;_reached_ &larr; a table of {_state_: _node_}; initially empty  
&emsp;_solution_ &larr; failure  
&emsp;__while__  _frontier_ is not empty __and__ _solution_ can possibly be improved __do__  
&emsp;&emsp;&emsp;_parent_ &larr; some node that we choose to remove from _frontier_  
&emsp;&emsp;&emsp;__for__ _child_ __in__ EXPAND(_parent_) __do__   
&emsp;&emsp;&emsp;&emsp;&emsp;_s_ &larr; _child_.state  
&emsp;&emsp;&emsp;&emsp;&emsp;__if__ _s_ is not in _reached_  __or__ _child_ is a cheaper path than _reached_[_s_] __then__  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;_reached_[_s_] &larr; _child_  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;add _child_ to _frontier_  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;__if__ _s_ is a goal and _child_ is cheaper than _solution_ __then__  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;_solution_  =  _child_  
&emsp;__return__ _solution_

---
__function__ EXPAND(_problem, parent_) __returns__ a list of nodes  
&emsp;_s_ &larr; _parent_.state  
&emsp;_nodes_ &larr; an empty list  
&emsp;__for__ _action_ __in__ _problem_.actions(_s_) __do__   
&emsp;&emsp;&emsp;_s'_ &larr; _problem_.result(_s_, _action_)  
&emsp;&emsp;&emsp;_cost_ &larr; _parent_.path-cost + _problem_.step-cost(_s, action, s')  
&emsp;&emsp;&emsp;add _node_ to _nodes_  
&emsp;__return__ _nodes_  

---
__Figure__ ?? In the GRAPH-SEARCH algorithm, we keep track of the best _solution_ found so far, as well as the states that we have already _reached_, and a _frontier_ of paths from which we will choose 
the next path to expand.
In any specific search algorithm, we specify (1) the criteria for ordering the paths in the frontier,
and (2) the procedure for determining when it is no longer possible to improve on a solution.

# TREE-SEARCH and GRAPH-SEARCH
## AIMA3e
__function__ TREE-SEARCH(_problem_) __returns__ a solution, or failure  
&emsp;initialize the frontier using the initial state of _problem_  
&emsp;__loop do__  
&emsp;&emsp;&emsp;__if__ the frontier is empty __then return__ failure  
&emsp;&emsp;&emsp;choose a leaf node and remove it from the frontier  
&emsp;&emsp;&emsp;__if__ the node contains a goal state __then return__ the corresponding solution  
&emsp;&emsp;&emsp;expand the chosen node, adding the resulting nodes to the frontier  

---
__function__ GRAPH-SEARCH(_problem_) __returns__ a solution, or failure  
&emsp;initialize the frontier using the initial state of _problem_  
&emsp;**_initialize the explored set to be empty_**  
&emsp;__loop do__  
&emsp;&emsp;&emsp;__if__ the frontier is empty __then return__ failure  
&emsp;&emsp;&emsp;choose a leaf node and remove it from the frontier  
&emsp;&emsp;&emsp;__if__ the node contains a goal state __then return__ the corresponding solution  
&emsp;&emsp;&emsp;**_add the node to the explored set_**  
&emsp;&emsp;&emsp;expand the chosen node, adding the resulting nodes to the frontier  
&emsp;&emsp;&emsp;&emsp;**_only if not in the frontier or explored set_**

---
__Figure__ ?? An informal description of the general tree\-search and graph\-search algorithms. The parts of GRAPH\-SEARCH marked in bold italic are the additions needed to handle repeated states.
