from matplotlib import pyplot as plt

'''
Utilities for plotting relative straight line speed graphs

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

'''
Revision 9/21:

We want to insert a datapoint where velocity = 0 at the
midpoint of the crossover range, then simply multiply by
-1 after that. NOT relative anymore.
'''


def get_relative_old(data: [float], turning_point_index: int) -> [float]:
    out: [float] = [item - data[turning_point_index] for item in data]
    out[turning_point_index] = 0.0

    for i in range(turning_point_index + 1, len(data)):
        out[i] *= -1.0

    return out


def graph_relative_old(data: [float],
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

    return


# Inserts a zero such that turning_point_index points to it,
# and multiplies everything afterwards by 1.
def get_relative(data: [float], turning_point_index: int) -> [float]:
    out: [float] = []

    for i in range(0, turning_point_index):
        out.append(data[i])

    out.append(0)

    for i in range(turning_point_index, len(data)):
        out.append(-1.0 * data[i])

    return out


def graph_multiple_relative(data: [[float]],
                            turning_points: [str],
                            labels: [[str]],
                            save_paths: [str],
                            axis_labels: (str),
                            line_labels: [str],
                            subtitle: str = None,
                            errors: [[float]] = None) -> None:

    # Create a complete list of all the labels
    # This keeps weird labels from being pushed to the end of the graph
    complete_labels: [str] = []

    for label_list in labels:
        for label in label_list:
            if label not in complete_labels:
                complete_labels.append(label)

    if turning_points is not None:
        for turning_point in turning_points:
            if turning_point not in complete_labels:
                complete_labels.append(turning_point)

    # Sort them so they are in numerical order on the x axis
    complete_labels.sort(key=lambda x: float(x))

    # We only need to graph one line out of our many lines
    # for all the complete_labels to appear in the correct
    # order, so we will just do the zeros line in it.
    zeros: [float] = [0.0 for _ in complete_labels]

    plt.clf()
    plt.xticks(rotation=-45)
    plt.plot(complete_labels, zeros)

    plt.title(axis_labels[1] + ' by ' + axis_labels[0] +
              ', Relative to Crossover Point.' + ('\n' + subtitle if subtitle is not None else ''))

    colors: [str] = ['r', 'g', 'b', 'c', 'y', 'm', 'k',
                     'tab:orange', 'tab:brown', 'tab:gray', 'pink', 'indigo']

    for i, dataset in enumerate(data):
        if turning_points is not None:
            turning_point_index: int = 0
            while turning_point_index < len(labels[i]) and float(labels[i][turning_point_index]) <= float(turning_points[i]):
                turning_point_index += 1

            relative_data: [float] = get_relative(dataset, turning_point_index)

            relative_labels: [str] = labels[i][:turning_point_index] + \
                [turning_points[i]] + labels[i][turning_point_index:]

            relative_errors: [float] = errors[i][:turning_point_index] + \
                [0.0] + errors[i][turning_point_index:]
        else:
            relative_data: [float] = dataset[:]
            relative_labels: [str] = labels[i][:]
            relative_errors: [float] = [
                err if err is not None else 0.0 for err in errors[i]]

        plt.errorbar(relative_labels, relative_data,
                     relative_errors, color=colors[i % len(colors)],
                     capsize=5, alpha=0.5)

        plt.plot(relative_labels, relative_data,
                 label=line_labels[i], color=colors[i % len(colors)])

    plt.xlabel(axis_labels[0])
    plt.ylabel(axis_labels[1])

    plt.legend()

    for path in save_paths:
        if path is not None:
            plt.savefig(path)

    return


def graph_multiple_relative_individually(data: [[float]],
                                         turning_points: [str],
                                         labels: [[str]],
                                         save_paths: [str],
                                         axis_labels: (str),
                                         line_labels: [str],
                                         subtitle: str = None,
                                         errors: [[float]] = None) -> None:

    # Create a complete list of all the labels
    # This keeps weird labels from being pushed to the end of the graph
    complete_labels: [str] = []

    for label_list in labels:
        for label in label_list:
            if label not in complete_labels:
                complete_labels.append(label)

    if turning_points is not None:
        for turning_point in turning_points:
            if turning_point not in complete_labels:
                complete_labels.append(turning_point)

    # Sort them so they are in numerical order on the x axis
    complete_labels.sort(key=lambda x: float(x))

    # We only need to graph one line out of our many lines
    # for all the complete_labels to appear in the correct
    # order, so we will just do the zeros line in it.
    zeros: [float] = [0.0 for _ in complete_labels]

    colors: [str] = ['r', 'g', 'b', 'c', 'y', 'm', 'k',
                     'tab:orange', 'tab:brown', 'tab:gray', 'pink', 'indigo']

    for i, dataset in enumerate(data):
        plt.clf()
        plt.xticks(rotation=-45)
        plt.rcParams['figure.dpi'] = 500
        plt.rc('font', size=6)
        plt.plot(complete_labels, zeros)

        plt.title(axis_labels[1] + ' by ' + axis_labels[0] +
                  ', Relative to Crossover Point.' + ('\n' + subtitle if subtitle is not None else ''))

        if turning_points is not None:
            turning_point_index: int = 0
            while turning_point_index < len(labels[i]) and float(labels[i][turning_point_index]) <= float(turning_points[i]):
                turning_point_index += 1

            relative_data: [float] = get_relative(dataset, turning_point_index)

            relative_labels: [str] = labels[i][:turning_point_index] + \
                [turning_points[i]] + labels[i][turning_point_index:]

            relative_errors: [float] = errors[i][:turning_point_index] + \
                [0.0] + errors[i][turning_point_index:]
            relative_errors = [
                err if err is not None else 0.0 for err in relative_errors]

        else:
            relative_data: [float] = dataset[:]
            relative_labels: [str] = labels[i][:]
            relative_errors: [float] = [
                err if err is not None else 0.0 for err in errors[i]]

        plt.errorbar(relative_labels, relative_data,
                     relative_errors, color=colors[i % len(colors)],
                     capsize=5, alpha=0.5)

        plt.plot(relative_labels, relative_data,
                 label=line_labels[i], color=colors[i % len(colors)])

        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

        plt.legend()

        for path in save_paths:
            if path is not None:
                plt.savefig(path[:-4] + str(i))

    return


def graph_relative(data_in: [float],
                   turning_point_label: str,
                   labels: [str],
                   title: str = 'title',
                   save_path: str = 'relative_graph.png',
                   axis_labels: (str) = ('x', 'y'),
                   do_erase: bool = True,
                   do_save: bool = True,
                   label: str = ''
                   ) -> [float]:

    # Find location of turning_point_label
    i: int = 0
    while i < len(labels) and float(labels[i + 1]) <= float(turning_point_label):
        i += 1

    real_data: [float] = get_relative(data_in, i)
    real_labels: [str] = labels[:i] + [turning_point_label] + labels[i:]

    plt.xticks(rotation=-45)

    if do_erase:
        plt.clf()
        plt.rcParams['figure.dpi'] = 500
        plt.rc('font', size=6)
        plt.title(title + ' relative to ' + labels[i])
        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

    plt.plot(real_labels, real_data, label=label)

    zeros: [float] = [0.0 for _ in real_data]
    plt.plot(zeros)

    if do_save:
        plt.savefig(save_path)

    return
