#!/bin/python3

import pandas as pd
import numpy as np
import os

# Folder location
folder: str = ''

# File suffix for input track files
suffix: str = '_tracks.csv'

# Output file suffix for csv files
output_suffix: str = 'tracksexport.csv'


# Standard deviation filter
def sd_filter(freq):
    try:
        # Match with file
        file = freq + suffix

        data = pd.read_csv(folder + file)

        # Jordan filter
        displacement = data[['TRACK_DISPLACEMENT']]
        displacement = displacement.drop([0, 1, 2])

        # Turn DF to Py list
        displacement_list: [float] = []
        for row in displacement:
            for whatever in displacement[row]:
                displacement_list.append(float(whatever))

        to_drop_msd: [float] = msd_filter(displacement_list)

        # Drop any item which was recommended to be dropped by the msd filter
        for ind in to_drop_msd:
            data = data.drop(ind + 3)

        data = data[['TRACK_MEAN_SPEED']]
        data = data.drop([0, 1, 2])
        data = data.to_numpy()
        data = data.astype(float)

        speedStd = np.std(data, axis=0)
        meanSpeed = np.mean(data, axis=0)

        # Filtering out data 2 StD away from the mean
        r = len(data) + len(to_drop_msd)

        # Filtering out data
        filtered_data = []
        for i in data:
            if (i >= meanSpeed - 2 * speedStd and i < meanSpeed + 2 * speedStd):
                filtered_data.append(i)

        data = np.array(filtered_data)
        rf = len(data)
        percent = rf / r
        count = r

        # Converting Unit from pixel/frame to um/s
        meanSpeed = np.mean(data, axis=0)
        meanSpeed = meanSpeed * 4 * 0.32

        speedStd = np.std(data, axis=0)
        speedStd = speedStd * 4 * 0.32

        return (meanSpeed, speedStd, percent, count)

    except Exception as e:
        print('Failure:', e)
        print('File',
              folder + freq + suffix,
              'failed. It likely does not exist.')
        raise Exception()


# Individual frequencies where anything below brownian is removed and outliers
def brownian_filter(freq, bmean):
    try:
        # Match with file
        file = freq + suffix

        data = pd.read_csv(folder + file)

        # Jordan filter
        displacement = data[['TRACK_DISPLACEMENT']]
        displacement = displacement.drop([0, 1, 2])

        # Turn DF to Py list
        displacement_list: [float] = []
        for row in displacement:
            for whatever in displacement[row]:
                displacement_list.append(float(whatever))

        to_drop_msd: [float] = msd_filter(displacement_list)

        # Drop any item which was recommended to be dropped by the msd filter
        for ind in to_drop_msd:
            data = data.drop(ind + 3)

        data = data[['TRACK_MEAN_SPEED']]

        data = data.drop([0, 1, 2])
        data = data.to_numpy()
        data = data.astype(float)
        r = len(data) + len(to_drop_msd)

        # Filtering out data less than brownian
        filtered_data = []
        for row in data:
            if row >= bmean:
                filtered_data.append(row)

        # filtered_data = [i for i in data if i >= bmean]

        data = np.array(filtered_data)
        speedStd = np.std(data, axis=0)
        meanSpeed = np.mean(data, axis=0)

        # Filtering out data 2 StD away from the mean
        filtered_data = []

        for i in data:
            if (i >= meanSpeed - 2 * speedStd and i < meanSpeed + 2 * speedStd):
                filtered_data.append(i)

        # filtered_data = [i for i in data if (i >= meanSpeed - 2 * speedStd and i < meanSpeed + 2 * speedStd)]

        data = np.array(filtered_data)
        rf = len(data)
        percent = rf / r
        count = r

        # Converting Unit from pixel/frame to um/s
        meanSpeed = np.mean(data)
        meanSpeed = meanSpeed * 4 * 0.32

        speedStd = np.std(data)
        speedStd = speedStd * 4 * 0.32

        return (meanSpeed, speedStd, percent, count)

    except Exception as e:
        print('Failure:', e)
        print('File',
              folder + freq + suffix,
              'failed. It likely does not exist.')
        raise Exception()


# Adding many frequencies to one array
def freq_sweep(*args):
    columns = ['Ave. Speed (um/s)', 'SD', '% Remaining', 'Initial Count']
    index = args
    array = np.zeros((len(args), 4))

    successes: int = 0

    try:
        for i in range(0, len(args)):
            if (i == 0):
                mSpeed, std, percent, count = sd_filter(args[0])
                array[i, 0] = mSpeed
                array[i, 1] = std
                array[i, 2] = percent
                array[i, 3] = count
                i = i + 1
            else:
                mSpeedb, stdb, percentb, count = brownian_filter(
                    args[i], mSpeed)
                array[i, 0] = mSpeedb
                array[i, 1] = stdb
                array[i, 2] = percentb
                array[i, 3] = count

            successes += 1

    except:
        if successes == 0:
            print('No files exist in the current directory: Not saving file.')
            return

    df = pd.DataFrame(array, columns=columns, index=index)
    print(df)

    df.to_csv(folder + output_suffix)

    return


# Mean squared displacement filter
# Filters out any data which is more than two standard
# deviations away from the Mean Squared Displacement.
# Takes a list of displacements, and returns the
# indices which should be dropped
def msd_filter(displacements: [float]) -> [int]:
    # Get msd
    mean: float = msd(displacements)

    # Get standard deviation
    std: float = msd_standard_deviation(displacements, mean)

    # Initialize output list
    out: [float] = []

    # Iterate through, adding any item which is within two standard deviations of msd
    for i in range(len(displacements)):
        num_std: float = msd_deviation(displacements, i, mean, std)

        # print(item, 'is', num_std, 'std away from msd from',
        #       mean, 'where std is', std)

        if abs(num_std) >= 2:
            out.append(i)

    # If you want a one-liner:
    # return [item for i, item in enumerate(displacements) if abs(
    #     msd_deviation(displacements, i, mean, std) < 2)]

    return out


# Return the mean squared displacement given a set of displacements
def msd(displacements: [float]) -> float:
    return sum([disp ** 2 for disp in displacements]) / len(displacements)


# Returns the number of standard deviations a certain displacement is above the msd
def msd_deviation(displacements: [float], index: int, mean: float, std: float) -> float:
    return (mean - (displacements[index] ** 2)) / std


# Returns the standard deviation from the msd of a set of displacements
def msd_standard_deviation(displacements: [float], mean: float) -> float:
    # If you want a one-liner:
    # return (sum([(item - mean) ** 2 for item in displacements]) / len(displacements)) ** 0.5

    # Inner bit
    out: float = sum([(item - mean) ** 2 for item in displacements])

    # Finish inner bit
    out /= len(displacements) - 1

    # Take sqrt
    out = out ** 0.5

    # Return
    return out


def sweep_current_folder() -> None:
    # Set the folder to the current working directory
    global folder
    folder = os.getcwd() + os.sep

    # Go
    freq_sweep('0khz', '1khz', '5khz', '10khz',
               '25khz', '50khz', '75khz', '100khz')


def sweep_folder(where: str) -> None:
    # Set the folder
    global folder
    folder = where + os.sep

    # cd so it gets saved in the right place
    old_place: str = os.getcwd()
    os.chdir(where)

    # Go
    freq_sweep('0khz', '1khz', '5khz', '10khz',
               '25khz', '50khz', '75khz', '100khz')

    os.chdir(old_place)


if __name__ == '__main__':
    sweep_current_folder()
