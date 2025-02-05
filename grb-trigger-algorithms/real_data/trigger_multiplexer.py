import warnings
import logging
from math import sqrt

import numpy as np

KDETS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b")
KRANGES = ("0", "1", "2")


def get_keys(ns=KDETS, rs=KRANGES):
    """
    build lists like ['n1_r0', 'n3_r0']
    :param ns: sequence representing dets
    :param rs: sequence representing ranges
    :return: list of strings
    """
    return [f"n{str(i)}_r{j}" for i in ns for j in rs]


def filter_keys(ls, ns, rs=None):
    """
    :param ls: list of string keys
    :param ns: detectors to keep
    :param rs: ranges to keep
    :return: filtered list of strings
    """
    if rs is None:
        rs = ["0", "1", "2"]
    index_labels = {i[1] for i in ls}
    range_labels = {i[-1] for i in ls}

    out_index = index_labels.intersection(ns)
    out_range = range_labels.intersection(rs)
    return sorted(get_keys(out_index, out_range))


def trigger_mux(
    observations_df,
    trig,
    thresholds,
    stride,
    t_start=0.0,
    max_consecutive_zeros=10,
    **trig_params,
):
    def reset_trigger(detector_key):
        trigs[detector_key] = trig(**trig_params)
        global_maximums[detector_key] = 0
        time_offsets[detector_key] = 0
        return True

    ndet = len(thresholds)

    mets_arr = observations_df["MET"].to_numpy()
    saa_arr = observations_df["SAA"].to_numpy()
    counts_arr = observations_df[get_keys()].to_numpy()
    det_keys = [(i, k) for i, k in enumerate(get_keys()) if np.isfinite(thresholds[i])]
    det_indeces, det_names = zip(*det_keys)

    consecutive_zeros = np.array([0 for _ in range(ndet)])
    global_maximums = np.array([0.0 for _ in range(ndet)])
    time_offsets = np.array([0 for _ in range(ndet)])
    trigs = [trig(**trig_params) for _ in range(ndet)]
    trig_registry = []

    nrows = len(mets_arr)
    t = int(t_start * nrows)
    while t < nrows:
        print(end="\r%6.2f %%" % (t / (nrows - 1) * 100))

        # deals with SAA passages
        if saa_arr[t]:
            for n, _ in det_keys:
                reset_trigger(n)
                consecutive_zeros[n] = 0

            try:
                next_out, *_ = np.where(saa_arr[t:] == 0)[0]
            except ValueError:
                # deals with the possibility of observations ending in saa
                if not np.all(saa_arr[t:]):
                    raise
                t = nrows
            else:
                t += next_out
            continue

        # deals with occasionally detectors turning off at same time
        elif not np.any(counts_arr[t]):
            for n, _ in det_keys:
                warnings.warn(
                    f"All detectors seems to be off. "
                    f"Resetting all triggers. "
                    f"MET: {mets_arr[t]}"
                )
                reset_trigger(n)
                consecutive_zeros[n] = 0
            try:
                next_out, *_ = np.where(np.all(counts_arr[t:], axis=1))[0]
            except ValueError:
                # deals with the possibility of signal never coming up again
                if not np.all(counts_arr[t:]):
                    raise
                t = nrows
            else:
                t += next_out
            continue

        for n, det_key in zip(det_indeces, det_names):
            x_t = counts_arr[t, n]
            if x_t <= 0:
                consecutive_zeros[n] += 1
            else:
                consecutive_zeros[n] = 0

            if consecutive_zeros[n] > max_consecutive_zeros:
                # data may contains segments in which the counts of some detector
                # is constantly zero because the detector is turned off.
                # this happens most often with sun-facing detectors.
                # if we pass too much zero data to the trigger, they will
                # pollute the background estimate, possibly causing
                # false detection. when we detect this, we restart the trigger.
                reset_trigger(n)
                warnings.warn(
                    f"Found a bad data segment for detector {det_key}. "
                    f"Resetting the corresponding trigger. "
                    f"MET: {mets_arr[t]}"
                )
                continue

            try:
                global_max, time_offset = trigs[n].step(x_t)
            except ValueError:
                raise ValueError(
                    f"Corrupted background estimate over {det_key}. "
                    f"Resetting this trigger."
                    f"MET: {mets_arr[t]}"
                )
            global_maximums[n] = global_max
            time_offsets[n] = time_offset

        # trigger condition.
        if len(np.unique(np.floor((np.argwhere(global_maximums > thresholds).T + 1) / 3))) > 1:
            print(", found a trigger.")
            logging.info("\n--------")
            logging.info("New trigger [key: {:3d}]".format(len(trig_registry)))
            trig_met = mets_arr[t]
            logging.info("MET: {}.".format(trig_met))
            logging.info("{:.1f}% done!".format(100 * t / nrows))
            logging.info("Iteration number: {}".format(t))
            trig_entry = [len(trig_registry), trig_met]
            for i, (key, to, gm) in enumerate(
                zip(get_keys(), time_offsets, global_maximums)
            ):
                if gm > thresholds[i]:
                    logging.info(
                        "det_name: {}, time-offset: {:3d}, significance {:.2f}".format(
                            key, -to, gm
                        )
                    )
                    trig_entry.append((key, to, sqrt(2 * gm)))
            trig_registry.append(tuple(trig_entry))
            for n, _ in det_keys:
                reset_trigger(n)
                consecutive_zeros[n] = 0
            t += stride
        else:
            t += 1
    return trig_registry
