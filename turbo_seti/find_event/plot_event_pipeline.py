#!/usr/bin/env python3

r"""
Front-facing script to plot drifting, narrowband events in a set of generalized
cadences of ON-OFF radio SETI observations.
"""

import pandas
from blimpy import Waterfall
from . import plot_event


def plot_event_pipeline(event_csv_string, fils_list_string, user_validation=False,
                        offset=0, filter_spec=None):
    r"""
    This function calls :func:`~turbo_seti.find_event.plot_event.plot_candidate_events` to
    plot the events in an output .csv file generated by find_event_pipeline.py

    Parameters
    ----------
    event_csv_string : str
        The string name of a .csv file that contains the
        list of events at a given filter level, created as
        output from find_event_pipeline.py. The
        .csv should have a filename containing information
        about its parameters, for example
        "kepler1093b_0015_f2_snr10.csv"
        Remember that the file was created with some cadence
        (ex. ABACAD) and ensure that the cadence matches the
        order of the files in fils_list_string

    fils_list_string : str
        The string name of a plaintext file ending in .lst
        that contains the filenames of .fil files, each on a
        new line, that corresponds to the cadence used to
        create the .csv file used for event_csv_string.

    user_validation : bool, optional 
        A True/False flag that, when set to True, asks if the
        user wishes to continue with their input parameters
        (and requires a 'y' or 'n' typed as confirmation)
        before beginning to run the program. Recommended when
        first learning the program, not recommended for
        automated scripts.

    offset : int, optional
        The amount that the overdrawn "best guess" line from
        the event parameters in the csv should be shifted from
        its original position to enhance readability. Can be
        set to 0 (default; draws line on top of estimated
        event) or 'auto' (shifts line to the left by an auto-
        calculated amount, with addition lines showing original
        position).

    Examples
    --------
    >>> import plot_event_pipeline;
    ... plot_event_pipeline.plot_event_pipeline(event_csv_string, fils_list_string,
    ...                                         user_validation=False, offset=0)

    """
    #reading in the .csv containing the events
    try:
        candidate_event_dataframe = pandas.read_csv(event_csv_string, comment='#')
        print("plot_event_pipeline: Opened file {}".format(event_csv_string))
    except:
        print("*** plot_event_pipeline: Oops, cannot access file {}".format(event_csv_string))
        return

    with open(event_csv_string, "r") as file:
        distances = file.readline()
    distance_list = distances[2:-2].split(',')
    for dummy, distance in enumerate(distance_list):
        if len(distance) == 1:
            distance = '0d'
    plot_snr_list = distance_list

    #reading in the list of .fil files
    fil_file_list = []
    for file in pandas.read_csv(fils_list_string, encoding='utf-8', header=None, chunksize=1):
        fil_file_list.append(file.iloc[0,0])

    #obtaining source names
    source_name_list = []
    for fil in fil_file_list:
        wf = Waterfall(fil)
        source_name = wf.container.header["source_name"]
        source_name_list.append(source_name)
        print("plot_event_pipeline: source_name={}".format(source_name))

    #get rid of bytestring "B'"s if they're there (early versions of
    #seti_event.py added "B'"s to all of the source names)
    on_source_name_original = candidate_event_dataframe.Source[0]
    if on_source_name_original[0] == 'B' and on_source_name_original[-1] == '\'':
        on_source_name = on_source_name_original[2:-2]
    else:
        on_source_name = on_source_name_original
    candidate_event_dataframe = candidate_event_dataframe.replace(to_replace=on_source_name_original,
                                           value=on_source_name)

    # Establish filter-level from filter_spec (preferred) 
    # or 3rd token of the .csv path (don't break an existing caller)
    if filter_spec is None:
        filter_level = event_csv_string.split('_')[2]
    else:
        filter_level = filter_spec

    #begin user validation
    print("Plotting some events for: ", on_source_name)
    print("There are " + str(len(candidate_event_dataframe.Source)) + " total events in the csv file " + event_csv_string)
    print("therefore, you are about to make " + str(len(candidate_event_dataframe.Source)) + " .png files.")

    if user_validation:
        question = "Do you wish to proceed with these settings?"
        while "the answer is invalid":
            reply = str(input(question+' (y/n): ')).lower().strip()
            if reply == '':
                return
            if reply[0] == 'y':
                break
            if reply[0] == 'n':
                return

    #move to plot_event.py for the actual plotting
    plot_event.plot_candidate_events(candidate_event_dataframe,
                                   fil_file_list,
                                   filter_level,
                                   source_name_list,
                                   offset=offset,
                                   plot_snr_list=plot_snr_list)
    
