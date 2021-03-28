import argparse
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, log_loss


def train_model(train_data, val_data):

    print('Reading training and validation data')
    train = pd.read_csv(train_data')
    val = pd.read_csv(val_data)

    y_train = train['install']
    train.drop(['install'], axis=1, inplace=True)

    y_val = val['install']
    val.drop(['install'], axis=1, inplace=True)

    model = XGBClassifier(scale_pos_weight=85, max_delta_step=5, learning_rate=0.05,
                          use_label_encoder=False, random_state=2021,
                          tree_method='gpu_hist', predictor='gpu_predictor',
                          n_estimators=500)

    model.fit(train, y_train, eval_set=[(train, y_train), (val, y_val)],
              # This can reflect in system logs once we enable a logging method.
              eval_metric=['logloss', 'auc'],
              verbose=True)

    pred = model.predict_proba(val)
    y_pred = pred[:, 1]

    ROC_AUC = roc_auc_score(y_val, y_pred)
    LOG_LOSS = log_loss(y_val, y_pred)

    print(f'\nThe ROC_AUC score on the val set is {ROC_AUC}.\n')
    print(f'\nThe LOG_LOSS on the val set is {LOG_LOSS}.\n')

    with open('val_output.txt', 'a') as f:
        f.write(str(f'ROC AUC : {ROC_AUC}'))
        f.write(str(f'LOG LOSS : {LOG_LOSS}'))

    model.save_model('finalized_model.sav')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_data')
    parser.add_argument('--val_data')
    args = parser.parse_args()
    train_model(args.train_data, args.val_data)
    print('Model trained and saved')
