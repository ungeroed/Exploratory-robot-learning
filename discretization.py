import random, math
from minisom import MiniSom
from scipy.cluster.vq import kmeans2
import numpy as np
from sys import maxint
from PIL import Image, ImageDraw
#from sklearn.manifold import MDS
import matplotlib.pyplot as plt

class Discretizer():

    def train(self, data):
        '''
        Train the discretizer on the raw data set

		data: (float list) list

		returns: None
        '''
        raise Exception('Not implemented')

    def discretize(self, data_point):
        '''
        Discretize the given sensor state

		data_point: float list

		returns: float list
        '''
        raise Exception('Not implemented')

    def visualize(self, filename, subset=None):
        '''
        Visualize the state of the discretizer.
        The visualization is stored in the given filename.
        If set subset index pair is given, only the dimensions indicated by the
        index range (low and high inclusive) are visualized.

		filename: string
        subset: int * int

		returns: None
        '''
        raise Exception('Not implemented')

    def norm_data_vector(self, data_point):
        '''
        Computes the normalized length of the given data point vector ( [0, 1] )

        data_point: float list

        returns: float
        '''
        max_length = np.linalg.norm( np.array( map(lambda x: 1.0, data_point) ) )
        actual_length = np.linalg.norm( np.array(data_point) )
        return actual_length / max_length

    def data_vector_difference(self, data_point_a, data_point_b):
        '''
        Computes the normalized length of the difference vector between the two
        given data point vectors ( [0, 1] )

        data_point_a: float list
        data_point_b: float list

        returns: float
        '''
        diff_vector = np.array(data_point_a) - np.array(data_point_b)
        return self.norm_data_vector(diff_vector)


class KMeansDiscretizer(Discretizer):
    def __init__(self, k):
        self.k = k

    def train(self, data):
        self.centroids, _ = kmeans2(data, self.k)

    def discretize(self, data_point):
        mincen = []
        mindist = maxint
        for c in self.centroids:
            dist = np.linalg.norm(data_point-c)
            if dist < mindist:
                mincen = c
                mindist = dist
        return mincen

    #def visualize(self, filename, subset=None):
        ## Check if only a subset is to be visualized
        #centroids = self.centroids
        #if subset is not None:
        #    centroids = [ x[subset[0]:subset[1]+1] for x in centroids ]

        ## If more than two dimensions are to be visualized, use
        ## multidimensional scaling
        #if len(centroids[0]) > 2:
        #    multi_dim_scaling = MDS()
        #    centroid_positions = multi_dim_scaling.fit(self.centroids).embedding_
        ## If two dimensions are to be visualized, plot the dimensions directly
        #elif len(centroids[0]) == 2:
        #    centroid_positions = centroids
        ## If a single dimensions is to be visualized, plot it on a line 
        #else:
        #    centroid_positions = np.array([ np.array([x[0], 0.5]) for x in centroids ])

        #x_pos = centroid_positions[:,0]
        #y_pos = centroid_positions[:,1]

        #x_min = math.floor( min(x_pos) )
        #x_max = math.ceil( max(x_pos) )
        #y_min = math.floor( min(y_pos) )
        #y_max = math.ceil( max(y_pos) )

        #fig = plt.figure()
        #plot = fig.add_subplot(1, 1, 1)
        #plot.plot(x_pos, y_pos, 'ro')
        #plot.axis([x_min, x_max, y_min, y_max])
        #for i in range( len(centroids) ):
        #    label = '\n'.join( map(lambda x: '%.2f' % x, centroids[i]) )
        #    label_x = centroid_positions[i][0] + 0.015
        #    label_y = centroid_positions[i][1] - 0.01 - (0.045 * (len(centroids[i])-1))

        #    plot.annotate(label, (label_x, label_y))
        #fig.savefig(filename)

class SOMDiscretizer(Discretizer):

    def __init__(self, width=4, height=4, sigma=0.3, learning_rate=0.5):
        self.width = width
        self.height = height
        self.sigma = sigma
        self.learning_rate = learning_rate

    def train(self, data):
        self.som = MiniSom(self.width, self.height, len(data[0]), sigma=self.sigma, learning_rate=self.learning_rate)
        self.som.train_random(data, 1000000)

    def discretize(self, data_point):
        x, y = self.som.winner(data_point)
        return self.som.weights[x,y]

    def visualize(self, filename, subset=None):
        box_side = 150
        border = 30

        text_height = 10
        text_offset_x = 60
        text_offset_y = 30

        w = (self.width * box_side) + ((self.width-1) * border)
        h = (self.height * box_side) + ((self.height-1) * border)
        img = Image.new('RGB', (w, h))

        draw = ImageDraw.Draw(img)
        for i in range(self.width):
            for j in range(self.height):
                offset = np.array([
                    i*(box_side + border), j*(box_side + border),
                    (i+1)*(box_side + border), (j+1)*(box_side + border)
                ])

                def coords(arr, offset):
                    a = arr + offset
                    return [ (a[0], a[1]), (a[2], a[3]) ]

                def dimension_subset(vector, subset):
                    if subset is not None:
                        return vector[subset[0]:subset[1]+1]
                    return vector

                # Draw the prototype vector box
                box_position = coords(np.array([ 
                    0, 0,
                    box_side, box_side
                ]), offset)

                prototype_vector = dimension_subset(self.som.weights[i, j], subset)
                fill = int(self.norm_data_vector(prototype_vector) * 200) + 55

                draw.rectangle(box_position, fill=(0, fill, 0))

                # Write the prototype vector as text
                text_position = box_position[0]
                line_no = 0
                for value in prototype_vector:
                    rounded_value = round(value * 100) / 100
                    base_x, base_y = box_position[0]
                    text_position = (base_x + text_offset_x, base_y + text_offset_y + text_height*line_no)
                    draw.text(text_position, str(rounded_value))
                    line_no += 1

                right_fill, bottom_fill, diagonal_fill = 0, 0, 0

                # Draw right border of U-matrix
                if i != self.width - 1:
                    right_border_position = coords(np.array([ 
                        box_side+1, 0,
                        box_side+1+border, box_side
                    ]), offset)

                    prototype_vector_a = dimension_subset(self.som.weights[i, j], subset)
                    prototype_vector_b = dimension_subset(self.som.weights[i+1, j], subset)
                    right_fill = 255 - int(self.data_vector_difference(prototype_vector_a, prototype_vector_b) * 255)

                    draw.rectangle(right_border_position, fill=(right_fill, right_fill, right_fill))

                # Draw bottom border of U-matrix
                if j != self.height - 1:
                    bottom_border_position = coords(np.array([
                        0, box_side+1,
                        box_side, box_side+1+border
                    ]), offset)

                    prototype_vector_a = dimension_subset(self.som.weights[i, j], subset)
                    prototype_vector_b = dimension_subset(self.som.weights[i, j+1], subset)
                    bottom_fill = 255 - int(self.data_vector_difference(prototype_vector_a, prototype_vector_b) * 255)

                    draw.rectangle(bottom_border_position, fill=(bottom_fill, bottom_fill, bottom_fill))

                # Draw diagonal border of U-matrix
                if i != self.width - 1 and j != self.height - 1:
                    diagonal_border_position = coords(np.array([
                        box_side+1, box_side+1,
                        box_side+1+border, box_side+1+border
                    ]), offset)

                    prototype_vector_a = dimension_subset(self.som.weights[i, j], subset)
                    prototype_vector_b = dimension_subset(self.som.weights[i+1, j+1], subset)
                    diagonal_fill = 255 - int(self.data_vector_difference(prototype_vector_a, prototype_vector_b) * 255)

                    draw.rectangle(diagonal_border_position, fill=(diagonal_fill, diagonal_fill, diagonal_fill))

        img.save(filename)


class NoDiscretizer(Discretizer):

    def train(self, data):
        pass

    def discretize(self, data_point):
        return data_point


class RoundingDiscretizer(Discretizer):

    def train(self, data):
        pass

    def discretize(self, data_point):
        return map(round, data_point)


class SimplifyingDiscretizer(Discretizer):

    def train(self, data):
        pass

    def discretize(self, data_point):
        front_sensors = data_point[:5]
        ground_sensors = data_point[7]
        lasso = data_point[8]

        close_to_object = len( filter(lambda x: x > 0, front_sensors) ) > 0
        facing_object = close_to_object and max(front_sensors) == front_sensors[2]
        on_color = ground_sensors > 0.7

        return map(float, [close_to_object, facing_object, lasso])


# Application entry point
if __name__ == '__main__':
    data = [ [random.random() for x in range(9)] for x in range(1000)]

    #discretizer = SOMDiscretizer()
    discretizer = SimplifyingDiscretizer()
    discretizer.train(data)

    data_point = [random.random() for x in range(9)]
    print(data_point)
    print(discretizer.discretize(data_point))
