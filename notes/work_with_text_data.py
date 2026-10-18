# Joshua Evans (thejoshuaevans.com) 2026-10-15
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

# Grab the training data
categories = ["alt.atheism", "soc.religion.christian", "comp.graphics", "sci.med"]
twenty_train = fetch_20newsgroups(
    subset="train", categories=categories, shuffle=True, random_state=42
)
twenty_test = fetch_20newsgroups(
    subset="test", categories=categories, shuffle=True, random_state=42
)

# Create the pipeline template
text_clf = Pipeline(
    [
        ("vect", CountVectorizer()),
        ("tfidf", TfidfTransformer()),
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

# Use grid search to identify ideal parameters
parameters = {
    "vect__ngram_range": [(1, 1), (1, 2)],
    "tfidf__use_idf": (True, False),
    "clf__alpha": (1e-2, 1e-3),
    "clf__penalty": ["l2", "l1", "elasticnet"],
}
gs_clf = GridSearchCV(text_clf, parameters, cv=5, n_jobs=-1)

print("Identifying best fit parameters...")
gs_clf = gs_clf.fit(twenty_train.data[:400], twenty_train.target[:400])


print(f"Best score found: {gs_clf.best_score_}")
print("Identified parameters:")
for param_name in sorted(parameters.keys()):
    print("    %s: %r" % (param_name, gs_clf.best_params_[param_name]))
