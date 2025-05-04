from rapidfuzz import fuzz, process
import numpy as np

from src.diploma_processing.data_types import Diploma

SHINGLE_SIM_THRESHOLD = 70


def calc_similarity(diploma1: Diploma, diploma2: Diploma, threshold=SHINGLE_SIM_THRESHOLD) -> float:
    """
    Calculates the similarity between two diplomas based on their shingles.

    This function computes a similarity matrix between the shingles of two diplomas
    using the fuzz.ratio scorer.  It then aggregates the similarity scores to
    produce a single similarity metric.

    Args:
        diploma1: The first diploma.
        diploma2: The second diploma.
        threshold: The minimum similarity score to consider a shingle as similar.

    Returns:
        A int representing the similarity between the two diplomas (%),
        ranging from 0 to 100.  A higher value indicates greater similarity.
    """

    similarity_matrix = process.cdist(
        queries=diploma1.shingles,
        choices=diploma2.shingles,
        scorer=fuzz.ratio,
        workers=-1
    )

    # Find the maximum similarity for each shingle in diploma1
    max_similarities_diploma1 = np.max(similarity_matrix, axis=1)

    # Find the maximum similarity for each shingle in diploma2
    max_similarities_diploma2 = np.max(similarity_matrix, axis=0)  # Axis 0 for columns

    # Calculate the number of shingles in diploma1 that have a similarity
    # greater than the threshold with any shingle in diploma2
    count_above_threshold_diploma1 = np.sum(max_similarities_diploma1 > threshold)

    # Calculate the number of shingles in diploma2 that have a similarity
    # greater than the threshold with any shingle in diploma1
    count_above_threshold_diploma2 = np.sum(max_similarities_diploma2 > threshold)


    # Calculate the Jaccard-like index
    union = len(diploma1.shingles) + len(diploma2.shingles) - (count_above_threshold_diploma1 + count_above_threshold_diploma2) / 2
    intersection = (count_above_threshold_diploma1 + count_above_threshold_diploma2) / 2

    if union == 0:
        return 0.0  # Handle the case where both sets are empty

    return intersection / union * 100