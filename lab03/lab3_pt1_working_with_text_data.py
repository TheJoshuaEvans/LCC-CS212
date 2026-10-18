# Joshua Evans (thejoshuaevans.com) 2026-10-15
from sklearn import metrics
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

# Grab the training and test data
categories = ["alt.atheism", "soc.religion.christian", "comp.graphics", "sci.med"]
print("Fetching training data...")
twenty_train = fetch_20newsgroups(
    subset="train", categories=categories, shuffle=True, random_state=42
)
print("Fetching test data...")
twenty_test = fetch_20newsgroups(
    subset="test", categories=categories, shuffle=True, random_state=42
)

# Create the pipeline and fit data
text_clf = Pipeline(
    [
        ("vect", CountVectorizer(ngram_range=(1, 1))),
        ("tfidf", TfidfTransformer(use_idf=True)),
        (
            "clf",
            SGDClassifier(
                loss="hinge",
                penalty="l2",
                alpha=1e-3,
                random_state=42,
                max_iter=5,
                tol=None,
            ),
        ),
    ]
)
text_clf.fit(twenty_train.data, twenty_train.target)

# Perform tests and classify results
docs_test = twenty_test.data
predicted = text_clf.predict(docs_test)

print("Classification Report:")
print(
    metrics.classification_report(
        twenty_test.target, predicted, target_names=twenty_test.target_names
    )
)
