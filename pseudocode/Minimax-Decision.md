# MINIMAX-DECISION and EXPECTIMINIMAX

## AIMA3e
__function__ MINIMAX-DECISION(_state_) __returns__ _an action_  
&emsp;__return__ arg max<sub> _a_ &Element; ACTIONS(_s_)</sub> MIN\-VALUE(RESULT(_state_, _a_))  

---
__function__ MAX\-VALUE(_state_) __returns__ _a utility value_  
&emsp;__if__ TERMINAL\-TEST(_state_) __then return__ UTILITY(_state_)  
&emsp;_v_ &larr; &minus;&infin;  
&emsp;__for each__ _a_ __in__ ACTIONS(_state_) __do__  
&emsp;&emsp;&emsp;_v_ &larr; MAX(_v_, MIN\-VALUE(RESULT(_state_, _a_)))  
&emsp;__return__ _v_  

---
__function__ MIN\-VALUE(_state_) __returns__ _a utility value_  
&emsp;__if__ TERMINAL\-TEST(_state_) __then return__ UTILITY(_state_)  
&emsp;_v_ &larr; &infin;  
&emsp;__for each__ _a_ __in__ ACTIONS(_state_) __do__  
&emsp;&emsp;&emsp;_v_ &larr; MIN(_v_, MAX\-VALUE(RESULT(_state_, _a_)))  
&emsp;__return__ _v_  

---
__Figure__ ?? An algorithm for calculating minimax decisions. It returns the action corresponding to the best possible move, that is, the move that leads to the outcome with the best utility, under the assumption that the opponent plays to minimize utility. The functions MAX\-VALUE and MIN\-VALUE go through the whole game tree, all the way to the leaves, to determine the backed\-up value of a state. The notation argmax <sub>_a_ &Element; _S_</sub> _f_(_a_) computes the element _a_ of set _S_ that has maximum value of _f_(_a_).

---
__function__ EXPECTIMINIMAX(_s_) =     
&emsp;UTILITY(_s_) __if__ TERMINAL\-TEST(_s_)  
&emsp;max<sub>_a_</sub> EXPECTIMINIMAX(RESULT(_s, a_)) __if__ PLAYER(_s_)= MAX  
&emsp;min<sub>_a_</sub> EXPECTIMINIMAX(RESULT(_s, a_)) __if__ PLAYER(_s_)= MIN  
&emsp;∑<sub>_r_</sub> P(_r_) EXPECTIMINIMAX(RESULT(_s, r_)) __if__ PLAYER(_s_)= CHANCE  
