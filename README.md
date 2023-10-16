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

#### Quick Update

Maya 2023 update added Trigonometry nodes, custom nodes and complicated node setups are not required anymore to have the clean formula with nodes.
If you are working on maya 2023 this script may not be relevant anymore.

### Houdini Equivalent

I am now in love with houdini, This piece of software make it really easy to create technical animation like this using its high perfommance compiled VEX language.

This is the result in houdini, very usefull since it works in evry directions

![piston](https://github.com/DaBaptisteFraboul/Maya---Piston-rig-plugin/assets/100163862/bd4505d8-a4f7-4ac4-ab17-0903577c7d4c)

This is the node network and the VEX code in the `PistonSolver` Attrwrangle node :

![image](https://github.com/DaBaptisteFraboul/Maya---Piston-rig-plugin/assets/100163862/0859f82b-0da8-469e-8477-a979cc38f553)

```C++
// Setup initial data
vector piston_dir, wheel_center, piston_contact, shaft_pivot;
vector up_vector = normalize(chv("Up_vector"));
float offset = radians(chf("Starting_rotation_offset"));
float rotation_angle = radians(chf("Rotation_Angle"));

// TODO:  Clean the code here
wheel_center = point(0, "P",0);
shaft_pivot= lerp(point(0,"P",0),point(1,"P",0), chf("Lerp_test"));
piston_contact = point(1, "P",0);
piston_dir = normalize(piston_contact - wheel_center);
float crank_length = length(piston_contact-shaft_pivot);
float connection_length = length(shaft_pivot);

// Formula implementation of crank shaft system
// Find a way to accelerate computation
float expension =  connection_length* sin(rotation_angle+offset) + sqrt(pow(crank_length,2) - pow(connection_length,2) * pow(cos(rotation_angle+offset),2)); 

// Create points
int pt_shaft = addpoint(geoself(), shaft_pivot);
int pt_piston = addpoint(geoself(), piston_contact);


// Crank Rotation using matrix to orient with the up vector
vector perp = cross(piston_dir, up_vector);

matrix3 mat= ident();
rotate(mat, rotation_angle, perp);


// New positions
vector new_pos = shaft_pivot * mat;
vector piston_new_pos = piston_dir * expension;


// Modify position
setpointattrib(geoself(), "P", pt_shaft, new_pos, "set"); 
setpointattrib(geoself(), "P", pt_piston, piston_new_pos, "set"); 

//Modify normal 

setpointattrib(geoself(), "N", 0, normalize(new_pos-wheel_center), "set");
setpointattrib(geoself(), "N", pt_shaft, normalize(piston_new_pos-new_pos), "set");
setpointattrib(geoself(), "N", pt_piston, normalize(piston_dir), "set");


//Add primitives 
int prim_wheel = addprim(geoself(), "polyline", 0, pt_shaft);
int prim_shaft = addprim(geoself(), "polyline", pt_shaft, pt_piston);

setprimattrib(geoself(), "name", prim_wheel, "Wheel", "set");
setprimattrib(geoself(), "name", prim_shaft, "Shaft", "set");


//Add name
setpointattrib(geoself(), "name", 0, "Wheel center", "set");
setpointattrib(geoself(), "name", pt_shaft, "Shaft" , "set");
setpointattrib(geoself(), "name", pt_piston, "Piston", "set");

```


