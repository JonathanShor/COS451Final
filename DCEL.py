'''
Created on Jan 12, 2016

@author: jonathanshor
'''


def Contains(point, poly):
    'Is point(2-tuple) not outside poly(list of 2-tuples)?'
    direction = CCW(poly[-1], poly[0], point)
    for i in range(len(poly) - 1):
        next_dir = CCW(poly[i], poly[i + 1], point)
        if next_dir == 0:
            continue
        if next_dir != direction:
            if direction == 0:
                direction = next_dir
            else:
                return False
    return True


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

    def getNeighbors(self):
        neighbors = set()
        for e in self.outs_:
            neighbors.add(e.getTwin().getOrigin())
        return neighbors


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
        print "Triangled_DCEL.Validation()"

        print "Number of vertices: ", len(self.verts_)
        for v in self.getVertices():
            for e in v.getOuts():
                assert v == e.getOrigin()

        assert self.getBox() <= self.getVertices()

        print "Number of half-edges: ", len(self.edges_)
        for e in self.getEdges():
            assert e == e.getNext().getPrev()  # No stand-alone edges
            assert e == e.getTwin().getTwin()  # No half-edges
            assert e.getTwin().getOrigin() == e.getNext().getOrigin()

        print "Faces: ", len(self.faces_)
        for f in self.getFaces():
            print f.getLabel()
            # Confirm representative edge leads to cycle of edges around f
            rep_e = f.getBoundary()
            assert rep_e.getFace() == f
            cur_e = rep_e.getNext()
            while rep_e != cur_e:
                assert cur_e.getFace() == f
                cur_e = cur_e.getNext()

    # TODO: make bbox NOT optional
    def __init__(self, labeled_polys, bbox=None):
        """labeled_polys is a list of 2-tuples:
        first element a label, or None
        second element a list of 2-tuple vertex coordinates in CounterClockWise order

        The polygons are assumed to be the triangles of a triangulated planar subdivision.
        bbox, if given, is a list of vertices for the convex hull in CCW order.
        """
        self.verts_ = dict()
        self.edges_ = set()
        self.faces_ = dict()
        self.box_ = set()  # Bounding box, subset of verts_

        # All faces within the bounding box that are not within a labeled polygon interior
        no_region = Face(None)
        self.faces_[no_region.getLabel()] = no_region

        if bbox is not None:
            face = no_region
            verts = []
            # Create new vertices (self.verts_ guarenteed to be empty)
            for pt in bbox:
                self.verts_[pt] = Vertex(pt)
                verts.append(self.verts_[pt])

            self.box_ = set(verts)

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

        for poly in labeled_polys:
            if poly[0] not in self.faces_:
                self.faces_[poly[0]] = Face(poly[0])
            face = self.faces_[poly[0]]

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
                # Follow the loop CCW, i.e. reverse the half edge direction
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

        if __debug__:
            self.Validate()

    def getVertices(self):
        return set(self.verts_.itervalues())

    def getEdges(self):
        return self.edges_

    def getFaces(self):
        return set(self.faces_.itervalues())

    def getBox(self):
        return self.box_

    def getLabeledPolys(self):
        'Retrieve graph in labeled polygon structure'
        labeled_polys = []
        for f in self.getFaces():
            rep_e = f.getBoundary()
            verts = [rep_e.getOrigin().getCoords()]

            cur_e = rep_e.getNext()
            while rep_e != cur_e:
                verts += [cur_e.getOrigin().getCoords()]
                cur_e = cur_e.getNext()

            labeled_polys += [(f.getLabel(), verts)]
        return labeled_polys

    def removeInteriorVertex(self, v):
        'Cleanly remove a vertex and retriangulate created star-polygon. Return new-> old face links.'
        if v in self.box_:
            raise Exception("Cannot remove bounding box vertices.")

        # CCW ordering of neighbors and edges from v to each neighbor
        del_edges = [v.getOuts().pop()]
        neighbors = [del_edges[-1].getTwin().getOrigin()]
        # Exploit strict triangulation to scan around neighborhood of v
        cur_e = del_edges[-1].getPrev().getTwin()
        while cur_e is not del_edges[0]:
            del_edges += [cur_e]
            neighbors += [del_edges[-1].getTwin().getOrigin()]
            cur_e = del_edges[-1].getPrev().getTwin()
        assert len(del_edges) == len(neighbors)

        from COS451PS1 import CCW
        cur_neigh_i = 0
        while len(neighbors) > 3:
            prev_neigh = neighbors[cur_neigh_i - 1]
            cur_neigh = neighbors[cur_neigh_i]
            next_neigh = neighbors[(cur_neigh + 1) % len(neighbors)]
            turn = CCW(prev_neigh.getOrigin(), cur_neigh.getOrigin(), next_neigh.getOrigin())
            if __debug__:
                assert (turn == -1) or (turn == 1)
            if turn == -1:  # Convex neighbor, ear cutting time
                # Ensure v not inside new face, otherwise skip for now
                if Contains(v.getCoords(), [prev_neigh.getCoords(), cur_neigh.getCoords(), next_neigh.getCoords()]):
                    cur_neigh_i += 1
                    continue

                # TODO: Face linking
                diag = Edge(next_neigh)
                diag_twin = Edge(prev_neigh)
                diag.setTwin(diag_twin)
                diag_twin.setTwin(diag)

                to_del = del_edges[cur_neigh_i]
                del_edges = del_edges[:cur_neigh_i] + del_edges[cur_neigh_i + 1:]
                neighbors = neighbors[:cur_neigh_i] + neighbors[cur_neigh_i + 1:]
                cur_neigh.removeEdge(to_del.getTwin())

                to_del.getTwin().getNext().setNext(diag_twin)  # a -> h
                to_del.getTwin().getNext().setPrev(to_del.getPrev())  # f <- a
                to_del.getTwin().getPrev().setNext(to_del.getNext())  # b -> e
                to_del.getTwin().getPrev().setPrev(diag)  # g <- b
                to_del.getNext().setNext(diag)  # e -> g
                to_del.getNext().setPrev(to_del.getTwin().getPrev())  # b <- e
                to_del.getPrev().setNext(to_del.getTwin().getNext())  # f -> a
                to_del.getPrev().setPrev(diag_twin)  # h <- f
                diag.setNext(to_del.getTwin().getPrev())  # g -> b
                diag.setPrev(to_del.getNext())  # e <- g
                diag_twin.setNext(to_del.getPrev())  # h -> f
                diag_twin.setPrev(to_del.getTwin().getNext())  # a <- h

                new_face = Face((prev_neigh.getCoords(), cur_neigh.getCoords(), next_neigh.getCoords()))
                new_face.setBoundary(diag)
                diag.setFace(new_face)
                diag.getNext().setFace(new_face)
                diag.getPrev().setFace(new_face)

                new_face = Face((prev_neigh.getCoords(), v.getCoords(), next_neigh.getCoords()))
                new_face.setBoundary(diag_twin)
                diag_twin.setFace(new_face)
                diag_twin.getNext().setFace(new_face)
                diag_twin.getPrev().setFace(new_face)
            else:  # Reflex point, skip for now
                cur_neigh_i += 1

        # Final 3 neighbors form final triangle
        assert Contains(v.getCoords(), [x.getCoords() for x in neighbors])
        new_face = Face((neighbors[0].getCoords(), neighbors[1].getCoords(), neighbors[2].getCoords()))
        for i in range(3):
            neighbors[i].removeEdge(del_edges[i].getTwin())
            del_edges[i].getNext().setNext(del_edges[(i + 1) % 3].getNext())
            del_edges[i].getNext().setPrev(del_edges[i - 1].getNext())
            del_edges[i].getNext().setFace(new_face)

        # And like that, its gone
        # TODO: return face links




