import random, pickle, datetime

from pybrain.structure import FeedForwardNetwork, LinearLayer, SigmoidLayer, FullConnection
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

class Graph():

    def construct(self, sensor_states, behaviors):
        '''
        Construct the graph (the neighborhood function) based on the given
        sensor states and behaviors between them

        sensor_states: (float list) list
        behaviors: string list

        returns: None
        '''
        raise Exception('Not implemented')

    def neighbors(self, sensor_state):
        '''
        Get the neighbors of the given sensor state. Returns a list of
        transitions consistion of the behavior starting the transition, the
        state transitioning to, and the edge weight

        sensor_state: float list

        returns: (string * (float list) * float) list
        '''
        raise Exception('Not implemented')

    def save(self, filename):
        with open(filename, 'w') as f:
            pickle.dump(self.__dict__, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            self.__dict = pickle.load(f)

    def state_to_key(self, sensor_state):
        return ', '.join(map(str, map(abs, sensor_state))) if not isinstance(sensor_state, str) else sensor_state

    def key_to_state(self, key):
        return map(float, key.split(', ')) if ',' in key else key

    def visualize(self, filename, initial_sensor_state):
        # Construct the full graph
        next_node_id = 0
        visited = {}
        edges = []

        def traverse(sensor_state, next_node_id, visited, edges):
            '''
            Traverses the graph, constructing the nodes and edges
            '''
            key = self.state_to_key(sensor_state)

            if key in visited:
                return next_node_id

            visited[key] = next_node_id
            next_node_id += 1

            for behavior, neighbor_state, weight in self.neighbors(sensor_state):
                other_key = self.state_to_key(neighbor_state)

                edges.append( (key, other_key, behavior, weight) )
                next_node_id = traverse(neighbor_state, next_node_id, visited, edges)

            return next_node_id

        traverse(initial_sensor_state, 0, visited, edges) 

        # Output the graph in DOT format
        with open(filename, 'w') as f:
            def wrln(s, indent=1):
                f.write("\t"*indent + s + "\n")

            # Start the graph
            wrln('digraph G {', 0)

            # Output the node definitions
            for key in sorted(visited, key=visited.get):
                node_label = key
                node_id = visited[key]
                wrln('%d [label = "%s"];' % (node_id, node_label))

            wrln('')

            # Output the edges
            for key_a, key_b, behavior, weight in edges:
                node_a_id = visited[key_a]
                node_b_id = visited[key_b]
                wrln('%d -> %d [ label = "%s, %d" ];' % (node_a_id, node_b_id, behavior, weight))

            # End the graph
            wrln('}', 0)


class MarkovChainGraph(Graph):

    def __init__(self):
        self.states = {}

    def construct(self, sensor_states, behaviors):
        previous_state = sensor_states[0]
        for i in range(1, len(sensor_states)):
            current_state = sensor_states[i]
            behavior = behaviors[i-1]

            key = self.state_to_key(previous_state)
            if not key in self.states:
                self.states[key] = {}
            neighbors = self.states[key]

            if not behavior in neighbors:
                neighbors[behavior] = {}
            chain = neighbors[behavior]

            key = self.state_to_key(current_state)
            if not key in chain:
                chain[key] = 0
            chain[key] += 1

            previous_state = current_state

    def neighbors(self, sensor_state):
        edges = []

        key = self.state_to_key(sensor_state)
        if not key in self.states:
            return []
        neighbors = self.states[key]

        for behavior in neighbors:
            total = sum(count for state, count in neighbors[behavior].iteritems())
            for neighbor_state_str, count in neighbors[behavior].iteritems():
                neighbor_state = self.key_to_state(neighbor_state_str)
                weight = (total+1) - count
                edges.append( (behavior, neighbor_state, weight) )

        return edges


class ANNGraph(Graph):

    def __init__(self, round_output=False, training_callback=None):
        self.round_output = round_output
        self.training_callback = training_callback
        self.behaviors = ['explore', 'faceObject', 'tryGrab', 'release']

    def _behavior_to_list(self, behavior):
        items = []
        for b in self.behaviors:
            items.append( float(b == behavior) )
        return items

    def construct(self, sensor_states, behaviors):

        input_len = len(sensor_states[0])
        state_len = input_len + len(self._behavior_to_list(''))

        # Initialize the network
        self.net = FeedForwardNetwork()

        input_layer = SigmoidLayer(state_len)
        hidden_layer = SigmoidLayer( int(state_len * 1.5) )
        output_layer = SigmoidLayer(input_len)

        input_to_hidden = FullConnection(input_layer, hidden_layer)
        hidden_to_output = FullConnection(hidden_layer, output_layer)

        self.net.addInputModule( input_layer )
        self.net.addModule( hidden_layer )
        self.net.addOutputModule( output_layer )

        self.net.addConnection(input_to_hidden)
        self.net.addConnection(hidden_to_output)

        self.net.sortModules()

        # Build the data set
        ds = SupervisedDataSet(state_len, input_len)

        previous_state = sensor_states[0]
        for i in range(1, len(sensor_states) - 1):
            behavior = behaviors[i-1]
            current_state = sensor_states[i]

            a = tuple( previous_state + self._behavior_to_list(behavior) )
            b = tuple( current_state )

            ds.addSample(a, b)

        # Train the network
        trainer = BackpropTrainer(self.net, ds, learningrate=0.3)
        for i in range(1000):
            t1 = datetime.datetime.now()
            err = trainer.train()
            t2 = datetime.datetime.now()
            print '%d: %f (%s)' % (i, err, t2 - t1)
            if self.training_callback is not None:
                self.training_callback(i, self)

    def neighbors(self, sensor_state):
        # A neighbor exists for each behavior
        edges = []
        for behavior in self.behaviors:
            neighbor_state = self.net.activate( sensor_state + self._behavior_to_list(behavior) )
            if self.round_output:
                neighbor_state = map(round, neighbor_state)
            edges.append( (behavior, neighbor_state, 1) )
        return edges


# Application entry point
if __name__ == '__main__':
    print('Graph')
