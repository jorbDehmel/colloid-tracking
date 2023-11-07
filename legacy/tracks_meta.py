#!/usr/bin/python3

'''
Outline:

- Process:
    - For a given folder, there are 5, 10, 15, 20 volt folders
    - For each of these, there are frequency files
    - Filterer returns stats on all csv things, but we only need
      mean straight line speed

    - For each voltage:
        - For each frequency
            - Load file and send through filterer
            - Record relevant data from filterer
        - Combine into unified voltage graph and csv
    - Combine into unified folder graph and csv

- Do process on Ramp wave
- Do process on Sine wave
- Do process on Square wave

'''

import os

import filterer
import reverser
import name_fixer

voltage_patterns: [str] = [
    '(?<!1)5[_ ]?[Vv][_ ]?',
    '10[_ ]?[Vv][_ ]?',
    '15[_ ]?[Vv][_ ]?',
    '20[_ ]?[Vv][_ ]?']

voltage_labels: [str] = [
    '5v',
    '10v',
    '15v',
    '20v']

frequency_patterns: [str] = [
    '((?<![015.])0 ?khz|control)', '(0.8 ?khz|800 ?hz)',
    '1 ?khz', '10 ?khz', '25 ?khz', '50 ?khz',
    '75 ?khz', '100 ?khz', '150 ?khz', '200 ?khz',
    '300 ?khz']


def analyze_folder(folder: str, voltage_patterns: [str] = voltage_patterns,
                   frequency_patterns: [str] = frequency_patterns,
                   save_prefix: str = '',
                   voltage_labels: [str] = voltage_labels) -> None:
    os.chdir(folder)
    print(os.getcwd())

    data_by_frequency_by_voltage: [[float]] = []
    std_by_frequency_by_voltage: [[float]] = []
    labels_by_frequency_by_voltage: [[str]] = []

    for voltage in voltage_patterns:
        # frequencies = frequencies present in voltage
        voltage_files: [str] = name_fixer.find_all_recursive(voltage)
        frequencies: [str] = name_fixer.fix_names(
            frequency_patterns, voltage_files)

        frequencies = [freq for freq in frequencies if freq is not None]

        data_by_frequency: [float] = []
        std_by_frequency: [float] = []
        labels_by_frequency: [str] = []

        for i, filepath in enumerate(frequencies):
            # Load file through filterer
            results, results_std, freq_string = filterer.do_file(filepath,
                                                                 filterer.brownian_speed_threshold,
                                                                 filterer.brownian_linearity_threshold,
                                                                 filterer.brownian_speed_threshold,
                                                                 filterer.do_std_filter_flags,
                                                                 filterer.do_iqr_filter_flags,
                                                                 True)

            if i == 0:
                filterer.brownian_displacement_threshold = results[0]
                filterer.quality_threshold = results[3]
                filterer.brownian_speed_threshold = results[5]
                filterer.brownian_linearity_threshold = results[6]

            # Record relevant data (sls + std)
            data_by_frequency.append(
                results[filterer.col_names.index('MEAN_STRAIGHT_LINE_SPEED')])
            std_by_frequency.append(
                results_std[filterer.col_names.index('MEAN_STRAIGHT_LINE_SPEED')])

            labels_by_frequency.append(float(freq_string))

        # Combine into unified voltage graph and csv

        # Append to unified data
        data_by_frequency_by_voltage.append(data_by_frequency[:])
        std_by_frequency_by_voltage.append(std_by_frequency[:])
        labels_by_frequency_by_voltage.append(labels_by_frequency[:])

    # Combine into unified folder graph and csv

    reverser.graph_multiple_relative_individually(data_by_frequency_by_voltage,
                                                  [12500.0 for _ in frequency_patterns],
                                                  labels_by_frequency_by_voltage,
                                                  [filterer.secondary_save_path +
                                                      os.sep + save_prefix + '.png',
                                                      '/home/jorb/Programs/physicsScripts/' + save_prefix + '.png'],
                                                  ('Applied Frequency (Hz)',
                                                      'Mean Straight Line Speed (Pixels / Frame)'),
                                                  voltage_labels,
                                                  '(Plus or Minus 1 STD w/ Interpolated Crossover Point, ' +
                                                  save_prefix + ')',
                                                  std_by_frequency_by_voltage)

    reverser.graph_multiple_relative(data_by_frequency_by_voltage,
                                     [12500.0 for _ in frequency_patterns],
                                     labels_by_frequency_by_voltage,
                                     [filterer.secondary_save_path +
                                      os.sep + save_prefix + '.png',
                                      '/home/jorb/Programs/physicsScripts/' + save_prefix + '.png'],
                                     ('Applied Frequency (Hz)',
                                      'Mean Straight Line Speed (Pixels / Frame)'),
                                     voltage_labels,
                                     '(Plus or Minus 1 STD w/ Interpolated Crossover Point, ' +
                                     save_prefix + ')',
                                     std_by_frequency_by_voltage)

    return


if __name__ == '__main__':
    filterer.do_displacement_thresh = False
    filterer.do_linearity_thresh = False
    filterer.do_std_filter_flags = None
    filterer.do_speed_thresh = False

    filterer.do_quality_percentile_filter = True

    # Ramp wave
    analyze_folder('/home/jorb/data/tracks/Ramp Wave', save_prefix='ramp')

    # Sine wave
    analyze_folder('/home/jorb/data/tracks/Sine Wave', save_prefix='sine')

    # Square wave
    analyze_folder('/home/jorb/data/tracks/Square Wave', save_prefix='square')

    pass
