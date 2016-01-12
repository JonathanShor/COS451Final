'''
Created on Jan 8, 2016

@author: jonathanshor
'''
import numpy as np
import pygame
# import COS451.COS451PS1 as CGfund
from scipy.spatial import Delaunay
from DCEL import Vertex, Edge, Face, Triangled_DCEL

BOXSIZE = 500.
SCALE = 1.   # Set to 1 for no scaling
BBOX = [(0., 0.), (BOXSIZE, 0.), (BOXSIZE, BOXSIZE), (0., BOXSIZE)]
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)


def ScaleUp(poly):
    'Poly should be a list of 2-tuples'
    return [(SCALE * x[0], SCALE * x[1]) for x in poly]


def Display(polys):
    'Expects just a list of polys, NO LABELS'
    screen = pygame.display.set_mode([int(BOXSIZE), int(BOXSIZE)])
    pygame.display.set_caption("Some Polygons?")

    screen.fill(WHITE)

    to_draw = [ScaleUp(x) for x in polys]

    for poly in to_draw:
        pygame.draw.polygon(screen, BLACK, poly, 1)

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
    return Delaunay(points)


def LabelInitialTriangulation(labeled_polys, triangle):
    'triangle is a 3-tuple or list of len 3, each element being a 2-tuple'
    pass


def FindIndSet():
    pass


def FindNextLayer():
    pass


def ProduceHeirarchy():
    pass


def Query():
    pass

# Assume fixed  bounding box BBOX, and a given list of labeled non-intersecting polygons POLYS
if __name__ == '__main__':
    POLYS = [("A", [(1, 2), (2, 5), (1, 9), (4, 7), (8, 3)]),
             ("B", [(40, 30), (30, 40), (45, 45), (50, 51), (85, 20)])]
    raw_polys = [x[1] for x in POLYS]
    # print raw_polys

    # first_layer = Triangulate([BBOX] + raw_polys)
    # input_pts = set()
    input_pts = []
    for poly in raw_polys:
        print poly
        # input_pts.update(poly)
        input_pts += poly
    points = np.array(BBOX + list(input_pts))
    print "Points:", points
    Display(raw_polys)
    first_tri = Triangulate(points)
    assert len(first_tri.coplanar) == 0
    Display(points[first_tri.simplices])
    # scaled_polys = [ScaleUp(x) for x in raw_polys]
    # print "Scaled:", scaled_polys
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
