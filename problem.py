from graph import Graph
class Problem():

    def required_state_sequence_length(self):
        '''
                Get the needed number of sensor states needed to compute the evalute
                and goal functions

                returns: int
        '''
        raise Exception('Not implemented')

    def evaluate(self, sensor_states):
        '''
                    Compute the value of the given sequence of sensor states

                    sensor_states: (float list) list

                    returns: float
        '''
        raise Exception('Not implemented')

    def goal(self, sensor_states):
        '''
                Determine if the given sequence of sensor states results in the problem being solved

                sensor_states: (float list) list

                returns: bool
        '''
        raise Exception('Not implemented')

class FindStateProblem(Problem):

    def __init__(self, goal_state):
        self.goal_state = goal_state

    def required_state_sequence_length(self):
        return 1

    def evaluate(self, sensor_states):
        graph = Graph()
        if self.goal_state == graph.state_to_key(sensor_states[0]):
            return 1

        return 0

    def goal(self, sensor_states):
        return self.evaluate(sensor_states) == 1

class FindUnexploredStateProblem(Problem):

    def __init__(self, state_behaviors,  min_count):
        self.state_behaviors = state_behaviors
        self.min_count = min_count  

    def required_state_sequence_length(self):
        return 1

    def evaluate(self, sensor_states):
        graph = Graph()
        sensor_count = self.state_behaviors[graph.state_to_key(sensor_states[0])]["count"]
        if abs(self.min_count - sensor_count) < 10:
            return 1

        return 0

    def goal(self, sensor_states):
        return self.evaluate(sensor_states) == 1


class BallPickupProblem(Problem):

    def required_state_sequence_length(self):
        return 1

    def evaluate(self, sensor_states):
        if sensor_states[0][-1] > 0.5:
            return 1
        return 0

    def goal(self, sensor_states):
        return self.evaluate(sensor_states) == 1


# Application entry point
if __name__ == '__main__':
    print('Problem')
