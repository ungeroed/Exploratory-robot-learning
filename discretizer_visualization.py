import sys, os, shutil # Third party imports
import dataloader, normalization, discretization # Local imports

def reset_dir(dirname):
    try:
        shutil.rmtree(dirname)
    except:
        pass
    os.mkdir(dirname)

def visualize(discretizer, dirname):
    reset_dir(dirname)

    discretizer.visualize("%s/full.png" % dirname)
    for i in range( len(norm_sensor_states[0]) ):
        discretizer.visualize("%s/%d.png" % (dirname, i), (i, i))

if __name__ == '__main__':
    output_dir = 'discretizer_visualizations'
    reset_dir(output_dir)

    sensor_states, behaviors = dataloader.load('test.out')
    norm_sensor_states = map(normalization.normalize, sensor_states)

    for data_length in [300, 1000, 10000]:
        data = norm_sensor_states[:data_length]

        for i in range(2, 26):
            dirname = '%s/kmeans_%d_%d' % (output_dir, i, data_length)

            discretizer = discretization.KMeansDiscretizer(i)
            discretizer.train(data)

            visualize(discretizer, dirname)

        for i in range(2, 6):
            dirname = '%s/som_%dx%d_%d' % (output_dir, i, i, data_length)

            discretizer = discretization.SOMDiscretizer(i, i)
            discretizer.train(data)

            visualize(discretizer, dirname)
