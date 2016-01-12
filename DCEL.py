'''
Created on Jan 12, 2016

@author: jonathanshor
'''


class Vertex:
    'Vertex'

    # def __init__(self, coords=None):
    #     if (coords is None) or (isinstance(coords, tuple)):
    #         self.coords_ = coords
    #     else:
    #         raise TypeError("Bad coords: {}".format(coords))
    #     self.outs_ = set()
    def __init__(self, coords):
        'Coords are fixed at instantiation'
        if isinstance(coords, tuple):
            self.coords_ = coords
        else:
            raise TypeError("Bad coords: {}".format(coords))
        self.outs_ = set()

    def __eq__(self, other):
        return (self.coords_ == other.coords_)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        # return hash(id(self.coords_))
        return hash(self.coords_)

    def __repr__(self):
        return str(self.coords_)

    def getCoords(self):
        return self.coords_

    def getOuts(self):
        return self.outs_

    def addEdge(self, e):
        'Returns 0 if e already in outs_, 1 if e is new'
        if isinstance(e, Edge):
            pre_size = len(self.outs_)
            self.outs_.add(e)
            return len(self.outs_) - pre_size
        else:
            raise TypeError("Bad edge: {}".format(e))

    def removeEdge(self, e):
        'Returns -1 if e successfully removed, raises KeyError if e not in outs_'
        if isinstance(e, Edge):
            pre_size = len(self.outs_)
            self.outs_.remove(e)
            return len(self.outs_) - pre_size
        else:
            raise TypeError("Bad edge: {}".format(e))

    def getDegree(self):
        return len(self.outs_)


class Edge:
    'Half edge'

    def __init__(self, origin):
        'Origin is fixed at instantiation'
        if isinstance(origin, Vertex):
            self.origin_ = origin
            origin.addEdge(self)
        else:
            raise TypeError("Bad Vertex: {}".format(origin))
        self.twin_ = None
        self.prev_ = None
        self.next_ = None
        self.face_ = None

    def getOrigin(self):
        return self.origin_

    def getTwin(self):
        return self.twin_

    def setTwin(self, e):
        'Does NOT set self to be the twin of e. Must be done independently.'
        if isinstance(e, Edge):
            self.twin_ = e
        else:
            raise TypeError("Bad edge: {}".format(e))

    def getPrev(self):
        return self.prev_

    def setPrev(self, e):
        if isinstance(e, Edge):
            self.prev_ = e
        else:
            raise TypeError("Bad edge: {}".format(e))

    def getNext(self):
        return self.next_

    def setNext(self, e):
        if isinstance(e, Edge):
            self.next_ = e
        else:
            raise TypeError("Bad edge: {}".format(e))

    def getFace(self):
        return self.face_

    def setFace(self, f):
        if isinstance(f, Face):
            self.face_ = f
        else:
            raise TypeError("Bad face: {}".format(f))


class Face:
    'Face represention'

    def __init__(self, label):
        self.label_ = label
        self.boundary_ = None

    def getLabel(self):
        return self.label_

    def getBoundary(self):
        return self.boundary_

    def setBoundary(self, e):
        'Set representative edge of face boundary'
        if isinstance(e, Edge):
            self.boundary_ = e
        else:
            raise TypeError("Bad edge: {}".format(e))


class Triangled_DCEL:
    'Planar graph rep via doublely connected edge list'

    def Validate(self):
        'Some (not exhaustive) internal consistency checks'
        for v in self.verts_.itervalues():
            for e in v.getOuts():
                assert v == e.getOrigin()

        for e in self.edges_:
            assert e == e.getNext().getPrev()  # No stand-alone edges
            assert e == e.getTwin().getTwin()  # No half-edges
            assert e.getTwin().getOrigin() == e.getNext().getOrigin()

        for f in self.faces_:
            # Confirm representative edge leads to cycle of edges around f
            rep_e = f.getBoundary()
            assert rep_e.getFace() == f
            cur_e = rep_e.getNext()
            while rep_e != cur_e:
                assert cur_e.getFace() == f
                cur_e = cur_e.getNext()

    def __init__(self, labeled_polys, bbox=None):
        """labeled_polys is a list of 2-tuples:
        first element a label, or None
        second element a list of 2-tuple vertex coordinates in ClockWise order

        The polygons are assumed to be the triangles of a triangulated planar subdivision.
        bbox, if given, is a list of vertices for the convex hull in CW order.

        [DEPRECIATED: Strictly simple polygons, with the sole exception possibly being bbox

        bbox is optional list of coords for bounding polygon
        One will be created if none given.
        If given, must actually contain all polys in labeled_polys,
        and must consist of vertices strictly distinct from labeled_polys]
        """
        self.verts_ = dict()
        self.edges_ = set()

        # All faces within the bounding box that are not within a labeled polygon interior
        no_region = Face(None)
        self.faces_ = set([no_region])

        if bbox is not None:
            face = no_region
            verts = []
            # Create new vertices (self.verts_ guarenteed to be empty)
            for pt in bbox:
                self.verts_[pt] = Vertex(pt)
                verts.append(self.verts_[pt])

            # Reverse vertex order to create exterior half edges
            verts = verts[::-1]
            edges = []
            for i in range(len(verts)):
                new_e = Edge(verts[i])
                edges.append(new_e)
                new_e.setFace(face)
                face.setBoundary(new_e)

            assert len(edges) == len(verts)
            # Set Next & Prev links
            for i in range(len(edges)):
                edges[i].setNext(edges[(i + 1) % len(edges)])
                edges[i].setPrev(edges[i - 1])

            self.edges_.update(edges)

        #     # Scan for needed bbox shape
        #     first_vert = labeled_polys[0][1][0]  # [First poly][verts of that poly][first vert]
        #     min_x = first_vert[0]
        #     max_x = first_vert[0]
        #     min_y = first_vert[1]
        #     max_y = first_vert[1]

        for poly in labeled_polys:
            face = Face(poly[0])
            verts = []
            # Create new/identify existing vertices
            for pt in poly[1]:
                if pt not in self.verts_:
                    self.verts_[pt] = Vertex(pt)
                verts.append(self.verts_[pt])

            edges = []
            # Create new edges
            for i in range(len(verts)):
                new_e = Edge(verts[i])
                edges.append(new_e)
                new_e.setFace(face)
                face.setBoundary(new_e)

            assert len(edges) == len(verts)
            # Set Next & Prev links
            for i in range(len(edges)):
                edges[i].setNext(edges[(i + 1) % len(edges)])
                edges[i].setPrev(edges[i - 1])

            self.edges_.update(edges)

        # Twin scan
        for e in self.edges_:
            # Scan for existing twin
            if e.getTwin() is None:
                e_next = e.getNext()
                # For all edges from e's destination that are not e.getNext
                for f in [x for x in e_next.getOrigin().getOuts() if x != e_next]:
                    if f.getNext().getOrigin() == e.getOrigin():
                        e.setTwin(f)
                        f.setTwin(e)
                        break
            # Produce new twin; should only occur if bbox was not given
            if e.getTwin() is None:
                if __debug__:
                    print "No twin: ", e.getOrigin, ", ", id(e)
                assert (hasattr(self, 'exterior_done') is False)
                new_twin = Edge(e.getNext().getOrigin())
                e.setTwin(new_twin)
                new_twin.setTwin(e)
                new_twin.setFace(no_region)
                no_region.setBoundary(new_twin)

                exterior_edges = [new_twin]
                # Should now be able to follow the exterior loop and set all remaining twins
                # Follow the loop CW, i.e. reverse the half edge direction
                while exterior_edges[-1].getOrigin() != e.getOrigin():
                    next_dest = exterior_edges[-1].getOrigin()
                    possible_outs = [x for x in next_dest.getOuts() if x.getTwin() is None]
                    assert len(possible_outs) == 1
                    f = possible_outs[0]
                    # TODO: Confirm there's no way f could be a non-exterior edge here
                    new_twin = Edge(f.getNext().getOrigin())
                    f.setTwin(new_twin)
                    new_twin.setTwin(f)
                    new_twin.setFace(no_region)
                    exterior_edges.append(new_twin)
                # Correct order to link Next & Prev
                exterior_edges = exterior_edges[::-1]
                for i in range(len(exterior_edges)):
                    exterior_edges[i].setNext(exterior_edges[(i + 1) % len(exterior_edges)])
                    exterior_edges[i].setPrev(exterior_edges[i - 1])

                self.edges_.update(exterior_edges)
                self.exterior_done = True

"""
        for poly in labeled_polys:
            face = Face(poly[0])
            prev_e = None
            for pt in poly[1]:
                if pt in self.verts_:
                    vert = self.verts_[pt]
                else:
                    vert = Vertex(pt)
                    if bbox is None:
                        min_x = min([pt[0], min_x])
                        max_x = max([pt[0], max_x])
                        min_y = min([pt[1], min_y])
                        max_y = max([pt[1], max_y])

                new_e = Edge(vert)
                new_e.setFace(face)
                new_e.setPrev(prev_e)
                prev_e.setNext(new_e)

                self.verts_[pt] = vert
                self.edges_.add(new_e)

                prev_e = new_e

            #Does this work? Need to ensure that verts with same coords ARE the same vert, and not separate
            #Then we can just plug in only half edges for all specificed polys, and then scan for edges without twins, and create missing twins pointing to the None face
"""
