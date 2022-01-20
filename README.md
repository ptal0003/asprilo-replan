# ASPRILO [![Github Release](https://img.shields.io/github/release/potassco/asprilo/all.svg)](https://github.com/potassco/asprilo/releases)

## About

This is source tree of **ASPRILO**, an intra-logistics benchmark suite for answer set
programming. For further details, please consult the documentation on our website at
<https://asprilo.github.io/>.

## Changes to dependencies:
- Deactivate the conda environment by running "conda deactivate"
- Run the following commands:
   - sudo apt install pip
   - pip install pybind11
   - sudo apt install python-is-python3
   - python3 -m pip install --user --upgrade clingo
   - sudo apt-get install python3-pyqt5

The reason behind not running asprilo through the conda environment is that pybind11 does not work with conda and fails to detect the module lazycbs which is present as a .so file.

## Directory Structure

- `./docs/` contains the documentation sources
- `./checker/` contains the instance generator sources
- `./generator/` contains the instance generator sources
- `./visualizer/` contains the instance visualizer sources

**Running Asprilo and lazycbs solver**
1. Clone or download this github repository
2. Set this-repository/visualizer/scripts as the current working directory.
3. Run the command "python3 viz"
4. Load the instance and plan you would like to work on
5. Go to **_Network_** -> **_Initialise Solver_** 
6. Change the mode from "default" to "lazycbs" and click OK
7. Check the terminal to see if the solver is running as expected. "Connection with <IP Address>" should be seen.
8. Click on "Solve" and press OK. 

****Adding a new solver****
 
Asprilo communicates with the solvers through sockets. Choosing the "Initialise Solver" option from the "Network" menu runs the script "viz-solver" by default which instantiates a solver, the solver it instantiates is determined by the mode specified while initialising the solver.
  
The communication between visualizer and the solver happens through the "Network.py" and "Solver.py" files. The "Network.py" file contains the code for the client side(Visualizer) that is responsible for sending instance/plan data to the solvers for solving. "Solver.py" is invoked by the script "viz-solver". To change the script being invoked, simply go to the "Initialise Solver" menu and specify the script of choice.

To modify the data being sent, have a look at https://github.com/ptal0003/asprilo-replan/blob/767806e69934934569deb5593205ff556c9869f7/visualizer/visualizer/model.py#L456 and https://github.com/ptal0003/asprilo-replan/blob/767806e69934934569deb5593205ff556c9869f7/visualizer/visualizer/model.py#L477
  
https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/solver.py#L23 is a parent class for any new solver. This class contains many crucial methods that allow the solver to communicate through sockets. The solver being added by you can override any of these methods if you want to implement things differently. If it is not overriden, then default methods will be used using Clingo. The https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/solver.py#L244 method is the method responsible for invoking a solver. To get a solution using your own solver, simply invoke the solver here.
  
The "Network.py" file should be notified once the solving is completed. This can be done by sending a unique command to the asprilo visualizer. https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/network.py#L172 can be modified to process the command being sent. Currently, the solver sends a "complete" command along with the name of the new instance and plan file so that the new solution can be loaded and visualised. This is done on https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/solver.py#L569 .

It is received by the "Network.py" file at  https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/network.py#L181

"Network.py" can be modified to make changes to the model and/or invoke the solver.
  
**Changes made to Asprilo**

The default solver in Asprilo uses encodings and passes instance/plan data directly to the Clingo which works using Answer Set Programming. This solver takes the model from the currently visualized instance/plan and generates a new solution. However, the specific manner in which Clingo generates solutions and makes use of encodings is not documented very well, and hence is hard to understand. Moreover, the lazycbs solver being used does not need any encodings, unlike Clingo. Since ASP may not be followed by every solver, it is difficult to extract data from the ASP solvers and creating middleware to convert that data into a format supported by the new solver. Therefore, Asprilo has been modified such that it stores the instance, the complete plan and the remaining plan. The new solver can simply read from these files and middleware can be written to convert the atoms into a format supported by the solver, which is more convenient and easier to understand than the existing approach.

When a solution is generated, the new instance file along with the compatible plan for that instance is stored in a new folder according to their timestamp at current-repo/visualizer. This is done at https://github.com/ptal0003/asprilo-replan/blob/7f6a1d6643e9ff11d14e6b75794b3eaafaa7041f/visualizer/visualizer/solver.py#L516-L571 An updated instance and a plan are stored because the user has the ability to add/remove obstacles, which would create a different instance file each time. Storing all of them would allow us to keep track as instances are modified and go to any state later.

The following flow chart shows how the entire process of interacting with lazycbs works:
  ![image](https://user-images.githubusercontent.com/62492172/148785076-45145e78-3774-46b1-8320-12e1b5929e6d.png)

In the image, lazycbs can be replaced with any other solver. Asprilo and the solver can only pass data to one another using sockets. However, the method to connect Asprilo and the solver has to be written separately for each solver. 
 
**13th January 2022 to 20th January 2022**
- Saving the time step in the instance file 
     * save_to_file() https://github.com/ptal0003/asprilo-replan/blob/dd0d2a428390fa16617096b324d5afb1aef35508/visualizer/visualizer/model.py#L514 was modified to          add as a comment each time the instance was saved
- Set the time step being visualized based on the data in the instance file.
     * https://github.com/ptal0003/asprilo-replan/blob/dd0d2a428390fa16617096b324d5afb1aef35508/visualizer/visualizer/parser.py#L278 checks the loaded file for the        presence of a time step, if a time step is found, https://github.com/ptal0003/asprilo-replan/blob/dd0d2a428390fa16617096b324d5afb1aef35508/visualizer/visualizer/model.py#L62 and https://github.com/ptal0003/asprilo-replan/blob/dd0d2a428390fa16617096b324d5afb1aef35508/visualizer/visualizer/model.py#L140 are called
- Storing the locations and movements of all agents at all time steps
     * Parser.py is responsible for storing the locations and movements.
     * When the solving is complete, on_model is called as a callback method. This method invokes on_atom() for all the atoms, depending on the type of atom,              on_init_atom() or on_occurs_atom() are called. If on_init_atom is called, the starting locations of all agents are stored in the format (ID,                        (starting_x,starting_y)), however if on_occurs_atom is called, movements of all agents are stored along with their ID and time step in the format                    (ID,(dx,dy),time_step).
 - Sorting locations of all agents according to time step and ID is done at https://github.com/ptal0003/asprilo-replan/blob/dd0d2a428390fa16617096b324d5afb1aef35508/visualizer/visualizer/parser.py#L63
- Displaying the information at each node: 
     * https://github.com/ptal0003/asprilo-replan/blob/dd0d2a428390fa16617096b324d5afb1aef35508/visualizer/visualizer/model.py#L652 accepts the coordinates of the          node, iterates through the location of all agents, finds if the robots pass/wait at the node(x,y), create a relevant string and return it.
     * Displaying the information on hover is done at: https://github.com/ptal0003/asprilo-replan/blob/dd0d2a428390fa16617096b324d5afb1aef35508/visualizer/visualizer/modelView.py#L205
 
 

