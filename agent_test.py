#agent_test.py

#IT24610328---Lab04---Added this test file to verify that the manhattan_distance and euclidean_distance methods in agent.py are working correctly.
from agent import SearchAgent

agent = SearchAgent()
print(agent.manhattan_distance((0, 0), (3, 4)))   # should print 7
print(agent.euclidean_distance((0, 0), (3, 4)))   # should print 5.0

#IT24610328---Lab04---Results of running this test file:
#cal\Programs\Python\Python313\python.exe //wsl.localhost/Ubuntu-22.04/home/it24610328/intelligent-systems-lab01/IT3012---Practical-Base---it24610328/agent_test.py
#7
#5.0