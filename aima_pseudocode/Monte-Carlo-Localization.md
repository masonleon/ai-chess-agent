# MONTE-CARLO-LOCALIZATION

## AIMA3e
__function__ MONTE-CARLO-LOCALIZATION(_a_, _z_, _N_, _P_(_X'_|_X_, _v_, _w_), _P_(_z_|_z\*_), _m_) __returns__ a set of samples for the next time step  
&emsp;__inputs__: _a_, robot velocities _v_ and _w_  
&emsp;&emsp;&emsp;&emsp;&emsp;_z_, range scan _z<sub>1</sub>_,..., _z<sub>M</sub>_  
&emsp;&emsp;&emsp;&emsp;&emsp;_P_(_X'_|_X_,_v_,_w_), motion model  
&emsp;&emsp;&emsp;&emsp;&emsp;_P_(_z_|_z\*_), range sensor noise model  
&emsp;&emsp;&emsp;&emsp;&emsp;_m_, 2D map of the environment  
&emsp;__persistent__: _S_, a vector of samples of size _N_  
&emsp;__local variables__: _W_, a vector of weights of size _N_  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;_S'_, a temporary vector of particles of size _N_  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;_W'_, a vector of weights of size _N_  

&emsp;__if__ _S_ is empty __then__&emsp;&emsp;&emsp;/\* initialization phase \*/  
&emsp;&emsp;&emsp;__for__ _i_ = 1 to _N_ __do__  
&emsp;&emsp;&emsp;&emsp;&emsp;_S_[_i_] &larr; sample from _P_(_X<sub>0</sub>_)  
&emsp;__for__ _i_ = 1 to _N_ __do__&emsp;&emsp;/\* update cycle \*/  
&emsp;&emsp;&emsp;_S'_[_i_] &larr; sample from _P_(_X'_|_X_ = _S_[_i_], _v_, _w_)  
&emsp;&emsp;&emsp;_W'_[_i_] &larr; 1  
&emsp;&emsp;&emsp;__for__ _j_ = 1 to _M_ __do__  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;_z_\* &larr; RAYCAST(_j_, _X_ = _S'_[_i_], _m_)  
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;_W'_[_i_] &larr; _W'_[_i_] . _P_(_z<sub>j</sub>_|_z\*_)  
&emsp;_S_ &larr; WEIGHTED-SAMPLE-WITH-REPLACEMENT(_N_, _S'_, _W'_)  
&emsp;__return__ _S_  

---
__FIGURE ??__ A Monte Carlo localization algorithm using a range-scan sensor model with independent noise.
