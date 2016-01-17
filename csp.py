import string
import Queue as queue
import copy
import random

#Function for finding first unassigned loction in the grid
def findUnassignedLocation(grid, N):
    
    for i in range(0,N):
        for j in range(0,N):
            if grid[i][j] == 0:
                return i,j
    
    return -1, -1

#Function for Checking validity of putting num value in (i,j) in corresponding row i
def isRowOK(grid, N, i, num):
    
    for x in range(0,N):
        if grid[i][x] == num:
            return False
    
    return True

#Function for Checking validity of putting num value in (i,j) in corresponding coilum j
def isColOK(grid, N, j, num):
    
    for x in range(0,N):
        if grid[x][j] == num:
            return False
    
    return True

#Function for Checking validity of putting num value in (i,j) in corresponding subgrid in which (i,j) lies
def isSubGridOK(grid, M, K, i, j, num):
    
    subGridStartRow = i - i%M
    subGridStartCol = j - j%K
    
    for x in range(0,M):
        for y in range(0,K):
            if grid[x+subGridStartRow][y+subGridStartCol] == num:
                return False
    
    return True

#Function for Checking validity of putting num value in (i,j) in corresponding its row, column and subgrid
def isValidMove(grid, N, M, K, i, j, num):
    
    if isRowOK(grid, N, i, num) and isColOK(grid, N, j, num) and isSubGridOK(grid, M, K, i, j, num):
        return True
    
    return False

consistencyChecks1 = 0

#Function to solve sudoku by back tracking
def solveSudokuBacktracking(grid, N, M, K):    
    global consistencyChecks1

    #Get a unassigned loaction from the grid
    i, j = findUnassignedLocation(grid, N)
    
    #Game over check, if sudoku is solved fully or not
    if i == -1:
        return True, consistencyChecks1
    
    #Solving sudoku by putting all possible values in unassigned loaction one by one and checking, backtrack if fail
    for num in range(1,M*K+1):
        if isValidMove(grid, N, M, K, i, j, num):
            grid[i][j] = num
            consistencyChecks1 = consistencyChecks1 + 1
            
            #Recursive Call
            if solveSudokuBacktracking(grid, N, M, K)[0]:
                return True, consistencyChecks1
            
            #Backtrack
            grid[i][j] = 0
                     
    return False, consistencyChecks1

#Get MRV (minimum remaining value) cell from the board, return that unassigned cell loction which can have minimum possible legal values
def get_MRV(grid, N, M, K):
    count = 0
    global_count = M*K + 1
    mrv_i = 0
    mrv_j = 0
    flag = False

    for i in range(0,N):
        for j in range(0,N):
            if grid[i][j] == 0:
                flag = True
                count = 0
                for num in range(1,M*K+1):
                    if isValidMove(grid, N, M, K, i, j, num):
                        count = count + 1
                #If current cell has mim minimum possible legal values than our previous count, update global count and update mrv cell values      
                if count < global_count:
                    global_count = count
                    mrv_i = i
                    mrv_j = j
    
    if flag == False:       # can't find any empty cell in sudoku board
        return -1, -1    
    
    return mrv_i, mrv_j

#Get LCV(Least Constrained Value) value of MRV cell, finds legal value which when we put in MRV cell, then it's domain (mrv cell's corresponding row, column and subgrid) has maximum possible legal values
# This function finds set of such legal values
def get_LCV(grid, N, M, K, i, j):
    count = 0
    lcv_queue = queue.PriorityQueue()
    grid1 = copy.deepcopy(grid)
    for num in range(1,M*K+1):
        if isValidMove(grid1, N, M, K, i, j, num):
            grid1[i][j] = num
            count = 0
            #Checking for col
            for x in range(0,N):
                if grid1[x][j] == 0:
                    for num1 in range(1,M*K+1):
                            if isValidMove(grid1, N, M, K, x, j, num1):
                                count = count + 1          
            #checking for row
            for x in range(0,N):
                if grid1[i][x] == 0:
                    for num1 in range(1,M*K+1):
                            if isValidMove(grid1, N, M, K, i, x, num1):
                                count = count + 1      
                    
            #checking for sub grid                    
            subGridStartRow = i - i%M
            subGridStartCol = j - j%K

            for x in range(0,M):
                for y in range(0,K):
                    if grid1[x+subGridStartRow][y+subGridStartCol] == 0:
                        for num1 in range(1,M*K+1):
                            if isValidMove(grid1, N, M, K, x+subGridStartRow, y+subGridStartCol, num1):
                                count = count + 1 
            #Putting LCV_value in priority queue with its count                    
            lcv_queue.put(num, -count)    
    return lcv_queue


consistencyChecks2 = 0

#Solve Sudoku using Backtracking + MRV + LCV
def solveSudokuBacktrackingMRV(grid, N, M, K):
    
    lcv_queue = queue.PriorityQueue()
    global consistencyChecks2
    #Game over check, if sudoku is solved fully or not
    i, j = findUnassignedLocation(grid, N)
    if i == -1:
        return True, consistencyChecks2
    
    #Get MRV cell from the grid
    i, j = get_MRV(grid, N, M, K)
    
    #Get set of lcv values for mrv cell
    lcv_queue = get_LCV(grid, N, M, K, i, j)
    
    #Check by putting all lcv_values in MRV cell one by one and try to solve sudoku by backtracking
    while not lcv_queue.empty():
        lcv_value = lcv_queue.get()
        if isValidMove(grid, N, M, K, i, j, lcv_value):
            grid[i][j] = lcv_value
            consistencyChecks2 = consistencyChecks2 + 1

            if solveSudokuBacktrackingMRV(grid, N, M, K)[0]:
                return True, consistencyChecks2

            grid[i][j] = 0

    return False, consistencyChecks2

#Do forward checking on the grid, Check if any unassigned cell in corresponding domain of (i,j) cell has some legal values remaining to put, if 0 legal values for that cell return false 
def do_forwardchecking(grid,N, M, K, i, j):
    count = 0
    #Checking for col
    for x in range(0,N):
        if grid[x][j] == 0:
            for num1 in range(1,M*K+1):
                if isValidMove(grid, N, M, K, x, j, num1):
                    count = count + 1
            
            #Count 0 means this cell has now 0 legal values do return false
            if count == 0:
                return False
            count = 0
            
    count = 0
    #checking for row
    for x in range(0,N):
        if grid[i][x] == 0:
            for num1 in range(1,M*K+1):
                if isValidMove(grid, N, M, K, i, x, num1):
                    count = count + 1 
                    
            #Count 0 means this cell has now 0 legal values do return false
            if count == 0:
                return False
            count = 0
                        
    count = 0
    #checking for sub grid                    
    subGridStartRow = i - i%M
    subGridStartCol = j - j%K

    for x in range(0,M):
        for y in range(0,K):
            if grid[x+subGridStartRow][y+subGridStartCol] == 0:
                for num1 in range(1,M*K+1):
                    if isValidMove(grid, N, M, K, x+subGridStartRow, y+subGridStartCol, num1):
                        count = count + 1 
             
                #Count 0 means this cell has now 0 legal values do return false
                if count == 0:
                    return False
                count = 0
    
    return True

consistencyChecks3 = 0

#Solve Sudoku using Backtracking + MRV + LCV + Forward Checking
def solveSudokuBacktrackingMRVfwd(grid, N, M, K):
    global consistencyChecks3
    lcv_queue = queue.PriorityQueue()
    #Game over check, if sudoku is solved fully or not
    i, j = findUnassignedLocation(grid, N) 
    if i == -1:
        return True, consistencyChecks3
    
    #Get MRV cell from the grid
    i, j = get_MRV(grid, N, M, K)
   
    #Get set of lcv values for mrv cell
    lcv_queue = get_LCV(grid, N, M, K, i, j)
    
    #Check by putting all lcv_values in MRV cell one by one and try to solve sudoku by backtracking and forward checking
    while not lcv_queue.empty():
        lcv_value = lcv_queue.get()   
        if isValidMove(grid, N, M, K, i, j, lcv_value):   
            grid[i][j] = lcv_value

            consistencyChecks3 = consistencyChecks3 + 1
            
            #Do forward checking after assigning value to the cell
            fwdcheckingresult = do_forwardchecking(grid,N, M, K, i, j)
            
            if fwdcheckingresult == True:
                if solveSudokuBacktrackingMRVfwd(grid, N, M, K)[0]:
                    return True, consistencyChecks3
            else:
                grid[i][j] = 0

    return False, consistencyChecks3


# Add all the neighbour elements of the cell to the queue,
# Keep a check of affect of this assignment in neighbour values, if Arc Consistent,return true else false.
def doArcConsistency(grid,N,M,K,i,j,boardDomain):

    import Queue
    arcQueue = Queue.Queue()
    #Add row and column
    for x in range(0,N):
        if x != j:
            arcQueue.put([i,j,i,x])
        if x != i:
            arcQueue.put([i,j,x,j])


    subGridStartRow = i - i%M
    subGridStartCol = j - j%K
    #Add subgrid values.
    for x in range(0,M):
        for y in range(0,K):
            if i != x+subGridStartRow and j != y+subGridStartCol:
                arcQueue.put([i,j,x+subGridStartRow,y+subGridStartCol])

    #Check if all the constraint present in Sudoku are valid for Arc consistency
    #If the above assingment affected any of neighbours, we will check the consistency for all of them. For checking we would add them back to the queue.
    while not arcQueue.empty():
        tuple = arcQueue.get()
        retVal = removeInconsistantValues(grid,N,M,K,tuple,boardDomain)
        #If retVal is 2: For any neighbour there is no valid assignment left.
        if retVal == 2:
            return False
        #retVal is 1: This assignment would remove some of the value from few of the cell.
        if  retVal == 1:
            for x in range(0,N):
                if x != j:
                    arcQueue.put([tuple[0],tuple[1],i,x])
                if x != i:
                    arcQueue.put([tuple[0],tuple[1],x,j])
            for x in range(0,M):
                for y in range(0,K):
                    if i != x+subGridStartRow and j != y+subGridStartCol:
                        arcQueue.put([tuple[0],tuple[1],x+subGridStartRow,y+subGridStartCol])

    return True

#The function to remove inconsistant values.
#This is a helper function for ARC Consistency, where if any assigning a value would result in change of domain from any
#Neighbour it would add them in the check queue.
def removeInconsistantValues(grid,N,M,K,tuple,boardDomain):
    removed = 0
    list1 = boardDomain[str(tuple[0])+" "+str(tuple[1])]
    list2 = boardDomain[str(tuple[2])+" "+str(tuple[3])]

    #If the count in the domain list is greater than 1, that means for any given value we would surely have another, so no domain update.
    if len(list2) > 1:
        return 0
    #If the neighbour's domain has updated or became null we will either return the assignment to be false or check neighbours.
    if len(list2) == 1 and list1.__contains__(list2[0]):
        list1.remove(list2[0])
        if len(list1) == 0:
            return 2
        removed = 1

    return removed

#Function would return a board with available domain values for each of the possible cells.
def currentBoardDomainMap(grid,N,M,K):
    boardDomain = {}
    for i in range (0,N):
        for j in range (0,N):
            domain = []
            for k in range (1,(M*K)+1):
                #It will check if it is a valid move, if yes, append the value.
                if isValidMove(grid,N,M,K,i,j,k):
                    domain.append(k)
            boardDomain[str(i)+" "+str(j)] = domain

    return boardDomain


consistencyChecks = 0
#This function would solve Sudoko by Backtracking + MRV + Constraint Propogation
def solveSudokuBacktrackingMRVCP(grid, N, M, K):
    global consistencyChecks
    
    #Game over check, if sudoku is solved fully or not
    i, j = findUnassignedLocation(grid, N)
    if i == -1:
        return (True,consistencyChecks)
    
    #Get MRV cell from the grid
    i, j = get_MRV(grid, N, M, K)
    
    for lcv_value in range (1,M*K+1):
        if isValidMove(grid, N, M, K, i, j, lcv_value):
            grid[i][j] = lcv_value
            consistencyChecks = consistencyChecks + 1

            #BoardDomain would contain the set of valid domains for a given cell.
            boardDomain = currentBoardDomainMap(grid,N,M,K)
            boardDomain[str(i)+" "+str(j)].append(lcv_value)

            #Will check arc Consistency and see if there is a problem with this assignment.
            retVal = doArcConsistency(grid,N,M,K,i,j,boardDomain)
            if retVal == True:
                tuple = solveSudokuBacktrackingMRVCP(grid, N, M, K)
                #consistencyChecks = consistencyChecks + tuple[1]
                if tuple[0]:
                    return (True,consistencyChecks)

            grid[i][j] = 0


    return (False,consistencyChecks)

#Count total no of conflicts in the whole grid, maximum possible conflicts is N*N (worst case)
def get_gridConflict(grid, N, M, K):
    conflict_count = 0
    
    for i in range(0,N):
        for j in range(0,N):
            num = grid[i][j]
            grid[i][j] = 0
            if not isValidMove(grid, N, M, K, i, j, num):
                conflict_count = conflict_count + 1
            grid[i][j] = num   
                
    return conflict_count

#Count total no of conflicts in the (row,col) cell's domain (cell's corrsponding row, column and subgrid), maximum possible conflicts is N*N (worst case)
def get_cellConflict(grid, N, M, K, row, col, num1):
    conflict_count = 0
    
    #checking for col
    for x in range(0,N):
        if grid[x][col] == num1:
            conflict_count =  conflict_count + 1

    #checking for row
    for x in range(0,N):
        if grid[row][x] == num1:
            conflict_count =  conflict_count + 1
                        
    #checking for sub grid                    
    subGridStartRow = row - row%M
    subGridStartCol = col - col%K

    for x in range(0,M):
        for y in range(0,K):
            if grid[x+subGridStartRow][y+subGridStartCol] == num1:
                conflict_count =  conflict_count + 1
            
    return conflict_count

#Function to read the game state, returning N, M, K and grid as tuple
def readGameState(filename):
    #Reading file
    fileHandle = open(filename, 'r')
    
    rawState = fileHandle.readline().split(',')         #read first line for N, M, K
    N = int(rawState[0])
    M = int(rawState[1])
    K = int(rawState[2].strip(';\n'))
    
    grid = [[0 for x in range(N)] for x in range(N)]

    #Read grid
    rawState = fileHandle.readlines()
    j = 0
    for line in rawState:
        data = line.split(',')
        for i in range(N):
		if data[i].strip(';\n') == '-':
                    grid[j][i] = 0
                else:
                    grid[j][i] = int(data[i].strip(';\n'))
        j = j + 1            
                             
    #print grid
    return (N, M, K, grid)
    
    
###########################################
# you need to implement five funcitons here
###########################################

def backtracking(filename):
    ###
    # use backtracking to solve sudoku puzzle here,
    # return the solution in the form of list of 
    # list as describe in the PDF with # of consistency
    # checks done
    ###

    # Reading Game State
    tuple = readGameState(filename)
    N = tuple[0]
    M = tuple[1]
    K = tuple[2]
    grid = tuple[3]
    consistencyChecks = 0
    
    #Call Util function to solve sudoku by backtracking
    tuple = solveSudokuBacktracking(grid, N, M, K)
    consistencyChecks = tuple[1]
    
    return (grid, consistencyChecks)

def backtrackingMRV(filename):
    ###
    # use backtracking + MRV to solve sudoku puzzle here,
    # return the solution in the form of list of 
    # list as describe in the PDF with # of consistency
    # checks done
    ###
    
    # Reading Game State
    tuple = readGameState(filename)
    N = tuple[0]
    M = tuple[1]
    K = tuple[2]
    grid = tuple[3]
    consistencyChecks = 0

    #Call Util function to solve sudoku by backtracking + MRV + LCV
    tuple = solveSudokuBacktrackingMRV(grid, N, M, K)
    consistencyChecks = tuple[1]
    
    return (grid, consistencyChecks)
    

def backtrackingMRVfwd(filename):
    ###
    # use backtracking +MRV + forward propogation
    # to solve sudoku puzzle here,
    # return the solution in the form of list of 
    # list as describe in the PDF with # of consistency
    # checks done
    ###
    
    # Reading Game State
    tuple = readGameState(filename)
    N = tuple[0]
    M = tuple[1]
    K = tuple[2]
    grid = tuple[3]
    consistencyChecks = 0

    #Call Util function to solve sudoku by backtracking + MRV + LCV + ForwardChecking
    tuple = solveSudokuBacktrackingMRVfwd(grid, N, M, K)
    consistencyChecks = tuple[1]
    
    return (grid, consistencyChecks)

def backtrackingMRVcp(filename):
    ###
    # use backtracking + MRV + cp to solve sudoku puzzle here,
    # return the solution in the form of list of 
    # list as describe in the PDF with # of consistency
    # checks done
    ###
    
    # Reading Game State
    tuple = readGameState(filename)
    N = tuple[0]
    M = tuple[1]
    K = tuple[2]
    grid = tuple[3]
    
    #Call Util function to solve sudoku by backtracking + MRV + LCV + Constraint Propagation
    tuple = solveSudokuBacktrackingMRVCP(grid, N, M, K)
    return (grid, tuple[1])


def minConflict(filename):
    ###
    # use minConflict to solve sudoku puzzle here,
    # return the solution in the form of list of 
    # list as describe in the PDF with # of consistency
    # checks done
    ###
    
    # Reading Game State
    tuple = readGameState(filename)
    N = tuple[0]
    M = tuple[1]
    K = tuple[2]
    grid = tuple[3]
    #min_conflict = N*N + 1
    min_conflict = 3*N + 1
    conflict = 0
    consistencyChecks = 0
    
    #Assign random values in unassigned loctions of grid
    for i in range(0,N):
        for j in range(0,N):
            if grid[i][j] == 0:
                grid[i][j] = random.randint(1,N)
     
    #print grid
    #Calculate total conflicts in the whole grid
    grid_conflict_count = get_gridConflict(grid, N, M, K)
    
    #Run loop upto 100000 iterations, if it can return solution in this much iterations, we say can't solve this sudoku grid by min conflict and stop
    while consistencyChecks <= 100000 and grid_conflict_count != 0:
        #Take a random cell
        row = random.randint(0,N-1)
        col = random.randint(0,N-1)
        
        num = grid[row][col]
        grid[row][col] = 0
        #Check for all possile values in selected cell one by one and count conflicts in cell's corresponding domain, assign that value for which conflicts count is minimum
        if not isValidMove(grid, N, M, K, row, col, num):        
            for num1 in range(1,M*K+1):
                #Getting count of conflicts in cell's corresponding domain
                conflict = get_cellConflict(grid, N, M, K, row, col, num1)
                if (conflict < min_conflict):
                    min_conflict = conflict
                    grid[row][col] = num1
        
            if grid[row][col] == 0:
                 grid[row][col] = num
        else:
            #If selected cell is valid cell from before, don't do anything in it and continue
            grid[row][col] = num

        #After assigning value in selected cell, once again calculate the total conflicts in the whole grid, if this count becomes 0 then our sudoku is solved
        grid_conflict_count = get_gridConflict(grid, N, M, K)
        if (grid_conflict_count == 0):
            break
        consistencyChecks = consistencyChecks + 1
        min_conflict = 3*N + 1
        
    
    return (grid, consistencyChecks)