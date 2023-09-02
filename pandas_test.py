#!/usr/bin/python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from natsort import index_natsorted
from os import sep
import time

do_big_graphs: bool = True


# Returns the distance between two points in a cartesian plane
def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    dx: float = x2 - x1
    dy: float = y2 - y1
    temp: float = (dx ** 2 + dy ** 2)

    return temp ** 0.5


def do_file(name: str, do_graphs: bool = False) -> (float, float, float, float, float, float, float):
    csv = pd.read_csv(name + "_spots.csv")

    csv.drop(axis=1, inplace=True, labels=[
             "SNR_CH1", "STD_INTENSITY_CH1", "CONTRAST_CH1",
             "MIN_INTENSITY_CH1", "MAX_INTENSITY_CH1",
             "TOTAL_INTENSITY_CH1", "MEDIAN_INTENSITY_CH1",
             "MANUAL_SPOT_COLOR", "QUALITY", "VISIBILITY",
             "POSITION_T", "LABEL", "POSITION_Z", "RADIUS",
             "ID"])

    csv.drop(axis=0, inplace=True, labels=[
        0, 1, 2])

    csv.sort_values(by=["FRAME"], inplace=True,
                    key=lambda x: np.argsort(index_natsorted(csv["FRAME"])))

    l = csv["FRAME"].astype(int).to_list()

    for i in range(1, len(l)):
        assert l[i] >= l[i - 1]

    bins: dict = {}
    for row in csv.iterrows():
        row = row[1]
        row = [float(item) for item in row]
        row[0] = int(row[0])
        row[3] = int(row[3])

        if row[0] not in bins:
            bins[row[0]] = []

        # Append a vector of the x, y, and frame num
        bins[row[0]].append(row[1:-1])

    # In pixels
    displacements: [float] = []

    # In pixels squared
    squared_displacement_sum: float = 0.0

    # In pixels
    distances: [float] = []

    # In pixels per frame
    average_velocities: [float] = []

    for key in bins:
        disp: float = 0.0
        dist: float = 0.0

        disp = distance(bins[key][0][0], bins[key][0][1],
                        bins[key][-1][0], bins[key][-1][1])

        displacements.append(disp)
        average_velocities.append(disp / (bins[key][-1][2] - bins[key][0][2]))

        squared_displacement_sum += disp * disp

        for i in range(0, len(bins[key]) - 1):
            dist += distance(bins[key][i][0], bins[key][i][1],
                             bins[key][i + 1][0], bins[key][i + 1][1])

        distances.append(dist)

    mean_disp: float = np.mean(displacements)
    std_disp: float = np.std(displacements)

    if do_graphs:
        plt.clf()
        plt.hist(displacements, bins=30)
        plt.title("Particle Net Displacements (File " +
                  name.replace("/", "_") + ")")

        plt.xlabel("Displacement (pixels)")
        plt.ylabel("Number of Particles")
        plt.vlines(x=[mean_disp - 2 * std_disp, mean_disp, mean_disp + 2 * std_disp],
                   ymin=[0, 0, 0], ymax=[10, 20, 10], colors=["black"])

        plt.savefig("displacements_" + name.replace("/", "_") + ".png")

    mean_dist: float = np.mean(distances)
    std_dist: float = np.std(distances)

    if do_graphs:
        plt.clf()
        plt.hist(distances, bins=30)
        plt.title("Particle Distance Traveled (File " +
                  name.replace("/", "_") + ")")

        plt.xlabel("Displacement (pixels)")
        plt.ylabel("Number of Particles")
        plt.vlines(x=[mean_dist - 2 * std_dist, mean_dist, mean_dist + 2 * std_dist],
                   ymin=[0, 0, 0], ymax=[10, 20, 10], colors=["black"])

        plt.savefig("distances_" + name.replace("/", "_") + ".png")

    mean_vel: float = np.mean(average_velocities)
    std_vel: float = np.std(average_velocities)

    if do_graphs:
        plt.clf()
        plt.hist(average_velocities, bins=30)
        plt.title("Particle Average Velocities (File " +
                  name.replace("/", "_") + ")")

        plt.xlabel("Displacement (pixels)")
        plt.ylabel("Number of Particles")
        plt.vlines(x=[mean_vel - 2 * std_vel, mean_vel, mean_vel + 2 * std_vel],
                   ymin=[0, 0, 0], ymax=[10, 20, 10], colors=["black"])

        plt.savefig("velocities_" + name.replace("/", "_") + ".png")

    msd: float = squared_displacement_sum / len(bins)

    return (mean_disp, std_disp, mean_dist, std_dist, mean_vel, std_vel, msd)


if __name__ == "__main__":

    do_little_graphs: bool = True

    frequencies: [int] = [0, 1, 5, 10, 25, 50, 75, 100]

    names: [str] = [str(f) + "khz" for f in frequencies]

    array = np.zeros(shape=(len(names), 7))

    mean_displacements: [float] = []
    mean_distances: [float] = []
    mean_velocities: [float] = []

    std_displacements: [float] = []
    std_distances: [float] = []
    std_velocities: [float] = []

    mean_squared_displacements: [float] = []

    for i, name in enumerate(names):
        start: float = time.time()
        array[i] = do_file("test" + sep + name, do_little_graphs)
        end: float = time.time()

        mean_displacements.append(array[i][0])
        std_displacements.append(array[i][1])
        mean_distances.append(array[i][2])
        std_distances.append(array[i][3])
        mean_velocities.append(array[i][4])
        std_velocities.append(array[i][5])
        mean_squared_displacements.append(array[i][6])

        print(name, "took", (end - start), "seconds.")

    out_csv: pd.DataFrame = pd.DataFrame(array, columns=[
                                         "Mean Displacement", "STD Displacement",
                                         "Mean Distance Traveled", "STD Distance Traveled",
                                         "Mean Net Velocity", "STD Net Velocity",
                                         "Mean Squared Displacement"],
                                         index=names)
    out_csv.to_csv("data.csv")

    if do_big_graphs:
        plt.clf()
        plt.plot(frequencies, mean_displacements)

        plt.title(
            "Mean Particle Displacements by Applied Frequency\n(With Standard Deviations)")
        plt.xlabel("Frequency (KiloHertz)")
        plt.ylabel("Displacement (Pixels)")

        plt.errorbar(frequencies, mean_displacements,
                     yerr=std_displacements)

        plt.savefig("displacements.png")

        plt.clf()
        plt.plot(frequencies, mean_distances)

        plt.title(
            "Mean Particle Distance Traveled by Applied Frequency\n(With Standard Deviations)")
        plt.xlabel("Frequency (KiloHertz)")
        plt.ylabel("Distance Traveled (Pixels)")

        plt.errorbar(frequencies, mean_distances,
                     yerr=std_distances)

        plt.savefig("distances.png")

        plt.clf()
        plt.plot(frequencies, mean_velocities)

        plt.title(
            "Mean Particle Net Velocities by Applied Frequency\n(With Standard Deviations)")
        plt.xlabel("Frequency (KiloHertz)")
        plt.ylabel("Net Velocity (Pixels Per Frame)")

        plt.errorbar(frequencies, mean_velocities,
                     yerr=std_velocities)

        plt.savefig("velocities.png")

        plt.clf()
        plt.plot(frequencies, mean_squared_displacements)

        plt.title(
            "Mean Squared Particle Displacement by Applied Frequency")
        plt.xlabel("Frequency (KiloHertz)")
        plt.ylabel("Mean Squared Displacement (Pixels Squared)")

        plt.savefig("msd.png")

    exit(0)
