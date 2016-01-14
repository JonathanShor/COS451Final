'''
Created on Jan 8, 2016

@author: jonathanshor
'''
import copy
import numpy as np
import pygame
from scipy.spatial import Delaunay
import DCEL
from COS451PS1 import CCW

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


class KP_Layer:
    'Triangulated planar graph rep for one layer of Kirkpatrick pt loc heirarchy'

    def __init__(self, layer_below, dcel):
        self.below_ = layer_below  # Layer below
        self.links_ = dict()    # Keys: Faces, Items: list of Faces
        self.dcel_ = dcel

    def getNext(self):
        return self.below_

    def addLink(self, link):
        """Add face of cur layer, and all faces it links to in below_.
           Expects link as a 2-element indexable key,value pair.
        """
        if __debug__:
            assert link[0] in self.dcel_.getFaces()
        self.links_[link[0]] = link[1]
        # TODO: data validation for link?

    def updateLinks(self, links):
        self.links_.update(links)

    def setLinks(self, links):
        'Add fully formed links_'
        if type(links) is dict:
            if __debug__:
                faces = self.dcel_.getFaces()
                for link in links.iter:
                    assert link[0] in faces
            self.links_ = links
        else:
            raise TypeError("Expected links to be dict, not {}".format(type(links)))

    def getLink(self, f):
        'Return list of Faces pointed to by f'
        return self.links_[f]

    def getDCEL(self):
        return self.dcel_

    def Display(self):
        Display([x[1] for x in self.dcel_.getLabeledPolys()])

    def FindIndieSet(self):
        'Return an independent set of non-CH vertices'
        verts = self.getDCEL().getVertices()
        verts -= self.getDCEL().getBox()

        for v in verts:
            if v.getDegree() > 8:
                verts.remove(v)

        ind_set = set()
        while len(verts) > 0:
            v = verts.pop()
            ind_set.add(v)
            # With degree limited to O(1), getNeighbors is O(1)
            for w in v.getNeighbors():
                verts.discard(w)

        return ind_set

    def FindPrevLayer(self):
        'Generate and return the parent layer of self'
        new_layer = KP_Layer(self, copy.deepcopy(self.getDCEL()))
        del_verts = new_layer.FindIndieSet()
        if __debug__:
            print "Building next layer"
            print "del_verts: ", del_verts
            for v in del_verts:
                assert del_verts.isdisjoint(v.getNeighbors())

        for v in del_verts:
            if __debug__:
                print v
            new_links = new_layer.getDCEL().removeInteriorVertex(v)
            new_layer.updateLinks(new_links)
            if __debug__:
                new_layer.getDCEL().Validate()

        return new_layer

    def ProduceHierarchy(self):
        'Generate the full KP hierarchy, and return the top layer.'
        cur_layer = self
        while len(cur_layer.getDCEL().getVertices()) > 2 + len(BBOX):
            cur_layer = cur_layer.FindPrevLayer()
            if __debug__:
                cur_layer.Display()
        return cur_layer

    def Depth(self):
        'Return number of layers.'
        next_layer = self.getNext()
        if next_layer is None:
            return 1
        else:
            return 1 + next_layer.Depth()

    def Query(self, q_point):
        """Return triangle coordinates (3-tuple of 2-tuples) for bottom layer triangle containing q_point.
            If __debug__, also displays query progress layer by layer.
        """
        search_faces = self.links_.iterkeys()
        cur_layer = self
        while cur_layer is not None:           # O(lg n) layers
            for tri_face in search_faces:             # O(1) search_faces at each layer
                if DCEL.Contains(q_point, tri_face.getLabel()): # O(1) per Contains() check
                    search_faces = cur_layer.getLink(tri_face)
                    cur_layer = cur_layer.getNext()
                    break   # for loop
            return None     # q_point not within the bounding box
        return tri_face.getLabel()








def LabelTriangle(triangle):
    'triangle is a length 3 iterable, each element being a 2-tuple'
    return (triangle[0], triangle[1], triangle[2])


# Assume fixed bounding box BBOX with O(1) vertices, and list of labeled non-intersecting polygons POLYS
# Polygon vertices given in CW order
if __name__ == '__main__':
    # POLYS = [("A", [(110, 20), (120, 50), (110, 90), (140, 70), (180, 30)]),
    #          ("B", [(20, 30), (30, 90), (45, 45), (50, 51), (85, 20)]),
    #          ("C", [(140, 100), (100, 100), (150, 150)]),
    #          ("D", [(140, 100), (150, 150), (180, 100)])]
    # POLYS = [("B", [(20, 30), (30, 90), (45, 45), (50, 51), (85, 20)])]
    # BBOX = []
    POLYS = [('A', [(120.0, 50.0), (140.0, 70.0), (110.0, 90.0)]),
             ('A', [(140.0, 70.0), (120.0, 50.0), (180.0, 30.0)]),
             ('A', [(120.0, 50.0), (110.0, 20.0), (180.0, 30.0)]),
             ('B', [(20.0, 30.0), (45.0, 45.0), (30.0, 90.0)]),
             ('B', [(85.0, 20.0), (50.0, 51.0), (45.0, 45.0)]),
             ('B', [(20.0, 30.0), (85.0, 20.0), (45.0, 45.0)]),
             ('C', [(100.0, 100.0), (140.0, 100.0), (150.0, 150.0)]),
             ('D', [(140.0, 100.0), (180.0, 100.0), (150.0, 150.0)])]
    # print POLYS
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
    # Display(raw_polys)
    # print "Points: ", points
    # first_tri = Delaunay(points, qhull_options="Qbb Qc Qz QJ")
    first_tri = Delaunay(points)

    assert len(first_tri.coplanar) == 0  # Ensure qhull didnt omit any points
    # print "Points: ", points[first_tri.simplices]
    # print "Indices: ", first_tri.simplices
    # Back to our point-tuple structure
    tri_points = [[(pt[0], pt[1]) for pt in tri] for tri in points[first_tri.simplices]]

    # Ensure qhull didnt mutate any points
    tri_points_check = set()
    for tri in tri_points:
        tri_points_check.update(tri)
    # print input_pts ^ tri_points_check
    assert input_pts == tri_points_check
    # Display(tri_points, raw_polys)

    labeled_tris = [(LabelTriangle(tri), tri) for tri in tri_points]
    # print "Labeled tris: ", labeled_tris

    first_layer = KP_Layer(None, DCEL.Triangled_DCEL(labeled_tris, BBOX))
    top_layer = first_layer.ProduceHierarchy()
    print "Depth: ", top_layer.Depth()
    print "(299, 299) contained with: ", top_layer.Query((299, 299))
    # first_layer.Display()
    # new_layer = FindPrevLayer(first_layer)
    # new_layer.Display()

    # while len(new_layer.getDCEL().getVertices()) > 2 + len(BBOX):
    #     new_layer = FindPrevLayer(new_layer)
    #     new_layer.Display()
