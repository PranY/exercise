import gc
import numpy as np
import pandas as pd
import pickle
import re

from collections import defaultdict
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

train_path = '../data/training_data.csv'
test_path = '../data/test_data.csv'
delim = ';'
target_var = 'install'


class LabelEncoderExt(object):
    def __init__(self):
        r"""It differs from LabelEncoder by handling new classes and providing a value for the unknown.
        Unknown will be added in fit and transform will take care of the new item.
        It gives unknown class id.
        """
        self.label_encoder = LabelEncoder()

    def fit(self, data_list):
        r"""This will fit the encoder for all the unique values and introduce unknown value
        Args:
            data_list: A list of data to be encoded
        Returns:
            self
        """
        self.label_encoder = self.label_encoder.fit(data_list + ['Unknown'])
        self.classes_ = self.label_encoder.classes_
        return self

    def transform(self, data_list):
        r"""This will transform the data_list to id list where the new values get assigned to Unknown class
        Args:
            data_list: data to be transformed
        Return:
            encoded input using transform from self
        """
        new_data_list = [
            'Unknown' if x not in self.label_encoder.classes_ else x for x in data_list]
        return self.label_encoder.transform(new_data_list)


def add_datepart(df, fldname, drop=True, time=True):
    r"""Converts a column of df from a datetime64 to many columns containing
    the information from the date. This applies changes inplace.
    Args:
        df: input dataframe
        fldname: column or date field to operate on
        drop: allows in-place dropping of field column from the dataframe
        time: adds time level granularity to feature creation
    Returns:
        None: Makes changes in-place on the provided dataframe

    """

    fld = df[fldname]
    targ_pre = re.sub('[Dd]ate$', '', fldname)
    attr = ['Year', 'Month', 'Week', 'Day', 'Dayofweek', 'Dayofyear',
            'Is_month_end', 'Is_month_start', 'Is_quarter_end', 'Is_quarter_start', 'Is_year_end', 'Is_year_start']
    if time:
        attr = attr + ['Hour', 'Minute', 'Second']
    for n in attr:
        try:
            df[targ_pre + n] = getattr(fld.dt, n.lower())
        except AttributeError:
            pass  # this attribute will be missing from the delta
    df[targ_pre + 'Elapsed'] = fld.astype(np.int64) // 10 ** 9
    if drop:
        df.drop(fldname, axis=1, inplace=True)


def add_encoding(df, cols):
    r"""Converts all the rows in cols list from an object to label encoded number.
       This applies changes in place.
    Args:
        df: input dataframe
        cols: columns to be encoded
    Returns:
        df: encoded dataframe with columns to-be-encoded dropped and replaced with respective encoded versions
        le_dict: a dictionary of columns to-be-encoded with the initialized label encoder
    """
    le_dict = defaultdict(list)

    for c in cols:
        le = LabelEncoderExt()
        le.fit(list(df[c].unique()))
        # Preserving the encoder in a 'column:encoder' dict for inverse transform
        le_dict[c].append(le)
        df[c+'_encoded'] = le.transform(list(df[c].astype(str)))
    df.drop(cols, axis=1, inplace=True)
    return df, le_dict


def preprocess(df, tag):
    r"""Preprocess the data frame and returns.
    Args:
        df: input dataframe
        tag: a string tag for train/test
    Returns:
        df: processed dataframe
    """
    temp = df['deviceType'].str.split(',', n=1, expand=True)
    df['deviceName'] = temp[0]
    temp = df['deviceName'].str.split(' ', n=1, expand=True)
    df['deviceName'] = temp[0]
    del temp

    print('>>> adding time features')
    df['timestamp'] = pd.to_datetime(
        df['timestamp'], infer_datetime_format=True)
    df['lastStart'] = pd.to_datetime(
        df['lastStart'], infer_datetime_format=True)
    df['deltaTime'] = df['timestamp']-df['lastStart']
    df['deltaTime'].fillna(pd.Timedelta(
        df['deltaTime'].median(), unit='s'), inplace=True)

    add_datepart(df, 'timestamp', time=True)
    add_datepart(df, 'lastStart', time=True)
    add_datepart(df, 'deltaTime', time=True)

    df['delayBucket'] = pd.cut(df['deltaTimeElapsed'],
                               [0, 60, 60*60, 60*60*24, 60*60*24*7, 60*60*24*365], labels=[1, 2, 3, 4, 5])

    feature_exclude = ['id', 'deviceType']
    df.drop(feature_exclude, axis=1, inplace=True)

    if tag == 'train':
        print('>>> adding encoding on train data')
        encode_cols = list(df.select_dtypes(include=['object']).columns)
        df, le_dict = add_encoding(df, encode_cols)
        for le, lv in le_dict.items():
            with open(f'{le}.pkl', 'wb') as output:
                pickle.dump(lv, output)
                output.close()
    else:
        print('>>> adding encoding on test data')
        encode_cols = list(df.select_dtypes(include=['object']).columns)
        for col in encode_cols:
            with open(f'{col}.pkl', 'rb') as inp:
                df[col +
                    '_encoded'] = pickle.load(inp)[0].transform(list(df[col]))
        df.drop(encode_cols, axis=1, inplace=True)

    print('>>> adding ratio features')
    df['ctre'] = df['clickCount']/df['startCount']
    df['vtre'] = df['viewCount']/df['startCount']
    df['etre'] = df['installCount']/df['startCount']
    df['ctr1d'] = df['clickCount']/df['startCount1d']
    df['vtr1d'] = df['viewCount']/df['startCount1d']
    df['etr1d'] = df['installCount']/df['startCount1d']
    df['ctr7d'] = df['clickCount']/df['startCount7d']
    df['vtr7d'] = df['viewCount']/df['startCount7d']
    df['etr7d'] = df['installCount']/df['startCount7d']

    df.fillna(df.median(), inplace=True)
    gc.collect()
    return df


if __name__ == "__main__":
    print(f'Reading training data from {train_path}')
    train_df = pd.read_csv(train_path, sep=delim, quoting=3,
                           error_bad_lines=False, warn_bad_lines=True)
    print(f'Reading test data from {test_path}')
    test_df = pd.read_csv(test_path, sep=delim, quoting=3,
                          error_bad_lines=False, warn_bad_lines=True)

    print('Please wait while we preprocess the data')

    target = train_df[target_var]
    train_df.drop([target_var], axis=1, inplace=True)

    train_df = preprocess(train_df, 'train')
    train_df[target_var] = target
    del target
    gc.collect()

    mask = np.random.rand(len(train_df)) < 0.8
    train = train_df[mask]
    val = train_df[~mask]

    print('Saving training dataframe in the data directory as train_df_processed')
    train.to_csv('../data/train_df_processed.csv', index=False)
    print('Saving validation dataframe in the data directory as val_df_processed')
    train.to_csv('../data/train_df_processed.csv', index=False)
    print('Preprocessing on training data completed, now starting with the test data')

    test_df = preprocess(test_df, 'test')
    print('Preprocessing on test data completed')
    print('Saving test dataframe in the data directory as train_df_processed')
    test_df.to_csv('../data/test_df_processed.csv', index=False)
