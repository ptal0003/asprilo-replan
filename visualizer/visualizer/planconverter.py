#python plan-converter.py incompatible-plan.txt number-of-agents
#             0                       1                 2
import sys
from pathlib import Path
import argparse
import os
import re
x_max = 0
y_max = 0 
def main():
    convert_solution_to_plan(sys.argv[1], sys.argv[2])
def convert_solution_to_plan(arg1, arg2):
    
    num_agents = arg2
    compatible_plan_path = "../lazycbs-generated-instances-and-plans/compatible-remaining-plan.lp"
    map_file_name = ""
    
    lines = arg1
    lines[0] = lines[0].split()
    map_file_name = lines[0][1]
    
    with open(map_file_name, 'r') as map_file:
        all_lines = map_file.readlines()
        
        x_max = int(all_lines[0][2]) 
        y_max = int(all_lines[0][0]) 
        all_lines_cleaned = [[0 for x in range(x_max - 2)] for y in range(int(y_max - 2))]  
        all_lines.remove(all_lines[0])
        for y in range(0, y_max):
            all_lines[y] = all_lines[y].strip()
            all_lines[y] = all_lines[y].split(",")
    for i in range(0, x_max):
        for j in range(0,y_max):
            if not((i ==0 or i == x_max -1) or (j ==0 or j == y_max -1)):
                all_lines_cleaned[j-1][i-1] = all_lines[j][i]
    all_lines = all_lines_cleaned
    y_max -= 2
    x_max -= 2
    node_counter = 0
    highway_counter = 0
    #Opening the compatible map file for writing, writing the layout(instance details) into asprilo compatible format
    with open(compatible_plan_path, 'w') as asprilo_plan:
            asprilo_plan.write("%Map: " + map_file_name)
            all_lines_constraint_extraction = arg1
            if(len(all_lines_constraint_extraction) > (int(num_agents) + 1)):
                all_lines_constraint_extraction_split = all_lines_constraint_extraction[int(num_agents) + 1].split()
                all_lines_constraint_extraction_split.remove("Constraints:")
                if(len(all_lines_constraint_extraction_split) > 0):
                    asprilo_plan.write("%Constraints:")
                
                for constraint in all_lines_constraint_extraction_split:
                    constraint = re.split(r"[,()[]",constraint) 
                    loc1 = [int(constraint[3]),int(constraint[2])]
                    loc2 = [int(constraint[7]),int(constraint[6])]
                    ai = int(constraint[9])
                    time = int(constraint[10][:-1])
                    asprilo_plan.write(" ("+str(ai)+","+"("+str(loc1[0])+","+str(loc1[1])+"),("+str(loc2[0])+","+str(loc2[1])+"),"+str(time)+")")
                asprilo_plan.write("\n")
            for y in range(0, y_max):
                for x in range(0, x_max):
                    node_counter += 1    
                    asprilo_plan.write("init(object(node,"+ str(node_counter) +"),value(at,("+str(x+1)+","+str(y+1)+"))).\n")
            for x in range(0, x_max):
                for y in range(0, y_max):
                    highway_counter += 1
                    if not(all_lines[y][x] == "1"):
                        asprilo_plan.write("init(object(highway,"+ str(highway_counter) +"),value(at,("+str(y+1)+","+str(x+1)+"))).\n")   
            #Opening the incompatible plan file to extract information about the robot         
            all_lines = all_lines_constraint_extraction
            all_lines.remove(all_lines[0])
            time_limit = 100
            all_paths = [[0 for x in range(time_limit)] for y in range(int(num_agents))]  
            all_movements = []   
            for i in range(int(num_agents)):
                agent_path = []
                agent_movement = []
                all_lines[i] = all_lines[i].strip()
                all_lines[i] = all_lines[i].split(" ")
                del all_lines[i][0]
                del all_lines[i][0]
                for j in range(len(all_lines[i])):
                    agent_path.append((int(all_lines[i][j][3]) + 1, int(all_lines[i][j][1]) + 1))
                asprilo_plan.write("init(object(robot,"+str(i+1)+"),value(at,"+str(agent_path[0])+")).\n") 
                all_paths[i] = agent_path
                agent_x_coord = [item[0] for item in all_paths[i]]
                agent_y_coord = [item[1] for item in all_paths[i]]
                for i in range(len(agent_x_coord) - 1):
                    agent_movement.append(((agent_x_coord[i+1] - agent_x_coord[i]),(agent_y_coord[i+1] - agent_y_coord[i])))
                all_movements.append(agent_movement)
            #print(all_movements)
            for i in range(int(num_agents)):
                for j in range(len(all_movements[i])):
                    asprilo_plan.write("occurs(object(robot,"+str(i+1)+"),action(move,"+str(all_movements[i][j])+"),"+str(j)+").\n")
            #    asprilo_plan.write("init(object(robot,"+str(i+1)+"),value(at,(1,6))).\n")

    map_file.close()
    return compatible_plan_path
if __name__ == "__main__":
    if(len(sys.argv) == 3):
        main()
    else:
        print("Invalid number of arguments. Please enter in format: python plan-converter.py map-to-be-used.ecbs incompatible-plan.txt number-of-agents")

