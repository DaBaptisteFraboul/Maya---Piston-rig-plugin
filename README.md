# Maya PistonPlugin

A short rigging plug-in made with Python for Crank shaft models. It is also a first step
toward plug-in programming with Pymel and Maya.OpenMaya 2.0 api.

## Quick Intro

Piston, even if looking simple are hard to make as a clean rig. 
Using regular rigging methods (constraints, joints etc.) will usually result with cycling
rig evaluation beetween constraints. Use of expression is quite painfull with maya and hard to 
replicate in large scale.

A proper piston rig should be :
  - Acyclic ;
  - Relying mostly on DAG graph evaluation (node based rig) ;
  - Easy to replicate.







![Presentation](https://user-images.githubusercontent.com/100163862/172736931-b1ffac75-84f4-41b4-bae3-0121aab8d77e.gif)
![001](https://user-images.githubusercontent.com/100163862/172805145-a6655b6c-e516-4495-b551-b4d2bf30bde8.PNG)
