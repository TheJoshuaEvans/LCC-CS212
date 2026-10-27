# /// script
# requires-python = ">=3.12"
# dependencies = ["scikit-learn>=1.9"]
# ///

# Joshua Evans (thejoshuaevans.com) 2026-10-22

# This is the implementation for Lab 4 Group A: Evaluating Text Classifiers (ChatGPT vs. Human)
# https://lcc-cit.github.io/CS212-CourseMaterials/Labs/Lab04-ClassifierEvaluation/GroupA/CS212_Lab04_Instructions_GroupA.html

# Developed with some assistance from Claude Opus 5.5

# To run this file and perform every step in sequence, use:
# ```
# uv run lab4_chatgpt_vs_human.py
# ```

# To run a particular step, use:
# ```
# uv run lab4_chatgpt_vs_human.py --step 3
# ```

import argparse
import json
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
from numpy.typing import NDArray
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

socket.setdefaulttimeout(60)  # give up with an error instead of waiting forever

BASE_URL = "https://huggingface.co/datasets/Hello-SimpleAI/HC3/resolve/main/"

# Step 7: paragraphs to rate with the tuned classifier
HUMAN_PARAGRAPH = """A hash table is a data structure that allows us to store data using an identifying "hash" or "key", so \
that we can then retrieve it extremely quickly with the same key. They are similar in concept to "dictionaries" in Python \
or "Maps" in JavaScript, but a "hash table" is a specific implementation that uses a "hashing" function to assign every value \
an array index. This does mean that conflicts are possible, and become inevitable as the data set grows, so various strategies \
are used to minimize this effect - like increased memory usage or using nested data structures"""


# Written by Claude Opus 5.5 on 2026-10-26, when asked for a paragraph about a computer science concept
CHATBOT_PARAGRAPH = """A hash table stores values under keys and finds them again in roughly constant time, no \
matter how many entries it holds. It does this by running each key through a hash function, which turns the key \
into a number, and using that number to pick a slot in an array. Two different keys can land in the same slot, so \
every hash table needs a way to handle these collisions, such as keeping a short list in each slot or probing for \
the next free one. When the table gets too full, collisions become common and lookups slow down, so most \
implementations grow the array and re-insert every entry once a set fraction of the slots is in use."""


# region Helpers


@dataclass
class Dataset:
    data: list[str]
    """A list of raw input data for this set"""

    labels: NDArray[np.int64]
    """The labels for this data set, as an array parallel to data"""


def parse_arguments() -> argparse.Namespace:
    """
    Read the command line arguments

    Returns:
        argparse.Namespace: The parsed arguments, one attribute per argument
    """
    parser = argparse.ArgumentParser(
        description="Evaluate text classifiers (ChatGPT vs. Human)"
    )
    parser.add_argument(
        "--step",
        type=int,
        choices=range(1, 8),
        default=0,
        help="run only this step of the lab (1-7); runs every step in sequence when omitted",
    )

    return parser.parse_args()


def get_relative_path(path: str) -> Path:
    """
    Get the path relative to this script's location.

    Args:
        path (str): The relative path to resolve

    Returns:
        Path: The absolute path relative to this script's location
    """
    return Path(Path(__file__).parent) / path


def fetch_data(data_dir: str) -> None:
    """
    Fetch the HC3 data files if they do not exist at the given path.

    Args:
        data_dir (str): The directory where the data files should be located
    """
    path = get_relative_path(data_dir)
    if not path.exists():
        print("No data found, downloading data...")
        os.makedirs(path, exist_ok=True)
        for name in ["wiki_csai.jsonl", "open_qa.jsonl"]:
            print("Downloading", name)
            urlretrieve(BASE_URL + name, os.path.join(path, name))
        print("Data downloaded.")


def load_hc3(path: str) -> tuple[list[str], list[str], list[str]]:
    """
    Read an HC3 file. Returns three lists with one item per question:
    the questions, the first human answer and the first ChatGPT answer.

    Args:
        path (str): The relative path to the HC3 file

    Returns:
        tuple[list[str], list[str], list[str]]: The questions, human answers, and ChatGPT answers
    """
    path = get_relative_path(path)
    questions = []
    human_answers = []
    chatgpt_answers = []
    with open(path, encoding="utf-8") as file:
        for line in file:
            item = json.loads(line)
            questions.append(item["question"])
            human_answers.append(item["human_answers"][0])
            chatgpt_answers.append(item["chatgpt_answers"][0])
    return questions, human_answers, chatgpt_answers


def make_samples(
    human_answers: list[str], chatgpt_answers: list[str], question_numbers: list[int]
) -> Dataset:
    """
    Build the texts and labels (0 = human, 1 = ChatGPT) for the chosen questions.

    Args:
        human_answers (list[str]): The list of human answers
        chatgpt_answers (list[str]): The list of ChatGPT answers
        question_numbers (list[int]): The indices of the questions to include

    Returns:
        Dataset: A dataset containing the texts and corresponding labels
    """
    texts = []
    labels = []
    for number in question_numbers:
        texts.append(human_answers[number])
        labels.append(0)
        texts.append(chatgpt_answers[number])
        labels.append(1)
    return Dataset(texts, np.array(labels, dtype=np.int64))


# endregion
# region Display


def format_confusion(matrix: NDArray[np.int64], names: list[str]) -> str:
    """
    Format a confusion matrix as a string for display.

    Args:
        matrix (NDArray[np.int64]): The confusion matrix to format
        names (list[str]): The names of the classes corresponding to the matrix rows and columns

    Returns:
        str: The formatted confusion matrix as a string
    """
    width = max(len(n) for n in names) + 2
    header = " " * width + "".join(f"{'→ ' + n:>{width}}" for n in names)
    rows = [
        f"{n:<{width}}" + "".join(f"{v:>{width}}" for v in row)
        for n, row in zip(names, matrix, strict=True)
    ]
    return "\n".join([header, *rows])


def print_evaluate_classifier(clf: Pipeline | GridSearchCV, dataset: Dataset) -> None:
    """
    Evaluate a classifier on a given dataset and return the accuracy.

    Args:
        clf (Pipeline | GridSearchCV): The classifier to evaluate
        dataset (Dataset): The dataset to evaluate on
    """
    predicted = clf.predict(dataset.data)
    accuracy = np.mean(predicted == dataset.labels)
    print("Test accuracy:", accuracy)
    print("\nClassification report:")
    print(metrics.classification_report(dataset.labels, predicted))
    print("\nConfusion matrix:")
    print(
        format_confusion(
            metrics.confusion_matrix(dataset.labels, predicted),
            ["human", "chatgpt"],
        )
    )


def print_rate_paragraph(clf: Pipeline, name: str, paragraph: str) -> None:
    """
    Print how likely a classifier thinks a single paragraph is to be human or ChatGPT writing.

    Args:
        clf (Pipeline): A fitted classifier that supports predict_proba
        name (str): A label for the paragraph, printed in the heading
        paragraph (str): The text to rate
    """
    human, chatgpt = clf.predict_proba([paragraph])[0]
    print(f"--- {name} ({len(paragraph.split())} words)")
    print(f"P(human) = {human:.3f}, P(ChatGPT) = {chatgpt:.3f}")


# endregion
# region Fitting


def fit_baseline(dataset: Dataset) -> Pipeline:
    """
    Create a baseline pipeline and fit it to the provided dataset.

    Args:
        dataset (Dataset): The data to use for fitting the classifier

    Returns:
        (Pipeline): A regular `Pipeline`
    """
    # Create the pipeline
    text_clf = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )

    fit_clf = text_clf.fit(dataset.data, dataset.labels)
    return fit_clf


def fit_comparisons(dataset: Dataset) -> list[Pipeline]:
    """
    Create multiple fit classifiers with different configurations for comparison.

    Args:
        dataset (Dataset): The dataset to use for fitting the classifiers

    Returns:
        list[Pipeline]: The fitted comparison classifier pipelines
    """
    pipelines = {}

    # The default pipeline
    default_clf = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )
    default_clf = default_clf.fit(dataset.data, dataset.labels)
    pipelines["default"] = default_clf

    # Words / Word pairs
    word_pair_clf = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )
    word_pair_clf = word_pair_clf.fit(dataset.data, dataset.labels)
    pipelines["word_pair"] = word_pair_clf

    # Characters
    characters_clf = Pipeline(
        [
            ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(2, 4))),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )
    characters_clf = characters_clf.fit(dataset.data, dataset.labels)
    pipelines["characters"] = characters_clf

    # Stop words
    stop_words_clf = Pipeline(
        [
            ("tfidf", TfidfVectorizer(stop_words="english")),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )
    stop_words_clf = stop_words_clf.fit(dataset.data, dataset.labels)
    pipelines["stop_words"] = stop_words_clf

    return pipelines


def fit_grid_search(dataset: Dataset) -> GridSearchCV:
    """
    Perform a grid search to find the best hyperparameters for a classifier.

    Args:
        dataset (Dataset): The dataset to use for the grid search

    Returns:
        GridSearchCV: The fitted grid search object
    """
    clf = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )

    # ruff: disable[ERA001]
    # This grid search was refined over time. Previous versions:
    # V1
    # "tfidf__analyzer": ["char"],
    # "tfidf__ngram_range": [(1, 1), (1, 2), (2, 3), (2, 4)],
    # "tfidf__min_df": [1, 2, 5],
    # "clf__C": [1, 10, 100, 1000],
    # Best parameters found: {'clf__C': 100, 'tfidf__analyzer': 'char', 'tfidf__min_df': 5, 'tfidf__ngram_range': (2, 4)}

    # V2
    # "tfidf__analyzer": ["char"],
    # "tfidf__ngram_range": [(1, 3), (1, 4), (2, 4), (3, 4), (3, 5)],
    # "tfidf__min_df": [3, 5, 7],
    # "clf__C": [50, 100, 500],
    # Best parameters found: {'clf__C': 100, 'tfidf__analyzer': 'char', 'tfidf__min_df': 3, 'tfidf__ngram_range': (3, 5)}
    # ruff: enable[ERA001]

    # V3
    param_grid = {
        "tfidf__analyzer": ["char"],
        "tfidf__ngram_range": [(2, 5), (3, 5), (4, 5), (2, 6), (3, 6), (4, 6)],
        "tfidf__min_df": [3, 4],
        "clf__C": [100],
    }
    grid_search = GridSearchCV(clf, param_grid, cv=5, verbose=2, n_jobs=-1)
    return grid_search.fit(dataset.data, dataset.labels)


def fit_optimal(dataset: Dataset) -> Pipeline:
    """
    Fit a classifier with the optimal hyperparameters found from the grid search.

    Args:
        dataset (Dataset): The dataset to fit the classifier on

    Returns:
        Pipeline: The fitted classifier pipeline with optimal hyperparameters
    """
    clf = Pipeline(
        [
            ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 6), min_df=3)),
            ("clf", LogisticRegression(max_iter=1000, C=100)),
        ]
    )
    return clf.fit(dataset.data, dataset.labels)


# endregion
# region Main


# Start here! :D
if __name__ == "__main__":
    # Get arguments
    args = parse_arguments()
    step = args.step

    # Fetch and load the datasets
    fetch_data("data")
    questions, human_answers, chatgpt_answers = load_hc3("data/wiki_csai.jsonl")

    # Split the questions into training and test sets
    question_numbers = list(range(len(questions)))
    train_numbers, test_numbers = train_test_split(
        question_numbers, test_size=0.25, random_state=42
    )
    train_dataset = make_samples(human_answers, chatgpt_answers, train_numbers)
    test_dataset = make_samples(human_answers, chatgpt_answers, test_numbers)

    # Also get the alternative "QA" dataset
    qa_questions, qa_human_answers, qa_chatgpt_answers = load_hc3("data/open_qa.jsonl")
    qa_question_numbers = list(range(len(qa_questions)))
    qa_dataset = make_samples(qa_human_answers, qa_chatgpt_answers, qa_question_numbers)

    if step == 0 or step == 1:
        print("\n=== Step 1: Baseline ===")

        # Fit the training data
        clf_baseline = fit_baseline(train_dataset)

        # Evaluate the classifier on the test data
        print_evaluate_classifier(clf_baseline, test_dataset)

    if step == 0 or step == 2:  # noqa: PLR2004
        print("\n=== Step 2: Experiment 1: Which features work best? ===")

        # Perform cross-validation on the training data
        classifiers = fit_comparisons(train_dataset)
        for name, clf in classifiers.items():
            scores = cross_val_score(
                clf, train_dataset.data, train_dataset.labels, cv=5
            )
            print(f"{name}: {scores.mean():.3f} ± {scores.std():.3f}")

        # QUESTIONS:
        # Which features were best? Is the difference bigger than the standard deviation? If not, you can’t say one is really better.
        # > Turns out "characters" (analyzer="char", ngram_range=(2, 4)) produces the best results of the proposed features (0.924 ± 0.011 vs a second best of 0.899 ± 0.010)

        # What happened when you removed the stop words? Does that surprise you? (Think about what kind of words are in the list.)
        # > Removing stop words moderately decreased performance, reducing accuracy to 0.862 ± 0.020. I think it's likely that the "stop words" take up such a large percentage
        # > of the dataset that we reduce our training surface too much when we use them

    if step == 0 or step == 3:  # noqa: PLR2004
        print("\n=== Step 3: Look inside the classifier ===")
        clf_baseline = fit_baseline(train_dataset)
        words = clf_baseline.named_steps["tfidf"].get_feature_names_out()
        weights = clf_baseline.named_steps["clf"].coef_[0]
        order = np.argsort(
            weights
        )  # positions of the words, from most "human" to most "ChatGPT"
        print(list(words[order[:15]]))  # the 15 most human-like words
        print(list(words[order[-15:]]))  # the 15 most ChatGPT-like words

        # QUESTIONS:
        # Which words are about style, and which are artifacts of how the data was collected? An artifact is something that
        # gives the answer away but wouldn’t be there in real writing.
        # > At first glance, it seems that using digits for numbers (10, 11, 12, 13, 14, 15) is a strong indicator of human-like writing,
        # > however, this is most likely an _artifact_, since the many of the answers from the "wiki" inputs contain references which take
        # > the form of a number within brackets, like in the example "...this formalisation is referred to as human-assisted Turing
        # > machine.[10]"
        #
        # > Beyond these tricky artifacts, it's very hard to tell exactly how the "style" differs between the wiki human answers and
        # > the ChatGPT-generated answers. Perhaps the human responses tend to be more formal? I suppose the difficulty in identifying
        # > the exact style differences is why this is such an interesting problem to try and solve!
        #
        # > In fact... I suspect that step 5 will show that a classifier trained with the wiki data will perform relatively poorly when
        # > applied to other sources of human writing because it will be missing these artifacts that give the game away

    if step == 0 or step == 4:  # noqa: PLR2004
        print("\n=== Step 4: Tune the hyperparameters ===")

        # Grid Search for hyperparameter tuning
        grid_search = fit_grid_search(train_dataset)

        # Print all the info on the best fit
        print_evaluate_classifier(grid_search.best_estimator_, test_dataset)

        # ruff: disable[ERA001]
        # Best parameters found: {
        #   'clf__C': 100,
        #   'tfidf__analyzer': 'char',
        #   'tfidf__min_df': 3,
        #   'tfidf__ngram_range': (3, 6)
        # }
        # ruff: enable[ERA001]

    if step == 0 or step == 5:  # noqa: PLR2004
        print("\n=== Step 5: Experiment 2: A new topic ===")

        # Use the classifier we trained with wiki data on the qa data
        wiki_clf = fit_optimal(train_dataset)
        print_evaluate_classifier(wiki_clf, qa_dataset)

        # QUESTIONS:
        # How much did the accuracy drop compared with the wiki_csai test set?
        # > The accuracy dropped significantly compared with the original test, as I predicted it would in step 3!

        # Which of the two classes did the model get wrong more often? Compare the lengths of the human and
        # ChatGPT answers in the two files (the median number of words is a good measure) and explain what you see.
        # > The model became significantly worse at categorizing the ChatGPT answers correctly, but it did stay
        # > fairly accurate at identifying human answers. For these responses, the ChatGPT answers tended to be
        # > exceptionally verbose and much longer than the human answers. This seems to indicate that, for some reason,
        # > the model would "default" to human when not given very many ngrams to work with, and it becomes much harder
        # > to classify the longer the text becomes. I would hypothesize that if we shortened the ChatGPT answers, the
        # > model would have an even harder time, misclassifying them as human even more often. Is this possibly because
        # > shorter text in the training data would have the "reference" artifacts (like [10]) less often, and these
        # > artifacts are missing in the qa data?
        # >
        # > I guess the beauty of machine learning is that we don't actually need to know!

    if step == 0 or step == 6:  # noqa: PLR2004
        print("\n=== Step 6: Error analysis ===")

        # Go back to using wiki test data on the wiki classifier
        wiki_clf = fit_optimal(train_dataset)
        print_evaluate_classifier(wiki_clf, test_dataset)

        predicted = wiki_clf.predict(test_dataset.data)
        wrong = np.flatnonzero(predicted != test_dataset.labels)
        names = ["human", "ChatGPT"]
        for i in wrong[:5]:
            print(
                f"--- true: {names[test_dataset.labels[i]]}, predicted: {names[predicted[i]]}"
            )
            print(test_dataset.data[i])

        # QUESTIONS:
        # What do the mistakes have in common? Are any of them hard even for you to judge?
        # > I honestly can't identify a clear pattern in the mistakes, I'm can't be sure why any particular answers were
        # > misclassified without carefully studying the entire dataset. However, looking at the samples printed out
        # > in my console, the true classification is _blindingly_ obvious because the ChatGPT answers have 3 empty
        # > lines between each paragraph, and the human answers do not. In fact, this artifact is so strong in my own
        # > brain, it might be part of why I'm not able to identify a clear pattern in the mistakes.

    if step == 0 or step == 7:  # noqa: PLR2004
        print("\n=== Step 7: Optional: your own text ===")

        wiki_clf = fit_optimal(train_dataset)
        print_rate_paragraph(wiki_clf, "My paragraph", HUMAN_PARAGRAPH)
        print_rate_paragraph(wiki_clf, "Chatbot paragraph", CHATBOT_PARAGRAPH)

        # QUESTIONS:
        # Is the model fooled? Why do you think so?
        # > HA! Funnily enough the paragraph I wrote is given a higher probably of being "ChatGPT" (74%), then the paragraph
        # > that was written by Claude Opus 5.5 (61%). Technically it classifies the "ChatGPT" response correctly, but not very
        # > confidently. Our model probably doesn't do particularly well for a few reasons:
        # > - We haven't used nearly enough data to fully generalize the model
        # > - The "wiki" artifacts are corrupting our data and crippling the model
        # > - It has been trained on a set of data generated by a very different model than it is actually working with

else:
    raise RuntimeError("This script should be run as the main module.")
