#!/bin/python3

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os

import matplotlib.pyplot as plt

'''
Original filter
'''

# Folder location
folder: str = ''

# File suffix for input track files
suffix: str = 'trackexport.csv'

# Output file suffix for csv files
output_suffix: str = 'out.tracksexport.csv'


# Standard deviation filter
def sd_filter(freq: str) -> (float, float, float, float, float, float):
    try:
        # Match with file
        file: str = freq + suffix

        data: pd.DataFrame = pd.read_csv(folder + file)

        # Get track displacements from dataframe before
        # it is overwritten
        displacement = data[['TRACK_DISPLACEMENT']]
        displacement = displacement.drop([0, 1, 2])

        # Turn DF to Py list for easy of use
        displacement_list: [float] = []
        for row in displacement:
            for item in displacement[row]:
                displacement_list.append(float(item))

        if len(displacement_list) == 0:
            raise Exception('Cannot apply filter to empty list')

        # Do MSD filter
        to_drop_msd, prefilter_msd = msd_filter_2(displacement_list)

        to_drop_msd.sort()
        for num, i in enumerate(to_drop_msd):
            del displacement_list[i - num]

        corrected_msd: float = msd(displacement_list)

        data: pd.DataFrame = data[['TRACK_MEAN_SPEED']]
        data: pd.DataFrame = data.drop([0, 1, 2])

        data: np.ndArray = data.to_numpy()
        data = data.astype(float)

        speedStd: float = np.std(data, axis=0)
        meanSpeed: float = np.mean(data, axis=0)

        # Filtering out data 2 StD away from the mean
        r: int = len(data) + len(to_drop_msd)

        # Filtering out data
        filtered_data: [float] = []
        for item in data:
            if item >= meanSpeed - 2 * speedStd and item < meanSpeed + 2 * speedStd:
                filtered_data.append(item)

        data = np.array(filtered_data)
        rf: int = len(data)
        percent: float = rf / r

        print('STD + MSD 2 filters recommended the removal of',
              r - rf, 'items, leaving', rf)

        # Converting Unit from pixel/frame to um/s
        meanSpeed: float = np.mean(data, axis=0)
        meanSpeed = meanSpeed * 4 * 0.32

        speedStd: float = np.std(data, axis=0)
        speedStd = speedStd * 4 * 0.32

        return (meanSpeed, speedStd, percent, r, prefilter_msd, corrected_msd)

    except Exception as e:
        print('Failure:', e)
        print('File',
              folder + freq + suffix,
              'failed. It likely does not exist.')
        raise Exception()


# Individual frequencies where anything below brownian is removed and outliers
def brownian_filter(freq: str, bmean: float, bmsd: float) -> (float, float, float, float, float, float):
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
            for item in displacement[row]:
                displacement_list.append(float(item))

        if len(displacement_list) == 0:
            raise Exception('Cannot apply filter to empty list')

        # Do MSD filter
        to_drop_msd, prefilter_msd = msd_filter_2(displacement_list)

        to_drop_msd.sort()
        for num, i in enumerate(to_drop_msd):
            del displacement_list[i - num]

        corrected_msd: float = msd(displacement_list)

        data = data[['TRACK_MEAN_SPEED']]

        data = data.drop([0, 1, 2])
        data = data.to_numpy()
        data = data.astype(float)
        r = len(data) + len(to_drop_msd)

        # Filtering out data less than brownian
        filtered_data = []

        for row, i in enumerate(data):
            if i in to_drop_msd:
                continue

            # Convert to um/s
            if row * 4 * 0.32 >= bmean:
                filtered_data.append(row)

        data = np.array(filtered_data)
        speedStd = np.std(data, axis=0)
        meanSpeed = np.mean(data, axis=0)

        # Filtering out data 2 StD away from the mean
        filtered_data = []

        for i in data:
            if (i >= meanSpeed - 2 * speedStd and i < meanSpeed + 2 * speedStd):
                filtered_data.append(i)

        data = np.array(filtered_data)
        rf = len(data)
        percent = rf / r
        count = r

        print('Brownian + MSD 2 filters recommended the removal of',
              r - rf, 'items, leaving', rf)

        # Converting Unit from pixel/frame to um/s
        meanSpeed = np.mean(data)
        meanSpeed = meanSpeed * 4 * 0.32

        speedStd = np.std(data)
        speedStd = speedStd * 4 * 0.32

        return (meanSpeed, speedStd, percent, count, prefilter_msd, corrected_msd)

    except Exception as e:
        print('Failure:', e)
        print('File',
              folder + freq + suffix,
              'failed. It likely does not exist.')
        raise Exception()


# Adding many frequencies to one array
def freq_sweep(*args) -> None:
    columns = ['Ave. Speed (um/s)', 'SD', '% Remaining',
               'Initial Count', 'MSD', 'Filtered MSD']
    index = args
    array = np.zeros((len(args), 6))

    successes: int = 0

    try:
        for i in range(0, len(args)):
            if (i == 0):
                mSpeed, std, percent, count, bmsd, corrected_msd = sd_filter(
                    args[0])
                array[i, 0] = mSpeed
                array[i, 1] = std
                array[i, 2] = percent
                array[i, 3] = count
                array[i, 4] = bmsd
                array[i, 5] = corrected_msd
            else:
                mSpeedb, stdb, percentb, count, msd, corrected_msd = brownian_filter(
                    args[i], mSpeed, bmsd)
                array[i, 0] = mSpeedb
                array[i, 1] = stdb
                array[i, 2] = percentb
                array[i, 3] = count
                array[i, 4] = msd
                array[i, 5] = corrected_msd

            successes += 1

    except:
        if successes == 0:
            print('No files exist in the current directory: Not saving file.')
            return

    df = pd.DataFrame(array, columns=columns, index=index)
    print(df)

    df.to_csv(folder + output_suffix)

    plt.clf()
    plt.plot(df["Ave. Speed (um/s)"])
    plt.title("Ave. Speed (um/s)")
    plt.savefig("speeds.png")

    plt.clf()
    plt.plot(df["MSD"])
    plt.title("Mean Squared Displacement (Square Pixels)")
    plt.savefig("msd.png")

    return


# Mean squared displacement filter
# Filters out any data which is more than two standard
# deviations away from the Mean Squared Displacement.
# Takes a list of displacements, and returns the
# indices which should be dropped
def msd_filter(displacements: [float]) -> ([int], float):
    # Get msd
    mean: float = msd(displacements)

    # Get standard deviation
    std: float = msd_standard_deviation(displacements, mean)

    # Initialize output list
    out: [float] = []

    # Iterate through, adding any item which is within two standard deviations of msd
    for i in range(len(displacements)):
        num_std: float = msd_deviation(displacements, i, mean, std)
        if num_std < -1 or num_std > 1:
            out.append(i)

    print('MSD filter recommended the removal of',
          len(out), 'items out of', len(displacements))

    return out, mean


# Return the mean squared displacement given a set of displacements
def msd(displacements: [float]) -> float:
    return sum([disp ** 2 for disp in displacements]) / len(displacements)


# Returns the number of standard deviations a certain displacement is above the msd
def msd_deviation(displacements: [float], index: int, mean: float, std: float) -> float:
    return ((displacements[index] ** 2) - mean) / std


# Returns the standard deviation from the msd of a set of displacements
def msd_standard_deviation(displacements: [float], mean: float) -> float:

    # Inner bit
    out: float = sum([(item - mean) ** 2 for item in displacements])

    # Finish inner bit
    out /= len(displacements) - 1

    # Take sqrt
    out = out ** 0.5

    # Return
    return out


# Mean squared displacement filter 2
# Filters items beyond 1.5 IQR rather than beyond 2 Standard deviation
def msd_filter_2(displacements: [float]) -> ([int], float):
    mean: float = msd(displacements)

    squared_displacements: [float] = [item ** 2 for item in displacements]

    # Get Q1 and Q3 boundaries
    q1, q3 = np.percentile(squared_displacements, [25, 75])

    # Compute IQR
    iqr: float = q3 - q1

    # Compute min and max range
    min_val: float = q1 - iqr
    max_val: float = q3 + iqr

    # Create to_drop list
    to_drop: [int] = []

    below = 0

    for i, item in enumerate(squared_displacements):
        if item < min_val or item > max_val:
            to_drop.append(i)
            below += 1

    print("MSD filter 2 recommended the removal of", len(to_drop),
          "items, leaving", len(displacements) - len(to_drop))

    return to_drop, mean


def sweep_current_folder() -> None:
    # Set the folder to the current working directory
    global folder
    folder = os.getcwd() + os.sep

    # Go
    freq_sweep('0khz', '0.8khz', '1khz', '10khz', '25khz', '50khz',
               '75khz', '100khz', '150khz', '200khz')


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
