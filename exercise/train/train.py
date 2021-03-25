import argparse
import numpy as np
import pandas as pd
import pickle

from imblearn.ensemble import BalancedBaggingClassifier
from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.ensemble import HistGradientBoostingClassifier


def train_model(training_data):
    clf = BalancedBaggingClassifier(
        base_estimator=HistGradientBoostingClassifier(random_state=2021),
        n_estimators=25, random_state=2021
    )

    df = pd.read_csv(f'../data/{training_data}')
    target = df['install']
    df.drop(['install'], axis=1, inplace=True)

    clf.fit(df, target)

    filename = 'finalized_model.sav'
    pickle.dump(clf, open(filename, 'wb'))


if __name__ == '__main__':
    train_model('train_df_processed.csv')
    print('Model trained and saved')
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--x_train')
    # parser.add_argument('--y_train')
    # args = parser.parse_args()
    # train_model(args.x_train, args.y_train)
