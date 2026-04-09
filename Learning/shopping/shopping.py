import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).
    """
    evidence = []
    labels = []

    # Diccionario para convertir los meses abreviados a números enteros
    months = {
        "Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3,
        "May": 4, "June": 5, "Jul": 6, "Aug": 7,
        "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11
    }

    with open(filename, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 1. Procesar la evidencia (las características del usuario)
            user_evidence = [
                int(row["Administrative"]),
                float(row["Administrative_Duration"]),
                int(row["Informational"]),
                float(row["Informational_Duration"]),
                int(row["ProductRelated"]),
                float(row["ProductRelated_Duration"]),
                float(row["BounceRates"]),
                float(row["ExitRates"]),
                float(row["PageValues"]),
                float(row["SpecialDay"]),
                months[row["Month"]],
                int(row["OperatingSystems"]),
                int(row["Browser"]),
                int(row["Region"]),
                int(row["TrafficType"]),
                1 if row["VisitorType"] == "Returning_Visitor" else 0,
                1 if row["Weekend"] == "TRUE" else 0
            ]
            evidence.append(user_evidence)
            
            # 2. Procesar la etiqueta (lo que que predice: ¿Compró?)
            user_label = 1 if row["Revenue"] == "TRUE" else 0
            labels.append(user_label)

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # Inicializa el clasificador pidiendo que evalúe solo al vecino más cercano (k=1)
    model = KNeighborsClassifier(n_neighbors=1)
    
    # Entrena el modelo con los datos
    model.fit(evidence, labels)
    
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).
    """
    true_positives = 0
    actual_positives = 0
    
    true_negatives = 0
    actual_negatives = 0

    # Itera comparando la realidad (labels) contra lo que dijo la IA (predictions)
    for actual, predicted in zip(labels, predictions):
        if actual == 1:
            actual_positives += 1
            if predicted == 1:
                true_positives += 1
        else:
            actual_negatives += 1
            if predicted == 0:
                true_negatives += 1

    # Sensibilidad (True Positive Rate): De todos los que SÍ compraron, ¿cuántos atino?
    sensitivity = true_positives / actual_positives if actual_positives > 0 else 0.0
    
    # Especificidad (True Negative Rate): De todos los que NO compraron, ¿cuántos atino?
    specificity = true_negatives / actual_negatives if actual_negatives > 0 else 0.0

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()