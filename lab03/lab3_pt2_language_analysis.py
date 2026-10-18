# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "scikit-learn>=1.9", "wikipedia-api>=0.16"]
# ///

# Joshua Evans (thejoshuaevans.com) 2026-10-18
# Developed with some help from Claude

# This is the implementation for Lab 3 Part 2 Group A (Exercise 1): Language Analysis
# https://lcc-cit.github.io/CS212-CourseMaterials/Tutorials/scikit-learn-1.7/WorkingWithTextData.html

# The "fetch_data" utility has been rolled into this file as the `_fetch_language_data` and `_chunk` functions,
# so this file can be run by itself - it will automatically fetch and prepare the language data if necessary.
# Requires: numpy, wikipedia-api, and scikit-learn. If using uv, dependencies will be installed automatically
#           using the inline script metadata above, otherwise you may need to install them manually.
import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import wikipediaapi
from numpy.typing import NDArray
from sklearn import metrics
from sklearn.datasets import load_files
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Perceptron
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline

USER_AGENT = "LCC-CS212-Lab3 (https://thejoshuaevans.com)"
LANGUAGES = ["ar", "de", "en", "es", "fr", "it", "ja", "nl", "pl", "pt", "ru"]
MIN_PARAGRAPH_CHARS = 100
SHORT_SAMPLE_WORDS = 5
SHORT_SAMPLE_CHARS_JA = 12  # Japanese words average ~2 characters, so ~5 words
MAX_SHORT_SAMPLES = 1000


# Written by Claude Opus 5.5
def _chunk(text: str, lang: str) -> list[str]:
    """
    Cut a paragraph into short samples of about five words each

    (Written by Claude Opus 5.5)

    Args:
        text (str): The paragraph to cut up
        lang (str): Its language code. Japanese is cut by characters, since it does
            not put spaces between words

    Returns:
        list[str]: The full-length samples, in order; a shorter remainder is dropped
    """
    if lang == "ja":
        units, size, sep = list(" ".join(text.split())), SHORT_SAMPLE_CHARS_JA, ""
    else:
        units, size, sep = text.split(), SHORT_SAMPLE_WORDS, " "
    return [
        sep.join(units[i : i + size]) for i in range(0, len(units) - size + 1, size)
    ]


def _fetch_language_data(root: Path) -> None:
    """
    Download the "Wikipedia" article in each of LANGUAGES and write it as samples

    Writes `paragraphs/<lang>/<lang>_NNNN.txt` (one paragraph per file) and
    `short_paragraphs/<lang>/<lang>_NNNN.txt` (about five words per file) under root.

    (Written by Claude Opus 5.5)

    Args:
        root (Path): The directory to write both data folders into
    """
    english = wikipediaapi.Wikipedia(USER_AGENT, "en").page("Wikipedia")
    for lang in LANGUAGES:
        print(f"    Fetching {lang}...")
        page = english if lang == "en" else english.langlinks[lang]
        paragraphs = [
            p for p in page.text.splitlines() if len(p) >= MIN_PARAGRAPH_CHARS
        ]
        short = [c for p in paragraphs for c in _chunk(p, lang)][:MAX_SHORT_SAMPLES]
        for folder, samples in (
            ("paragraphs", paragraphs),
            ("short_paragraphs", short),
        ):
            out_dir = root / folder / lang
            out_dir.mkdir(parents=True, exist_ok=True)
            for i, sample in enumerate(samples):
                (out_dir / f"{lang}_{i:04d}.txt").write_text(sample, encoding="utf-8")


@dataclass
class Dataset:
    data: list[bytes]
    """A list of raw input data for this set"""

    labels: NDArray[np.int64]
    """The labels for this data set, as an array parallel to data"""


@dataclass
class SplitData:
    training: Dataset
    """Data to use for training"""

    testing: Dataset
    """Data to use for testing"""

    target_names: list[str]
    """List of target names parallel to the possible label values"""


def _parse_arguments() -> argparse.Namespace:
    """
    Read the command line arguments

    Returns:
        argparse.Namespace: The parsed arguments, one attribute per argument
    """
    parser = argparse.ArgumentParser(
        description="Perform language analysis on wikipedia pages"
    )
    parser.add_argument(
        "data_folder",
        nargs="?",
        default="paragraphs",
        help="directory holding the language data",
    )
    parser.add_argument(
        "--search", action="store_true", help="run a grid search on the pipeline"
    )

    return parser.parse_args()


def _get_split_data(
    dirname: str, test_size: float = 0.5, random_state: int = 42
) -> SplitData:
    """
    Retrieve data from a directory with labeled sub-directories, and splits the data
    into "training" and "testing" corpuses. Downloads the language data from
    Wikipedia first if the directory does not exist.

    Args:
        dirname (str): The directory to retrieve data from

    Returns:
        (SplitData): Data and labels, split into "training" and "testing" sets
    """
    # Normalize the dirname
    root_dir_name = Path(__file__).parent  # The directory containing this script
    full_path = Path(root_dir_name, dirname)
    if not full_path.exists():
        print("No data found, downloading data...")
        _fetch_language_data(full_path.parent)
        print(f"Data downloaded to {full_path.parent}")

    # Load the data
    data_raw = load_files(full_path)

    # Split the data into "training" and "testing" sets
    data_train, data_test, labels_train, labels_test = train_test_split(
        data_raw.data, data_raw.target, test_size=test_size, random_state=random_state
    )
    return SplitData(
        Dataset(data_train, labels_train),
        Dataset(data_test, labels_test),
        data_raw.target_names,
    )


def _fit_data(dataset: Dataset, search: bool = False) -> Pipeline | GridSearchCV:
    """
    Create a pipeline and fit it to the provided dataset. Can also perform a grid search

    Args:
        dataset (Dataset): The data to use for fitting the classifier
        search (bool): If a grid search should be performed. Default `False`

    Returns:
        (Pipeline | GridSearchCV): A regular `Pipeline` if no search was requested, otherwise a `GridSearchCV`
    """
    # Create the pipeline
    text_clf = Pipeline(
        [
            ("vect", TfidfVectorizer(analyzer="char", ngram_range=(1, 3))),
            ("clf", Perceptron(random_state=42)),
        ]
    )

    fit_clf = None
    if search:
        # Grid search was requested
        parameters = {
            "vect__analyzer": ["char", "char_wb"],
            "vect__ngram_range": [(1, 2), (1, 3), (1, 4)],
        }
        gs_clf = GridSearchCV(text_clf, parameters, cv=5, n_jobs=-1)
        fit_clf = gs_clf.fit(dataset.data, dataset.labels)
    else:
        # No grid search, just fit the pipeline as-is
        fit_clf = text_clf.fit(dataset.data, dataset.labels)

    return fit_clf


if __name__ == "__main__":
    # Get arguments and the data
    args = _parse_arguments()

    print("Starting language analysis. Fetching and preparing data if necessary...")
    split_data = _get_split_data(args.data_folder)
    print("Data preparation complete.\n")

    # Fit the data
    print("Fitting the classifier to the training data...")
    fit_clf = _fit_data(split_data.training, search=args.search)
    print("Classifier fitting complete.\n")

    if args.search:
        # If we are in "search" mode, print the identified "best" parameters
        print("Search mode enabled.")
        print(f"    Best score: {fit_clf.best_score_}")
        for name, value in sorted(fit_clf.best_params_.items()):
            print(f"    {name}: {value!r}")

    # Perform the prediction and render the report
    print("Performing predictions on the test data...")
    predicted = fit_clf.predict(split_data.testing.data)
    print("Prediction complete.\n")

    print("Classification Report:")
    print(
        metrics.classification_report(
            split_data.testing.labels, predicted, target_names=split_data.target_names
        )
    )
    print("Done!")
else:
    raise RuntimeError("This script should be run as the main module.")
