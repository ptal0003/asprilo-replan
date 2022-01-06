#!/usr/bin/env python
# This script is an example for a solver for the asprilo visualizer.
# It contains 3 different ways to solve instances and delivers plans for visualization.
# All solvers use a given encoding to solve the problems. The solvers use the networking
# interface from the visualizer and are written to work along with it.
# This script provides an one shot varaint, an incremental and an interactive solver variant.

import argparse
import select
import socket
import time
from lazycbs import init
from clingo.control import Control
from clingo.symbol import Function, parse_term
import os
from lazycbs import init
from .createscen import *
from .planconverter import *
from os import path
from datetime import date, datetime
VERSION = '0.2.2'
#default one shot solver
class Solver(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument('-p', '--port', help='the port the solver will send the anwsers to',
                            type=int, default = 5000)
        self._parser.add_argument('-v', '--version',
                            help='show the current version', action='version',
                            version=VERSION)
        self._parser.add_argument('-e', '--encoding',
                            help='the name of the encoding the solver shall use to solve instances',
                            type = str, default = './encoding.lp')
        self._parser.add_argument('-m', '--mode',
                            help='the mode that the solver should use to solve instances',
                            type = str, choices=['default', 'incremental', 'interactive', 'online', 'lazycbs'], default = 'default')
        self._parser.add_argument('-t', '--timeout',
                            help='The maximal number of seconds the solver waits for a solution. 0 means no limit.',
                            type = int, default = 0)
        self._parser.add_argument('-s', '--steps',
                            help='The maximal number of steps the incremental solver searchs for a solution. 0 means no limit.',
                            type = int, default = 0)
        self._parser.add_argument('-a', '--atoms',
                            help='Prints all output atoms to the default output channel.',
                            action='store_true')
        self._parser.add_argument('-o', '--occurs',
                            help='Prints all output occurs atoms to the default output channel.',
                            action='store_true')
        self._parser.add_argument('-i', '--input',
                            help='Prints all input atoms to the default output channel.',
                            action='store_true')
        self._args = None

        #socket properties
        self._host = '127.0.0.1'
        self._port = '5000'
        self._socket = None
        self._connection = None
        self._name = 'solver'

        #clingo interface
        self._control = Control()
        #time for timeout
        self._solve_start = time.time()

        #saves the raw sended data
        self._raw_data = ''
        #array of processed data
        self._data = []
        #this dictonary contains all occurs atoms
        #the key is the time step in which they should be sended to the visualizer
        self._to_send = {}
        #the last sended time step
        self._sended = -1
        self._args = self._parser.parse_args()
        self._port = self._args.port

    def __del__(self):
        print("Solver.py 78")
        self.close()

    #return the solver mode
    def get_mode(self):
        print("Solver.py 83")
        return self._args.mode

    #open the socket and wait for an incomming connection
    def connect(self):
        
        try:
            self._socket = socket.socket()
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self._host, self._port))
            self._socket.listen(1)
            self._connection, addr = self._socket.accept()
            print("Connection Successful")
            print('Connection with: ' + str(addr))
            
            self.on_connect()
        except socket.error as error:
            self.close()
            print(error)
            return -1
        return 0

    #is called when a connection is etablished
    #not used yet
    def on_connect(self):
        pass

    #close the connection and the socket
    def close(self):
        print("Solver.py 112")
        if self._connection is not None:
            try:
                self._connection.shutdown(socket.SHUT_RDWR)
            except socket.error as error:
                print(error)
            self._connection.close()
            self._connection = None
            print('close ' + self._name)

        if self._socket is not None:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except socket.error as error:
                print(error)
            self._socket.close()
            self._socket = None

    #checks whether data can be read from the socket
    def is_ready_to_read(self, time_out = 0.1):
        print("Solver.py 132")
        if self._connection is None:
            return False
        ready = select.select([self._connection], [], [], time_out)
        if ready[0]:
            return True
        else:
            return False

    #sends data to the visualizer
    def send(self, data):
        print("Solver.py 143")
        if self._connection is None:
            return
        self._connection.send(data.encode())

    #receive data from the visualizer
    def receive(self, time_out):
        print("Solver.py 150")
        if self._connection is None:
            return -1
        try:
            #checks whether new data is available
            if self.is_ready_to_read(time_out):
                while True:
                    #read data
                    new_data = self._connection.recv(2048).decode()
                    #close the socket if the visualizer closed the socket
                    if not new_data or new_data == '':
                        self.close()
                        return 1
                    self._raw_data += new_data
                    #process the data if the visualizer finished sending
                    #the visualizer ends every sending process with the '\n' character
                    if not new_data.find('\n') == -1:
                        self.on_raw_data(self._raw_data)
                        return 0
            else:
                return 0

        except socket.error as error:
            self.close()
            print(error)
            return -1

    #process the raw data received by the receive function
    #primally splits data in seperate control symbols and asp atoms
    def on_raw_data(self, raw_data):
        print("Solver.py 179")
        #the visualizer seperates every atom and control symbol with the '.' character
        data = raw_data.split('.')
        for atom in data:
            if len(atom) > 0:
                if not (len(atom) == 1 and atom[0] == '\n'):    #the split function returns the string "\n" as last string which should not be processed
                    if self._args.input:
                        print(atom)
                    if atom[0] == '%' and atom[1] == '$':       #strings that begin with '%$' are control symbols and are handles by the on_control_symbol function
                        atom = atom[2 :].lower()
                        self.on_control_symbol(parse_term(atom))
                    else:
                        self._data.append(atom)
        self._raw_data = ''
        if len(self._data) > 0:
            #processed asp atoms
            self.on_data(self._data)
        self._data = []

    #process received control symbols
    def on_control_symbol(self, symbol):
        print("Solver.py 201")
        if symbol.name == 'reset':
            #resets the solver to receive a new instance and discard old data
            #the visualizer will send this symbol when it is sending a new instance afterwards
            self._to_send = {}
            self._data = []
            self._control = Control()
            self._sended = - 1
        elif symbol.name == 'done' and len(symbol.arguments) == 1:
            try:
                #the visualizer sends 'done([time step])' after it has visualized the time step [time step]
                #sends the data from the _to_send dictonary
                #the key is the next time step
                self.send_step(symbol.arguments[0].number + 1)
            except:
                return

    #sends the data from the _to_send dictonary
    def send_step(self, step):
        print("Solver.py 220")
        #only sends data if it was not send yet
        if step in self._to_send and step > self._sended:
            self._sended = step
            #send the atoms
            for atom in self._to_send[step]:
                self._connection.send((str(atom) + '.').encode())
        #send the '\n' charater to show end of sending
        self._connection.send('\n'.encode())

    #handels the asp atoms
    def on_data(self, data):
        #add atoms to clingo
        for atom in data:
            self._control.add('base', [], atom + '.')
        if not self.solve().satisfiable:
            return
        print("I can be solved")
        #send data to the visualizer after solving
        self.send('%$RESET.')
        self.send_step(0)

    #solve the instance
    def solve(self):
        print("Solver.py 244")
        #loads the given encoding and ground
        self._control.load(self._args.encoding)

        self._control.ground([('base', [])])
        solve_future = self._control.solve(on_model = self.on_model, async_ = True)
        self._solve_start = time.time()
        #check if data was sended to the solver while solving to interrupt solving if needed
        while(True):
            if self.is_ready_to_read():
                solve_future.cancel()
                return solve_future.get()
            finished = solve_future.wait(5.0)
            if finished:
                return solve_future.get()
            #check timeout
            elif self._args.timeout > 0 and (time.time() - self._solve_start) > self._args.timeout:
                print('solver timeout after ' , time.time() - self._solve_start, 'seconds')
                return solve_future.get()

    #model callback for self._control.solve in self.solve
    def on_model(self, model):
        print("Solver.py 265")
        print('found solution')
        #add empty entry to dictonary
        self._to_send[0] = []
        #append all occurs atoms to the self._to_send dictonary
        #Note: all atoms are added to the key 0 to send all atoms immeditly after solving
        #this is different in the interactive variant
        symbols = model.symbols(shown=True)
        if len(symbols) == 0:
            symbols = model.symbols(atoms=True)
        for atom in symbols:
            if self._args.atoms:
                print(atom)
            if (atom.name == 'occurs'
                and len(atom.arguments) == 3
                and atom.arguments[0].name == 'object'
                and atom.arguments[1].name == 'action'):
                if self._args.occurs:
                    print(atom)
                self._to_send[0].append(atom)
        print(self._to_send[0])
        return True

    #solver main function
    def run(self):
        print("Solver.py 290")
        print('Start ' + self._name)
        self.connect()
        #loop to receive data
        while(True):
            if self.receive(1.0) != 0:
                return

#incremental solver
#overrides only the solve function
class SolverInc(Solver):
    def __init__(self):
        print("SOLVERINC Constructor")
        super(SolverInc, self).__init__()

    def solve(self):
        print("SOLVERINC Solve")
        #loads the given encoding
        self._control.load(self._args.encoding)
        self._control.add("check", ["t"], "#external query(t).")
        result = None
        step = 0

        #solve incremental
        self._solve_start = time.time()
        while True:
            if step > self._args.steps and self._args.steps > 0:
                print("maximum number of steps exceeded")
                return result
            print('ground: ' + str(step))
            if step == 0:
                self._control.ground([('base', []), ('init', []),
                                      ('step', [step]),('check', [step])])
            else:
                self._control.ground([('step', [step]),('check', [step])])
            self._control.assign_external(Function('query', [step]), True)

            print('solve: ' + str(step))
            solve_future = self._control.solve(on_model = self.on_model, async_ = True)
            #check if data was sended to the solver while solving to interrupt solving if needed
            while(True):
                if self.is_ready_to_read():
                    solve_future.cancel()
                    print('solving interrupted')
                    return solve_future.get()
                finished = solve_future.wait(5.0)
                if finished:
                    result = solve_future.get()
                    print(result)
                    break
                #check timeout
                elif self._args.timeout > 0 and (time.time() - self._solve_start) > self._args.timeout:
                    print('solver timeout after ' , time.time() - self._solve_start, 'secounds')
                    return solve_future.get()

            self._control.assign_external(Function('query', [step]), False)
            step += 1
            if not result.unsatisfiable:
                return result

#interactive solver
#uses solve function from the incremental solver
#but implements own model callback and data callback functions
class SolverInt(SolverInc):

    def __init__(self):
        super(SolverInt, self).__init__()
        #saves initial data
        self._inits = []

    #handels the asp atoms
    def on_data(self, data):
        #add atoms to the inits list
        for atom in data:
            self._inits.append(atom)
        #reset clingo
        self._control = Control()

        #add inits to clingo
        for atom in self._inits:
            self._control.add('base', [], atom + '.')
        #add finished steps to clingo
        for ii in range(0, self._sended + 1):
            if ii in self._to_send:
                for atom in self._to_send[ii]:
                    self._control.add('base', [], str(atom) + '.')

        if not self.solve().satisfiable:
            return
        #send step to the visualizer after solving
        if self._sended + 1 in self._to_send:
            self.send_step(self._sended + 1)
        elif self._sended + 2 in self._to_send:
            self.send_step(self._sended + 2)

    #model callback for self._control.solve in self.solve
    def on_model(self, model):
        print('found solution')
        #clear self._so_send
        self._to_send = {}
        #append all occurs atoms to the self._to_send dictonary
        #Note: all atoms are added to the step in which their occur
        #so the self._send_step function sends only the atoms for the next step
        symbols = model.symbols(shown=True)
        if len(symbols) == 0:
            symbols = model.symbols(atoms=True)
        for atom in symbols:
            if self._args.atoms:
                print(atom)
            if (atom.name == 'occurs'
                and len(atom.arguments) == 3
                and atom.arguments[0].name == 'object'
                and atom.arguments[1].name == 'action'):
                if self._args.occurs:
                    print(atom)
                step = atom.arguments[2].number
                #add step to dictonary
                if step not in self._to_send:
                    self._to_send[step] = []
                self._to_send[step].append(atom)
        return True

class Solverlazycbs(Solver):
    def __init__(self):
        super(Solverlazycbs, self).__init__()
        self.grid_size_and_time = ""
        self.time_step = 0
        self.number_of_robots = 0
    # handels the asp atoms
    def on_data(self, data):
        print("Solver.py 420")
        # # create asp file to translate
        # with open('viz_instance2solve.lp', 'w') as f:
        #     for atom in data:
        #         f.write(atom + '.\n')
        viz_instance2solve = []
        #Data contains all the information from the visualizer, it is called in network.py and contains the content of model.to_actions_str()
        for line in data:
            #Extracting time step and grid size from the data sent
            if("Time Step and Grid Size:" in line):
               line = line.replace('\n','')
               line_split = line.split("\t")
               self.grid_size_and_time = line_split
            #Increasing the number of robots each time an init robot statement is encountered
            elif "init" in line and "robot" in line:
                self.number_of_robots += 1
            else:
                viz_instance2solve.append(line + '.\n')
        #Creating a temp folder in case it does not exist already
        if not path.exists("../temp"):
            os.mkdir("../temp")
        #Extracting the time step from data
        self.time_step = int(self.grid_size_and_time[1])
        #Width and height of the ecbs file is 2 more than the width of the map, this is because of the padding
        w = int(self.grid_size_and_time[2])+2
        h = int(self.grid_size_and_time[3])+2
        #Creating a 2D matrix of all 1s
        arr = [[1 for x in range(w)] for y in range(h)] 
        #Extracting all data from an instance to create a .ecbs file that represents the map layout being visualized
        for line in data:
            if "init" in line and "highway" in line:
                line = line.replace("(",",")
                line = line.replace(")",",")
                line = line.split(',')
                line[-5] = line[-5].replace(" ", "")
                line[-4] = line[-4].replace(" ", "")
                x_coord = int(line[-5])
                y_coord = int(line[-4])
                arr[x_coord][y_coord] = 0
        #Writing to the .ecbs file
        with open("../temp/map.ecbs",'w') as f:
            f.write(str(w) + "," + str(h) + "\n")
            for i in range(h):
                for j in range(w):
                    f.write(str(arr[j][i]))
                    if(j < (w-1)):
                        f.write(",")
                        
                f.write("\n")
        self.solve()
        
    def solve(self):
        #Opening the file name
        map_file_name = "../temp/map.ecbs"
        #Getting the scen file through the instance and remaining plan
        scene_file_name = convert("../temp/current-instance.lp","../temp/remaining-plan.lp",map_file_name ,self.number_of_robots)
        #Resetting the number of robots each time it is solved
        self.number_of_robots = 0
        new_cost = 0
        with open("../temp/remaining-plan.lp", "r") as plan_file_reader:
            all_lines = plan_file_reader.readlines()
            for line in all_lines:
                if "move" in line:
                    new_cost += 1
        all_constraints = []
        with open("../temp/remaining-plan.lp","r") as current_plan_file_reader:
            all_lines = current_plan_file_reader.readlines()
            for line in all_lines:
                if "Constraints:" in line:
                    line = line.split()
                    line.pop(0)
                    if(len(line) > 0):
                        for i in range(len(line)):
                            individual_constraint = line[i]
                            individual_constraint = individual_constraint.replace('(','')
                            individual_constraint = individual_constraint.replace(')','')
                            individual_constraint = individual_constraint.split(",")
                            constraint_tuple = (int(individual_constraint[0]),(((int(individual_constraint[1]),int(individual_constraint[2]))),(int(individual_constraint[3]),int(individual_constraint[4]))),int(individual_constraint[5]) - int(self._model.get_current_step()), int(new_cost) )
                            all_constraints.append(constraint_tuple)
        temp=init("../temp/map.ecbs",scene_file_name, 2, all_constraints)
        solution_file_name = "../temp/solution.txt"
        with open(solution_file_name, "w") as backend_solution:
            backend_solution.write(temp)
        new_plan_file_name = convert_solution_to_plan(solution_file_name, 2)
        lines = []
        past_actions = []
        with open("../temp/current-instance.lp","r") as current_instance_reader:
            lines = current_instance_reader.readlines()
        now = datetime.now()
        date_and_time = now.strftime("%d-%m-%Y-%H:%M:%S")
        os.mkdir("../temp/"+date_and_time)
        final_plan_and_instance = "../temp/"+date_and_time+"/new-instance-and-plan.lp"
        with open(final_plan_and_instance,"w") as current_plan_writer:
            for line in lines:
                agent_num = -1
                agent_x = -1
                agent_y = -1
                agent_dx = 0
                agent_dy = 0
                if "highway" in line or "node" in line or "%" in line:
                        current_plan_writer.write(line)
                if "init" in line and "robot" in line and "at" in line:
                        line = line.replace("(",",")
                        line = line.replace(")",",")
                        line = line.split(",")
                        agent_num = int(line[3])
                        agent_x = int(line[-5])
                        agent_y = int(line[-4])
                        with open("../temp/complete-plan.lp","r") as past_movement_reader:
                            all_actions = past_movement_reader.readlines()
                            for current_action in all_actions:
                                current_action = current_action.replace("(",",")
                                current_action = current_action.replace(")",",")
                                current_action = current_action.split(",")
                                if(agent_num == int(current_action[3])):
                                    if int(current_action[-2]) < self.time_step:
                                        agent_dx += int(current_action[-6])
                                        agent_dy += int(current_action[-5])
                            agent_x -= agent_dx
                            agent_y -= agent_dy
                        line_to_be_written = "init(object(robot,"+str(agent_num)+"),value(at,("+str(agent_x)+", "+str(agent_y)+"))).\n"
                        agent_x = -1
                        agent_y = -1
                        agent_dx = 0
                        agent_dy = 0
                        current_plan_writer.write(line_to_be_written)
            with open("../temp/complete-plan.lp","r") as current_plan_reader:
               
                all_plan_lines = current_plan_reader.readlines()

                for line in all_plan_lines:
                    if "move" in line:
                        result = [int(d) for d in re.findall(r'-?\d+', line)]
                        if(result[len(result) - 1] < self.time_step):
                            current_plan_writer.write(line)
            with open(new_plan_file_name,"r") as new_plan_reader:
                all_lines = new_plan_reader.readlines()
                for line in all_lines:
                    if "occurs" in line and "move" in line and "robot" in line:
                        line_split = re.split("\(|\,|\)",line)
                        line_final = "occurs(object(robot,"+line_split[3]+"),action(move,("+line_split[8]+", "+line_split[9]+")),"+str(int(line_split[12]) + int(self.time_step))+").\n"
                        current_plan_writer.write(line_final)
        self.send("%$COMPLETE " + final_plan_and_instance + " \n")
#main
def main():
    print("MAIN")
    solver = Solver()
    mode = solver.get_mode()
    #choose solver mode
    if mode == 'default':
        pass
    elif mode == 'incremental':
        solver = SolverInc()
    elif mode == 'interactive':
        solver = SolverInt()
    elif mode == 'online':
        solver = SolverInt()
    
    elif mode == 'lazycbs':
        solver = Solverlazycbs()
    solver.run()

if __name__ == "__main__":
    main()

