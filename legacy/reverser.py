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

Revision 9/21:

We want to insert a datapoint where velocity = 0 at the
midpoint of the crossover range, then simply multiply by
-1 after that. NOT relative anymore.
'''


from typing import List, Union, Tuple
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd


def get_relative_old(data: List[float], turning_point_index: int) -> List[float]:
    '''
    Invert all data which are beyond the turning point index
    '''

    out: List[float] = [item - data[turning_point_index] for item in data]
    out[turning_point_index] = 0.0

    for i in range(turning_point_index + 1, len(data)):
        out[i] *= -1.0

    return out


def graph_relative_old(data: List[float],
                       turning_point_label: str,
                       labels: List[str],
                       title: str = 'title',
                       save_path: str = 'relative_graph.png',
                       axis_labels: Tuple[str, str] = ('x', 'y'),
                       do_erase: bool = True,
                       do_save: bool = True,
                       label: str = ''
                       ) -> None:
    '''
    An old version of the graph_relative function.
    Mostly outdated now, but the sunk cost fallacy
    says that I can't delete it.
    '''

    turning_point_index: int = 0
    while (turning_point_index < len(labels)
            and float(labels[turning_point_index + 1]) <= float(turning_point_label)):
        turning_point_index += 1

    if do_erase:
        plt.clf()
        plt.title(title + ' relative to ' + labels[turning_point_index])
        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

    plt.plot(labels, get_relative(data, turning_point_index), label=label)

    zeros: List[float] = [0.0 for _ in data]
    plt.plot(zeros)

    if do_save:
        plt.savefig(save_path)


def get_relative(data: List[float], turning_point_index: int) -> List[float]:
    '''
    Inserts a zero such that turning_point_index points to it,
    and multiplies everything afterwards by 1.
    '''

    out: List[float] = []

    for i in range(0, turning_point_index):
        out.append(data[i])

    out.append(0)

    for i in range(turning_point_index, len(data)):
        out.append(-1.0 * data[i])

    return out


def save_multiple_relative(data: List[List[float]],
                           turning_points: List[str],
                           labels: List[List[str]],
                           save_paths: List[str],
                           line_labels: List[str],
                           errors: Union[List[List[float]], None] = None) -> None:
    '''
    Like graph_multiple_relative,  but saves to .csv instead of .png.
    Save multiple sets of data, flipping velocities
    after the turning frequency.
    '''

    # Create a complete List of all the labels
    # This keeps weird labels from being pushed to the end of the graph
    complete_labels: List[str] = []

    for label_list in labels:
        for label in label_list:
            if label not in complete_labels:
                complete_labels.append(label)

    for turning_point in turning_points:
        if turning_point not in complete_labels:
            complete_labels.append(turning_point)

    # Sort them so they are in numerical order on the x axis
    complete_labels.sort(key=float)

    # DataFrame width should be twice the length of complete_labels + len(extra_columns)
    # DataFrame height should be the number of entries in data

    # Columns will be [complete labels] + [complete labels _STD] + extra_columns
    # Rows will be line_labels

    extra_columns: List[str] = ['INVERSION_FREQ_HZ']

    array: List[List[float]] = [[] for _ in data]

    for i, dataset in enumerate(data):
        turning_point_index: int = 0
        while (turning_point_index < len(labels[i])
                and float(labels[i][turning_point_index]) <= float(turning_points[i])):
            turning_point_index += 1

        relative_data: List[float] = get_relative(dataset, turning_point_index)

        relative_labels: List[str] = labels[i][:turning_point_index] + \
            [turning_points[i]] + labels[i][turning_point_index:]

        relative_errors: List[float] = errors[i][:turning_point_index] + \
            [0.0] + errors[i][turning_point_index:]

        complete_data: List[float] = []
        complete_errors: List[float] = []
        for item in complete_labels:
            if item in relative_labels:
                j = relative_labels.index(item)

                complete_data.append(relative_data[j])
                complete_errors.append(relative_errors[j])

            else:
                complete_data.append(None)
                complete_errors.append(None)

        extra: List[float] = [0.0 for _ in extra_columns]

        # Extra data stuff here
        extra[0] = turning_points[i]

        array[i] = complete_data + complete_errors + extra

    # Array to DF
    columns: List[str] = [str(f) + 'HZ_SLS' for f in complete_labels] + \
        [str(f) + 'HZ_SLS_STD' for f in complete_labels] + extra_columns
    frame: pd.DataFrame = pd.DataFrame(array,
                                       index=line_labels,
                                       columns=columns)

    for path in save_paths:
        frame.to_csv(path)

    return


def graph_multiple_relative(data: [List[float]],
                            turning_points: List[str],
                            labels: [List[str]],
                            save_paths: List[str],
                            axis_labels: (str),
                            line_labels: List[str],
                            subtitle: str = None,
                            errors: [List[float]] = None) -> None:
    '''
    Graph multiple sets, flipping velocities after the
    turning point.
    '''

    # Create a complete List of all the labels
    # This keeps weird labels from being pushed to the end of the graph
    complete_labels: List[str] = []

    for label_list in labels:
        for label in label_list:
            if label not in complete_labels:
                complete_labels.append(label)

    if turning_points is not None:
        for turning_point in turning_points:
            if turning_point not in complete_labels:
                complete_labels.append(turning_point)

    # Sort them so they are in numerical order on the x axis
    complete_labels.sort(key=float)

    # We only need to graph one line out of our many lines
    # for all the complete_labels to appear in the correct
    # order, so we will just do the zeros line in it.
    zeros: List[float] = [0.0 for _ in complete_labels]

    plt.clf()

    plt.xticks(rotation=-45)
    plt.rc('font', size=8)

    plt.figure(figsize=(10, 10), dpi=200)
    plt.plot(complete_labels, zeros)

    plt.title(axis_labels[1] + ' by ' + axis_labels[0] +
              ', Relative to Crossover Point.' + ('\n' + subtitle if subtitle is not None else ''))

    colors: List[str] = ['r', 'g', 'b', 'c', 'y', 'm', 'k',
                         'tab:orange', 'tab:brown', 'tab:gray', 'pink', 'indigo']

    for i, dataset in enumerate(data):
        if turning_points is not None:
            turning_point_index: int = 0
            while (turning_point_index < len(labels[i]) and
                   float(labels[i][turning_point_index]) <= float(turning_points[i])):
                turning_point_index += 1

            relative_data: List[float] = get_relative(
                dataset, turning_point_index)

            relative_labels: List[str] = labels[i][:turning_point_index] + \
                [turning_points[i]] + labels[i][turning_point_index:]

            if errors is not None:
                relative_errors: List[float] = errors[i][:turning_point_index] + \
                    [0.0] + errors[i][turning_point_index:]
            else:
                relative_errors: List[float] = None

        else:
            relative_data: List[float] = dataset[:]
            relative_labels: List[str] = labels[i][:]

            if errors is not None:
                relative_errors: List[float] = [
                    err if err is not None else 0.0 for err in errors[i]]
            else:
                relative_errors: List[float] = None

        if relative_errors is not None:
            plt.errorbar(relative_labels, relative_data,
                         relative_errors, color=colors[i % len(colors)],
                         capsize=5, alpha=0.5)

        plt.plot(relative_labels,
                 relative_data,
                 label=line_labels[i % len(line_labels)],
                 color=colors[i % len(colors)])

    plt.xlabel(axis_labels[0])
    plt.ylabel(axis_labels[1])

    lgd = plt.legend(bbox_to_anchor=(1.1, 1.05))

    for path in save_paths:
        if path is not None:
            plt.savefig(path, bbox_extra_artists=(lgd,), bbox_inches='tight')

    plt.close()


def graph_multiple_relative_individually(data: List[List[float]],
                                         turning_points: List[str],
                                         labels: List[List[str]],
                                         save_paths: List[str],
                                         axis_labels: Tuple[str],
                                         line_labels: List[str],
                                         subtitle: str = None,
                                         errors: List[List[float]] = None) -> None:
    '''
    IDK honestly it's been a while
    '''

    # Create a complete List of all the labels
    # This keeps weird labels from being pushed to the end of the graph
    complete_labels: List[str] = []

    for label_list in labels:
        for label in label_list:
            if label not in complete_labels:
                complete_labels.append(label)

    if turning_points is not None:
        for turning_point in turning_points:
            if turning_point not in complete_labels:
                complete_labels.append(turning_point)

    # Sort them so they are in numerical order on the x axis
    complete_labels.sort(key=float)

    # We only need to graph one line out of our many lines
    # for all the complete_labels to appear in the correct
    # order, so we will just do the zeros line in it.
    zeros: List[float] = [0.0 for _ in complete_labels]

    colors: List[str] = ['r', 'g', 'b', 'c', 'y', 'm', 'k',
                         'tab:orange', 'tab:brown', 'tab:gray', 'pink', 'indigo']

    for i, dataset in enumerate(data):
        plt.clf()
        plt.xticks(rotation=-45)
        plt.rcParams['figure.dpi'] = 500
        plt.rc('font', size=6)
        plt.plot(complete_labels, zeros)

        plt.title(axis_labels[1] + ' by ' + axis_labels[0]
                  + ', Relative to Crossover Point.'
                  + ('\n' + subtitle if subtitle is not None else ''))

        if turning_points is not None:
            turning_point_index: int = 0
            while (turning_point_index < len(labels[i]) and
                    float(labels[i][turning_point_index]) <= float(turning_points[i])):
                turning_point_index += 1

            relative_data: List[float] = get_relative(
                dataset, turning_point_index)

            relative_labels: List[str] = labels[i][:turning_point_index] + \
                [turning_points[i]] + labels[i][turning_point_index:]

            relative_errors: List[float] = errors[i][:turning_point_index] + \
                [0.0] + errors[i][turning_point_index:]
            relative_errors = [
                err if err is not None else 0.0 for err in relative_errors]

        else:
            relative_data: List[float] = dataset[:]
            relative_labels: List[str] = labels[i][:]
            relative_errors: List[float] = [
                err if err is not None else 0.0 for err in errors[i]]

        plt.errorbar(relative_labels, relative_data,
                     relative_errors, color=colors[i % len(colors)],
                     capsize=5, alpha=0.5)

        plt.plot(relative_labels, relative_data,
                 label=line_labels[i], color=colors[i % len(colors)])

        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

        lgd = plt.legend(bbox_to_anchor=(1.1, 1.05))

        for path in save_paths:
            if path is not None:
                plt.savefig(path[:-4] + str(i),
                            bbox_extra_artists=(lgd,), bbox_inches='tight')

    return


def graph_relative(data_in: List[float],
                   turning_point_label: str,
                   labels: List[str],
                   title: str = 'title',
                   save_path: str = 'relative_graph.png',
                   axis_labels: (str) = ('x', 'y'),
                   do_erase: bool = True,
                   do_save: bool = True,
                   label: str = ''
                   ) -> List[float]:
    '''
    Graph frequencies, flipping velocities after the turning
    point.
    '''

    # Find location of turning_point_label
    i: int = 0
    while i + 1 < len(labels) and float(labels[i + 1]) <= float(turning_point_label):
        i += 1

    real_data: List[float] = get_relative(data_in, i)
    real_labels: List[str] = labels[:i] + [turning_point_label] + labels[i:]

    if do_erase:
        plt.clf()
        plt.xticks(rotation=-45)
        plt.rcParams['figure.dpi'] = 500
        plt.rc('font', size=6)
        plt.title(title + ' relative to ' + labels[i])
        plt.xlabel(axis_labels[0])
        plt.ylabel(axis_labels[1])

    real_labels.sort(key=float)

    zeros: List[float] = [0.0 for _ in real_data]
    plt.plot(real_labels, zeros)

    plt.plot(real_labels, real_data, label=label)

    if do_save:
        plt.savefig(save_path)


def display_kept_lost_histogram(pre: pd.DataFrame, post: pd.DataFrame, name: str,
                                brownian_speed_threshold: float = None) -> None:
    '''
    Create, show, and save a histogram comparing the pre- and
    post-filtering data.
    :param pre: The full Pandas DataFrame before any filtering
    :param post: The output Pandas DataFrame after all filtering
    :param name: The input filename
    :return: None
    '''

    # Before
    plt.clf()
    plt.hist([float(row[1]['MEAN_STRAIGHT_LINE_SPEED'])
              for row in pre.iterrows()], bins=30, color='r', label='PRE')

    m = np.mean([float(row[1]['MEAN_STRAIGHT_LINE_SPEED'])
                 for row in pre.iterrows()])
    s = np.std([float(row[1]['MEAN_STRAIGHT_LINE_SPEED'])
                for row in pre.iterrows()])
    plt.hlines([m - s, m, m + s], 0, 5, colors=['r'])

    # After
    plt.hist([float(row[1]['MEAN_STRAIGHT_LINE_SPEED'])
              for row in post.iterrows()], bins=30, alpha=0.5, color='b', label='POST')
    plt.title('Pre V. Post Filter SLS w/ Means\n' + name)

    m = np.mean([float(row[1]['MEAN_STRAIGHT_LINE_SPEED'])
                 for row in post.iterrows()])
    s = np.std([float(row[1]['MEAN_STRAIGHT_LINE_SPEED'])
                for row in post.iterrows()])
    plt.vlines([m - s, m, m + s], 0, 5, colors=['b'])

    if brownian_speed_threshold is not None:
        plt.vlines([brownian_speed_threshold], 0, 10, colors=['black'])

    lgd = plt.legend(bbox_to_anchor=(1.1, 1.05))

    plt.savefig('/home/jorb/Programs/physicsScripts/filtering/' + name.replace('/', '_') + '.png',
                bbox_extra_artists=(lgd,), bbox_inches='tight')

    plt.show()

    plt.close()
