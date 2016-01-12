'''
Created on Jan 8, 2016

@author: jonathanshor
'''
import numpy as np
import pygame
# import COS451.COS451PS1 as CGfund
from scipy.spatial import Delaunay
# from COS451.COS451PS1 import CCW
from DCEL import Vertex, Edge, Face, Triangled_DCEL

BOXSIZE = 300.
SCALE = 1.   # Set to 1 for no scaling
BBOX = [(0., 0.), (BOXSIZE, 0.), (BOXSIZE, BOXSIZE), (0., BOXSIZE)]
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED =   (255,   0,   0)


def ScaleUp(poly):
    'Poly should be a list of 2-tuples'
    return [(SCALE * x[0], SCALE * x[1]) for x in poly]


def Display(polys, red_polys=None):
    'Expects just a list of polys, NO LABELS'
    screen = pygame.display.set_mode([int(BOXSIZE), int(BOXSIZE)])
    pygame.display.set_caption("Some Polygons?")

    screen.fill(WHITE)

    to_draw = [ScaleUp(x) for x in polys]

    for poly in to_draw:
        pygame.draw.polygon(screen, BLACK, poly, 1)

    if red_polys is not None:
        to_draw = [ScaleUp(x) for x in red_polys]

        for poly in to_draw:
            pygame.draw.polygon(screen, RED, poly, 1)

    # Update the screen with what we've drawn.
    pygame.display.flip()

    # Hold until the user does anything.
    done = False
    clock = pygame.time.Clock()
    while not done:
        clock.tick(4)
        for event in pygame.event.get():  # User did something
            if event.type == pygame.KEYDOWN:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                done = True
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop


def Triangulate(points):
    # points is a list of 2-tuples
    # Can assume this returns a triangulated version of graph
    # return Delaunay(points, qhull_options="Qbb Qc Qz QJ")
    return Delaunay(points)


# TODO: Delete, this needs a lot more testing to confirm triangle is inside a non-convex polygon
def LabelTriangle(labeled_polys, triangle):
    'triangle is a 3-tuple or list of len 3, each element being a 2-tuple'
    for i in labeled_polys:
        if (triangle[0] in i[1]) and (triangle[1] in i[1]) and (triangle[2] in i[1]):
            return i[0]
    return None


def FindIndSet():
    pass


def FindNextLayer():
    pass


def ProduceHeirarchy():
    pass


def Query():
    pass

# Assume fixed bounding box BBOX, and list of labeled non-intersecting polygons POLYS
# Polygon vertices given in CW order
if __name__ == '__main__':
    POLYS = [("A", [(110, 20), (120, 50), (110, 90), (140, 70), (180, 30)]),
             ("B", [(20, 30), (30, 90), (45, 45), (50, 51), (85, 20)]),
             ("C", [(140, 100), (100, 100), (150, 150)]),
             ("D", [(140, 100), (150, 150), (180, 100)])]
    # POLYS = [("B", [(20, 30), (30, 90), (45, 45), (50, 51), (85, 20)])]
    # BBOX = []
    print POLYS
    raw_polys = [x[1] for x in POLYS]
    # print raw_polys

    input_pts = set()
    # input_pts = []
    for poly in raw_polys:
        # print poly
        input_pts.update(poly)
        # input_pts += poly
    input_pts.update(BBOX)
    # points = np.array(BBOX + list(input_pts))
    points = np.array(list(input_pts))
    # points = np.array([[pt[0], pt[1]] for pt in raw_polys[0]]) # DELETE THIS
    # print "Points:", points
    Display(raw_polys)
    print "Points: ", points
    first_tri = Triangulate(points)
    assert len(first_tri.coplanar) == 0  # Ensure qhull didnt omit any points
    print "Points: ", first_tri.points
    print "Indices: ", first_tri.simplices
    # Back to our point-tuple structure
    tri_points = [[(pt[0], pt[1]) for pt in tri] for tri in points[first_tri.simplices]]

    # Ensure qhull didnt mutate any points
    tri_points_check = set()
    for tri in tri_points:
        tri_points_check.update(tri)
    # print input_pts ^ tri_points_check
    assert input_pts == tri_points_check

    labeled_tris = [(LabelTriangle(POLYS, tri), tri) for tri in tri_points]
    print "Labeled: "
    print [x for x in labeled_tris if x[0] == 'A']
    print [x for x in labeled_tris if x[0] == 'B']
    print [x for x in labeled_tris if x[0] == 'C']
    print [x for x in labeled_tris if x[0] == 'D']

    Display(tri_points, raw_polys)

"""
    verts = set()
    verts.add(Vertex((0, 2)))
    print verts
    verts.add(Vertex((1, 0)))
    print verts
    origin = Vertex((0, 0))
    e = Edge(origin)
    verts.add(origin)
    print verts
    verts.add(Vertex((0, 0)))
    print verts
    print "Origin edges: "
    for edge in origin.getOuts():
        print edge.getOrigin()
"""
