""" File dpt.py

Discrete Pulse Transform

Dirk Laurie, July 2009

"""

from sys import maxint
from collections import deque
from math import sqrt

""" Since we are importing deque anyway, it is simplest to define 
queue as a specialization of deque."""
class queue(deque):
    get = deque.popleft
    put = deque.append


""" Coding style: I don't use 'self' for the object itself, but
a lower-case version of the class name.
"""

""" Node is a specialization of set.  There is no "neighbors" entry:
    node.add is used instead of node.neighbors.add, etc.
"if node:" is a test whether the node is empty.  
The members of a node are indices into a list.  Therefore algorithms 
    involving neighbours of nodes must be able to see the list of nodes.
    They are implemented as methods of class GraphFunction, below.
node.tag is the index of the node itself into that list.
NB: it is not possible to have a set of nodes, since sets and therefore
    nodes too are unhashable.
"""
class Node(set):

    def __init__(node,tag,value,size=1):
        node.parent = node
        node.tag = tag
        node.value = value
        node.size = size

    def active(node,size):
        return node.parent is node and node.size == size
   
    def __repr__(node): 
        return "%s_%r(%r)=>%s;%s" % (node.tag,
            node.size,node.value,node.parent.tag,list(node))

""" Add the arc between a and b.  This procedure does not require
access to the list of nodes.  """
def arc(a,b): a.add(b.tag); b.add(a.tag)


""" Programming convention: the 'self' parameter is called either
'graph' or 'tree'.  Functions that should be called only before "dpt" 
is done, use "graph" for self; functions that should be called only 
afterwards, use "tree". """
class GraphFunction:    

    def __init__(graph,values,arcs):       
        """ 
Initialize a graph function from a list of values and a list of arcs,
where each arc is a tuple of two integers. """
        n = len(values)
        graph.schedule = Schedule(cutoff=int(sqrt(n))) 
        graph.nodes = tuple([Node(a,values[a]) for a in xrange(n)]) 
        for (a,b) in arcs: arc(graph.nodes[a],graph.nodes[b])
# The following parameters are only academic.  
        graph.nnodes = n
        graph.narcs = sum([len(node) for node in graph.nodes])/2
        graph.count = graph.border = 0

    def shrink(graph,node):
        """ Read the description in the paper. """
        agenda = queue([node])            
        sign = [0,0]
        while agenda:
            item = agenda.get()
            for c in list(item):
                graph.count += 1
                child = graph.nodes[c]
                child.remove(item.tag)
                if child.parent is not node:
                    if node.value == child.value:
                        agenda.put(child)
                        child.parent = node
                        child.value = 0
                        node.discard(child.tag)
                        node.size += child.size
                    else:
                        arc(node,child)
                        sign[node.value>child.value] = 1
        feature = sign[1]-sign[0] 
        graph.border += len(node)
        if not node:
            graph.root = node
        elif feature: 
            graph.schedule.push(node,node.size,feature)

    def nearest(graph,node):
        neg = -maxint
        pos = maxint
        for i in node:
            diff = node.value - graph.nodes[i].value
            if diff>0 and diff<pos:
                pos = diff
                nearest = i
            elif diff<=0 and diff>neg:
                neg = diff
                nearest = i
        return graph.nodes[nearest]

    def dpt(graph,thispolicy=None):
        """ Transform graph function to DPT tree.  Read the description 
in the paper. """

        global policy        
        policy = thispolicy or ceilingDPT
        schedule = graph.schedule

        for node in graph.nodes:
            if node.parent is node:
                graph.shrink(node)

        graph.border1 = graph.border
        graph.border=0

        while True:
            node = schedule.pop()
            if node is None: break
            survivor = graph.nearest(node)
            height = node.value - survivor.value
            node.value = survivor.value
            graph.shrink(survivor)
            node.value = height

        for node in graph.nodes:
            node.clear()
        for child in graph.nodes:
            if child is not graph.root:
                child.parent.add(child.tag)

    def revalue(tree):
        for child in tree.traverse():
            child.value += child.parent.value

    def traverse(tree,root=None,include_root=False):
        """
tree.traverse(node) returns a breadth-first iterator for the subtree 
    starting at but not including node.  Default: node is tree.root.
tree.traverse(node,include_root=True) does include node.  
"""
        if root is None:
            root = tree.root
        if include_root:
            yield root
        agenda = queue([root])
        while agenda:
            node = agenda.get()
            for c in node:
                child = tree.nodes[c]
                yield child
                agenda.put(child)

    def __repr__(graph):
        return str(graph.nodes)


class Schedule:

    def __init__(schedule,cutoff=100):
        schedule.cutoff = cutoff
        schedule.boxes = [deque() for k in range(cutoff)]
        schedule.start = schedule.stop = 0
# start is the bumber of the box from which the next item will be popped.
# stop-1 is the number of the last box that has actually been used.
        schedule.tiebreak = policy(1)
        schedule.store = {} 
                   
    def __getitem__(schedule,i):
        """ Return the deque that holds items of width i+1. """
        if i<schedule.cutoff: return schedule.boxes[i]
        if not schedule.store.has_key(i): 
            schedule.store[i] = deque()
        return schedule.store[i]

    def current(schedule):        
        """ Find the deque off which the next item will be popped. """
        box = None
        while schedule.start<schedule.stop:
            if schedule.start<schedule.cutoff:
                box = schedule.boxes[schedule.start]
            elif schedule.store.has_key(schedule.start):
                box = schedule.store[schedule.start]
            if box:
                return box
            schedule.start += 1
            schedule.tiebreak = policy(schedule.start+1)
        return None

    def pop(schedule):
        while True:
            pulse = None
            box = schedule.current()
            if not box:
                break
            if schedule.tiebreak: 
                pulse = box.pop()
            else:
                pulse = box.popleft()
            if pulse is None: break
            if pulse.active(schedule.start+1):
                break
        return pulse
        
    def push(schedule,node,size,sign):
        schedule.stop = max(schedule.stop,size)
        box = schedule[size-1]
        if sign>0: box.append(node)
        else: box.appendleft(node) 

    def debug(schedule):
        print('-------- start = %i ---- stop = %i --------')%(
            schedule.start,schedule.stop)
        for k in range(schedule.cutoff):
            if schedule.boxes[k]:
                print 'size %i' % (k+1), schedule.boxes[k]
        if schedule.store: print 'store', schedule.store

ceilingDPT = lambda(size): False
floorDPT = lambda(size): True
policy = ceilingDPT

def ABC(k):
    return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[k]

def label(node):
    return ''.join([ABC(j) for j in sorted(node)])
   
if __name__ == '__main__':
    print "   Small example from paper: size, neighbors, value, parent"
    d = GraphFunction((9,7,6,0,8,13,6,7,7,0,13,13,8),
            [(12,4),(4,6),(4,8),(6,2),(0,2),(8,7),(8,1),(0,1),(0,3),
            (2,3),(2,5),(2,10),(11,10),(7,1),(1,3),(3,5),(5,10),(3,9)])
    for node in d.nodes:
        print "%s_%i(%s) = %i -> %s" % ( ABC(node.tag),node.size,
            label(node),node.value,ABC(node.parent.tag))
    d.dpt()
    print '   After DPT'
    for node in d.traverse(include_root=True):
        print "%s_%i(%s) = %i -> %s" % ( ABC(node.tag),node.size,
            label(node),node.value,ABC(node.parent.tag))
    d.revalue()
    print '   Node values recomputed from DPT'
    for node in d.traverse(include_root=True):
        print "%s = %i" % (ABC(node.tag),node.value)

