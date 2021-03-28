# This deployment file is not needed as we are using the prepackaged XGBoost server from seldon core.
# NOTE: model.bst is renamed finalized_model.sav

# from xgboost import XGBClassifier


# class Deploy(object):
#     """
#     Model template to expose model as a rest service via docker
#     """

#     def __init__(self):
#         """
#         Add any initialization parameters. These will be passed at runtime from the graph definition parameters \
#         defined in your seldondeployment kubernetes resource manifest.

#         We should ideally pass a model file path but for this exercise we are keeping it simple.
#         """
#         print("Initializing model")

#         self.model = XGBClassifier(scale_pos_weight=85, max_delta_step=5, learning_rate=0.05,
#                                    use_label_encoder=False, random_state=2021,
#                                    tree_method='gpu_hist', predictor='gpu_predictor')

#         self.model.load_model('model.bst')

#     def predict(self, X, features_names):
#         """
#         Return a prediction.

#         Parameters
#         ----------
#         X : array-like
#         feature_names : array of feature names (optional)
#         """
#         print("Predict called - will run identity function")
#         return self.model.predict_proba(X)
