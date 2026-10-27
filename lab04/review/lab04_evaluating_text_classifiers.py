# Maksym Kholodenko, 10/25/2026, Group B. Used GitHub Copilot for minimal punctuation corrections and minor suggestions.
# Routes BANKING77 customer messages to six bank departments.
# The main stages are baseline evaluation, class weighting, hyperparameter
# tuning, and error analysis. Discussion answers are included in comments.

import csv
import random
import socket
from collections import Counter
from pathlib import Path
from urllib.request import urlretrieve

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

# The 77 BANKING77 intents, grouped into six departments as specified in the lab.
DEPARTMENTS = {
    "Cards": [
        "activate_my_card",
        "card_arrival",
        "card_delivery_estimate",
        "card_linking",
        "card_not_working",
        "card_swallowed",
        "card_about_to_expire",
        "change_pin",
        "contactless_not_working",
        "disposable_card_limits",
        "get_disposable_virtual_card",
        "get_physical_card",
        "getting_spare_card",
        "getting_virtual_card",
        "order_physical_card",
        "pin_blocked",
        "virtual_card_not_working",
        "apple_pay_or_google_pay",
        "card_acceptance",
        "visa_or_mastercard",
        "supported_cards_and_currencies",
    ],
    "Payments": [
        "card_payment_fee_charged",
        "card_payment_not_recognised",
        "card_payment_wrong_exchange_rate",
        "declined_card_payment",
        "pending_card_payment",
        "reverted_card_payment?",
        "direct_debit_payment_not_recognised",
        "transaction_charged_twice",
        "extra_charge_on_statement",
        "request_refund",
        "Refund_not_showing_up",
        "cash_withdrawal_charge",
        "cash_withdrawal_not_recognised",
        "declined_cash_withdrawal",
        "pending_cash_withdrawal",
        "wrong_amount_of_cash_received",
        "wrong_exchange_rate_for_cash_withdrawal",
        "atm_support",
    ],
    "Transfers": [
        "cancel_transfer",
        "declined_transfer",
        "failed_transfer",
        "pending_transfer",
        "transfer_fee_charged",
        "transfer_into_account",
        "transfer_not_received_by_recipient",
        "transfer_timing",
        "beneficiary_not_allowed",
        "receiving_money",
        "balance_not_updated_after_bank_transfer",
        "balance_not_updated_after_cheque_or_cash_deposit",
    ],
    "TopUps": [
        "automatic_top_up",
        "pending_top_up",
        "top_up_by_bank_transfer_charge",
        "top_up_by_card_charge",
        "top_up_by_cash_or_cheque",
        "top_up_failed",
        "top_up_limits",
        "top_up_reverted",
        "topping_up_by_card",
        "verify_top_up",
    ],
    "Security": [
        "compromised_card",
        "lost_or_stolen_card",
        "lost_or_stolen_phone",
        "unable_to_verify_identity",
        "verify_my_identity",
        "why_verify_identity",
        "verify_source_of_funds",
        "passcode_forgotten",
    ],
    "Account": [
        "age_limit",
        "country_support",
        "edit_personal_details",
        "terminate_account",
        "exchange_charge",
        "exchange_rate",
        "exchange_via_app",
        "fiat_currency_support",
    ],
}
DEPARTMENT_NAMES = list(DEPARTMENTS)
DEPARTMENT_OF = {
    intent: department
    for department, intents in DEPARTMENTS.items()
    for intent in intents
}

# Keep dataset paths relative to the Python file, not to a particular computer.
DATA_DIR = Path(__file__).resolve().parent / "data"
BASE_URL = (
    "https://raw.githubusercontent.com/PolyAI-LDN/"
    "task-specific-datasets/master/banking_data/"
)
KEEP_FRACTIONS = {"Security": 0.15, "Account": 0.25}


def ensure_data_files():
    """Download the original BANKING77 CSV files if they are not already present."""
    # Truststore can help on systems with a custom certificate authority.
    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:
        pass

    socket.setdefaulttimeout(60)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename in ("train.csv", "test.csv"):
        path = DATA_DIR / filename
        if path.is_file():
            continue
        temporary_path = DATA_DIR / (filename + ".download")
        print(f"Downloading {filename}...")
        try:
            urlretrieve(BASE_URL + filename, temporary_path)
            temporary_path.replace(path)
        except Exception as error:
            temporary_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"Unable to download {filename}. Check the internet connection "
                "or place the CSV files in the data folder."
            ) from error


def load_messages(path):
    """Load messages, their six-department labels, and original BANKING77 intents."""
    texts, departments, intents = [], [], []
    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if not {"text", "category"}.issubset(reader.fieldnames or []):
            raise ValueError(f"Expected text and category columns in {path}")
        for row in reader:
            intent = row["category"]
            if intent not in DEPARTMENT_OF:
                raise ValueError(f"Unrecognized intent in {path}: {intent}")
            texts.append(row["text"])
            departments.append(DEPARTMENT_OF[intent])
            intents.append(intent)
    return texts, departments, intents


def make_imbalanced(texts, departments, intents, keep_fractions, seed=42):
    """Downsample rare departments and shuffle while preserving corresponding labels."""
    generator = random.Random(seed)
    kept_indices = [
        index
        for index, department in enumerate(departments)
        if generator.random() < keep_fractions.get(department, 1.0)
    ]
    generator.shuffle(kept_indices)
    return (
        [texts[i] for i in kept_indices],
        [departments[i] for i in kept_indices],
        [intents[i] for i in kept_indices],
    )


def build_pipeline(balanced=False):
    """Create the exact TF-IDF and logistic-regression pipeline required by the lab."""
    weight = "balanced" if balanced else None
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("clf", LogisticRegression(max_iter=2000, class_weight=weight)),
        ]
    )


def evaluate_model(name, model, test_texts, test_departments):
    """Report accuracy, class-level metrics, and a labeled confusion matrix."""
    predicted = model.predict(test_texts)
    accuracy = accuracy_score(test_departments, predicted)
    macro_f1 = f1_score(
        test_departments,
        predicted,
        labels=DEPARTMENT_NAMES,
        average="macro",
        zero_division=0,
    )
    weighted_f1 = f1_score(
        test_departments,
        predicted,
        labels=DEPARTMENT_NAMES,
        average="weighted",
        zero_division=0,
    )
    precision, recall, f1, support = precision_recall_fscore_support(
        test_departments,
        predicted,
        labels=DEPARTMENT_NAMES,
        zero_division=0,
    )
    by_department = {
        name: {"precision": p, "recall": r, "f1": score, "support": int(n)}
        for name, p, r, score, n in zip(
            DEPARTMENT_NAMES, precision, recall, f1, support
        )
    }

    print(f"\n=== {name} ===")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")
    print(f"Weighted F1: {weighted_f1:.4f}")
    print("\nClassification report:")
    print(
        classification_report(
            test_departments,
            predicted,
            labels=DEPARTMENT_NAMES,
            digits=3,
            zero_division=0,
        )
    )
    print("Confusion matrix (rows = actual, columns = predicted):")
    print("Labels:", ", ".join(DEPARTMENT_NAMES))
    print(confusion_matrix(test_departments, predicted, labels=DEPARTMENT_NAMES))
    return {
        "predicted": predicted,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "by_department": by_department,
    }


def describe_baseline(results):
    """Identify weak departments and explain how imbalance affects averaging."""
    by_department = results["by_department"]
    weakest = sorted(DEPARTMENT_NAMES, key=lambda d: by_department[d]["f1"])[:2]
    print("\nBaseline interpretation:")
    for department in weakest:
        scores = by_department[department]
        if scores["recall"] < scores["precision"]:
            lower = "recall"
        elif scores["precision"] < scores["recall"]:
            lower = "precision"
        else:
            lower = "both equally"
        print(
            f"  {department}: F1={scores['f1']:.3f}, "
            f"precision={scores['precision']:.3f}, "
            f"recall={scores['recall']:.3f}; lower measure: {lower}."
        )
    print(
        "  Accuracy and weighted F1 reflect frequent departments much more than "
        "rare ones; macro F1 weights all six departments equally."
    )
    # Baseline answers: The smallest classes, especially Security and Account,
    # tend to have lower recall because missing them costs little in total accuracy.
    # Macro F1 treats every department equally; weighted F1 uses class support,
    # while accuracy counts all correct predictions without class-level balancing.


def compare_balancing(baseline, balanced):
    """Explain observed precision/recall changes from balanced class weights."""
    print("\nClass-weight comparison (balanced minus baseline):")
    for department in ("Security", "Account", "Cards"):
        before = baseline["by_department"][department]
        after = balanced["by_department"][department]
        print(
            f"  {department}: precision {after['precision'] - before['precision']:+.3f}; "
            f"recall {after['recall'] - before['recall']:+.3f}."
        )
    print(f"  Accuracy change: {balanced['accuracy'] - baseline['accuracy']:+.4f}")
    print(f"  Macro F1 change: {balanced['macro_f1'] - baseline['macro_f1']:+.4f}")
    # Experiment 1 answers: Class weighting gives rare departments a larger
    # influence during training. Their recall generally rises, while precision
    # can fall because more messages are predicted as rare departments.
    # Prioritize Security recall: missing fraud or a lost card can delay urgent
    # action. For Cards, a more balanced precision/recall trade-off is sensible;
    # there is less reason to accept many false alarms for ordinary card issues.


def compare_tuning(balanced, tuned):
    """Compare grid-search improvements with the balanced untuned classifier."""
    print("\nGrid-search comparison (tuned minus balanced):")
    print(f"  Accuracy change: {tuned['accuracy'] - balanced['accuracy']:+.4f}")
    print(f"  Macro F1 change: {tuned['macro_f1'] - balanced['macro_f1']:+.4f}")
    for department in ("Security", "Account"):
        before = balanced["by_department"][department]
        after = tuned["by_department"][department]
        print(
            f"  {department}: F1 {after['f1'] - before['f1']:+.3f}; "
            f"recall {after['recall'] - before['recall']:+.3f}."
        )
    # Experiment 2 answers: GridSearchCV uses f1_macro because accuracy can
    # overlook rare Security and Account errors. Macro F1 assigns equal weight
    # to each department, regardless of the number of messages in that class.
    # The printed metric differences establish whether tuning beat Experiment 1;
    # this cannot be assumed before the test data is evaluated.


def analyze_errors(test_texts, true_departments, test_intents, predicted):
    """Display five missed Security messages and count common routing mistakes."""
    print("\n=== Error analysis: misrouted Security messages ===")
    security_errors = [
        i
        for i, (actual, guess) in enumerate(zip(true_departments, predicted))
        if actual == "Security" and guess != actual
    ]
    if not security_errors:
        print("No misrouted Security messages in this test set.")
    for number, i in enumerate(security_errors[:5], start=1):
        print(f"\n{number}. Intent: {test_intents[i]}")
        print(f"   Actual: Security | Predicted: {predicted[i]}")
        print(f"   Message: {test_texts[i]}")
    if len(security_errors) < 5:
        print(f"Only {len(security_errors)} Security misclassifications were found.")

    mistakes = Counter(
        (intent, actual, str(guess))
        for intent, actual, guess in zip(test_intents, true_departments, predicted)
        if actual != guess
    )
    print("\nMost common (intent, actual, predicted) errors:")
    if not mistakes:
        print("No classification errors were found.")
    for (intent, actual, guess), count in mistakes.most_common(10):
        print(f"  {count:3d}  {intent}: {actual} -> {guess}")

    print("\nError-analysis interpretation:")
    if mistakes:
        (intent, actual, guess), count = mistakes.most_common(1)[0]
        print(
            f"  Most frequent error: {intent} ({actual} -> {guess}), "
            f"occurring {count} times."
        )
    print(
        "  Banking language often overlaps across departments: for example, "
        "lost-card and unrecognized-payment messages can mention the same "
        "cards, charges, and security concerns. Some routes are debatable."
    )
    print(
        "  Possible grouping change to evaluate: route "
        "'card_payment_not_recognised' to Security rather than Payments "
        "if bank policy treats unrecognized charges as potential fraud."
    )
    # Error-analysis answers: Short messages can omit the specific detail that
    # distinguishes a transfer, a payment, and a possible fraud report. The
    # original intent grouping contains some reasonable overlaps; a wrong model
    # prediction may still represent a sensible route from a service perspective.
    # A defensible potential change is to consider "card_payment_not_recognised"
    # a Security intent, subject to human review and the bank's routing policy.
    # Changing labels solely to improve a score is not an appropriate reason.
    # Think-about-it answer: Security -> Cards is generally more harmful than
    # Cards -> Security, since urgent fraud-related action may be delayed.
    # High Security recall is especially important, even at some precision cost.


def main():
    """Run all three required experiments and the final error analysis."""
    ensure_data_files()
    train_texts, train_departments, train_intents = load_messages(
        DATA_DIR / "train.csv"
    )
    test_texts, test_departments, test_intents = load_messages(DATA_DIR / "test.csv")
    print("Original training counts:", dict(Counter(train_departments)))

    # Imbalance is applied independently to both original datasets; they are
    # never mixed, and the test set is not used during training or grid search.
    train_texts, train_departments, train_intents = make_imbalanced(
        train_texts, train_departments, train_intents, KEEP_FRACTIONS
    )
    test_texts, test_departments, test_intents = make_imbalanced(
        test_texts, test_departments, test_intents, KEEP_FRACTIONS
    )
    print("Imbalanced training counts:", dict(Counter(train_departments)))
    print("Imbalanced test counts:    ", dict(Counter(test_departments)))

    # Step 1: ordinary logistic-regression baseline.
    baseline_model = build_pipeline()
    baseline_model.fit(train_texts, train_departments)
    baseline = evaluate_model("Baseline", baseline_model, test_texts, test_departments)
    describe_baseline(baseline)

    # Step 2: balanced class weights reduce the bias toward frequent classes.
    balanced_model = build_pipeline(balanced=True)
    balanced_model.fit(train_texts, train_departments)
    balanced = evaluate_model(
        "Experiment 1 - Balanced class weights",
        balanced_model,
        test_texts,
        test_departments,
    )
    compare_balancing(baseline, balanced)

    # Step 3: 2 x 2 x 3 combinations, evaluated with three-fold cross-validation.
    # Balanced weighting is retained for a fair comparison with Experiment 1.
    grid = GridSearchCV(
        estimator=build_pipeline(balanced=True),
        param_grid={
            "tfidf__ngram_range": [(1, 1), (1, 2)],
            "tfidf__min_df": [1, 2],
            "clf__C": [0.1, 1.0, 10.0],
        },
        scoring="f1_macro",
        cv=3,
        n_jobs=1,
        refit=True,
    )
    grid.fit(train_texts, train_departments)
    print("\nGridSearchCV best settings:", grid.best_params_)
    print(f"GridSearchCV best mean CV macro F1: {grid.best_score_:.4f}")
    tuned = evaluate_model(
        "Experiment 2 - Tuned balanced classifier",
        grid.best_estimator_,
        test_texts,
        test_departments,
    )
    compare_tuning(balanced, tuned)

    # Step 4: inspect mistakes with the best model from the held-out test set.
    analyze_errors(test_texts, test_departments, test_intents, tuned["predicted"])


if __name__ == "__main__":
    main()
