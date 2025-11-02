from __future__ import annotations

"""
carbonfly
    a lightweight, easy-to-use Python API and 
    toolbox for indoor CO2 CFD simulations in Grasshopper
    based on OpenFOAM and WSL

- Author: Qirui Huang
- License: LGPL-3.0
- Website: https://github.com/RWTH-E3D/carbonfly
"""

# carbonfly/iaq.py
"""
Indoor Air Quality (IAQ) evaluation based on international standards.
"""

from typing import Union, List


def iaq_co2(
    co2_indoor: Union[float, int, List[float], List[int]],
    co2_outdoor: Union[float, int, List[float], List[int]] = 400,
    standard: str = "EN",
) -> tuple:
    """
    Calculate CO2-based Indoor Air Quality (IAQ) indices based on different standards.

    Warnings:
        CO2 is only suitable for assessing IAQ as an **indirect** proxy indicator of ventilation rate.
        The assessment should be made aware of the following limitations:
        1. CO2 below the threshold does not ensure an acceptable overall IAQ, but an excessively high CO2
        may indicate that the room is not well ventilated, e.g. the ventilation system is not functioning
        correctly or the windows are closed for a long period of time.
        2. The direct impact of CO2 on health, well-being, and performance is still controversial.
        At the same time CO2 should not be used directly as a direct indicator of the risk of disease transmission,
        but should only be considered as an indirect indicator of ventilation rates.
        3. CO2 measurements are greatly influenced by the accuracy of the sensor, its installation location
        and calibration method.
        Therefore, ASHRAE does not have a CO2-based IAQ index, see:
        Persily A. 2020. Quit Blaming ASHRAE Standard 62.1 for 1000 ppm CO2, Indoor Air 2020 - The 16th Conference of
        the Internatinal Society of Indoor Air Quality & Climate.

    Args:
        co2_indoor: float, int or 1d array-like, support numpy array or pandas series
            CO2 concentration indoors in ppm.

        co2_outdoor: float, int or 1d array-like, support numpy array or pandas series, default=400
            CO2 concentration outdoors in ppm.

        standard: str
            standard applied for evaluation, support "EN", "LEHB", "SS", "HK", "UBA", "DOSH", "NBR", see Notes.

    Returns:
        report: dict
            IAQ report as dictionary, includes calculated 'indices' / applied 'standard'
            raw data indoors 'co2_indoor' / outdoors 'co2_outdoor'.
        indices: list
            IAQ indices, see Notes.

    Notes:
        - EN: European standard CEN/EN 16798-1, based on german version DIN EN 16798-1:2019 (Page 55).
        Evaluation based on CO2 concentration differences between indoors and outdoors.
            - [Index = 1] Category I: delta(CO2) <= 550 ppm
            - [Index = 2] Category II: delta(CO2) <= 800 ppm
            - [Index = 3] Category III: delta(CO2) <= 1350 ppm
            - [Index = 4] Category IV: delta(CO2) > 1350 ppm

        - LEHB: Japanese law for environmental health in buildings (LEHB).
        Evaluation based on CO2 concentration indoors.
            - [Index = 1] Acceptable: CO2 <= 1000 ppm
            - [Index = 2] Unacceptable: CO2 > 1000 ppm

        - SS: Singapore standard SS 554:2016 (Page 22).
        Evaluation based on CO2 concentration differences between indoors and outdoors.
            - [Index = 1] Acceptable: delta(CO2) <= 700 ppm
            - [Index = 2] Unacceptable: delta(CO2) > 700 ppm

        - HK: Hong Kong Environmental Protection Department.
        "Hongkong Guidance Notes for the Management of Indoor Air Quality in Offices and Public Places" (Page 17).
        Evaluation based on CO2 concentration indoors (averaging time 8-hour). Here the average is changed
        to an instantaneous evaluation for each measurment.
            - [Index = 1] Excellent Class: CO2 <= 800 ppm
            - [Index = 2] Good Class: CO2 <= 1000 ppm
            - [Index = 3] Unacceptable: CO2 > 1000 ppm

        - UBA: German environmental protection agency (Umweltbundesamt).
        "Gesundheitsschutz 11-2008: Gesundheitliche Bewertung von Kohlendioxid in der Innenraumluft" (Page 1368).
        Evaluation based on CO2 concentration indoors.
            - [Index = 1] Hygienically safe: CO2 < 1000 ppm
            - [Index = 2] Hygienically conspicuous: CO2 <= 2000 ppm
            - [Index = 3] Hygienically unacceptable: CO2 > 2000 ppm

        - DOSH: Department of Occupational Safety and Health (DOSH) Malaysia.
        "Industry Code of Practice on Indoor Air Quality 2010 (ICOP IAQ 2010)."
        Evaluation based on CO2 concentration indoors.
            - [Index = 1] Acceptable: CO2 <= 1000 ppm
            - [Index = 2] Unacceptable: CO2 > 1000 ppm

        - NBR: Brazilian standard ABNT NBR 16401-3:2008
            "Air-conditioning installations – Central and unitary systems – Part 3: Indoor air quality"
            and ABNT NBR 17037:2023
            "Indoor air quality in artificially heated non-residential environments – Referential standards"
        Evaluation based on CO2 concentration differences between indoors and outdoors.
            - [Index = 1] Acceptable: delta(CO2) <= 700 ppm
            - [Index = 2] Unacceptable: delta(CO2) > 700 ppm
    """
    standards = ["EN", "LEHB", "SS", "HK", "UBA", "DOSH", "NBR"]
    if standard not in standards:
        raise ValueError(
            f"Error: Unknow standard for iaq_co2(). Supported standards are {standards}."
        )

    # convert to list
    ## indoor
    if isinstance(co2_indoor, (float, int)):
        co2_indoor_list = [float(co2_indoor)]
    elif isinstance(co2_indoor, list):
        co2_indoor_list = [float(x) for x in co2_indoor]
    else:
        raise TypeError("co2_indoor must be a float, int, or list of floats/ints.")

    if isinstance(co2_outdoor, (float, int)):
        co2_outdoor_is_list = False
        co2_outdoor_scalar = float(co2_outdoor)
    elif isinstance(co2_outdoor, list):
        co2_outdoor_is_list = True
        if len(co2_outdoor) != len(co2_indoor_list):
            raise ValueError(
                "Error: co2_indoor and co2_outdoor have different length. "
                "They have to be aligned if using dynamic outdoor CO2 concentration!"
            )
        co2_outdoor_list = [float(x) for x in co2_outdoor]
    else:
        raise TypeError("co2_outdoor must be a float, int, or list of floats/ints.")

    report = {}
    indices = []

    for i in range(0, len(co2_indoor_list)):
        co2_indoor_i = co2_indoor_list[i]

        if co2_outdoor_is_list:
            co2_outdoor_i = co2_outdoor_list[i]
        else:
            co2_outdoor_i = co2_outdoor_scalar

        if standard == "LEHB":
            source = "Japanese law for environmental health in buildings (LEHB)"
            index = _iaq_co2_single_th(co2_indoor_i, threshold=1000, includingth=True)
        elif standard == "SS":
            source = "Singapore standard SS 554:2016"
            index = _iaq_delta_co2_single_th(
                co2_indoor_i, co2_outdoor_i, threshold=700, includingth=True
            )
        elif standard == "HK":
            source = "Hong Kong Environmental Protection Department"
            index = _iaq_co2_hk(co2_indoor_i)
        elif standard == "UBA":
            source = "German environmental protection agency"
            index = _iaq_co2_uba(co2_indoor_i)
        elif standard == "DOSH":
            source = "Department of Occupational Safety and Health (DOSH) Malaysia"
            index = _iaq_co2_single_th(co2_indoor_i, threshold=1000, includingth=True)
        elif standard == "NBR":
            source = "Brazilian standard ABNT NBR 16401-3:2008 and ABNT NBR 17037:2023"
            index = _iaq_delta_co2_single_th(
                co2_indoor_i, co2_outdoor_i, threshold=700, includingth=True
            )
        else:
            # default: EN standard
            source = "European standard CEN/EN 16798-1, based on german version DIN EN 16798-1:2019"
            index = _iaq_co2_en(co2_indoor_i, co2_outdoor_i)

        indices.append(index)

    report["indices"] = indices
    report["standard"] = source
    report["co2_indoor"] = co2_indoor
    report["co2_outdoor"] = co2_outdoor

    return report, indices


def _iaq_co2_en(co2_indoor: Union[float, int], co2_outdoor: Union[float, int]) -> int:
    """
    Helper function to calculate IAQ index for a single measurement based on CEN/EN 16798-1.

    Args:
        co2_indoor : float or int
            single data point of CO2 concentration indoors in ppm.
        co2_outdoor : float or int
            single data point of CO2 concentration outdoors in ppm.

    Returns:
        index : int
            single IAQ index, range 1 (best) - 4 (worst), corresponds to categories I-IV in EN 16798-1.
    """
    delta_co2 = co2_indoor - co2_outdoor
    if delta_co2 <= 550:
        index = 1
    elif delta_co2 <= 800:
        index = 2
    elif delta_co2 <= 1350:
        index = 3
    else:
        index = 4

    return index


def _iaq_co2_hk(co2_indoor: Union[float, int]) -> int:
    """
    Helper function to calculate IAQ index for a single measurement based on Hongkong EPD standard.

    Args:
        co2_indoor : float or int
            single data point of CO2 concentration indoors in ppm.

    Returns:
        index : int
            single IAQ index, range 1 (best) - 3 (worst), corresponds to
            categories Excellent Class (1) / Good Class (2) / Unacceptable (3).
    """
    if co2_indoor <= 800:
        index = 1
    elif co2_indoor <= 1000:
        index = 2
    else:
        index = 3

    return index


def _iaq_co2_uba(co2_indoor: Union[float, int]) -> int:
    """
    Helper function to calculate IAQ index for a single measurement based on German EPA standard (Umweltbundesamt).

    Args:
        co2_indoor : float or int
            single data point of CO2 concentration indoors in ppm.

    Returns:
        index : int
            single IAQ index, range 1 (best) - 3 (worst), corresponds to
            categories hygienically safe (1) / hygienically conspicuous (2) / Hygienically unacceptable (3).
    """
    if co2_indoor < 1000:
        index = 1
    elif co2_indoor <= 2000:
        index = 2
    else:
        index = 3

    return index


def _iaq_co2_single_th(
    co2_indoor: Union[float, int], threshold: Union[float, int], includingth: bool
) -> int:
    """
    Helper function to calculate IAQ index for a single measurement based on co2 concentration indoors and
    a single threshold value.

    Args:
        co2_indoor : float or int
            single data point of CO2 concentration indoors in ppm.
        threshold : float or int
            threshold value for acceptable IAQ
        includingth : bool
            whether or not the threshold value is included for acceptable IAQ, depends on standard.

    Returns:
        index : int
            single IAQ index, range 1 (accpetable) - 2 (unacceptable).
    """
    if includingth is True:
        # acceptable including threshold, 1: acceptable, 2: unacceptable
        index = 1 if co2_indoor <= threshold else 2
    else:
        index = 1 if co2_indoor < threshold else 2

    return index


def _iaq_delta_co2_single_th(
    co2_indoor: Union[float, int],
    co2_outdoor: Union[float, int],
    threshold: Union[float, int],
    includingth: bool,
) -> int:
    """
    Helper function to calculate IAQ index for a single measurement based on co2 concentration difference
    indoors/outdoors and a single threshold value.

    Args:
        co2_indoor : float or int
            single data point of CO2 concentration indoors in ppm.
        co2_outdoor : float or int
            single data point of CO2 concentration outdoors in ppm.
        threshold : float or int
            threshold value for acceptable IAQ
        includingth : bool
            whether or not the threshold value is included for acceptable IAQ, depends on standard.

    Returns:
        index : int
            single IAQ index, range 1 (accpetable) - 2 (unacceptable).
    """
    delta_co2 = co2_indoor - co2_outdoor
    if includingth is True:
        # acceptable including threshold, 1: acceptable, 2: unacceptable
        index = 1 if delta_co2 <= threshold else 2
    else:
        index = 1 if delta_co2 < threshold else 2

    return index
