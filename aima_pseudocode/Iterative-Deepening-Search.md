# ITERATIVE-DEEPENING-SEARCH

## AIMA3e / AIMA4e
__function__ ITERATIVE-DEEPENING-SEARCH(_problem_) __returns__ a solution, or failure  
&emsp;__for__ _depth_ = 0 to &infin; __do__  
&emsp;&emsp;&emsp;_result_ &larr; DEPTH\-LIMITED\-SEARCH(_problem_,_depth_)  
&emsp;&emsp;&emsp;__if__ _result_ &ne; cutoff __then return__ _result_

---
__Figure__ ?? The iterative deepening search algorithm, which repeatedly applies depth\-limited search with increasing limits. It terminates when a solution is found or if the depth\-limited search returns _failure_, meaning that no solution exists.
