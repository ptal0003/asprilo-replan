
%Vertex Constraints: ((5,2),2,1) ((2,6),3,8) ((3,5),2,8) ((2,5),2,8)  

%Edge Constraints: ((4,5),(3,5),2,8) ((3,5),(2,5),2,8) ((2,5),(2,4),2,8)  
%Time Step: 4
occurs(object(robot, 1), action(move,(0,1)), 0).
occurs(object(robot, 1), action(move,(0,1)), 1).
occurs(object(robot, 1), action(move,(0,1)), 2).
occurs(object(robot, 1), action(move,(-1,0)), 3).
occurs(object(robot, 2), action(move,(0,0)), 0).
occurs(object(robot, 2), action(move,(-1,0)), 1).
occurs(object(robot, 2), action(move,(0,1)), 2).
occurs(object(robot, 2), action(move,(0,1)), 3).
occurs(object(robot,1),action(move,(0,  1)),4).
occurs(object(robot,1),action(move,(-1,  0)),5).
occurs(object(robot,1),action(move,(0,  1)),6).
occurs(object(robot,1),action(move,(-1,  0)),7).
occurs(object(robot,2),action(move,(-1,  0)),4).
occurs(object(robot,2),action(move,(0,  1)),5).
occurs(object(robot,2),action(move,(-1,  0)),6).
occurs(object(robot,2),action(move,(0,  1)),7).
occurs(object(robot,2),action(move,(0,  -1)),8).
occurs(object(robot,2),action(move,(-1,  0)),9).
occurs(object(robot,2),action(move,(0,  -1)),10).
occurs(object(robot,2),action(move,(-1,  0)),11).
occurs(object(robot,3),action(move,(-1,  0)),4).
occurs(object(robot,3),action(move,(0,  1)),5).
occurs(object(robot,3),action(move,(0,  1)),6).
occurs(object(robot,3),action(move,(1,  0)),7).
occurs(object(robot,3),action(move,(1,  0)),8).
occurs(object(robot,3),action(move,(1,  0)),9).
