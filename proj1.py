# I pledge on my honor that I have not given or received
# any unauthorized assistance on this project.
# William Sentosatio UID 114545749
# Project 1 CMSC421

import math, racetrack
import sys

from collections import deque

# borrowing heuristics'
infinity = float('inf')  # alternatively, we could import math.inf

# global variables
g_fline = False
g_walls = False
grid = []


def print2d(a):
    for i in range(len(a)):
        for j in range(len(a[i])):
            print(a[i][j], end=' ')
        print()


def h_proj1(state, fline, walls):
    """
    The first time this function is called, for each gridpoint that's not inside a wall
    it will cache a rough estimate of the length of the shortest path to the finish line.
    The computation is done by a breadth-first search going backwards from the finish 
    line, one gridpoint at a time.
    
    On all subsequent calls, this function will retrieve the cached value and add an
    estimate of how long it will take to stop. 
    """
    global g_fline, g_walls
    if fline != g_fline or walls != g_walls or grid == []:
        bfs(fline, walls)
    ((x, y), (u, v)) = state
    hval = float(grid[x][y])

    # add a small penalty to favor short stopping distances
    au = abs(u)
    av = abs(v)
    sdu = au * (au - 1) / 2.0
    sdv = av * (av - 1) / 2.0
    sd = max(sdu, sdv)
    penalty = sd / 10.0

    # compute location after fastest stop, and add a penalty if it goes through a wall
    if u < 0: sdu = -sdu
    if v < 0: sdv = -sdv
    sx = x + sdu
    sy = y + sdv
    if racetrack.crash([(x, y), (sx, sy)], walls):
        penalty += math.sqrt(au ** 2 + av ** 2)
    hval = max(hval + penalty, sd)
    return hval


##my
def bfs(fline, walls):
    global grid, g_fline, g_walls, xmax, ymax
    xmax = max([max(x, x0) for ((x, y), (x0, y0)) in walls])
    ymax = max([max(y, y0) for ((x, y), (x0, y0)) in walls])
    # [[0 for i in range(cols)] for j in range(rows)]
    grid = [[infinity for i in range(ymax + 1)] for j in range(xmax + 1)]
    ((x1, y1), (x2, y2)) = fline
    frontier = deque([])
    visited = []
    if x1 == x2:
        for y3 in range(min(y1, y2), max(y1, y2) + 1):
            grid[x1][y3] = 0
            visited.append((x1, y3))

        for y3 in range(min(y1, y2), max(y1, y2) + 1):
            for n in range(max(0, y3 - 1), min(ymax + 1, y3 + 2)):
                for m in range(max(0, x1 - 1), min(xmax + 1, x1 + 2)):
                    if frontier.count((m, n)) == 0 and grid[m][n] == infinity:
                        frontier.append((m, n))
    else:
        for x3 in range(min(x1, x2), max(x1, x2) + 1):
            grid[x3][y1] = 0
            visited.append((x3, y1))

        for x3 in range(min(x1, x2), max(x1, x2) + 1):
            for n in range(max(0, y1 - 1), min(ymax + 1, y1 + 2)):
                for m in range(max(0, x3 - 1), min(xmax + 1, x3 + 2)):
                    if frontier.count((m, n)) == 0 and grid[m][n] == infinity:
                        frontier.append((m, n))
    flag = True

    while frontier:
        (v1, v2) = frontier.popleft()
        visited.append((v1,v2))
        temp = edistw_to_finish((v1, v2), fline, walls)
        ##print (frontier)
        ##print()
        ##print(temp)
        ##print(v1,v2)
        if grid[v1][v2] != infinity and temp == grid[v1][v2]:
            flag = False
        else:
            grid[v1][v2] = temp

        if grid[v1][v2] == infinity:

            for g in range(max(0, v1 - 1), min(xmax + 1, v1 + 2)):
                for h in range(max(0, v2 - 1), min(ymax + 1, v2 + 2)):
                    if grid[g][h] != infinity and not racetrack.crash(((v1, v2), (g, h)), walls):
                        if g == v1 or h == v2:
                            d = grid[g][h] + 1
                        else:

                            d = grid[g][h] + 1.4142135623730951
                        if d < grid[v1][v2]:
                            grid[v1][v2] = d
                            flag = True

        for i in range(max(0, v1 - 1), min(xmax + 1, v1 + 2)):
            for j in range(max(0, v2 - 1), min(ymax + 1, v2 + 2)):
                if frontier.count((i, j)) == 0 and visited.count((i,j))==0: ##and grid[i][j] == infinity:
                    frontier.append((i, j))
    print2d(grid)

    g_fline = fline
    g_walls = walls
    return grid
    ##my 


def edistw_to_finish(point, fline, walls):
    """
    straight-line distance from (x,y) to the finish line ((x1,y1),(x2,y2)).
    Return infinity if there's no way to do it without intersecting a wall
    """
    #   if min(x1,x2) <= x <= max(x1,x2) and  min(y1,y2) <= y <= max(y1,y2):
    #       return 0
    (x, y) = point
    ((x1, y1), (x2, y2)) = fline
    # make a list of distances to each reachable point in fline
    if x1 == x2:  # fline is vertical, so iterate over y
        ds = [math.sqrt((x1 - x) ** 2 + (y3 - y) ** 2) \
              for y3 in range(min(y1, y2), max(y1, y2) + 1) \
              if not racetrack.crash(((x, y), (x1, y3)), walls)]
    else:  # fline is horizontal, so iterate over x
        ds = [math.sqrt((x3 - x) ** 2 + (y1 - y) ** 2) \
              for x3 in range(min(x1, x2), max(x1, x2) + 1) \
              if not racetrack.crash(((x, y), (x3, y1)), walls)]
    ds.append(infinity)  # for the case where ds is empty
    return min(ds)
