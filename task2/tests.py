import json
import numpy as np

from scipy.special import erfc, gammainc

from constsnts import (
    BINARY_SEQUENCE_CPP_TXT,
    BINARY_SEQUENCE_JAVA_TXT,
    PII
)


def read_sequence(path: str) -> str:
    """
    reads a bit sequence from a file
    :param path: sequence file
    :return: string with sequence
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError as e:
        print(f"Error: File not found at path {path}. {e}")
        raise
    except IOError as e:
        print(f"Error reading file {path}. {e}")
        raise


def frequency_test(_sequence: str) -> float:
    """
    checks the generated sequence for randomness using frequency analysis
    :param _sequence: sequence
    :return: randomness coefficient of a sequence
    """
    sn = abs(sum(1 if char == '1' else -1 for char in _sequence) / np.sqrt(len(_sequence)))
    return erfc(sn/np.sqrt(2))


def frequency_of_units(_sequence: str) -> float:
    """
    counts the frequency of occurrence of ones in a string
    :param _sequence: sequence
    :return: frequency of occurrence of ones
    """
    return _sequence.count('1') / len(_sequence)


def count_sign_changes(_sequence: str) -> int:
    """
    counts the number of value changes in a sequence
    :param _sequence: sequence
    :return: number of value changes
    """
    count = 0
    previous_char = _sequence[0]

    for char in _sequence[1:]:
        if char != previous_char:
            count += 1
            previous_char = char

    return count


def block_test(_sequence: str) -> float:
    """
    test for identical consecutive bits
    :param _sequence: sequence
    :return: randomness coefficient of a sequence
    """
    freq = frequency_of_units(_sequence)
    if abs(freq - 0.5) < 2 / np.sqrt(len(_sequence)):
        sign_changes = count_sign_changes(_sequence)
        return erfc(abs(sign_changes - 2 * len(_sequence) * freq * (1 - freq)) /
                    (2 * np.sqrt(2 * len(_sequence)) * freq * (1 - freq)))
    else:
        return 0


def analyze_blocks(_sequence: str) -> list:
    """
    counts the maximum number of consecutive units in blocks of a sequence
    :param _sequence: sequence
    :return: array with the number of occurrences of consecutive units of different lengths
    """
    block_size = 8
    blocks = [_sequence[i:i + block_size] for i in range(0, len(_sequence), block_size)]
    counts = [0] * 4

    for block in blocks:
        max_run = 0
        current_run = 0

        for char in block:
            if char == '1':
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0

        match max_run:
            case run if run <= 1:
                counts[0] += 1
            case 2:
                counts[1] += 1
            case 3:
                counts[2] += 1
            case _:
                counts[3] += 1

    return counts


def longest_run_test(_sequence: str) -> float:
    """
    Longest Sequence of ones Test
    :param _sequence: sequence
    :return: randomness coefficient of a sequence
    """
    units_counts = analyze_blocks(_sequence)
    xi_sqared = 0
    for i in range(4):
        xi_sqared += (units_counts[i] - 16 * PII[i]) ** 2 / (16 * PII[i])
    return gammainc(1.5, xi_sqared / 2)


def save_results_to_json(results: dict, filename: str) -> None:
    """
    Saves the results of checks to a JSON file

    :param results: dictionary with results
    :param filename: file name to save
    """
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=4)


def test_status(p: float) -> str:
    """
    Determines the status of a test based on its p-value

    :param p: p-value of the test

    :return: Test status line
    """
    return "Passed" if p > 0.01 else "Not passed"


if __name__ == "__main__":
    res = {}

    binary_sequence_java = read_sequence(BINARY_SEQUENCE_JAVA_TXT)
    binary_sequence_cpp = read_sequence(BINARY_SEQUENCE_CPP_TXT)

    for lang, sequence in zip(["Java", "C++"], [binary_sequence_java, binary_sequence_cpp]):
        res[lang] = {}
        p_value = frequency_test(sequence)
        res[lang]['Frequency test'] = {
            'p-value': p_value,
            'Status': test_status(p_value)
        }
        print(f'Frequency test {lang}: p-value = {p_value}, Статус = {res[lang]["Frequency test"]["Status"]}')

        p_value = block_test(sequence)
        res[lang]['Test for identical consecutive bits'] = {
            'p-value': p_value,
            'Status': test_status(p_value)
        }
        print(
            f'Test for identical consecutive bits {lang}: p-value = {p_value}, Статус = {res[lang]["Test for identical consecutive bits"]["Status"]}')

        p_value = longest_run_test(sequence)
        res[lang]['Longest Sequence of 1s Test'] = {
            'p-value': p_value,
            'Status': test_status(p_value)
        }
        print(
            f'Longest Sequence of 1s Test{lang}: p-value = {p_value}, Статус = {res[lang]["Longest Sequence of 1s Test"]["Status"]}')
    save_results_to_json(res, 'results.json')
