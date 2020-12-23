import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

passv = lambda x: x
MONTHS = ['Jan', 'Feb', 'Mar', 'April', 'May', 'June', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


TEST_SIZE = 0.4
CONVERSION_FUNCTIONS = [int, float, int, float, int, float, float, float,
						float, float, MONTHS.index , int, int, int, int, lambda x: 1 if x == "Returning_Visitor" else 0,
						lambda x: 1 if x!="FALSE" else 0]

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

	evidence should be a list of lists, where each list contains the
	following values, in order:
		- Administrative, an integer
		- Administrative_Duration, a floating point number
		- Informational, an integer
		- Informational_Duration, a floating point number
		- ProductRelated, an integer
		- ProductRelated_Duration, a floating point number
		- BounceRates, a floating point number
		- ExitRates, a floating point number
		- PageValues, a floating point number
		- SpecialDay, a floating point number
		- Month, an index from 0 (January) to 11 (December)
		- OperatingSystems, an integer
		- Browser, an integer
		- Region, an integer
		- TrafficType, an integer
		- VisitorType, an integer 0 (not returning) or 1 (returning)
		- Weekend, an integer 0 (if false) or 1 (if true)

	labels should be the corresponding list of labels, where each label
	is 1 if Revenue is true, and 0 otherwise.
	"""
	data = []
	labels = []
	with open("shopping.csv", "r") as f:
		reader = csv.reader(f)
		first = True
		for line in reader:
			if first:
				first = False
				continue
			row = list(line)
			data.append([None] * (len(row) - 1))
			for i in range(len(row) - 1):
				data[-1][i] = CONVERSION_FUNCTIONS[i](row[i])
			labels.append(1 if row[-1]!="FALSE" else 0)
	return data, labels


def train_model(evidence, labels):
	"""
	Given a list of evidence lists and a list of labels, return a
	fitted k-nearest neighbor model (k=1) trained on the data.
	"""
	model = KNeighborsClassifier(n_neighbors=10)
	model.fit(evidence,labels)
	return model

def evaluate(labels, predictions):
	"""
	Given a list of actual labels and a list of predicted labels,
	return a tuple (sensitivity, specificty).

	Assume each label is either a 1 (positive) or 0 (negative).

	`sensitivity` should be a floating-point value from 0 to 1
	representing the "true positive rate": the proportion of
	actual positive labels that were accurately identified.

	`specificity` should be a floating-point value from 0 to 1
	representing the "true negative rate": the proportion of
	actual negative labels that were accurately identified.
	"""
	true_n = 0
	true_p = 0
	negatives = 0
	positives = 0
	for i, j in zip(labels, predictions):
		if i == 0:
			if i == j:
				true_n += 1
			negatives += 1
		else:
			if i == j:
				true_p += 1
			positives += 1	
	specificity = true_n / negatives
	sensitivity = true_p / positives
	return sensitivity, specificity


if __name__ == "__main__":
	main()
