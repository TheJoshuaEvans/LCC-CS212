# Maksym Kholodenko, 10/17/2026, Group B. Used GitHub Copilot for minimal punctuation corrections and minor suggestions.
# Sentiment classification of positive and negative movie reviews.

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def load_movie_reviews():
    """Load labeled movie reviews from the NLTK movie_reviews corpus."""
    import nltk
    from nltk.corpus import movie_reviews

    try:
        file_ids = movie_reviews.fileids()
    except LookupError:
        print("Downloading the movie reviews dataset...")
        if not nltk.download("movie_reviews", quiet=True):
            raise RuntimeError("Could not download NLTK movie_reviews dataset.")
        file_ids = movie_reviews.fileids()

    documents = [movie_reviews.raw(file_id) for file_id in file_ids]
    labels = [movie_reviews.categories(file_id)[0] for file_id in file_ids]
    return documents, labels


def build_classifier():
    """Create a text-classification pipeline and its parameter search."""
    pipeline = Pipeline([
        ("vect", CountVectorizer()),
        ("tfidf", TfidfTransformer()),
        ("clf", MultinomialNB()),
    ])
    parameters = {
        "vect__ngram_range": [(1, 1), (1, 2)],
        "tfidf__use_idf": [True, False],
        "clf__alpha": [0.1, 1.0],
    }
    return GridSearchCV(pipeline, parameters, cv=3, n_jobs=1)


def main():
    documents, labels = load_movie_reviews()

    # Keep the test documents separate from the grid-search training data.
    train_docs, test_docs, train_labels, test_labels = train_test_split(
        documents, labels, test_size=0.20, random_state=42, stratify=labels
    )

    classifier = build_classifier()
    classifier.fit(train_docs, train_labels)
    predicted = classifier.predict(test_docs)

    print(f"Training reviews: {len(train_docs)}")
    print(f"Test reviews: {len(test_docs)}")
    print(f"Best grid-search parameters: {classifier.best_params_}")
    print(f"Test accuracy: {accuracy_score(test_labels, predicted):.4f}")
    print("\nClassification report:")
    print(classification_report(test_labels, predicted, zero_division=0))


if __name__ == "__main__":
    main()
