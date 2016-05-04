"""

Adapter classes for message processing

(c) syntazo 1996- 2016


syntazo opensource

coded by: thanos vassilakis

$RCSfile: __init__.py,v $
$Date: 2004/07/16 17:36:28 $
$Revision: 1.3 $
"""

import sys

from ilabs.core import Node, DeliveryAgent


class Adapter(Node):
    """
    Abstarct adapter.
    The abtsract adapter is designed to take on input, L{source}.

    """
    source = None
    agentClass = DeliveryAgent

    def __init__(self, source=None):
        """
        @param source: some source 
        @type source: any object
        """
        if source:
            self.source = source

    def read(self, *args):
        """
        Basic logic of an adapter.
        Read from  source a message, L{pack} it and then send it. 
        Continue until there are no more messages.
        
        @param args: an argument list of what ever you whant to pass to readMessage
        """
        while 1:
            message = self.readMessage(*args)
            if not message:
                break
            agent = self.pack(message)
            self.receive(agent)

    def readMessage(self, *args):
        """
        You should implement this method to extract 
        a single message. 
        @param args: You can use the args to help implement 
        an early low level filtering.
        @return: a message
        """
        raise NotImplementedError(self)

    def pack(self, message):
        """
        pack a message in an L{agentClass}, return the delivery agent
        Uses agentClass to create an agent instance and gives message to the delivery agent.
        
        @param message: a message extracted by readMessage
        @return: a delivery agent, with message (usually !?!)
        @rtype: an agent, some subclass of   DeliveryAgent
        """
        return self.agentClass(message=message)

    def close(self):
        """
        Use close to clean up.
        """

    run = read


class File(Adapter):
    """
    File adapter.
    Will not send agent containing None messages.
    """
    destination = sys.stdout
    source = sys.stdin

    def __init__(self, source=None):
        """
        @param source: The file type object you want to read. 
        Defaults to sys.stdin
        """
        if source:
            self.source = source

    def send(self, agent):
        """
        Sends the  message not the agent.
        Will not send a None message.
        """
        if agent.message: self.destination.write(agent.message)

    def readMessage(self, *args):
        """
        By default reads line by line of file.
        """
        return self.source.readline()


if __name__ == '__main__':
    print "test file copy"
    import os

    source = file('ilabs/adapters.py')
    dest = file('test', 'w')


    class FileCopier(File):
        pass


    fa = FileCopier(source).connect(dest).read()
    dest.close()
    os.system("diff ilabs/adapters.py test")


    class Methods(File):
        count = 0

        def process(self, message):
            self.count += 1
            if message.find('def') > -1:
                return '%d:%s' % (self.count, message)


    Methods(file('ilabs/adapters.py')).read()
