import argparse
import joblib
import numpy as np
from sklearn.metrics import roc_auc_score, log_loss


def test_model(x_test, y_test, model_path):
    x_test_data = np.load(x_test)
    y_test_data = np.load(y_test)

    model = joblib.load(model_path)
    y_pred = model.predict(x_test_data)

    ROC_AUC = roc_auc_score(y_test_data, y_pred)
    LOG_LOSS = log_loss(y_test_data, y_pred)

    print(f'\nThe ROC_AUC score on the test set is {ROC_AUC}.\n')
    print(f'\nThe LOG_LOSS on the test set is {LOG_LOSS}.\n')

    with open('output.txt', 'a') as f:
        f.write(str(f'ROC AUC : {ROC_AUC}'))
        f.write(str(f'LOG LOSS : {LOG_LOSS}'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--x_test')
    parser.add_argument('--y_test')
    parser.add_argument('--model')
    args = parser.parse_args()
    test_model(args.x_test, args.y_test, args.model)
