import random
from sys import maxint

minint = -maxint - 1

class Search():

    def choose_behavior(self, sensor_state_history, graph, problem):
        '''
        Choose the next behavior by searching the given graph from the start
        state defined as the last state in the given sensor state history

        sensor_state_history: (float list) list
        graph: Graph
        problem: Problem

        returns: string
        '''
        raise Exception('Not implemented')


class DepthFirstSearch(Search):

    def choose_behavior(self, sensor_state_history, graph, problem):

        # Define an auxiliary function for recursive graph traversal
        def traverse(states, weight, path, limit):
            if limit == 0:
                return []


            # Get the subsequence of states used for evaluation
            n = problem.required_state_sequence_length()
            eval_seq = states[-n:]

            # Initiate the computed paths
            paths = []
            
            # Evaluate the current path
            if len(path) > 0:
                e = problem.evaluate(eval_seq)
                paths.append( ( e, weight, path ) )

            # Search the neighborhood recursively
            current_state = states[-1]
            for b, s, w in graph.neighbors(current_state):
                    paths.extend( traverse(states + [s], weight + w, path + [b], limit - 1) )
            
            return paths
        
        paths = traverse(sensor_state_history, 0, [], 4)

        if len(paths) == 0:
            return ("explore", minint)

        best_eval = max( map(lambda x: x[0], paths) )
        best_paths = filter(lambda x: x[0] == best_eval, paths)
        best_weight = min( map(lambda x: x[1], best_paths) )
        best_paths = filter(lambda x: x[1] == best_weight, best_paths)
        best_path = random.choice(best_paths)
        print("DFS Paths:", paths)
        print("DFS Best Path:", best_path)

        return (best_path[2][0], best_eval)


class RandomWalkSearch(Search):

    def __init__(self, walks_per_behavior=5, search_depth=30):
        self.walks_per_behavior = walks_per_behavior
        self.search_depth = search_depth
        self.behaviors = ['explore', 'faceObject', 'tryGrab', 'release']

    def choose_behavior(self, sensor_state_history, graph, problem):

        # Define an auxiliary function for recursive graph traversal
        def traverse(states, weight, path, limit):
            if limit == 0:
                return minint, maxint

            # Get the subsequence of states used for evaluation
            n = problem.required_state_sequence_length()
            eval_seq = states[-n:]
            

            # Choose a neighbor for recursive search
            current_state = states[-1]
            neighbors = graph.neighbors(current_state)

            if len(neighbors) == 0:
                return minint, maxint

            choice = random.choice(neighbors)

            b, s, w = choice
            best_e, best_w = traverse(states + [s], weight + w, path + [b], limit - 1)

            # Evaluate the current path
            if len(path) > 0:
                e = problem.evaluate(eval_seq)
                current_path = ( e, weight, path )
                if e > best_e or (e == best_e and w < best_w):
                    return e, w
                else:
                    return best_e, best_w
            else:
                return best_e, best_w
            
        # Do the random walks
        best_behavior = "explore"
        best_e = minint
        best_w = maxint
        for behavior in self.behaviors:
            for i in range(self.walks_per_behavior):
                e, w = traverse(sensor_state_history, 0, [], self.search_depth)
                if e > best_e or (e == best_e and w < best_w):
                    best_behavior = behavior
                    best_e, best_w = e, w

        return (best_behavior, best_e)
		

# Application entry point
if __name__ == '__main__':
    print('Search')
