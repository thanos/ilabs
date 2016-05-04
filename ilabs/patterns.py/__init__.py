"""

integration pattern classes for message processing

(c) syntazo 1996- 2016

coded by: thanos and friends

syntazo opensource

$RCSfile: __init__.py,v $
$Date: 2004/07/16 17:31:19 $
$Revision: 1.3 $

"""
from types import ListType, TupleType

from ilabs.core import Node, RoutingStrategy, RouteTable, Router


class NodeList(Node):
    deferChange = False
    onChange = None

    def __init__(self, name='', *args):
        Node.__init__(self, name)
        self.list = []
        if self.onChange: self.onChange(self.__init__, *args)

    def __setitem__(self, i, item):
        elf.list[i] = item
        if self.onChange: self.onChange(self.__setitem__, i, item)

    def __delitem__(self, i):
        del self.list[i]
        if self.onChange: self.onChange(self.__delitem__, i)

    def __setslice__(self, i, j, other):
        self.list[i:j] = other
        if self.onChange: self.onChange(self.__setslice__, i, j, other)

    def __delslice__(self, i, j):
        del self.list[i:j]
        if self.onChange: self.onChange(self.__delslice__, i, j)

    def append(self, value):
        self.list.append(value)
        if self.onChange: self.onChange(self.append, value)

    def insert(self, where, value):
        self.list.insert(where, value)
        if self.onChange: self.onChange(self.insert, value)

    def pop(self, i=-1):
        result = self.list.pop(i)
        if self.onChange: self.onChange(self.pop, value)
        return result

    def remove(self, item):
        self.list.remove(item)
        if self.onChange: self.onChange(self.remove, value)

    def count(self, item):
        result = self.list.count(item)
        if self.onChange: self.onChange(self.count, value)
        return result

    def index(self, item, *args):
        result = self.list.index(item, *args)
        if self.onChange: self.onChange(self.index, value)
        return result

    def reverse(self):
        self.list.reverse()
        if self.onChange: self.onChange(self.reverse, value)

    def sort(self, *args):
        self.list.sort(*args)
        if self.onChange: self.onChange(self.sort, value)

    def extend(self, other):
        self.list.extend(other)
        if self.onChange: self.onChange(self.extend, value)

    def __repr__(self):
        return repr(self.list)

    def __lt__(self, other):
        return self.list < other.list

    def __le__(self, other):
        return self.list <= other.list

    def __eq__(self, other):
        return self.list == other.list

    def __ne__(self, other):
        return self.list != other.list

    def __gt__(self, other):
        return self.list > other.list

    def __ge__(self, other):
        return self.list >= other.list

    def __cmp__(self, other):
        return cmp(self.list, other.list)

    def __contains__(self, item):
        return item in self.list

    def __len__(self):
        return len(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def __getslice__(self, i, j):
        i = max(i, 0);
        j = max(j, 0)
        return self.list[i:j]


class PipeLine(NodeList):
    """ 
    Behaves as a chained list of Nodes. Received messages are passed to the first node, and the 
    last node in turn sends the message to the destination.

    The PipeLine's process is called before and of the containing nodes.
    Use list operations (append, insert, del, setitem, etc)  to set the nodes in the bank.
    When Nodes are added, inserted removed they are relinked to maintain the pipeline.

    PipeLine = [Node1, Node2.. NodeN]
    NodeA -> PipeLine -> NodeB
    Expands to:
    NodeA -> PipeLine -> Node1 - > Node2 -> ...-> NodeN -> NodeB
    """

    def onChange(self, *args):
        """ called every time the list is altered to relink the nodes """
        self.link()

    def send(self, agent):
        """ send the agent and sends it to 1st node """
        if len(self):
            self[0].receive(agent)
        else:
            Node.send(self, agent)

    def connect(self, receiver, *args):
        """ connects 1st as the pipelines destination and last node of chain to the actual destination """
        Node.connect(self, receiver, *args)
        if len(self):
            self[-1].connect(receiver)
        return self

    def link(self):
        """ used to relink the nodes """
        if len(self):
            for i in xrange(len(self[:-1])):
                self[i].connect(self[i + 1])
            if self.destination:
                self[-1].connect(self.destination)


class NodeBank(NodeList):
    """ 
    Behaves as a "parallel" bank  of Nodes. 
    Received messages are passed to the all the nodes in turn, the resulting messages are 
    then sent on to the destination.
    
    As with PipeLine this can be treated as a list.
    Use list operations (append, insert, del, setitem, etc)  to set the nodes in the bank.
    """

    def connect(self, receiver, *args):
        assert receiver, "receiver must not be None"
        Node.connect(self, receiver, *args)
        if len(self):
            map(lambda x, r=receiver, a=args: x.connect(r, *a), self)

    def receive(self, agent):
        if len(self):
            for node in self:
                node.receive(agent)
        else:
            Node.recieve(self, agent)

    def append(self, node):
        NodeList.append(self, node)
        self.connectNode(node)

    def __setitem__(self, index, node):
        NodeList.__setitem__(self, index, node)
        self.connectNode(node)

    def connectNode(self, node):
        if self.destination:
            node.connect(self.destination)

    def onChange(self, *args):
        "do nothing"
        pass


class RouteList(RouteTable):
    def addRoute(self, route, *criteria):
        if not criteria:
            return RouteTable.addRoute(self, route, route)
        return RouteTable.addRoute(self, route, *criteria)


class AllRoutes(RoutingStrategy):
    def getRoutesUsingAgent(self, agent, table):
        return table.allRoutes()


class Distributor(Router):
    strategyClass = AllRoutes
    tableClass = RouteList
    """
        Will send messages to a list of connected subscribers
    """


class SubscriptionTable(RouteTable):
    """
    Implements a router table adds subscribing route (node) 
    to an approriate distributer.
    """

    def addRoute(self, node, *criteria):
        for criterion in criteria:
            if criterion not in self.table:
                self.table[criterion] = Distributor()
            self.table[criterion].connect(node)


class RecipientList(Router):
    """
    Implements a router that sends a message to each route 
    on the approriate subscription list
    """
    tableClass = SubscriptionTable


class MessageProcessor(Node):
    routerClass = RecipientList
    concentratorClass = Node

    def __init__(self, name='', router=None, concentrator=None):
        Node.__init__(self, name)
        if not router:
            router = routerClass()
        self.router = router
        if not concentrator:
            concentrator = concentratorClass()
        self.destination = concentrator

    def register(self, processor, *criteria):
        if id not in table:
            processor.connect(self.destination)
            self.router.connect(processor, *criteria)

    def send(self, envelope):
        self.router.receive(envelope)

    def connect(self, recipient):
        self.destination.connect(recipient)


class StateMachine(Node):
    """
    Implements a hierachical state machine.
    Add attribute  the states where
    states is a tuple of  entries.
    Each entry can be one of:
    entry := current, message, next
    entry := current state, message, test, resultset

    current := 	StateMachine.INIT
            State
            collection of State
            StateMachine.ANY

    message	:= 	Message
            collection of Message
            StateMachine.ANY

    next	:= 	State
            StateMachine.CURRENT

    test 	:= 	python expression

    resultset:= 	(result, next)+

    some simple examples:
    states=((DrawerClosed, Eject, DrawerOpen),
        (DrawerOpen, Eject, CDStopped),
        (CDStopped, Play, CDPlaying),
        (CDPlaying, Pause, CDPaused),
        ((CDPlaying,CDPaused), Stoped, CDStoped),
        (CDPaused, (Pause,Play) CDPlaying)
        )
        
    states=((DrawerClosed, Eject, DrawerOpen),
    (DrawerOpen, Eject, "hasCd()", (False, CDStopped), (True, DrawerClosed)),
    ((CDStopped, CDPlaying, CDPause), Eject, DrawerOpen),
    ((CDStopped, CDPause), Play, CDPlaying),
    (CDPlaying,CDPaused), Stoped, CDStoped),
    ((CDPlaying,CDPaused), NextTrack, "isLastTrack()", (False, StateMachine.CURRENT), (True, CDStop)),
    ((CDPlaying,CDPaused), PrevTrack", isFirstTrack()", (False, StateMachine.CURRENT), (True, CDStop))
    )

    for more and hierachicle see the test code

    """

    class State(Node):
        def __repr__(self): return self.name or self.__class__.__name__

        def process(self, node, message):
            Node.process(self, message)

    INIT = State('INIT')
    ANY = State('ANY')
    LAST = State('LAST')
    CURRENT = State('CURRENT')
    UNDEF = INIT
    DEFAULT = object()
    debug = False

    def __init__(self, name, *args):
        Node.__init__(self, name, *args)
        self.state = self.INIT
        self.buildTable()

    def buildTable(self):
        states = {}
        for entry in self.states:
            currentState, transitions = entry[0], entry[1:]
            for transition in transitions:
                if len(transition) == 2:
                    messageList, nextStates = transition
                    test = None
                elif len(transition) > 3:
                    messageList, test, nextStates = transition[0], compile(transition[1], '<string>', 'eval'), dict(
                        transition[2:])
                    if self.DEFAULT not in nextStates:
                        nextStates[self.DEFAULT] = None
                if not type(messageList) in (ListType, TupleType):
                    messageList = [messageList]
                for message in messageList:
                    states[self.getInitKey(currentState, message)] = test, nextStates
        self.states = states

    def getKey(self, message, currentState):
        return (currentState, message)

    getInitKey = getKey

    def getNextState(self, message, *varspace):

        key = self.getKey(self.state, message)
        entry = self.states.get(key)
        # print '1.StateMachine key:%s, nextState: %s' % (key, entry)
        if entry is None:
            key = self.getKey(StateMachine.ANY, message)
            entry = self.states.get(key)
        # print '2.StateMachine key:%s, nextState: %s' % (key, entry)
        retval = self.UNDEF
        if entry is not None:
            import time
            test, resultStates = entry[0], entry[1]
            if test:
                res = eval(test, *varspace)
                try:
                    newState = resultStates[res]
                except KeyError:
                    newState = resultStates[self.DEFAULT]

                """
                print test, 'TEST', time.strftime("%H:%M:%S.%%04d", time.localtime(message.header[0])) % message.header[7]
                print res, newState, resultStates
                """
            else:
                newState = resultStates
        else:
            if self.UNDEF == StateMachine.CURRENT:
                newState = self.state
            else:
                newState = self.INIT
        # print self.getNextState, retval, self.state
        return newState

    def process(self, message, *varspace):
        state = self.getNextState(message, *varspace)
        if state != self.state:
            if 0:
                import time
                print time.strftime("%H:%M:%S.%%04d", time.localtime(message.header[0])) % message.header[7]
                print self.state, state, message.header
            self.state = state
            if hasattr(state, 'process'):
                return state.process(self, message)

    def ofInterest(self):
        return [message for state, message in self.states if state == self.state]
