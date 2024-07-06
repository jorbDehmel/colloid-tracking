'''
Attempts to use existing models to determine what amount of the
observed movement is not attributable to known mechanisms (IE
particle-particle interactions).
'''

import math
import sys
from typing import List, Optional, Tuple, Dict
import numpy as np
from matplotlib import pyplot as plt
import speckle as s


def split_by_radius(tracks: List[s.Track],
                    r: float,
                    k: int) -> List[s.Track]:
    '''
    Breaks the given tracks, removing any regions wherein they
    are too close to each other (within k radii). Runs in time
    complexity $O(t p^2)$ for $p$ particles over $t$ frames.
    Some heavy optimization could bring this down (IE LAMMPS'
    neighbor lists), but I do not have the motivation to do so
    rn.

    :param tracks: The list of un-split tracks
    :param r: Particle radius
    :param k: Number of radii to use as a cutoff
    :returns: A new list of tracks
    '''

    # Minimal distance threshold
    thresh: float = k * r

    # Maps a frame id to a list of all particles' positions
    # (or None if they are not present in that frame)
    particle_positions: \
        Dict[int, List[Optional[Tuple[float, float]]]] \
        = {}

    # A list of all frames. This is used for iteration
    frames: List[int] = []

    # A list of the canonical tracks for a given track index.
    # This is used for splitting the input tracks.
    canon_tracks: List[Optional[s.Track]] = \
        [None for _ in tracks]

    # Output list
    out: List[s.Track] = []

    # Initialize list of frames which exist
    # O(tp)
    for t in tracks:
        for f in t.frames:
            if f not in particle_positions:
                particle_positions[f] = [None for _ in tracks]

    # Mark times where each particle exists
    # O(tp)
    for track_ind, t in enumerate(tracks):
        for i, frame in enumerate(t.frames):
            particle_positions[frame][track_ind] = \
                (t.x_values[i], t.y_values[i])

    # Obtain and sort list of all frame ids
    frames = list(particle_positions.keys())
    frames.sort()

    # Iterate over timesteps
    # O(t p^2)
    for t in frames:

        # Iterate over particles
        # O(p^2)
        snapshot: List[Optional[Tuple[int, int]]] = \
            particle_positions[t]

        for p_id, p in enumerate(snapshot):

            # Skip non-existant particles
            if p is None:
                continue

            # Compute distances of all to this
            # O(p)
            did_fail: bool = False
            for other_id, other in enumerate(snapshot):

                if other_id == p_id or other is None:
                    continue

                # Calculate distance
                d: float = math.hypot(p[0] - other[0],
                                      p[1] - other[1])

                if d < thresh:
                    did_fail = True
                    break

            # Operate based on results of distance computations
            if canon_tracks[p_id] is not None:

                if did_fail:

                    # A particle is too close; deactivate
                    out.append(canon_tracks[p_id])
                    canon_tracks[p_id] = None

                else:

                    # Normal case: Log this position
                    canon_tracks[p_id].append(p[0], p[1], t)

            elif not did_fail:

                # No particles are too close; activate
                canon_tracks[p_id] = \
                    s.Track([p[0]], [p[1]], [t])

    # Log final canon tracks
    out += [t for t in canon_tracks if t is not None]

    # Return output list
    return out


def main(v: List[str]) -> None:
    '''
    Main function. Loads, splits and plots the given filepath to
    demonstrate the splitting function.

    :param v: sys.argv
    '''

    assert len(v) == 3, 'Please provide a path and radius.'
    filepath: str = v[1]
    r: float = float(v[2])

    # Load speckle file specified by argv
    ff: s.FreqFile = s.load_frequency_file(filepath, 'speckles')

    # Initialize vars
    original_tracks: List[s.Track] = ff.tracks[:]
    data: List[Tuple[int, float, float]] = []

    # Iterate over different k values
    for k in range(0, 20):

        split_tracks: List[s.Track] = \
            split_by_radius(original_tracks, r, k)

        pre_x_values: List[float] = []
        pre_y_values: List[float] = []

        for t in original_tracks:
            pre_x_values += t.x_values
            pre_y_values += t.y_values

        post_x_values: List[float] = []
        post_y_values: List[float] = []

        for t in split_tracks:
            post_x_values += t.x_values
            post_y_values += t.y_values

        plt.clf()
        plt.scatter(pre_x_values, pre_y_values,
                    c='r', s=1.0, label='Pre')
        plt.scatter(post_x_values, post_y_values,
                    c='b', s=1.0, alpha=0.5, label='Post')
        plt.title(f'r={r}, k={k}')
        plt.legend()
        plt.savefig(f'r_{r}_k_{k}.png')

        msd_values: List[float] = \
            [t.msd() for t in split_tracks]
        data.append((k, np.mean(msd_values),
                     np.std(msd_values)))

    # Summary plot
    plt.clf()
    plt.title('Mean MSD +- 1 STD Pre/Post Instantaneous k-radii Filter')
    plt.xlabel('k')
    plt.ylabel('Mean MSD')
    plt.errorbar([i[0] for i in data],
                 [i[1] for i in data],
                 [i[2] for i in data])
    plt.savefig('msd_by_k.png')


# If this is being run as a script
if __name__ == '__main__':
    main(sys.argv)
