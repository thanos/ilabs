"""

Core classes for message processing

(c) integrationLabs 1996- 2016

coded by: thanos vassilakis

syntazo opensource

$RCSfile: core.py,v $
$Date: 2004/07/16 17:35:39 $
$Revision: 1.2 $

"""

try:
    class ilabsObject(object):
        pass
except:
    class ilabsObject:
        pass


class DeliveryAgent(ilabsObject):
    """ 
        Implements  a form of Visitor pattern.
        Its responsibility is to hold a message and deliver it to the 
        correct processor method of the current node.
            
        Use this class to encapsule a business message 
        and control what method processes it at a node.

        Was called Envelope - renamed to avoid confusion.
    """
    wayslip = None

    def __init__(self, wayslip=None, message=None):
        """ 	
        @param wayslip: this is by default None but can be used for routing information.
        @type wayslip: Wayslip object.
        @param message: message to be delivered
        @type message: 	any object.
        """
        if wayslip: self.wayslip = wayslip
        self.message = message

    def processNode(self, node):
        """ 
        invokes Node.processAgent 
        @param node: The node the message will be delivered to.
        @type node: Node object 
        @return: a message instance.
        """
        return node.processAgent(self)


class Node(ilabsObject):
    """ 
        abstract node - don't use - always subclass 
        implentation of Node - with a single destination
    """
    destination = None
    name = ''

    def __init__(self, name=''):
        if name:
            self.name = name

    def receive(self, agent):
        """ 
        if you override invoke the agent's 
        process method and pass result with send 
        """
        assert agent, "Got to receive an agent"
        agent = agent.processNode(self)
        if agent:
            self.send(agent)

    def send(self, agent):
        """ 
            Must be overridden.
            Should normally implement sending the agent onto the next node in the net work.
            override and always return self
            @param agent: the devilery agent
            @type 	agent: DeliveryAgent
            @return: self
        """
        if self.destination:
            self.destination.receive(agent)
        return self

    def connect(self, receiver, *args):
        """ 
            Must be overridden.
            - override and always return self
            @param receiver: the node to receive the processed message
            @type 	receiver: Node subclass
            @param args: a list of args to facilitate the connection.
            @return: self
        """
        assert receiver, "receiver must not be None"
        self.destination = receiver
        return self

    def disconnect(self, receiver=None, *args):
        """
        disconnects a node to this pipe.
        @param reciever: the node to be connected.
        @type receiver: node to be disconnected.
        @param *args: list of args to facilitate disconnection.

        @return: must return  self 
        @rtype: Node
        """
        self.destination = None
        return self

    def processAgent(self, agent):
        """ 
            Override is you need access to the delivery agent

            @param agent: the delivery agent
            @type 	agent: DeliveryAgent
            @return:  the delivery agent
            @rtype: DeliveryAgent
        """
        agent.message = self.process(agent.message)
        return agent

    def process(self, message):
        """ 
            Override to process message

            @param message: the sage to process
            @return:  the message
        """
        return message


class Proxy(Node):
    """ 
    This is a node place holder or socket. 
    You use this class when you want to be able to replace nodes without rewiring them.
    a Proxy pattern.
    """

    UNWIRED = True
    WIREDTHRU = False

    def __init__(self, name='', node=None, whenEmpty=UNWIRED):
        Node.__init__(self, name=name)
        self.node = None
        self.connections = []
        self.whenEmpty = whenEmpty

    def send(self, agent):
        """ send the agent and sends it to 1st node """
        if self.node:
            self.node.receive(agent)
        elif self.whenEmpty == self.WIREDTHRU:
            for node, args in self.connections:
                node.receive(agent)

    def connect(self, receiver, *args):
        """ 
        connects 1st as the pipelines destination and last node of chain to the actual destination 
        @param reciever: the node to be connected.
        @type receiver: node

        @return: must return  self 
        @rtype: Node
        """
        assert receiver, "receiver must not be None"
        if self.node:
            self.node.connect(receiver, *args)
        self.connections.append((receiver, args))
        return self

    def plugin(self, node):
        """ 
        Plugs node into socket of Proxy. 
        Will unplug and existing plugged-in node.
        @param reciever: the node to be connected.
        @type receiver: node
        @return: must return  self 
        @rtype: Node
        """
        assert node, "plugin must take a node"
        self.unplug()
        self.node = node
        for node, args in self.connections:
            self.node.connect(node, *args)
        return self

    def unplug(self):
        """ 
        Un plugs current node from socket of Proxy. 
        Disconects 
        @param reciever: the node to be connected.
        @type receiver: node
        @return: must return  self 
        @rtype: Node
        """

        if self.node:
            self.node.disconnect()
            self.node = None
        return self


class RoutingStrategy(ilabsObject):
    """
        Abstarct  routing strategy.
    """

    def getRoutesUsingAgent(self, agent, table):
        result = self.getRoutesUsingMessage(agent.message, table)
        return result

    def getRoutesUsingMessage(self, message, table):
        # print
        # print "PY message:", message
        # print
        criteria = self.criteriaFromMessage(message, table)
        result = table.routes(*criteria)
        return result

    def criteriaFromMessage(self, message, table):
        """
            extracts  routing citeria from an agents's message.
        """
        "should implement routing stategy"
        raise NotImplementedError()


class RouteTable(ilabsObject):
    """
        Implements a default route table as a dictionary.
    """
    NoRoutes = []
    tableClass = dict
    cache = {}

    def __init__(self):
        self.table = self.tableClass()

    def allRoutes(self):
        return self.table.values()

    def addRoute(self, route, *criteria):
        """
        inserts a route for each criterion.

        @param route: Node to add to table keyed by criteria
        @type route: Node
        @param criteria: criteria by which router chooses the node to route Agent.
        @type criteria: list of any hashable parameters.
        
        @return: self
        """
        for criterion in criteria:
            self.table[criterion] = route
        return self

    def removeRoute(self, route, *criteria):
        for criterion in criteria:
            del self.table[criterion]
        return self

    def routes(self, *criteria):
        """
        returns a list of routes given a set of criterion.

        @param criteria: criteria by which router chooses the node to route Agent.
        @type criteria: list of any hashable parameters.
        @return: list of routes
        """
        if not criteria:
            return self.NoRoutes
        return [self.table[criterion] for criterion in criteria if criterion in self.table]
        try:
            routes = self.cache[criteria]
        except KeyError:
            routes = [self.table[criterion] for criterion in criteria if criterion in self.table]
            self.cache[criteria] = routes
        return routes

    def __repr__(self):
        return "%s routes: %s" % (self.__class__, str(self.table.items()))


class Router(Node):
    """
    Abstarct  message router

    tableClass = route table class
    strategyClass = routing strategy 
    """
    tableClass = RouteTable
    strategyClass = RoutingStrategy

    def __init__(self, name='', table=None, strategy=None):
        """
        table - the route table instance
        strategy - the routing table strategy
        """
        Node.__init__(self, name=name)
        if table is None:
            table = self.tableClass()
        self.table = table
        if strategy is None:
            strategy = self.strategyClass()
        self.strategy = strategy
        self.default = []
        Node.__init__(self, name=name)

    def connect(self, route, *criteria):
        """
         use to added a route with a given criteria 
        @param route: Node to add to table keyed by criteria
        @type route: Node
        @param criteria: criteria by which router chooses the node to route Agent.
        @type criteria: list of any hashable parameters.
        
        @return: self
        """
        assert route, "receiver must not be None"
        self.table.addRoute(route, *criteria)
        return self

    def setDefault(self, *routes):
        self.default = routes

    def disconnect(self, *criteria):
        self.table.removeRoute(route, *criteria)
        return self

    def send(self, agent):
        routes = self.strategy.getRoutesUsingAgent(agent, self.table)
        if not routes:
            routes = self.default
        for route in routes:
            message = agent.message
            route.receive(agent)
            agent.message = message

    def __repr__(self):
        return "%s table: %s" % (self.__class__, self.table)


class System(ilabsObject):
    def __init__(self, name='', configurator=None):
        self.setup(configurator)

    def setup(self, configurator):
        configurator.configure(self)

    def run(self): pass
