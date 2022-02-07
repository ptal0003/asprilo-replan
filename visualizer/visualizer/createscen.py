#python create-scen instance-name.txt plan-name.txt map-name.map 2
#             0            1               2             3       4
import sys
import os
from pathlib import Path
import argparse
import re
def main():
    convert(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
def convert(arg1, arg2, arg3, arg4):
    currentAgent = 0
    x_dim = 0
    y_dim = 0
    time_step = 0
    #Opening the instance file with the remaining plan
    with open(arg1, 'r') as instance_file:
        all_lines = instance_file.readlines()
        #Extracting Grid Size, current time step from the plan remaining plan
        for line in all_lines:
            if "Grid size X:" in line:
                split_line = line.split()
                x_dim = int(split_line.pop()) + 2
            elif "Grid size Y:" in line:
                split_line = line.split()
                y_dim = int(split_line.pop()) + 2
            elif "Time Step" in line:
                split_line = line.split()
                time_step = int(split_line.pop())
        #Setting the new scenario file name
        scen_file_name = os.path.splitext(arg1)[0]+ ".scen"  

        #Creating the new scen file
        
        with open(scen_file_name, 'w') as scen_file:
            scen_file.write("version 1\n")
            #Opening the plan file with the remaining plan
            with open(arg2, 'r') as plan_file:
                all_lines_instance = all_lines
                all_lines_plan = plan_file.readlines()
                all_movements = []
                #All movements in asprilo are of broken down into steps, this variable will store the difference in x and y between final and initial plan
                agent_movement = [0,0]
                past_plan_movements = []
                #Reading through plans for all agents
                for i in range(len(all_lines_plan)):
                    #Getting the line and checking if the movement in the current line is for a later time step or the current time step.
                    line = all_lines_plan[i]
                    line = line.split()
                    line[-1] = line[-1][:-2]
                    if(int(line[-1]) < time_step):
                        past_plan_movements.append(i)
                past_plan_movements.reverse()
                #Removing the past movements
                for index in past_plan_movements:    
                    del all_lines_plan[index]    
                #Retrieving the total change in robot's location to reach the final location, adding sum_movement to current location would give the target location to be fed into the scen file
                for counter in range(int(arg4)):
                    for line in all_lines_plan:
                        line = line.split()
                        line[1] = line[1][:-2]
                        if(line[1]) == str(counter + 1):
                            if(line[2][13] == '-'):
                                agent_movement[0] -= 1
                            elif(line[2][13] == '0'):
                                agent_movement[0] += 0
                            else:
                                agent_movement[0] += 1 
                    for line in all_lines_plan:
                        line = line.split()
                        line[1] = line[1][:-2]
                        if(line[1]) == str(counter + 1):
                            if(line[2][15] != ','):
                                if(line[2][15] == '-'):
                                    agent_movement[1] -= 1
                                elif(line[2][15] == '0'):
                                    agent_movement[1] += 0
                                else:
                                    agent_movement[1] += 1 
                            else:
                                if(line[2][16] == '-'):
                                    agent_movement[1] -= 1
                                elif(line[2][16] == '0'):
                                    agent_movement[1] += 0
                                else:
                                    agent_movement[1] += 1 
                    #all_movements has the sum of x and y movements for all the agents, agent_movement is the sum of movements for x
                    all_movements.append(agent_movement)
                    agent_movement = [0,0]
                #Writing in the new scen file with updated positions.
                for line in all_lines_instance:
                    if(("robot" in line) and ("value" in line) and ("at" in line) and ("init" in line)):
                        start_loc = [int(line[32]) -1, int(line[34]) - 1]
                        goal_loc = [start_loc[0] + all_movements[currentAgent][0],start_loc[1] + all_movements[currentAgent][1]]
                        distance = abs(goal_loc[0] - start_loc[0]) + abs(goal_loc[1] - start_loc[1])
                        #line[32],line[34] has the coordinates of the robot when the plan was saved, need to subtract 1 in order to convert it to solver coordinates 
                        scen_file.write(str(currentAgent) + "\t" + arg3 + "\t" + str(x_dim)+ "\t"+str(y_dim) + "\t" + str(start_loc[0]) + "\t" + str(start_loc[1]) + "\t" + str(goal_loc[0]) + "\t" + str(goal_loc[1]) + "\t"+(str(abs(distance)))+"\n")
                        currentAgent += 1
                return scen_file_name
def create_scene_file_interactively(agent_starting_locs_dict, agent_final_locs_dict, agent_distance_dict, map_file_name, x_dim, y_dim):
    scene_file_name = os.path.splitext(map_file_name)[0]+ ".scen"
    with open(scene_file_name, 'w') as scene_file_writer:
        scene_file_writer.write("version 1\n")            
        for key in agent_starting_locs_dict:
            x1 = agent_starting_locs_dict[key][0] - 1
            y1 = agent_starting_locs_dict[key][1] - 1

            x2 = agent_final_locs_dict[key][0] - 1
            y2 = agent_final_locs_dict[key][1] - 1
            
            scene_file_writer.write(str(key) + "\t" + map_file_name + "\t" + str(x_dim)+ "\t"+str(y_dim) + "\t" + str(x1) + "\t" + str(y1) + "\t" + str(x2) + "\t" + str(y2) + "\t"+(str(agent_distance_dict[key]))+"\n")
    
    return scene_file_name
if __name__ =="__main__":
    if len(sys.argv) == 5:
        main()
    else:
        print("Incorrect number of arguments. Enter in the following format:\n python create-scen.py instance-name.txt plan-name.txt map-name.map 2")
    
