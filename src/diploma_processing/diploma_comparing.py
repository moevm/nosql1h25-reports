from src.diploma_processing.data_types import Diploma


def calc_similarity(diploma1: Diploma, diploma2: Diploma) -> float:
    """
    Finds the normalized count of similar integer values in two lists.

    The result is in the range [0, 100], where 100 indicates all elements in
    the shorter list are present in the longer list, and 0 indicates no
    common elements. The normalization factor is the length of the *shorter* list.

    Args:
      diploma1: The first diploma.
      diploma2: The second diploma.

    Returns:
      The normalized count of similar integers (a float in [0, 100]).
    """

    set1 = set(diploma1.shingles)
    set2 = set(diploma2.shingles)

    common_elements = set1.intersection(set2)
    common_count = len(common_elements)

    normalization_factor = min(len(set1), len(set2))

    if normalization_factor == 0:  # Handle the case where either list is empty.
        return 0.0
    else:
        return float(common_count) / normalization_factor * 100
