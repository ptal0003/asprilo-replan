# ASPRILO [![Github Release](https://img.shields.io/github/release/potassco/asprilo/all.svg)](https://github.com/potassco/asprilo/releases)

## About

This is source tree of **ASPRILO**, an intra-logistics benchmark suite for answer set
programming. For further details, please consult the documentation on our website at
<https://asprilo.github.io/>.


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
  
**Adding a new solver**
  
Asprilo communicates with the solvers through sockets. Choosing the "Initialise Solver" option from the "Network" menu runs the script "viz-solver" by default which instantiates a solver, the solver it instantiates is determined by the mode specified while initialising the solver.
  
The communication between visualizer and the solver happens through the "Network.py" and "Solver.py" files. The "Network.py" file contains the code for the client side(Visualizer) that is responsible for sending instance/plan data to the solvers for solving. "Solver.py" is invoked by the script "viz-solver". To change the script being invoked, simply go to the "Initialise Solver" menu and specify the script of choice.

To modify the data being sent, have a look at https://github.com/ptal0003/asprilo-replan/blob/767806e69934934569deb5593205ff556c9869f7/visualizer/visualizer/model.py#L456 and https://github.com/ptal0003/asprilo-replan/blob/767806e69934934569deb5593205ff556c9869f7/visualizer/visualizer/model.py#L477
  
https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/solver.py#L23 is a parent class for any solver. This class contains many crucial methods that allow the solver to communicate through sockets. The solver being added by you can override any of these methods if you want to implement things differently. The https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/solver.py#L244 method is the method responsible for invoking a solver. To get a solution using your own solver, simply invoke the solver here.
  
The "Network.py" file should be notified once the solving is completed. This can be done by sending a unique command to the asprilo visualizer. https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/network.py#L172 can be modified to process the command being sent. Currently, the solver sends a "complete" command along with the name of the new instance and plan file so that the new solution can be loaded and visualised. This is done on https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/solver.py#L569 .

It is received by the "Network.py" file at  https://github.com/ptal0003/asprilo-replan/blob/3ee81e8e97b1fca0f340b2b6da6a743fd89efd0b/visualizer/visualizer/network.py#L181

