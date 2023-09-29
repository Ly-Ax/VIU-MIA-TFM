"""Classifier models"""
import pandas as pd
import numpy as np
import os
import sys
import yaml
import joblib
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

sys.path.append(str(Path(__file__).parents[1]))

import transform_main as trn_main
from classifier import custom_classifier as cs_cl


class GenerateTestData:
    """Generate test data"""

    def __init__(self, num_sample=0):
        """Initialize variables"""
        self.path = os.getcwd()
        with open("config.yaml", "r") as yaml_file:
            self.config = yaml.safe_load(yaml_file)

        self.sample = num_sample

    def SampleData(self):
        """Generate sample data"""
        df_test = pd.read_csv(
            self.path + self.config["data"]["data_test"], low_memory=False
        )
        if self.sample > 0:
            df_test = df_test.sample(self.sample)

        df_test["MIS_Status"] = np.where(
            df_test["MIS_Status"] == "CHGOFF", 1, df_test["MIS_Status"]
        )
        df_test["MIS_Status"] = np.where(
            df_test["MIS_Status"] == "P I F", 0, df_test["MIS_Status"]
        )
        df_test["MIS_Status"] = df_test["MIS_Status"].astype("Int64")
        df_test.rename(columns={"MIS_Status": "Default"}, inplace=True)

        df_test.dropna(subset=["Default"], inplace=True)
        df_test["Default"] = df_test["Default"].astype(int)

        df_test.drop_duplicates(inplace=True)

        X_test = df_test.drop(columns=["Default"])
        y_test = df_test["Default"]

        return X_test, y_test


class LogRegModel:
    """Logistic Regression model"""

    def __init__(self):
        """Initialize variables"""
        self.path = os.getcwd()
        with open("config.yaml", "r") as yaml_file:
            self.config = yaml.safe_load(yaml_file)

        self.num_cols = [
            "Term",
            "NoEmp",
            "SecuredSBA",
            "GrDisburs",
            "GrApprov",
            "ApprovSBA",
        ]
        self.target = ["Default"]

    def TrainLogReg(self, SaveModel=False):
        """Train Logistic Regression model"""
        df_train = pd.read_csv(
            self.path + self.config["data"]["data_train"], low_memory=False
        )

        trn_data = trn_main.TransformData()
        df_train = trn_data.Preprocessing(df_train)

        X = df_train.drop(columns=self.target)
        y = df_train[self.target[0]]

        logreg_pipeline = Pipeline(
            [
                ("scaler", cs_cl.ZScoreTransformer(self.num_cols)),
                ("custom_model", cs_cl.LogisticRegressionModel()),
            ]
        )
        logreg_pipeline.fit(X, y)

        if SaveModel == True:
            joblib.dump(
                logreg_pipeline, self.path + self.config["models"]["logreg_model"]
            )

        return logreg_pipeline

    def LogRegPredict(self, X, PreData=True):
        """Logistic Regression Predict"""
        if PreData == True:
            trn_data = trn_main.TransformData()
            X = trn_data.Preprocessing(X)

        logreg_model = joblib.load(self.path + self.config["models"]["logreg_model"])

        y_pred = logreg_model.predict(X)
        return y_pred


class KnnModel:
    """K Nearest Neighbors model"""

    def __init__(self):
        """Initialize variables"""
        self.path = os.getcwd()
        with open("config.yaml", "r") as yaml_file:
            self.config = yaml.safe_load(yaml_file)

        self.num_cols = [
            "Term",
            "NoEmp",
            "SecuredSBA",
            "GrDisburs",
            "GrApprov",
            "ApprovSBA",
        ]
        self.target = "Default"

    def TrainKnn(self, SaveModel=False):
        """Train K Nearest Neighbors model"""
        df_train = pd.read_csv(
            self.path + self.config["data"]["data_train"], low_memory=False
        )
        df_val = pd.read_csv(
            self.path + self.config["data"]["data_val"], low_memory=False
        )

        trn_data = trn_main.TransformData()
        df_train = trn_data.Preprocessing(df_train)
        df_val = trn_data.Preprocessing(df_val)

        df_train_val = pd.concat([df_train, df_val], axis=0)
        X = df_train_val.drop(columns=[self.target])
        y = df_train_val[self.target]

        knn_pipeline = Pipeline(
            [
                ("scaler", cs_cl.MinMaxTransformer(self.num_cols)),
                ("custom_model", cs_cl.KNeighborsModel()),
            ]
        )
        knn_pipeline.fit(X, y)

        if SaveModel == True:
            joblib.dump(knn_pipeline, self.path + self.config["models"]["knn_model"])

        return knn_pipeline

    def KnnPredict(self, X, PreData=True):
        """K Nearest Neighbors Predict"""
        if PreData == True:
            trn_data = trn_main.TransformData()
            X = trn_data.Preprocessing(X)

        knn_model = joblib.load(self.path + self.config["models"]["knn_model"])

        y_pred = knn_model.predict(X)
        return y_pred


class DecTreeModel:
    """Decision Tree Classifier"""

    def __init__(self):
        """Initialize variables"""
        self.path = os.getcwd()
        with open("config.yaml", "r") as yaml_file:
            self.config = yaml.safe_load(yaml_file)

        self.target = "Default"

    def TrainDecTree(self):
        """Train Decision Tree Classifier"""
        df_train = pd.read_csv(
            self.path + self.config["data"]["data_train"], low_memory=False
        )
        df_val = pd.read_csv(
            self.path + self.config["data"]["data_val"], low_memory=False
        )

        trn_data = trn_main.TransformData()
        df_train = trn_data.Preprocessing(df_train)
        df_val = trn_data.Preprocessing(df_val)

        df_train_val = pd.concat([df_train, df_val], axis=0)
        X = df_train_val.drop(columns=[self.target])
        y = df_train_val[self.target]

        dectree_pipeline = Pipeline([("custom_model", cs_cl.DecisionTreeModel())])
        dectree_pipeline.fit(X, y)

        joblib.dump(
            dectree_pipeline, self.path + self.config["models"]["dectree_model"]
        )

    def DecTreePredict(self, X, PreData=True):
        """Decision Tree Predict"""
        if PreData == True:
            trn_data = trn_main.TransformData()
            X = trn_data.Preprocessing(X)

        dtc_model = joblib.load(self.path + self.config["models"]["dectree_model"])

        y_pred = dtc_model.predict(X)
        return y_pred


if __name__ == "__main__":
    try:
        test_data = GenerateTestData(100)
        X_test, y_test = test_data.SampleData()

        # lr_model = LogRegModel()
        # # log_reg = lr_model.TrainLogReg(SaveModel=True)
        # y_pred = lr_model.LogRegPredict(X_test)

        # knn_model = KnnModel()
        # # knn = knn_model.TrainKnn(SaveModel=True)
        # y_pred = knn_model.KnnPredict(X_test)

        dtc_model = DecTreeModel()
        # dtc_model.TrainDecTree()
        y_pred = dtc_model.DecTreePredict(X_test)

        print("Exactitud:    %.4f" % (accuracy_score(y_test, y_pred)))
        print("Precisión:    %.4f" % (precision_score(y_test, y_pred, average="macro")))
        print("Sensibilidad: %.4f" % (recall_score(y_test, y_pred, average="macro")))
        print("F1-score:     %.4f" % (f1_score(y_test, y_pred, average="macro")))

    except Exception as err:
        print("Error: ", str(err))
