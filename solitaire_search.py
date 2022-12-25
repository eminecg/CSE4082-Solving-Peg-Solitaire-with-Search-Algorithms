#CSE 4082 – Assignment 1
# Emine Çığ              150118012
# Ahsen Yağmur Kahyaoglu 150119788


import numpy as np
import queue as q
import time
from copy import copy, deepcopy
from random import shuffle

# Node class to hold the node information
class Node:
    def __init__(self, row, col, parent,state, index, depth,distance ):
        self.row = row                              # row 
        self.col = col                              # column
        self.index =index                           # index of the node in the matrix  
        self.currentMatrixState = state             # current state of the matrix                            
        self.depth = depth                          # depth of the node          
        self.parent = parent                        # parent of the node   
        self.manhattanDistance = distance           # manhattan distance of the node
            

 
centerIndex=[3,3]    # center index of the matrix

# the return messages to be printed
returnMessages= [ 
    "Optimum solution found.",
    "Sub-optimum Solution Found with XX remaining pegs",
    "No solution found – Time Limit",
    "No solution found – Out of Memory"]

# indexes on start state matrix as 2d list
indexStates=[
    [0,0,1,2,3,0,0],
    [0,0,4,5,6,0,0],
    [7,8,9,10,11,12,13],
    [14,15,16,17,18,19,20],
    [21,22,23,24,25,26,27],
    [0,0,28,29,30,0,0],
    [0,0,31,32,33,0,0],
]
    

# function to remove frontier depend on search strategy
def removeFrontier(searchType,frontier):
    if searchType == "BFS":
        return frontier.pop(0)
    elif searchType == "DFS":
        return frontier.pop()
    elif searchType == "IDS":
        return frontier.pop()
    elif searchType == "DFS_R":
        return frontier.pop()        
    elif searchType == "DFS_H":
        return frontier.pop()

# function to check if the frontier is empty or not
def isFrontierEmpty(frontier):
    if len(frontier) == 0:
        return True
    else:
        return False

# function to check if the node is goal state with the depth
def isGoalState(node):    
    if node.depth == 31 and node.index == 17: 
        return True
    else:
        return False

# function to check the time limit is exceeded or not ,if yes return the current node 
def isTimeLimitExceeded(initialTime,timeLimit):
    
    timeSpended = time.time() - initialTime
    if (timeSpended) > timeLimit:
        return True
    else:
        return False

# function for getting the path from the final node
def getPath(node):
    path = []
    while node != None:
        path.append(node)
        node = node.parent

    print("Solution Path:")
    for i in range(len(path)):        
        print("Depth: ",path[i].depth," Index: ",path[i].index," ")       
    print()

    for i in range(len(path)):        
        printCurrentMatrix(path[i])
    print()

# function to get the empty holes as list of tuple as coordinates of row and column, 
# update them on the matrix , then print the current matrix
def printCurrentMatrix(node):   
    print("-------------------")
    for i in range(0,7):
        for j in range(0,7):
            if (i,j) in nonUsedCoordinates:
                print(" ", end=" ")
            elif node.currentMatrixState[i][j]==0:
                print("0", end=" ")         
            else:
                print("x", end=" ")
        print()
    print("-------------------")
               
# create a list of tuples to hold non used coordinates
nonUsedCoordinates = [
    (0,0),(0,1),(0,5),(0,6),
    (1,0),(1,1),(1,5),(1,6),
    (5,0),(5,1),(5,5),(5,6),
    (6,0),(6,1),(6,5),(6,6)
]

# function performs search on the matrix with given search type as BFS,DFS,DFS_R,DFS_H and initial time
def search(searchType,initialTime,timeLimit):
    numberOfNodesExpanded = 0
    maximumNumberOfNodesInMemory = 0
    bestSubOptimalSolutionPegs = 32
    bestSubOptimalSolutionNode = None

    startState=[
    [0,0,1,1,1,0,0],
    [0,0,1,1,1,0,0],
    [1,1,1,1,1,1,1],
    [1,1,1,0,1,1,1],
    [1,1,1,1,1,1,1],
    [0,0,1,1,1,0,0],
    [0,0,1,1,1,0,0],
    ]   

    frontier=[]

    # create the start node and add it to the frontier
    startNode = Node(centerIndex[0],centerIndex[1],None,startState,17,0,0)
    frontier.append(startNode)
    
    
    # loop until the frontier is empty or time limit is exceeded
    while  not isFrontierEmpty(frontier) :
        if  isTimeLimitExceeded(initialTime,timeLimit)  :
            break
        
        # remove the node from the frontier, then increase the number of nodes expanded with 1
        node = removeFrontier(searchType,frontier)
        numberOfNodesExpanded = numberOfNodesExpanded + 1

        # calculates the number of remaining pegs and update the best sub optimal solution        
        remainPegs=countRemainPegs(node.currentMatrixState)
        if remainPegs < bestSubOptimalSolutionPegs:
            bestSubOptimalSolutionPegs = remainPegs
            bestSubOptimalSolutionNode = node
        
        # check if the node is goal state, if yes print the message and break the loop
        if isGoalState(node): 
            isGoalFound=True           
            print(returnMessages[0])                       
            break
        else:
            # collect the ordered accessible nodes list
            nodes=collectOrderedAccessibleNodesList(node)

            isReverse=True # order of the nodes is reversed by default
            if (searchType=="BFS"):
                isReverse=False
            else:
                isReverse=True

            # nodes list sequence is differ depending on the search type
            # randomize the nodes list if the search type is DFS_R
            if (searchType=="DFS_R"):
                randomIndex = [] 
                for i in range (0,(len(nodes))):                        
                    randomIndex.append(i)

                shuffle(randomIndex) # shuffle the index list

                # change the index of the nodes according to the random index
                tempNodes =[]                
                size=len(nodes)                
                for i in range (0,size):
                    tempNodes.append(nodes[randomIndex[i]])

                for i in range (0,len(nodes)):
                    nodes[i]=tempNodes[i]    
            # sort the nodes list according to the manhatten distance from large to small if the search type is DFS_H
            elif (searchType=="DFS_H"):
                 
                 calculateManhattanDistance(nodes)
            
                 # sort the list according to the manhatten distance from large to small                 
                 nodes.sort(key=lambda x: x.manhattanDistance, reverse=True)

            # For BFS , DFS 
            else:  
                nodes.sort(key=lambda x: x.index, reverse=isReverse)                    

            # add the nodes to the frontier with checking the goal state is found or not,    
            for i in range(0,len(nodes)):
                if isGoalState(nodes[i]):
                    isGoalFound=True
                    
                    remainPegs=countRemainPegs(node[i].currentMatrixState)
                    if remainPegs < bestSubOptimalSolutionPegs:
                        bestSubOptimalSolutionPegs = remainPegs
                        bestSubOptimalSolutionNode = node[i]
                                        
                    print("---------------------------goal----------------------------------------------")                    
                    break
                else:                                                            
                    frontier.append(nodes[i])

            # update the maximum number of nodes in memory if the frontier size is greater than the current maximum number of nodes in memory
            if len(frontier) > maximumNumberOfNodesInMemory:
                maximumNumberOfNodesInMemory = len(frontier)
                       
            
    return bestSubOptimalSolutionNode,bestSubOptimalSolutionPegs,numberOfNodesExpanded,maximumNumberOfNodesInMemory
    


#   ---------------------------    IDS   --------------------------------
def IDS(initialTime,timeLimit):

    numberOfNodesExpanded = 0
    maximumNumberOfNodesInMemory = 0
    bestSubOptimalSolutionPegs = 32
    bestSubOptimalSolutionNode = None

    startState=[
    [0,0,1,1,1,0,0],
    [0,0,1,1,1,0,0],
    [1,1,1,1,1,1,1],
    [1,1,1,0,1,1,1],
    [1,1,1,1,1,1,1],
    [0,0,1,1,1,0,0],
    [0,0,1,1,1,0,0],
    ]
      
    # loop for the iteration of the depth until 
    for l in range(0,32):
        
        frontier=[]

        # create and assign a start node to the frontier
        startNode = Node(3,3,None,startState,17,0,0)
        frontier.append(startNode)
        
        # loop runs until the frontier is empty or time limit is exceeded
        while not (isFrontierEmpty(frontier)  ):
            if  isTimeLimitExceeded(initialTime,timeLimit)  :
                break        
            
            # expand the node from the frontier depend on the search type, then increase the number of expanded nodes
            node = removeFrontier("IDS",frontier)
            numberOfNodesExpanded = numberOfNodesExpanded + 1

            # count the number of remain pegs and update the best sub optimal solution
            remainPegs=countRemainPegs(node.currentMatrixState)
            if remainPegs < bestSubOptimalSolutionPegs:
                bestSubOptimalSolutionPegs = remainPegs
                bestSubOptimalSolutionNode = node

            #print("Remain Pegs: ",remainPegs," Depth: ",node.depth," Index: ",node.index)
            #printCurrentMatrix(node)
            ## print the frontier list
            #print( "Frontier: ")
            #for i in range(0,len(frontier)):
            #    print(frontier[i].index, end=" ")
            #print()

            # check if the node is goal state, if yes print the goal message and break the loop
            if isGoalState(node):
                isGoalFound=True
                print(returnMessages[0])
                print("---------------------------goal----------------------------------------------")
                break
            else:
                # check if the depth of the node is less than the limit
                if node.depth+1<=l:
                    
                    # function returns the list of the nodes that can be reached from the current node, 
                    # each node has updated state matrix as a result of the movement
                    nodes=collectOrderedAccessibleNodesList(node)
                    
                    # sort the list according to the index from large to small due to depth first search approach
                    nodes.sort(key=lambda x: x.index, reverse=True)                    

                    # loop runs until the list of the nodes is empty, 
                    # then add the nodes to the frontier after checking the goal state is reached or not 
                    # if reached update the best sub optimal solution
                    for i in range(0,len(nodes)):
                        if isGoalState(nodes[i]):
                            isGoalFound=True

                            remainPegs=countRemainPegs(node.currentMatrixState)
                            if remainPegs < bestSubOptimalSolutionPegs:
                                bestSubOptimalSolutionPegs = remainPegs
                                bestSubOptimalSolutionNode = node                                                        
                            break
                        else:
                            frontier.append(nodes[i])  

                    # checks if the number of nodes in the frontier is greater than the maximum number of nodes in memory,
                    # then update the maximum number of nodes in memory
                    if len(frontier) > maximumNumberOfNodesInMemory:
                       maximumNumberOfNodesInMemory = len(frontier)

    return bestSubOptimalSolutionNode,bestSubOptimalSolutionPegs,numberOfNodesExpanded,maximumNumberOfNodesInMemory



#---------------------------------------------------------------------------


# function to get zero value coordinates from the current matrix as tuple list
def getZeroValueCoordinates(currentMatrix):
    zeroValueCoordinates=[]
    for i in range(0,7):
        for j in range(0,7):
            # if this coordinate not inside the non used coordinates list
            if (currentMatrix[i][j]==0 and (i,j) not in nonUsedCoordinates):
                zeroValueCoordinates.append((i,j))
    return zeroValueCoordinates


# function to get getAccessibleNodes list of each node comes from getZeroValueCoordinates function , then concat and order them
def collectOrderedAccessibleNodesList(node): # expand edilen node üzerinden currentMatrixState
    
    # list of the zero value coordinates
    zeroValueCoordinates=getZeroValueCoordinates(node.currentMatrixState) # (x,y)    

    nodes=[]
    
    # for each zero value coordinate gets the accessible movements as a list of nodes then concat them as a final list of nodes
    for i in range(0,len(zeroValueCoordinates)):

        nodeList=getAccessibleNodes(node,zeroValueCoordinates[i][0],zeroValueCoordinates[i][1])

        if nodeList !=None :  
            nodes.extend(nodeList)
    return nodes
    
# function to get the accessible nodes from the current node, then add them to the list to return       
def getAccessibleNodes(node,row,col):
    actionOrder = ["up","left","right","down"] 
    
    nodes=[]
    
    for i in range(0,len(actionOrder)):
        tempNode=checkAccessiblity(node,row,col,actionOrder[i])
        if tempNode !=False :  
            # create a new node with the return values
            
            nodes.append(tempNode)
        else:
            continue
    return nodes

# function to check the accessibility of the movement from the current direction of the empty hole using the given node state matrix
def checkAccessiblity(node,controlRow,controlCol,direction):
    
    # holds 0 or 1 for checking near coordinates are empty or not
    first = -1
    second= -1
           
    # holds the coordinates of new empty hole to create a new node           
    row=-1
    col=-1
    
    # creates a new the current matrix state of the new node to update movement result
    currentMatrix= deepcopy(node.currentMatrixState)

    # For each movement direction, checks the near coordinates are empty or not,
    # gets the new empty hole coordinates to create a new node, 
    # updates the current matrix state with movement result 

    if(direction=="up"): 
        # check any coordinates is out of bound        
        if(controlRow-2<0  ):
            return False
        else :            
            first=    node.currentMatrixState[controlRow-1][controlCol] 
            second=   node.currentMatrixState[controlRow-2][controlCol]
            row=controlRow-1
            col=controlCol

            currentMatrix[controlRow-1][controlCol]=0
            currentMatrix[controlRow-2][controlCol]=0

    elif (direction=="left"):   
           
        if (controlCol-2<0):
            return False
        else:
            first= node.currentMatrixState  [controlRow ][controlCol-1]
            second= node.currentMatrixState [controlRow] [controlCol-2]
            row=controlRow
            col=controlCol-1

            currentMatrix[controlRow][controlCol-1]=0
            currentMatrix[controlRow][controlCol-2]=0

    elif (direction=="right"):
        
        if (controlCol+2>6):
            return False
        else:    
            first= node.currentMatrixState  [controlRow ][controlCol+1]
            second= node.currentMatrixState [controlRow] [controlCol+2]
            row=controlRow
            col=controlCol+1

            currentMatrix[controlRow][controlCol+1]=0
            currentMatrix[controlRow][controlCol+2]=0

    elif (direction=="down"):
        
        if (controlRow+2>6):
            return False
        else:    
            first=  node.currentMatrixState [controlRow+1][controlCol]
            second= node.currentMatrixState [controlRow+2][controlCol]
            row=controlRow+1
            col=controlCol

            currentMatrix[controlRow+1][controlCol]=0
            currentMatrix[controlRow+2][controlCol]=0
    else:
        print("error unvalid direction")

    # if the near coordinates are full, performs the movement and creates a new node with its parameters
    if( first==1 and second==1): 

        # check the coordinate is out of bound or not
        if(row>=0 and row<=6 and col>=0 and col<=6):

          # check the coordinate is non used or not
            if((row,col) not in nonUsedCoordinates):  
                currentMatrix[controlRow][controlCol]=1
                index=indexStates[row][col]
                
                return Node(row,col,node,currentMatrix,index,node.depth+1,0)
    else:        
        return False

# function to get the path from the goal node to the root node  
def countRemainPegs(matrix):
    count=0
    for i in range(0,len(matrix)):
        for j in range(0,len(matrix[i])):
            if(matrix[i][j]==1):
                count+=1
    return count

# function calculates manhattan distance from the center to the each node on the current state of the matrix, 
# then divides sum to the number of remaining pegs on the current state of the matrix 
# to obtain average manhattan distance to updates the node's manhattan distance value
def calculateManhattanDistance(nodes):
    remainPegs=[]
    
    # calculates number of remaining pegs
    for i in range(0,len(nodes)):
        remainPegs.append(countRemainPegs(nodes[i].currentMatrixState))

    # calculate sum of  manhatten distances for each peg has value 1 to the center (3,3) , then divide sum to the remain pegs number
    for i in range(0,len(nodes)):
        nodes[i].manhattanDistance=0

        for j in range(0,len(nodes[i].currentMatrixState)):
            for k in range(0,len(nodes[i].currentMatrixState[j])):

                if(nodes[i].currentMatrixState[j][k]==1):
                    nodes[i].manhattanDistance+=abs(j-3)+abs(k-3)

        nodes[i].manhattanDistance=nodes[i].manhattanDistance/remainPegs[i]

isGoalFound=False
def menu():
    timeLimit=3600
    initialTime = time.time()
    
    searchType=""
    print("1- Breadth-First Search")
    print("2- Depth-First Search")
    print ("3-Iterative Deepening Search")
    print("4- Depth-First Search with Random Selection")
    print("5- Depth-First Search with a Node Selection Heuristic")
    print("6- Exit")
    choice=int(input("Please enter your choice as a number: "))
    if(choice==1):        
        searchType="BFS"                       
    elif(choice==2):        
        searchType="DFS"
    elif(choice==3):        
        searchType="IDS"        
    elif(choice==4):               
        searchType="DFS_R"        
    elif(choice==5):       
        searchType="DFS_H"
    elif(choice==6):
        print("Goodbye!")
        exit()
    else:
        print("Please enter a valid choice")
        menu()
    # get the second input from user as time limit
    
    timeLimit=int(input("Please enter the time limit in seconds: "))
    print()     
    try :
        initialTime = time.time()
        if searchType=="IDS":
            bestSubOptimalSolutionNode,bestSubOptimalSolutionPegs,numberOfNodesExpanded,maximumNumberOfNodesInMemory=  IDS(initialTime,timeLimit)
        else:
            bestSubOptimalSolutionNode,bestSubOptimalSolutionPegs,numberOfNodesExpanded,maximumNumberOfNodesInMemory= search(searchType,initialTime,timeLimit)
                
    except MemoryError as error:
        print(returnMessages[3])
        
    finally:    
        print("Search Type                      : ",searchType)
        print("Time Limit                       : ",timeLimit," seconds")
        print("Time Spended                     : ",(time.time()-initialTime))
        print("Number of Nodes Expanded         : ",numberOfNodesExpanded)
        print("Maximum Number of Nodes in Memory : ",maximumNumberOfNodesInMemory)
        
        if(not isGoalFound):
            # replace xx to count in the message string
            
            print(returnMessages[1].replace("XX",str(bestSubOptimalSolutionPegs)))
        elif(isGoalFound):
            print(returnMessages[0])
        print("Remaining Pegs                   : ",bestSubOptimalSolutionPegs)  
        getPath(bestSubOptimalSolutionNode)    

            


menu()
#BFS()
#DFS()
#IDS()
#DFS_random()
#DFS_huristic()




