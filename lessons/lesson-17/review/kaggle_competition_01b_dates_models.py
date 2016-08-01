"""
This file provides you with tools and a framework to quickly get you started
making predictions and winning the competition!

There are two places you could make a great impact

    1. Selecting and calibrating your model
    2. Selecting and creating your features

Good luck!

@author You!
@author Ruben Naeff - rubennaeff@gmail.com
August 2015
"""

from datetime import datetime
import numpy as np
import pandas as pd
import time

from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, \
    ExtraTreesClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cross_validation import train_test_split, cross_val_score


PATH_TO_DATA = "/Users/ruben/Downloads/"  # change this to your local path
USER = os.getlogin()  # you could change this to your own name if you like

TRAIN_FILE = PATH_TO_DATA + "train.csv"
TEST_FILE = PATH_TO_DATA + "test.csv"

NOW = datetime.now().strftime("%y%m%d_%H%M%S")  # get timestamp
SUBMISSION_FILE = PATH_TO_DATA + "%s_submission_%s.csv" % (USER, NOW)  # include timestamp for archiving


class KaggleCompetition():

    def __init__(self, train_file=TRAIN_FILE, test_file=TEST_FILE):
        """Load training set and test set from disk"""

        print "Loading %s..." % train_file
        self.train = pd.read_csv(train_file, index_col=0)
        print "Loading %s..." % test_file
        self.test = pd.read_csv(test_file, index_col=0)

        self.n_train, self.n_test = len(self.train), len(self.test)
        print "Loaded", self.n_train, "training samples and", self.n_test, "testing samples"

        # Just checking if you have indeed the right file
        if (self.n_train != 140272) or (self.n_test != 73290):
            raise ValueError("It seems like you have loaded the wrong datasets!")

# ------------------------------------------------------------------------------------ #
# You only need to worry about the code below here

    def setup_model(self):
        """Choose your favorite model and initialize it using your favorite parameters"""

        # kNN model: options include n_neighbors, weights='uniform'/'distance', etc.
        # model = KNeighborsClassifier()

        # Logistic Regression: inverse-regularization parameter C, with L1 or L2 norm
        # (big C leads to overfitting)
        # model = LogisticRegression()

        # Naive Bayes: options include alpha for smoothing (see doc)
        model = MultinomialNB()

        # Decision Trees and Random Forests: options include n_estimators (number of trees),
        # gini or entropy purtiy measures, pruning settings, etc.
        # model = DecisionTreeClassifier()  # one tree
        # model = RandomForestClassifier()  # random forest
        # model = ExtraTreesClassifier()  # random forest variation
        # model = AdaBoostClassifier()  # random forest variation
        # model = GradientBoostingClassifier()  # random forest variation

        # Support Vector Machines: inverse-regularization parameter C, with L1 or L2 norm
        # Kernels could be 'linear', 'poly', 'rbf', 'sigmoid', or 'precomputed'
        # Kernel 'poly' has option `degree`, kernel 'rbf' has option 'gamma', etc. (see doc)
        # model = LinearSVC()  # linear SVM
        # model = SVC()  # Gaussian kernel by default

        return model

    def extract_features(self, data, training=True):
        """Create additional features by adding columns to your dataset
        :param dataset: both training and test set
        :param training: if True, fit vectorizers, otherwise just transform
        :return: X, y  -- feature matrix and target values"""

        print "Extracting features from %s set..." % ['test', 'training'][training]

        # You can choose from the following columns (and you can make more, obviously)
        # all_columns = \
        #     ['PostId', 'PostCreationDate', 'OwnerUserId', 'OwnerCreationDate',
        #      'ReputationAtPostCreation', 'OwnerUndeletedAnswerCountAtPostTime',
        #      'Title', 'BodyMarkdown', 'Tag1', 'Tag2', 'Tag3', 'Tag4', 'Tag5',
        #      'PostClosedDate', 'OpenStatus']

        # Convert dates to datetime format, aggregate by year, compute ages
        print "Converting dates to datetime format..."
        data['PostCreationDate_dt'] = pd.to_datetime(data.PostCreationDate)
        data['PostCreationDate_ord'] = data.PostCreationDate_dt.astype(int)  # just ordinal no
        data['PostCreationDate_year'] = data.PostCreationDate_dt.dt.year
        data["PostAge"] = (data.PostCreationDate_dt.max() - data.PostCreationDate_dt).dt.days

        data['OwnerCreationDate_dt'] = pd.to_datetime(data.OwnerCreationDate)
        data['OwnerCreationDate_ord'] = data.OwnerCreationDate_dt.astype(int)
        data['OwnerCreationDate_year'] = data.OwnerCreationDate_dt.dt.year
        data["OwnerAgeAtPosting"] = (data.PostCreationDate_dt - data.OwnerCreationDate_dt).dt.days

        # ....
        # You could do much, much more to improve your score here
        # Add and create more features (including parsing the text columns)
        # Select and calibrate your model (see above)
        # ....

        # Include the following columns in your feature matrix
        self.features = \
            ['OwnerUserId', 'ReputationAtPostCreation', 'OwnerUndeletedAnswerCountAtPostTime',
             'PostCreationDate_ord', 'PostCreationDate_year',
             'PostAge',
             'OwnerCreationDate_ord', 'OwnerCreationDate_year',
             'OwnerAgeAtPosting']

        # Create feature matrix
        X = data[self.features]

        if training:
            return X, data.OpenStatus
        else:
            return X

# ------------------------------------------------------------------------------------ #
# You don't need to do much below here

    def make_predictions(self, model, X_train, y_train, X_test, submission_file=SUBMISSION_FILE):
        """Train model on training set and make predictions for the test set.
        Then save predictions to disk."""

        if self.n_test != len(X_test):
            raise ValueError("Somewhere along the way you lost test samples! Please fix.")

        print "Training %s using %d samples (%d%% of original training set)" % \
            (model.__class__.__name__, len(X_train), 100. * len(X_train) / self.n_train)

        try:
            model.fit(X_train, y_train)
        except ValueError:
            scale_features = self.features  # ['ReputationAtPostCreation', 'AgeAccount']
            scaler = MinMaxScaler()
            X_train.loc[:, scale_features] = scaler.fit_transform(X_train[scale_features].astype(float))
            X_test.loc[:, scale_features] = scaler.transform(X_test[scale_features].astype(float))
            model.fit(X_train, y_train)

        print "Making predictions on the test set.."
        # We want the probabilities, not just 0 or 1. Just take 2nd column
        try:
            y_pred = model.predict_proba(X_test)[:, 1]
        except:
            sigmoid = lambda x: 1. / (1 + np.exp(-x))
            y_pred = sigmoid(model.decision_function(X_test))

        print "Cross-validating model..."
        scores = cross_val_score(model, X_train, y_train, cv=3, scoring="roc_auc")
        print "Cross-validated AUC score: %.4f  (%s)" % (scores.mean(), scores.round(4))

        print "Saving predictions in %s..." % submission_file
        submission = pd.DataFrame(dict(id=self.test.index, OpenStatus=y_pred)).set_index('id')
        submission.to_csv(submission_file)


def main():
    start_time = time.time()
    kaggle = KaggleCompetition()
    X_train, y_train = kaggle.extract_features(kaggle.train)
    X_test = kaggle.extract_features(kaggle.test, training=False)
    model = kaggle.setup_model()
    kaggle.make_predictions(model, X_train, y_train, X_test)
    duration = time.time() - start_time
    print "Done! That took %dm%02ds" % (duration / 60, int(duration) % 60)


if __name__ == "__main__":
    main()
