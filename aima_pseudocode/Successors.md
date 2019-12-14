# Successors

## AIMA4e


__function__ SUCCESSORS(_problem_, _parent_) __returns__ an action  
&emsp;_s_ &larr; _parent_.state  
&emsp;_nodes_ &larr; an empty list  
&emsp;__for__ _action_ in _problem_.actions(_s_) __do__  
&emsp;&emsp;&emsp;_s'_ &larr; _problem_.result(s,_action_)  
&emsp;&emsp;&emsp;_cost_ &larr; _parent_.pathCost + _problem_.stepCost(_s, action, s′_ )  
&emsp;&emsp;&emsp;_node_ &larr; Node(state = _s'_,  parent = _parent_, action = _action_, pathCost = _cost_)  
&emsp;&emsp;&emsp;add _node_ to _nodes_  
&emsp;__return__ _nodes_   
