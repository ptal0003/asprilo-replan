from time import time
from .visualizerItem import *
from .visualizerGraphicItem import *
from .modelView import ModelView

class Model(object):
    def __init__(self):
        self._windows = []
        self._sockets = []
        self._items = {}
        self._graphic_items = {}
        self._new_items = {}
        self._editable = True
        self._grid_size = (1, 1)
        self._nodes = []                #pairs of x and y
        self._blocked_nodes = [(1,1)]   #pairs of x and y
        self._highways = []             #pairs of x and y
        self._node_ids = {}
        self._inits = []                #list of unhandled inits
        self._notifier = None
        self._num_steps = 0
        self._current_step = 0

        self._displayed_steps = -1
        self.init_agent_locations = []
        self.all_agent_movements = []
        self.agent_locations_sorted = []
        self.instance_loaded = False
        self.time_step_provided = False
        self.instance_files_loaded = []
        self.plan_files_loaded = []
        self.agent_count = 0
        self.vertex_constraints = []
        self.edge_constraints = []
    def clear(self):
        for window in self._windows:
            if isinstance(window, ModelView):
                window.clear()
        self._graphic_items = {}
        self._items = {}
        self._new_items = {}
        self._editable = True
        self.agent_count = 0
        self._grid_size = (1, 1)
        self._nodes = []                #pairs of x and y
        self._blocked_nodes = [(1,1)]   #pairs of x and y
        self._highways = []             #pairs of x and y
        self._inits = []                #list of unhandled inits
        self._num_steps = 0
        self._current_step = 0
        self._displayed_steps = -1

        self.init_agent_locations = []
        self.all_agent_movements = []
        self.agent_locations_sorted = []
        self.instance_loaded = False
        self.time_step_provided = False
        self.vertex_constraints = []
        self.edge_constraints = []
        self.update_windows()
    
    def set_instance_loaded(self,loaded):
        self.instance_loaded = loaded
    def set_vertex_constraints(self,new_vertex_constraints):
        self.vertex_constraints = new_vertex_constraints
    def set_edge_constraints(self,new_edge_constraints):
        self.edge_constraints = new_edge_constraints
    def get_vertex_constraints(self):
        return self.vertex_constraints
    def get_edge_constraints(self):
        return self.edge_constraints
    def is_instance_loaded(self):
        return self.instance_loaded
    def set_time_step_provided(self,provided):
        self.time_step_provided = provided
    def update_initial_location_with_change(self,ID, dx, dy):
        original_record = ()
        for location in self.init_agent_locations:
            if location[0] == ID:
                original_record = location
        self.init_agent_locations.remove(original_record)
        updated_record = (ID,(int(original_record[1][0]) - dx, int(original_record[1][1]) - dy )  )
        self.init_agent_locations.append(updated_record)
        
    def add_agent_movements(self,record):
        self.all_agent_movements.append(record)
    def get_agent_movements(self):
        return self.all_agent_movements
    def add_agent_locations(self,ID, x, y):
        record = (ID,(x,y))
        self.init_agent_locations.append(record)
    def get_starting_agent_locs(self):
        return self.init_agent_locations
    def is_time_step_provided(self):
        return self.time_step_provided
    def _add_item2(self, item):
        if item is None:
            return
        dictionarie = self._map_item_to_dictionarie(item, True)
        if dictionarie is None:
            return
        if str(item.get_id()) in dictionarie:
            return
        key = (item.get_kind_name(), str(item.get_id()))
        if key in self._new_items and not ignore_duplicates:
            return
        item.set_model(self)
        if isinstance(item, VisualizerGraphicItem):
            item.enable_drag(self._editable)
        dictionarie[str(item.get_id())] = item

    def add_item(self, item, add_immediately = False):
        if add_immediately:
            return self._add_item2(item)
        if item is None:
            return
        key = (item.get_kind_name(), str(item.get_id()))
        if key in self._new_items:
            return
        self._new_items[key] = item

    def accept_new_items(self, item_kinds = None):
        add_items = []
        if item_kinds == None:
            for item in self._new_items.values():
                add_items.append(item)
        else:
            for item_kind in item_kinds:
                for key in self._new_items:
                    if key[0] == item_kind:
                        add_items.append(self._new_items[key])
        self.discard_new_items(item_kinds)
        for item in add_items:
            self._add_item2(item)
        for socket in self._sockets:
            for item in add_items:
                socket.model_expanded(item.to_init_str())
            if len(add_items) > 0:
                socket.model_expanded('\n')

    def discard_new_items(self, item_kinds = None):
        if item_kinds == None:
            self._new_items.clear()
            return
        delete_items = []
        for item_kind in item_kinds:
            for key in self._new_items:
                if key[0] == item_kind:
                    delete_items.append(key)
        for key in delete_items:
            del self._new_items[key]
    def go_to_time_step(self, time_step):
        self.set_current_step(time_step)
        self.update_windows() 
    def add_agent_locations_sorted(self, list):
        self.agent_locations_sorted.append(list)
    def get_agent_locations_sorted(self):
        return self.agent_locations_sorted
    def remove_item(self, item):
        if item is None:
            return
        key = (item.get_kind_name(), str(item.get_id()))
        item2 = self._new_items.pop(key, None)
        if item2 is not None:
            item2.set_model(None) 
            return

        dictionarie = self._map_item_to_dictionarie(item, True)
        if dictionarie is None:
            return
        if str(item.get_id()) not in dictionarie:
            return
        item.set_model(None)
        del dictionarie[str(item.get_id())]

    def add_init(self, init):
        self._inits.append(str(init) + '.')

    def add_window(self, window):
        if window not in self._windows:
            self._windows.append(window)

    def remove_window(self, window):
        if window in self._windows:
            self._windows.remove(window)

    def add_socket(self, socket):
        if socket not in self._sockets:
            self._sockets.append(socket)

    def remove_socket(self, socket):
        if socket in self._sockets:
            self._sockets.remove(socket)

    def add_node(self, x, y, node_id = None):
        if (x,y) in self._nodes:
            return

        self._nodes.append((x, y))
        self._node_ids[(x,y)] = node_id
        if (x,y) in self._blocked_nodes:
            self._blocked_nodes.remove((x,y))
        if x > self._grid_size[0] or y > self._grid_size[1]:
            self.set_grid_size(max(x, self._grid_size[0]), max(y, self._grid_size[1]))

    def add_highway(self, x, y):
        self._highways.append((x, y))

    def is_node(self, x, y):
        return (x, y) in self._nodes

    def is_highway(self, x, y):
        return (x, y) in self._highways
    def is_blocked_node(self, x, y):
        return (x, y) in self._blocked_nodes

    def remove_node(self, x, y):
        if (x,y) not in self._nodes:
            return

        self._nodes.remove((x, y))
        if (x,y) not in self._blocked_nodes:
            self._blocked_nodes.append((x,y))

    def remove_highway(self, x, y):
        if (x,y) not in self._highways:
            return
        self._highways.remove((x,y))

    def set_grid_size(self, X, Y, enable_nodes = False):
        if X < 1:
            X = 1
        if Y < 1:
            Y = 1

        to_remove = []
        for node in self._nodes:        #remove old nodes
            if node[0] > X:
                to_remove.append(node)
            elif node[1] > Y:
                to_remove.append(node)
        for node in to_remove:
            self._nodes.remove(node)
            self._blocked_nodes.remove(node)

        if enable_nodes:
            for x in range(self._grid_size[0] + 1, X + 1):
                for y in range(1, Y + 1):
                    self._nodes.append((x,y))

            for x in range(1, self._grid_size[0] + 1):
                for y in range(self._grid_size[1] + 1, Y + 1):
                    self._nodes.append((x,y))


        else:
            self._blocked_nodes = []
            for x in range(1, X+1):
                for y in range(1, Y+1):
                    self._blocked_nodes.append((x,y))
            for node in self._nodes:
                self._blocked_nodes.remove(node)
        self._grid_size = (X, Y)

    def set_editable(self, editable):
        self._editable = editable
        for items_dic in self._graphic_items.values():
            for item in items_dic.values():
                item.enable_drag(self._editable)

    def set_num_steps(self, num_steps):
        self._num_steps = num_steps

    def create_item(self, item_kind, ID = None, add_immediately = False):
        item = None
        if ID is None:
            dic = None
            if item_kind == 'shelf':
                if 'shelf' not in self._graphic_items:
                    self._graphic_items['shelf'] = {}
                dic = self._graphic_items['shelf']
            elif item_kind == 'pickingStation':
                if 'pickingStation' not in self._graphic_items:
                    self._graphic_items['pickingStation'] = {}
                dic = self._graphic_items['pickingStation']
            elif item_kind == 'chargingStation':
                if 'chargingStation' not in self._graphic_items:
                    self._graphic_items['chargingStation'] = {}
                dic = self._graphic_items['chargingStation']
            elif item_kind == 'robot':
                if 'robot' not in self._graphic_items:
                    self._graphic_items['robot'] = {}
                dic = self._graphic_items['robot']
            elif item_kind == 'order':
                if 'order' not in self._graphic_items:
                    self._graphic_items['order'] = {}
                dic = self._graphic_items['order']
            elif item_kind == 'checkpoint':
                if 'checkpoint' not in self._graphic_items:
                    self._graphic_items['checkpoint'] = {}
                dic = self._graphic_items['checkpoint']
            elif item_kind == 'task':
                if 'task' not in self._graphic_items:
                    self._graphic_items['task'] = {}
                dic = self._graphic_items['task']

            ID = 1
            break_loop = False
            while not break_loop:
                break_loop = True
                for key in dic:
                    if str(key) == str(ID): 
                        ID += 1
                        break_loop = False
                        break

        ID = str(ID)
        if item_kind == 'shelf':
            item = Shelf(ID)
        elif item_kind == 'pickingStation':
            item = PickingStation(ID)
        elif item_kind == 'chargingStation':
            item = ChargingStation(ID)
        elif item_kind == 'robot':
            item = Robot(ID)
            self.agent_count += 1
        elif item_kind == 'order':
            item = Order(ID)
        elif item_kind == 'checkpoint':
            item = Checkpoint(ID)
        elif item_kind == 'task':
            item = Task(ID)

        if item is not None:
            self.add_item(item, add_immediately)
        return item

    def update(self, update_windows = True):
        if self._current_step > self._num_steps or self._num_steps == 0:
            return self._current_step
        for socket in self._sockets:
            if socket.is_waiting():
                return self._current_step
        for items_dic in self._items.values():
            for item in items_dic.values():
                item.on_step_update(self._current_step)
        for items_dic in self._graphic_items.values():
            for item in items_dic.values():
                item.do_action(self._current_step)

        if self._displayed_steps < self._current_step and len(self._sockets) > 0 and self._num_steps <= self._current_step:
            self._displayed_steps = self._current_step
            iterator = iter(self._sockets)
            value = next(iterator)
            value.done_step(self._current_step)
            self.notify_sockets(iterator, value, self._current_step)

        self._current_step += 1
        if(update_windows):
            self.update_windows()
        return self._current_step

    def notify_sockets(self, iterator, value, step):
        if value.is_waiting():
            if self._notifier is not None:
                self._notifier.stop()

            self._notifier = QTimer()
            self._notifier.setSingleShot(True)
            self._notifier.timeout.connect(lambda: self.notify_sockets(iterator, value, step))
            self._notifier.start(100)
            return
        else:
            try:
                value = next(iterator)
            except StopIteration:
                return
            self.notify_sockets2(iterator, value, step)

    def notify_sockets2(self, iterator, value, step):
        if value.is_waiting():
            if self._notifier is not None:
                self._notifier.stop()

            self._notifier = QTimer()
            self._notifier.setSingleShot(True)
            self._notifier.timeout.connect(lambda: self.notify_sockets2(iterator, value, step))
            self._notifier.start(100)
            return
        value.done_step(step)
        self.notify_sockets(iterator, value, step)

    def undo(self):
        if self._current_step == 0:
            return self._current_step
        self._current_step -= 1
        for items_dic in self._items.values():
            for item in items_dic.values():
                item.on_step_undo(self._current_step)
        for items_dic in self._graphic_items.values():
            for item in items_dic.values():
                item.undo_action(self._current_step)
        self.update_windows()
        return self._current_step

    def clear_actions(self):
        for items_dic in self._graphic_items.values():
            for item in items_dic.values():
                item.clear_actions()
        self._num_steps = 0

    def restart(self):
        for items_dic in self._graphic_items.values():
            for item in items_dic.values():
                item.restart()
        for items_dic in self._items.values():
            for item in items_dic.values():
                item.restart()
        self._current_step = 0
        self.update_windows()

    def skip_to_end(self):
        if self._editable:
            return
        while(self.update(False) <= self._num_steps):
            pass
        self.update_windows()

    def filter_items(self, item_kind = None, 
                        ID = None, position = None, 
                        return_first = False,
                        return_non_buffered = True,
                        return_buffered = False):
        result = []
        if ID is not None:
            ID = str(ID)
        if return_non_buffered:
            search_in = []
            if item_kind is None:
                for items_dic in self._graphic_items.values():
                    search_in.append(items_dic)
                if position is None:
                    for items_dic in self._items.values():
                        search_in.append(items_dic)
            else:
                if item_kind in self._graphic_items:
                    search_in.append(self._graphic_items[item_kind])
                if position is None:
                    if item_kind in self._items:
                        search_in.append(self._items[item_kind])
        
            for items_dic in search_in:
                if ID is not None:
                    if ID in items_dic:
                        item = items_dic[ID]
                        if position is None:
                            result.append(item)
                            if return_first:
                                return result
                        elif position == item.get_position():
                            result.append(item)
                            if return_first:
                                return result
                else:
                    for item in items_dic.values():
                        if position is None:
                            result.append(item)
                            if return_first:
                                return result
                        elif position == item.get_position():
                            result.append(item)
                            if return_first:
                                return result
            
        if return_buffered and position is None:
            for key in self._new_items:
                if ((key[0] == item_kind or item_kind is None)
                    and (key[1] == ID or ID is None)):
                    result.append(self._new_items[key])

        if return_first:
            return [None]
        return result

    def contains(self, item):
        if item is None:
            return False
        if item.get_kind_name() in self._graphic_items:
            return item.get_id() in self._graphic_items[item.get_kind_name()]
        elif item.get_kind_name() in self._items:
            return item.get_id() in self._items[item.get_kind_name()]

    def update_windows(self):
        for window in self._windows:
            window.update()

    def to_init_str(self):
        s = []
        for node in self._nodes:
            s.append('init(object(node, '
                    + str(node[0] + (node[1]-1) * self._grid_size[0])
                    +  '), value(at, ('
                    + str(node[0]) + ', ' + str(node[1]) + '))).')
        for node in self._highways:
            s.append('init(object(highway, '
                    + str(node[0] + (node[1]-1) * self._grid_size[0])
                    +  '), value(at, ('
                    + str(node[0]) + ', ' + str(node[1]) + '))).')
        for items_dic in self._graphic_items.values():
            for item in items_dic.values():
                s.append(item.to_init_str())
        for items_dic in self._items.values():
            for item in items_dic.values():
                s.append(item.to_init_str())
        for init in self._inits:
            s.append(str(init))
        return s
    def to_actions_str(self):
        s = []
        for items_dic in self._graphic_items.values():
                for item in items_dic.values():
                    for action in item.to_occurs_str():
                        if action is not None:
                            s.append(action)
        return s
    def save_to_file(self, file_name):
        ofile = open(file_name, 'w')
        try:
            #head
            ofile.write('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            ofile.write('\n%Grid size X: ' + str(self._grid_size[0]))
            ofile.write('\n%Grid size Y: ' + str(self._grid_size[1]))
            #Stores time step additionally when saving instance file, this is to ensure that the instance/plan can be reloaded right from where the user left
            ofile.write('\n%Time Step: ' + str(self.get_current_step()))
            ofile.write('\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
            #body
            ofile.write('#program base.\n\n')

            ofile.write('%init\n')
            for ss in self.to_init_str():
                 ofile.write(str(ss.replace(".", ".\n")))
    
        except IOError:
            ofile.close()
            return
        ofile.close()

    def save_answer_to_file(self, file_name):
        ofile = open(file_name, 'w')
        try:

            for items_dic in self._graphic_items.values():
                for item in items_dic.values():
                    for action in item.to_occurs_str():
                        if action is not None:
                            ofile.write(action)

        except IOError:
            ofile.close()
            return
        ofile.close()

    def save_pending_answer_to_file(self, file_name):
        time_step = self.get_current_step()
        ofile = open(file_name, 'w')
        try:

            for items_dic in self._graphic_items.values():
                for item in items_dic.values():
                    for action in item.to_occurs_str():
                        if action is not None:
                            action_split = action.split()
                            action_split = action_split[-1][:-2]
                            if(time_step <= int(action_split)):
                                ofile.write(action)

        except IOError:
            ofile.close()
            return
        ofile.close()
    def get_item(self, item_kind, ID, create = False, add_immediately = False):
        items_dic = None
        if ID is not None:
            ID = str(ID)
        if item_kind in self._graphic_items:
            items_dic = self._graphic_items[item_kind]
        elif item_kind in self._items:
            items_dic = self._items[item_kind]
        elif (item_kind, str(ID)) in self._new_items:
            return self._new_items[(item_kind, str(ID))]
        elif create:
            return self.create_item(item_kind, ID, add_immediately)
        else:
            return None

        if ID in items_dic:
            return items_dic[ID]
        elif (item_kind, str(ID)) in self._new_items:
            return self._new_items[(item_kind, str(ID))]
        elif create:
            return self.create_item(item_kind, ID, add_immediately)
        else:
            return None

    def get_editable(self):
        return self._editable

    def get_current_step(self):
        return self._current_step
    def set_current_step(self,step):
        self._current_step = step
    def get_num_steps(self):
        return self._num_steps

    def get_nodes(self):
        return self._nodes

    def get_node_id(self, node):
        if node in self._node_ids:
            return self._node_ids[node]
        return None

    def get_blocked_nodes(self):
        return self._blocked_nodes

    def get_highways(self):
        return self._highways

    def get_grid_size(self):
        return self._grid_size

    def iterate_graphic_dictionaries(self):
        for items_dic in self._graphic_items.values():
            yield items_dic

    def iterate_graphic_items(self):
        for items_dic in self._graphic_items.values():
            for item in items_dic.values():
                yield item

    def _map_kind_to_dictionarie(self, item_kind, 
                                    dictionaries, 
                                    create_dictionarie = False):
        if item_kind not in dictionaries:
            if not create_dictionarie:
                return None
            dictionaries[item_kind] = {}
        return dictionaries[item_kind]

    def _map_item_to_dictionarie(self, item, create_dictionarie = False):
        if item is None:
            return None
        dictionarie = None
        if isinstance(item, VisualizerGraphicItem):
            dictionarie = self._graphic_items
        elif isinstance(item, VisualizerItem):
            dictionarie = self._items
        else: 
            return None
        return self._map_kind_to_dictionarie(item.get_kind_name(), 
                                                dictionarie, 
                                                create_dictionarie)
    #Takes coordinates on the grid as input and gives information about robots at the cell
    def get_robot_info_at_node(self, x, y):
        output_str = ''
        #List of robots passing x,y along with the time step at which they are at x,y
        robots_passing = []
        #Iterating through the array containing the path for each agent and checking if the node is in the path of the robot
        for i in range(self.agent_count):
            for j in range(len(self.agent_locations_sorted[i])):
                if self.agent_locations_sorted[i][j] == (x,y):
                    robots_passing.append((i+1,j))
        #Concatenating the output string containing information about all the robots passing (x,y)        
        for i in range(len(robots_passing)):
            output_str += "\nRobot " + str(robots_passing[i][0]) + " passes at " + str(robots_passing[i][1])
        #Iterating through all the agents and checking if any two consecutive locations are the same, if so, that means the agent is waiting at the node x,y
        for i in range(self.agent_count):
            counter = 0
            flag = False
            for time_step in range(len(self.agent_locations_sorted[i]) - 1 ):
                current_time_step_location = self.agent_locations_sorted[i][time_step]
                next_time_step_location = self.agent_locations_sorted[i][time_step + 1]
                if current_time_step_location[0] == x and current_time_step_location[1] == y and current_time_step_location == next_time_step_location:
                    output_str += "\nRobot " + str(i+1) + " waiting" + " at time step " + str(time_step)    

        return output_str
    def process_new_constraints(self, new_vertex_constraints, new_edge_constraints, existing_vertex_constraints, existing_edge_constraints, time_step):
        updated_vertex_constraints = []
        updated_edge_constraints = []
        for vertex_constraint in existing_vertex_constraints:
            if vertex_constraint[2] < time_step:
                updated_vertex_constraints.append(vertex_constraint)

        for vertex_constraint in new_vertex_constraints:
            updated_vertex_constraints.append(vertex_constraint)   

        for edge_constraint in existing_edge_constraints:
            if edge_constraint[3] < time_step:
                updated_edge_constraints.append(vertex_constraint)

        for edge_constraint in new_edge_constraints:
            updated_edge_constraints.append(vertex_constraint)
        print(updated_vertex_constraints)   
        self.vertex_constraints = updated_vertex_constraints
        self.edge_constraints = updated_edge_constraints