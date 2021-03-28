import kfp
from kfp import dsl


def preprocess_op():

    return dsl.ContainerOp(
        name='Preprocess Data',
        image='prany/exercise_preprocessing:latest',
        arguments=[],
        file_outputs={
            'train_data': '/app/data/train_df_processed.csv',
            'val_data': '/app/data/val_df_processed.csv',
            'test_data': '/app/data/test_df_processed.csv'
        }
    )


def train_op(train_data, val_data):

    return dsl.ContainerOp(
        name='Train Model',
        image='prany/exercise_train:latest',
        arguments=[
            '--train_data', train_data,
            '--val_data', val_data
        ],
        file_outputs={
            'model': '/app/finalized_model.sav',
            'metrics': '/app/val_output.txt'
        }
    )


def test_op(test_data, model_file):

    return dsl.ContainerOp(
        name='Test Model',
        image='prany/exercise_test:latest',
        arguments=[
            '--test_data', test_data,
            '--model_file', model_file
        ],
        file_outputs={
            'preds': '/app/data/test_predictions.csv'
        }
    )


def deploy_model_op(model):

    return dsl.ContainerOp(
        name='Deploy Model',
        image='prany/exercise_deploy:latest',
        arguments=[
            '--model', model
        ]
    )


@dsl.pipeline(
    name='Exercise',
    description='An example of an end-to-end ML pipeline.'
)
def exercise():
    _preprocess_op = preprocess_op()

    _train_op = train_op(
        dsl.InputArgumentPath(_preprocess_op.outputs['train_data']),
        dsl.InputArgumentPath(_preprocess_op.outputs['val_data'])
    ).after(_preprocess_op)

    _test_op = test_op(
        dsl.InputArgumentPath(_preprocess_op.outputs['test_data']),
        dsl.InputArgumentPath(_train_op.outputs['model'])
    ).after(_train_op)

    deploy_model_op(
        dsl.InputArgumentPath(_train_op.outputs['model'])
    ).after(_test_op)


client = kfp.Client()
client.create_run_from_pipeline_func(exercise, arguments={})
