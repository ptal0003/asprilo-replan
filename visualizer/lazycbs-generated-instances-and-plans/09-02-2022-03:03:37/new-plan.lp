
%Vertex Constraints: ((2,3),2,3) ((2,1),1,3) ((2,2),1,3) ((2,2),2,2)  

%Edge Constraints: ((3,3),(2,3),2,3) ((2,3),(2,2),2,3) ((2,2),(2,1),2,2) ((2,3),(2,2),2,2)  
%Time Step: 1
occurs(object(robot, 1), action(move,(1,0)), 0).
occurs(object(robot, 2), action(move,(-1,0)), 0).
occurs(object(robot,1),action(move,(0,  1)),1).
occurs(object(robot,1),action(move,(0,  1)),2).
occurs(object(robot,1),action(move,(1,  0)),3).
occurs(object(robot,2),action(move,(-1,  0)),1).
occurs(object(robot,2),action(move,(0,  0)),2).
occurs(object(robot,2),action(move,(1,  0)),3).
occurs(object(robot,2),action(move,(0,  -1)),4).
occurs(object(robot,2),action(move,(0,  -1)),5).
occurs(object(robot,2),action(move,(-1,  0)),6).
