#python plan-converter.py map-to-be-used.map.ecbs incompatible-plan.txt number-of-agents
#             0               1                       2                 3
import sys
from pathlib import Path
import argparse
import os
x_max = 0
y_max = 0 
def main():
    convert_solution_to_plan(sys.argv[1],sys.argv[2], sys.argv[3])
def convert_solution_to_plan(arg1, arg2, arg3):
    #Opening the ecbs map file to read from it and getting the number of agents
    num_agents = arg3
    with open(arg1, 'r') as map_file:
        all_lines = map_file.readlines()
        x_max = int(all_lines[0][0]) 
        y_max = int(all_lines[0][2]) 
        all_lines_cleaned = [[0 for x in range(x_max - 2)] for y in range(int(y_max - 2))]  
        all_lines.remove(all_lines[0])
        for y in range(0, y_max):
            all_lines[y] = all_lines[y].strip()
            all_lines[y] = all_lines[y].split(",")
    for i in range(0, x_max):
        for j in range(0,y_max):
            if (i ==0 or i == x_max -1) or (j ==0 or j == y_max -1):
                print("Border")
            else:
                all_lines_cleaned[i-1][j-1] = all_lines[i][j]
    all_lines = all_lines_cleaned
    y_max -= 2
    x_max -= 2
    node_counter = 0
    highway_counter = 0
    compatible_plan_path = os.path.splitext(arg2)[0] + "converted-compatible-plan.txt"
    #Opening the compatible map file for writing, writing the layout(instance details) into asprilo compatible format
    with open(compatible_plan_path, 'w') as asprilo_plan:
        with open(arg2, 'r') as lazycbs_plan_file:
            all_lines_constraint_extraction = lazycbs_plan_file.readlines()
            if(len(all_lines_constraint_extraction) > int(num_agents)):
                all_lines_constraint_extraction_split = all_lines_constraint_extraction[int(num_agents)].split()

                for line in all_lines_constraint_extraction_split:
                    if "Constraints:" in line:
                        line = line.split()
                        if(len(line) >= 2):
                            print("There are constraints to be taken care of in the generated solution")
            for y in range(0, y_max):
                for x in range(0, x_max):
                    node_counter += 1    
                    asprilo_plan.write("init(object(node,"+ str(node_counter) +"),value(at,("+str(x+1)+","+str(y+1)+"))).\n")
            for x in range(0, x_max):
                for y in range(0, y_max):
                    highway_counter += 1
                    if not(all_lines[x][y] == "1"):
                        asprilo_plan.write("init(object(highway,"+ str(highway_counter) +"),value(at,("+str(y+1)+","+str(x+1)+"))).\n")   
            #Opening the incompatible plan file to extract information about the robot         
            all_lines = all_lines_constraint_extraction
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
                    asprilo_plan.write("occurs(object(robot,"+str(i+1)+"),action(move,"+str(all_movements[i][j])+"),"+str(j+1)+").\n")
            #    asprilo_plan.write("init(object(robot,"+str(i+1)+"),value(at,(1,6))).\n")

    map_file.close()
    return compatible_plan_path
if __name__ == "__main__":
    if(len(sys.argv) == 4):
        main()
    else:
        print("Invalid number of arguments. Please enter in format: python plan-converter.py map-to-be-used.ecbs incompatible-plan.txt number-of-agents")

