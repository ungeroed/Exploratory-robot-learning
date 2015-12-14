import sys, os, shutil, subprocess # Third party imports
import dataloader, normalization, discretization, graph # Local imports

def reset_dir(dirname):
    try:
        shutil.rmtree(dirname)
    except:
        pass
    os.mkdir(dirname)

def visualize(grph, name, output_dir, states, behaviors):
    grph.construct(states, behaviors)

    filename = '%s/%s_%d' % (output_dir, name, len(states))
    grph.visualize(filename+'.dot', disc_sensor_states[0])

    subprocess.call(['dot', '-Tpng', '-o', filename+'.png', filename+'.dot'])

if __name__ == '__main__':
    output_dir = 'graph_visualizations'
    reset_dir(output_dir)

    discretizer = discretization.SimplifyingDiscretizer()

    sensor_states, behaviors = dataloader.load('test.out')
    norm_sensor_states = map(normalization.normalize, sensor_states)
    disc_sensor_states = map(discretizer.discretize, norm_sensor_states)

    for data_length in [10, 50, 100, 300, 1000, 10000]:
        s = disc_sensor_states[:data_length]
        b = behaviors[:data_length-1]

        ann_trace_output_dir = '%s/ann_trace_%d' % (output_dir, data_length)
        os.mkdir(ann_trace_output_dir)
        def ann_callback(i, grph):
            filename = '%s/%06d' % (ann_trace_output_dir, i)
            grph.visualize(filename+'.dot', s[0])
            subprocess.call(['dot', '-Tpng', '-o', filename+'.png', filename+'.dot'])
            grph.save(filename+'.pickle')

        visualize(graph.MarkovChainGraph(), "markov", output_dir, s, b)
        visualize(graph.ANNGraph(round_output=True, training_callback=ann_callback), "ann", output_dir, s, b)
