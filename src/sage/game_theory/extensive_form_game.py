"""
This file will contain a class for extensive form games.
"""

class ExtensiveFormGame():
    """
    """
    def __init__(self, input, name = False):


    def set_info_set(nodes):
        """
        We can assign information set to  a set of nodes::
            
            sage: player1 = Player(Player 1)
            sage: player2 = Player(Player 2)
            sage: leaf_1 = Leaf({Player 1: 0, Player 2: 1}); leaf_2 = Leaf({Player 1: 1, Player 2: 0}), leaf_3 = Leaf({Player 1: 2, Player 2: 4}), leaf_4 = ({Player 1: 2, Player 2: 1})
            sage: node_1 = Node({'A': leaf_1, 'B': leaf_2})
            sage: node_2 = Node({'A': leaf_3, 'B': leaf_4})
            sage: egame_1 = ExtensiveFormGame()
            sage: egame_1.set_info_set([node_1, node_2])
            sage: egame_1.set_info_set
            Information set with nodes, [node_1, node_2]


        If two nodes don't have the same actions, an error is returned::
            
            sage: player1 = Player(Player 1)
            sage: player2 = Player(Player 2)
            sage: leaf_1 = Leaf({Player 1: 0, Player 2: 1}); leaf_2 = Leaf({Player 1: 1, Player 2: 0}), leaf_3 = Leaf({Player 1: 2, Player 2: 4}), leaf_4 = ({Player 1: 2, Player 2: 1})
            sage: node_2 = Node({'AlternativeA': leaf_3, 'AlternativeB': leaf_4})
            sage: root_1 = Root({'C': node_1, 'D': node_2})
            sage: egame_1 = ExtensiveFormGame(root_1)
            sage: egame_1.set_info_set([node_1, node_2])
            Traceback (most recent call last):
            ...
            AttributeError: One or two of the nodes do not share the same actions.


        If two nodes have different players, an error is returned::
            
            sage: player1 = Player(Player 1)
            sage: player2 = Player(Player 2)
            sage: leaf_1 = Leaf({Player 1: 0, Player 2: 1}); leaf_2 = Leaf({Player 1: 1, Player 2: 0}), leaf_3 = Leaf({Player 1: 2, Player 2: 4}), leaf_4 = ({Player 1: 2, Player 2: 1})
            sage: node_1 = Node({'A': leaf_1, 'B': leaf_2})
            sage: node_2 = Node({'A': leaf_3, 'B': leaf_4})
            sage: node_1.player = 'Player 1'
            sage: node_2.player = 'Player 2'
            sage: root_1 = Root({'C': node_1, 'D': node_2})
            sage: egame_1 = ExtensiveFormGame(root_1)
            sage: egame_1.set_info_set([node_1, node_2])
            Traceback (most recent call last):
            ...
            AttributeError: One or two of the nodes do not share the same players.
        """


class Node():
    def __init__(self, input, name = 'False'):
        """
        Node input can be read to determine actions of node and children of node.
        
            sage: player1 = Player(Player 1)
            sage: player2 = Player(Player 2)
            sage: child_1 = Leaf({Player 1: 0, Player 2: 1}); child_2 = Leaf({Player 1: 1, Player 2: 0})
            sage: mothernode = Node({'Action1': child_1, 'Action2'L child_2})
            sage: mothernode.actions
            ['Action1', 'Action2']
            sage: mothernode.children
            [child_1, child_2]

        If we then create a second node, who has :code:`mothernode` as one of it's children, then the parent of :code:`mothernode` will be set to that node::
        
            sage: sisternode = Node()
            sage: mothernode.parent
            False
            sage: grandmothernode = Node({'ActionA':mothernode, 'ActionB':sisternode})
            sage: mothernode.parent
            grandmothernode


        We can also set names for the Node, which will then be returned instead::
        
            sage: grandmothernode = Node({'ActionA':mothernode, 'ActionB':sisternode}, 'Node A')
            sage: mothernode.parent
            Node A

        Node input can only be in dictionary form.

            sage: falsenode = Node([Fight, Flight])
            Traceback (most recent call last):
            ...
            TypeError: Node can only have its input in dictionary form.


        """
        #self.player = False
        
    
    def attributes():
        """
        We can use this function to check the attributes of each singular node, the following is what would happen if no attibutes are assigned::
           
            sage: laura_1 = Node()
            sage: laura_1.attributes 
            The node has the following attributes. Actions: False. Children: False. Parent: False. Player: False. 
        """

    
    def to_root():
        """
        If a node has no parents, and a root node hasn't been set, a node can become a root node::
        
            sage: andy_1 = Node()
            sage: type(andy_1) is Node
            True
            sage: type(andy_1) is Root
            False
            sage: andy_1.to_root()
            sage: type(andy_1) is Root
            True
            sage: type(andy_1) is Node
            False


        If the node has parents, an error message will be returned::
        
            sage: andy_1 = Node()
            sage: andy_2 = Node()
            sage: dave_1 = Node({'A': andy_1, 'B': andy_2})
            sage: andy_1.to_root()
            Traceback (most recent call last):
            ...
            AttributeError: Node with parents cannot be a root.


        If the node is connected to a set of nodes that have a root associated with them, an error is returned::
           
            sage: jill_1 = node({'A'; helen_1 'B'; helen_2})
            sage: helen_1 = Root()
            sage: jill_1 = to_root()
            Traceback (most recent call last):
            ...
            AttributeError: Extensive Form Game cannot have two roots
        """


    def to_leaf(payoffs):
        """
        A node can also be changed into a leaf if it has no parents, children, or actions. (i.e it is a blank node)::
            sage: player1 = Player(Player 1)
            sage: player2 = Player(Player 2)
            sage: jones_1 = Node()
            sage: type(jones_1) is Leaf
            False
            sage: jones_1.to_leaf({Player 1: 0, Player 2: 1})
            sage: type(jones_1) is Leaf
            True
            sage: type(jones_1) is Node
            False


        If a node has any attribues other than parent, an error is returned::

            sage: williams_1 = Node({'A', 'B'})
            sage: williams_1.to_leaf({Player 1: 0, Player 2: 1})
            Traceback (most recent call last):
            ...
            AttributeError: Node has attributes other than parent, cannot be leaf.

        """


class Leaf():
    def __init__(self, payoffs):
        """
        We can check payoffs of any leaf.
            sage: leaf_1 = Leaf({player 1: 0, player 2: 1})
            sage: leaf_1.payoffs
            ({player 1: 0, player 2: 1})
        """

class Root(Node):
    """
    A root is just another type of node, so we can get attributes, however Parent will always be false. Attempting to add a parent will return an error::
        
        sage: bethan_1 = Root({'Red': jess_1, 'Blue': jess_2}))
        sage: bethan_1.attribues
        some output of attributes specific to bethan_1
    
    We cannot have more than one Root in a game, so if we try to connect a second Root to a connected set of nodes that already have a root, an error will be displayed::
        
        sage: jess_1 = Node([Green, Yellow]); jess_2 = Node([Green, Yellow]); jess_3 = Node([Green, Yellow])
        sage: bonnie_1 = Root({'Black': jess_1, 'White': jess_3})
        Traceback (most recent call last):
        ...
        AttributeError: Extensive Form Game cannot have two roots
    """


class Player():
    def __init__(self, name):
        """
        We can use Player() to assign players to nodes::
            sage: jack_1 = Node()
            sage: jack_1.player = Player('Jack')
            sage: jack_1.player
            Jack


        If a node is not specificed a player, then this should return false::
            sage: sam_1 = Node()
            sage: sam_1.player
            False
        """

