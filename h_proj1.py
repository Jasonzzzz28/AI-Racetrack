"""
This file contains an optimized heuristic function for the Racetrack domain:
- h_proj1 is a modified version of h_walldist that computes the grid faster and finds the optimal path more efficiently.

The heuristic function takes three arguments: state, fline, walls.
   - state is the current state. It should have the form ((x,y), (u,v)), where
      (x,y) is the current location and (u,v) is the current velocity.
   - fline is the finish line. It should have the form ((x1,y1), (x2,y2)),
      where (x1,y1) and (x2,y2) are the two endpoints, and it should be either
      either vertical (x1 == x2) or horizontal (y1 == y2).
   - walls is a list of walls, each wall having the form ((x1,y1), (x2,y2))
"""
import math, racetrack
import sys
from collections import deque

# global variables
infinity = float('inf')
negainfinity = float('-inf')
g_fline = False
g_walls = False
grid = []
find = False  # check if it already finds a path to the fline


def listfl(a):
    """
    This helper function finds all the nodes on fline
    :param a: fline
    :return: list of nodes on fline
    """
    ((x1, y1), (x2, y2)) = a
    res = []
    if x1 == x2:
        for y3 in range(min(y1, y2), max(y1, y2) + 1):
            res.append((x1, y3))

    else:
        for x3 in range(min(x1, x2), max(x1, x2) + 1):
            res.append((x3, y1))
    return res


def h_proj1(state, fline, walls):
    """
    The first time this function is called, it will use optimized breath first search to find the cost for all the
    points on the grid.
    On all subsequent calls, this function will retrieve the cached value and add an
    estimate of how long it will take to stop.

    :param a: state, fline, walls
    :return: estimate cost of the step
    """
    global g_fline, g_walls, find

    # if it has already found a solution path, stop exploring other nodes
    if find:
        return infinity

    if fline != g_fline or walls != g_walls or grid == []:
        bfs(fline, walls)
    ((x, y), (u, v)) = state
    ((h1, w1), (h2, w2)) = fline
    li = listfl(fline)
    hval = float(grid[x][y])

    au = abs(u)
    av = abs(v)
    sdu = au * (au - 1) / 2.0
    sdv = av * (av - 1) / 2.0
    sd = max(sdu, sdv)

    if u < 0: sdu = -sdu
    if v < 0: sdv = -sdv
    sx = x + sdu
    sy = y + sdv

    # check if it has already found a solution path
    # if yes, stop exploring other nodes
    if li.count((x, y)) > 0 and u == 0 and v == 0:
        find = True
        return negainfinity

    # add a small penalty to favor short stopping distances
    penalty = sd / 10.0

    # compute location after fastest stop, and add a penalty if it goes through a wall
    if racetrack.crash([(x, y), (sx, sy)], walls):
        penalty += math.sqrt(au ** 2 + av ** 2)
    else:
        penalty -= sd / 10.0

    # compute the slowest stopping distance
    ssu = (au - 2) * (au - 1) / 2.0
    ssv = (av - 2) * (av - 1) / 2.0
    if u < 0: ssu = -ssu
    if v < 0: ssv = -ssv
    ssx = x + ssu
    ssy = y + ssv

    if not racetrack.crash([(x, y), (ssx, ssy)], walls):
        # check if the slowest stop point land on the fline
        # if yes, significantly reduce the return cost
        if li.count((ssx, ssy)) > 0:
            return (-100) * (grid[x][y] + math.sqrt(ssu ** 2 + ssv ** 2))
        # check if the slowest stopping x or y point is on the fline and reduce the return cost
        elif li.count((h1, ssy)) > 0 or li.count((h2, ssy)) > 0 or li.count((ssx, w1)) > 0 or li.count((ssx, w2)) > 0:
            penalty -= sd / 10.0

    hval += penalty

    return hval


def bfs(fline, walls):
    """
    Use a breath-first-search from the fline to compute costs for points on the grid
    (combine edistw_to_finish and edist_grid into one time traversal of the nodes;
    significantly reduce the runtime)
    :param: fline, walls
    :return: return the grid
    """
    global grid, g_fline, g_walls, xmax, ymax
    xmax = max([max(x, x0) for ((x, y), (x0, y0)) in walls])
    ymax = max([max(y, y0) for ((x, y), (x0, y0)) in walls])
    grid = [[infinity for i in range(ymax + 1)] for j in range(xmax + 1)]
    ((x1, y1), (x2, y2)) = fline
    frontier = deque([])
    visited = []

    # set the points on fline as 0 in the grid
    # and put all neighbors of the fline in the frontier
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

    # use breath-first-search to compute the costs in the grid
    while frontier:
        (v1, v2) = frontier.popleft()
        visited.append((v1, v2))
        grid[v1][v2] = edistw_to_finish((v1, v2), fline, walls)

        # check if edistw_to_finish is able to compute the cost
        # if not, compute the cost using its non-infinity neighbors
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

        if grid[v1][v2] != infinity:
            for i in range(max(0, v1 - 1), min(xmax + 1, v1 + 2)):
                for j in range(max(0, v2 - 1), min(ymax + 1, v2 + 2)):
                    if frontier.count((i, j)) == 0 and visited.count((i, j)) == 0:  ##and grid[i][j] == infinity:
                        frontier.append((i, j))

    g_fline = fline
    g_walls = walls
    return grid


def edistw_to_finish(point, fline, walls):
    """
    The function from h_walldist:
    straight-line distance from (x,y) to the finish line ((x1,y1),(x2,y2)).
    Return infinity if there's no way to do it without intersecting a wall

    :param a: point, fline, walls
    :return: straight-line distance from point to finish line (considering walls)
    """

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
