import argparse
import pandas as pd
from xgboost import XGBClassifier


def test_model(test_data, model_file):

    model = XGBClassifier(scale_pos_weight=85, max_delta_step=5, learning_rate=0.05,
                          use_label_encoder=False, random_state=2021,
                          tree_method='gpu_hist', predictor='gpu_predictor')

    model.load_model(model_file)

    print('Successfully read model.')
    print('Generating predictions on the test data.')
    test = pd.read_csv(test_data)
    test_pred = model.predict_proba(test)

    result = pd.DataFrame({
        'id': test.index,
        'prob_install': test_pred[:, 1]
    })

    print('Writing predictions in the data directory as test_predictions')
    result.to_csv('data/test_predictions.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_data')
    parser.add_argument('--model_file')
    args = parser.parse_args()
    test_model(args.test_data, args.model_file)
