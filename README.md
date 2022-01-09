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

