from dataclasses import replace
import os.path
from shutil import move
from clingo.control import Control
from clingo.ast import ProgramBuilder, parse_string

from . import configuration
import traceback
from .model import *

class AspParser(object):
    def __init__(self):
        self._model = Model()
        self._control = Control()
        self._model_view = None
        self._solver = None
        self._programs = {}
        self._str_model = ''
        self._parser_widget = None
        self.reset_programs()

    def set_model_view(self, model_view):
        self._model_view = model_view

    def set_solver(self, solver):
        self._solver = solver

    def set_program(self, program_name, program):
        self._programs[program_name] = program

    def add_program(self, program_name, program):
        if program_name in self._programs:
            self._programs[program_name] += program
        else:
            self._programs[program_name] = program
        if self._parser_widget is not None:
            self._parser_widget.update()

    def delete_program(self, program_name):
        if program_name in self._programs:
            del self._programs[program_name]
        if self._parser_widget is not None:
            self._parser_widget.update()

    def set_parser_widget(self, parser_widget):
        if self._parser_widget is parser_widget:
            return
        temp = self._parser_widget
        self._parser_widget = parser_widget
        if temp is not None:
            temp.set_parser(None)
        if parser_widget is not None:
            parser_widget.set_parser(self)
            parser_widget.update()

    def on_model(self, m):
        #Adding all the symbols in the atom to the model, if it is the instance file, these would be action atoms, in instance files, it would be mainly init atoms
        for x in m.symbols(atoms=True):
            #Inside on_atom, different methods are called depending on the type of the atom
            self.on_atom(x)
            self._str_model += str(x) + '\n'
        #When the instance followed by the plan have been loaded, all occurs atoms would have been loaded in the model, this would mean that the array containing the movements of all agents at different timesteps would be ready. That array is being accessed in the next line
        all_movements = self._model.get_agent_movements()
        #Checking if the instance file provided a time step. If a time step was provided, then the initial location would be the one before the movements until the current time step were made. Therefore, requiring us to update the initial location if a timestep was provided.
        if self._model.is_instance_loaded():
            #Iterating through all agents 
            for i in range(self._model.agent_count):
                #Stores the sum of movements until the current time step for the current agent
                agent_movement_before_time_step_loaded = [0,0]
                #Iterating through all the movements
                for movement in all_movements:
                    #Checking if the movement is for the current agent and occurred before the current time step
                    if (int(movement[0]) - 1) == i and int(movement[2]) < self._model.get_current_step():
                        temp_str = str(movement[1]).replace("(",",")
                        temp_str = temp_str.replace(")",",")
                        temp_split = temp_str.split(",")
                        #Adding the current movement to the sum of movements before the timestep
                        agent_movement_before_time_step_loaded[0] += int(temp_split[1])
                        agent_movement_before_time_step_loaded[1] += int(temp_split[2])
                #Updating the initial location by subtracting the movements before the current time step from the current position        
                self._model.update_initial_location_with_change(i+1, agent_movement_before_time_step_loaded[0], agent_movement_before_time_step_loaded[1])
        #Getting the correct starting location of all the agents with their ID in format [(ID,(x,y))]
        all_initial_locations = self._model.get_starting_agent_locs()
        
        for i in range(self._model.agent_count):
            #Store the timestep-wise location and movements of all agents
            current_agent_locs = []
            current_agent_movements = []
            #Adding the first location for each agent from the initial locations array calculated above
            for initial_loc in all_initial_locations:
                if (initial_loc[0] - 1) == i:
                    current_agent_locs.append(initial_loc[1])
            #Checking if the movemement was for the current agent, adding it to the array if it was
            for movement in all_movements:
                if (int(movement[0]) - 1) == i:
                    current_agent_movements.append(movement)
            #Bubble sorting all the movements according to time step to get a sorted array of robot movements for the current agent
            number_of_movements = len(current_agent_movements)
            for k in range(number_of_movements-1):
                # range(n) also work but outer loop will
                # repeat one time more than needed.
                # Last k elements are already in place
                for j in range(0, number_of_movements-k-1):
 
                    # traverse the array from 0 to n-k-1
                    # Swap if the element found is greater
                    # than the next element
                    if current_agent_movements[j][2] > current_agent_movements[j + 1][2] :
                        current_agent_movements[j], current_agent_movements[j + 1] = current_agent_movements[j + 1], current_agent_movements[j]
            #Iterating through the sorted agent movemements to calculate the agent locations at each timestep
            for movement in current_agent_movements:
                temp_str = str(movement[1]).replace("(",",")
                temp_str = temp_str.replace(")",",")
                temp_split = temp_str.split(",")
                new_agent_loc = (current_agent_locs[len(current_agent_locs) - 1][0] + int(temp_split[1]),current_agent_locs[len(current_agent_locs) - 1][1] + int(temp_split[2]))
                current_agent_locs.append(new_agent_loc)
            if (self._model.is_time_step_provided() and self._model.is_instance_loaded()) or not self._model.is_time_step_provided():
                self._model.add_agent_locations_sorted(current_agent_locs)
            #Turning on the path for each robot by default
            robot = self._model.get_item('robot',i + 1)
            if robot is not None:
                robot.set_draw_path(True)
        self.done_instance()

    def on_atom(self, atom):
        if atom is None:
            return
        if len(atom.arguments) < 2:
            return
        obj = atom.arguments[0]
        value = atom.arguments[1]
        #If it is an occurs atom, on_occurs_atom is called, otherwise on_init_atom is called
        if atom.name == 'occurs' and len(atom.arguments) == 3:
            self._on_occurs_atom(obj, value, atom.arguments[2].number)
        elif atom.name == 'init' and len(atom.arguments) == 2:
            self._on_init_atom(obj, value)

    def _on_occurs_atom(self, obj, action, time_step):
        try:
            if obj.name == 'object' and action.name == 'action':

                kind = str(obj.arguments[0])
                ID = str(obj.arguments[1])
                
                action_name = str(action.arguments[0])
                action_value = action.arguments[1]
                #If it is a movement, the movement is added to the list of agent movement. This list contains the list of agent movements along with their ID's
                if action_name == 'move':
                    self._model.add_agent_movements((ID,action_value,time_step))
                
                item = self._model.get_item(kind, ID, True, True)
                if item is not None:
                    item.set_action(action, time_step)
                if time_step > self._model.get_num_steps(): 
                    self._model.set_num_steps(time_step)
                self._model.set_editable(True)
        except:
            print('invalid occurs format, expecting: occurs(object([object], [objectID]), action([action], [arguments]), [time step])')

    def _on_init_atom(self, obj, value):
        try:
            if (obj.name == 'object' and value.name == 'value'
                    and len(obj.arguments) == 2
                    and len(value.arguments) == 2):
                kind = str(obj.arguments[0])
                ID = str(obj.arguments[1])
                value_name = str(value.arguments[0])
                value_value = value.arguments[1]
                
                item = self._model.get_item(kind, ID, True, self._model.get_editable())
                #If the item is a robot, the initial location of the robot is added to the list storing agent locatiions
                if kind == 'robot' and value_name == 'at' and not self._model.is_instance_loaded():
                    #Extracting relevant information about ID and location from the atom
                    replacement_str = str(value_value).replace('(',',')
                    replacement_str = replacement_str.replace(')',',')
                    split_val = replacement_str.split(",")
                    self._model.add_agent_locations(int(ID), int(split_val[1]), int(split_val[2]) )
                if item is not None:
                    result = item.parse_init_value(value_name,
                                                    value_value)
                    if result == 0: 
                        return
                if kind == 'node' and value_name == 'at':                  #init nodes
                    if (value_value.arguments[0].number, 
                                            value_value.arguments[1].number) not in self._model._nodes:
                        self._model.add_node(value_value.arguments[0].number, 
                                         value_value.arguments[1].number, ID)
                    return

                elif kind == 'highway' and value_name == 'at':             #init highways
                    if (value_value.arguments[0].number, 
                                            value_value.arguments[1].number) not in self._model.get_highways():
                        self._model.add_highway(value_value.arguments[0].number, 
                                            value_value.arguments[1].number)
                    return

                elif kind == 'product' and value_name == 'on':              #init products
                    if value_value.arguments is None:
                        shelf = self._model.get_item('shelf', value_value, True, True)
                        shelf.set_product_amount(ID, 0)
                        return
                    else:
                        shelf = self._model.get_item('shelf', value_value.arguments[0], True, True)
                        shelf.set_product_amount(ID, value_value.arguments[1].number)
                        return

                self._model.add_init('init(' + str(obj) + ', ' + str(value) + ')')

        except Exception as e:
            if ll_config.get('features', 'debug'):
                traceback.print_exc()
            print(('invalid init: init(' + str(obj) + ', ' + str(value) + ')'))

    def done_instance(self, enable_auto_solve = True):
        #If a time step was present in the file, that means an instance file was loaded into asprilo.
        if self._model.is_time_step_provided():
            self._model.set_instance_loaded(True)
        self._model.accept_new_items()
        self._model.update_windows()
        if (self._solver is not None
            and configuration.config.get('visualizer', 'auto_solve') 
            and enable_auto_solve):
            self._solver.set_model(self._model)
            self._solver.solve()

        if (self._model_view is not None):
            self._model_view.update()
            self._model_view.resize_to_fit()

        if self._parser_widget is not None:
            self._parser_widget.update()

    def clear_model(self):
        self._model.clear()

    def clear_model_actions(self, restart = True):
        self._model.clear_actions()
        if restart:
            self._model.restart()

    def reset_programs(self):
        self._programs = {}
        str_load_files = configuration.ll_config.get('features', 'load_files')
        try:
            str_load_files = str_load_files.replace(' ', '')
            files = str_load_files.split(',')
            for file_name in files:
                if file_name != '':
                    if os.path.isfile(file_name):
                        ff = open(file_name)
                        self._programs[file_name] = ff.read()
                        ff.close()
        except RuntimeError as error:
            print(error)
            print('file parsing failed')
            return -1
        if self._parser_widget is not None:
            self._parser_widget.update()

    def reset_grounder(self):
        self._str_model = ''
        self._control = Control()
        if self._parser_widget is not None:
            self._parser_widget.update()

    def load(self, file_name):
        if not os.path.isfile(file_name):
            print('can not open file: ', file_name)
            return -1

        print('load file: ' + file_name)
        try:
            ff = open(file_name)
            self._programs[file_name] = ff.read()
            #Reading the lines from the last loaded file and looking for time step information in it, if it is found that means that it is an instance file and relevant variables are updated accordingly.
            all_lines = self._programs[file_name].split("\n")
            for line in all_lines:
                if "Time Step:" in line:
                    #Getting the time step from the instance file
                    time_step = int(line.split()[2])
                    #Setting the time step in the model, so that it knows when to execute the plan from
                    self._model.set_time_step_provided(True)
                    self._model.go_to_time_step(time_step)
            ff.close()
            if self._parser_widget is not None:
                self._parser_widget.update()
        except RuntimeError as error:
            print(error)
            print('file loading failed')
            return -2
        return 0

    def parse(self):
        if self._control is None:        
            return
        try:
            with ProgramBuilder(self._control) as bb:
                for key in self._programs:
                    parse_string(self._programs[key], lambda stm: bb.add(stm))
            self._control.ground([('base', [])])
            result = self._control.solve(on_model=self.on_model)
        except RuntimeError as error:
            print(error)
            return -2
        return 0

    def parse_file(self, file_name, clear = False, clear_actions = False, clear_grounder = True):
        if not os.path.isfile(file_name):
            print('can not open file: ', file_name)
            return -1
        #If the time step was detected in the instance file, the model will not execute the clear statements
        if self._model.is_time_step_provided():
            print("Nothing will be cleared as time step is provided in instance")
        else:
            if clear:
                self.reset_programs()
                self.clear_model()

            if clear_actions:
                self.reset_programs()
                self.clear_model_actions()

            if (clear or clear_actions) and self._model_view is not None:
                self._model_view.stop_timer()

            if clear_grounder:
                self.reset_grounder()
        #Loading the file into the parser, the time step(If provided) is set in this function
        if self.load(file_name) < 0:
            return -1
        #Parses individual atoms and adds them to the model, depending on actions/init statements, different methods are called inside on_atom
        if self.parse() < 0:
                return -2
        return 0

    def load_instance(self, file_name, create_png = False):
        #Parsing all the atoms from the file and adding them to the model
        result = self.parse_file(file_name, clear = True)
        if result < 0:
            return result

        if (self._model_view is not None 
            and (configuration.config.get('visualizer', 'create_pngs') or create_png)):

            rect = self._model_view.sceneRect()
            position  = self._model_view.mapFromScene(QPoint(rect.x(), rect.y()))
            position2 = self._model_view.mapFromScene(QPoint(rect.x() + rect.width(), 
                                                            rect.y() + rect.height()))
            pixmap = self._model_view.grab(QRect(position.x(), position.y(), 
                                                position2.x() - position.x(), 
                                                position2.y() - position.y()))
            pixmap.save(file_name[0 : file_name.rfind('.')] + '.png')
        self._model.update_windows()
        return 0

    def list_programs(self):
        for key in self._programs:
            yield key

    def get_model(self):
        return self._model

    def get_program(self, program_name):
        if program_name in self._programs:
            return self._programs[program_name]
        return None

    def get_program_count(self):
        return len(self._programs)

    def get_str_model(self):
        return self._str_model
