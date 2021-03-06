# Code from the NWUtils package (Michael Eden, 2021) put in a simple-to-use format with sample data viewing capability.

import numpy as np
import pandas as pd
import pyedflib
from datetime import datetime

# If nwutils is not already installed, open the Terminal and enter command:
# pip install git+https://github.com/nimbal/nwutils.git

from nwutils.gui.annotator import WindowAnnotator, AnnotationManager
from nwutils.gui.plotter import Plotter
from nwutils.gui.utils import run_app
from nwutils.io.annotation import Flag, AnnotationWindow
from nwutils.signal.signal import Signal


def window_annotator(data_array=(), sample_f=1, start_time=None, flags=()):

    annots = []  # list of each annotation made

    async def app():
        signals = []

        # if data_array is multi-dimensional...
        if len(data_array.shape) > 1:
            for arr in data_array:
                signal = Signal.from_array(data=arr,
                                           sample_rate=sample_f,
                                           start_time=start_time if start_time is not None else datetime.now())
                signals.append(signal)

            plotter = Plotter()
            for signal in signals:
                plotter.add_signal(signal)

        # if data_array is single dimension
        if len(data_array.shape) == 1:
            signal = Signal.from_array(data=data_array,
                                       sample_rate=sample_f,
                                       start_time=start_time if start_time is not None else datetime.now())

            plotter = Plotter()
            plotter.add_signal(signal)

        annotator = WindowAnnotator(plotter=plotter, flags=flags,
                                    start_time=signal.get_start_time(), end_time=signal.get_end_time())

        annotation_manager = AnnotationManager(AnnotationWindow, annotator)
        annotation_manager.show()

        annotations = await annotation_manager.wait_for_annotations()
        for annotation in annotations:
            annots.append(annotation)
            print(annotation)

    run_app(app())

    return pd.DataFrame(annots)


""" -------------------------------------------------- DATA IMPORT -------------------------------------------------"""

# Import using pyedflib
file = pyedflib.EdfReader(f"O:/OBI/ONDRI@Home/Device Validation Protocols/Bittium Faros/Data Files/OmegaSnap/008_OmegaSnap.EDF")

# First 1000 seconds of data
acc = np.array([file.readSignal(1, n=250000), file.readSignal(2, n=250000), file.readSignal(3, n=250000)])

start_stamp = file.getStartdatetime()  # start stamp
acc_fs = int(file.getSampleFrequency(1))  # accelerometer sample rate
file_dur = file.file_duration
file.close()

# Defining what events to flag in what colour
flag = [Flag("Walking", "Walk", "green"), Flag("Nonwear", "Nonwear", 'grey')]

""" ------------------------------------------------ FUNCTION CALL -------------------------------------------------"""

annots = window_annotator(data_array=acc, sample_f=25, start_time=start_stamp, flags=flag)
# annots.to_csv("Test_Annotations.csv", index=False)  # csv in working directory
