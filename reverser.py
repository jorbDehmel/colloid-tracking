from matplotlib import pyplot as plt

'''
Jordan Dehmel, 2023
jdehmel@outlook.com

For correcting the relative straight
line speed values such that some are
negative.

Proposed process 1:
- After a given frequency, just multiply all values by -1

Proposed process 1.5:
- Set the mean straight line speed at a given frequency to zero
- Graph / save values RELATIVE to this value, with everything
  after automatically multiplied by -1

Proposed process 2:
- Manually create .csv file for turning point frequencies
- Set the mean straight line speed at this point to zero
- Graph / save values RELATIVE to this value, with everything
  after automatically multiplied by -1

'''


def get_relative(data: [float], turning_point_index: int) -> [float]:
    out: [float] = [item - data[turning_point_index] for item in data]
    out[turning_point_index] = 0.0

    for i in range(turning_point_index + 1, len(data)):
        out[i] *= -1.0

    return out


def graph_relative(data: [float],
                   turning_point_label: str,
                   labels: [str],
                   title: str = 'title',
                   save_path: str = 'relative_graph.png',
                   axis_labels: (str) = ('x', 'y'),
                   do_erase: bool = True,
                   do_save: bool = True,
                   label: str = ''
                   ) -> [float]:

    turning_point_index: int = 0
    while turning_point_index < len(labels) and float(labels[turning_point_index + 1]) <= float(turning_point_label):
        turning_point_index += 1

    if do_erase:
        plt.clf()
        plt.title(title + ' relative to ' + labels[turning_point_index])
        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

    plt.plot(labels, get_relative(data, turning_point_index), label=label)

    zeros: [float] = [0.0 for _ in data]
    plt.plot(zeros)

    if do_save:
        plt.savefig(save_path)

    pass
