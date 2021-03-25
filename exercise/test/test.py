import argparse
import numpy as np
import pickle
import pandas as pd
from sklearn.metrics import roc_auc_score, log_loss


def test_model(test_data, val_data, model_file):

    with open(f'../train/{model_file}', 'rb') as inp:
        model = pickle.load(inp)

    print('Successfully read model, generating predictions stats on validation set')
    val = pd.read_csv(f'../data/{val_data}')
    target = val['install']
    val.drop(['install'], axis=1, inplace=True)
    val_pred = model.predict_proba(val)

    ROC_AUC = roc_auc_score(target, val_pred)
    LOG_LOSS = log_loss(target, val_pred)

    print(f'\nThe ROC_AUC score on the val set is {ROC_AUC}.\n')
    print(f'\nThe LOG_LOSS on the val set is {LOG_LOSS}.\n')

    with open('val_output.txt', 'a') as f:
        f.write(str(f'ROC AUC : {ROC_AUC}'))
        f.write(str(f'LOG LOSS : {LOG_LOSS}'))

    print('Generating predictions on the test data')
    test = pd.read_csv(f'../data/{test_data}')
    test_pred = model.predict_proba(test)

    result = pd.DataFrame({
        'id': test.index,
        'prob_install': test_pred[:, 1]
    })

    print('Writing predictions in the data directory as test_predictions')
    result.to_csv('../data/test_predictions.csv', index=False)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--x_test')
    # parser.add_argument('--y_test')
    # parser.add_argument('--model')
    # args = parser.parse_args()
    test_model('test_df_processed.csv',
               'val_df_processed.csv', 'finalized_model.sav')
