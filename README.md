# Maya PistonPlugin

A short rigging plug-in made with Python for Crank shaft models. It is also a first step
toward plug-in programming with Pymel and Maya.OpenMaya 2.0 api.

### Quick Intro

Piston, even if looking simple are hard to make as a clean rig. 
Using regular rigging methods (constraints, joints etc.) will usually result with cycling
rig evaluation beetween constraints. Use of expression is quite painfull with maya and hard to 
replicate in large scale and expressions need to evaluate each frame.

🚩 A proper piston rig should be :
  * Acyclic ;
  * Relying mostly on DAG graph evaluation (node based rig) ;
  * Easy to replicate.

The solution I came with was creating tools that didn't existed.\
The [crank-slider](https://en.wikipedia.org/wiki/Slider-crank_linkage) movement behind pistons rely on the following equation :

<p align="center">
   <img width="570" height="56" src="https://user-images.githubusercontent.com/100163862/172856495-b9fdfeff-6f41-4a79-b97c-6b0080a74cb5.png">
</p>

* x is the distance of piston 
* r is the length of the crank
* a is the angle of the the crank 
* l is the length of the rod

This was a proper excuse launch myself into plugin conception.

#### What does the plugin add :

The plugin add followings components :

* 2 new nodetypes :
  * pistonNode [solvernode]   
  * pistonVectorLength [utility vector length node]
  
* 1 new command :
  * generatePiston() [Generate a rigging nodegraph from selected joints]

* 1 new shelf tab :
  * A button for each command and node added by the plugin
  * A flushUndo() shorcut button 
  * A cleanCommand() button that delete all nodes with plugin added nodetypes 

<p align="center">
  <img width="226" height="62" src="https://user-images.githubusercontent.com/100163862/172846324-d6f71036-57cb-4b2b-b497-67df8b937d52.PNG">
</p>

#### Rig created by generatePiston()

The command create a clean outliner hierarchy and genereate a proper node graph.\
The piston are generated regardless of the postion of the given 3-joints chain. 

![Presentation](https://user-images.githubusercontent.com/100163862/172736931-b1ffac75-84f4-41b4-bae3-0121aab8d77e.gif)

##### Tree graph generated
![001](https://user-images.githubusercontent.com/100163862/172805145-a6655b6c-e516-4495-b551-b4d2bf30bde8.PNG)
