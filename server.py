from flask import Flask, request, send_from_directory
import numpy as np
import pandas as pd
from hmmlearn import hmm
import json

app = Flask(__name__)


@app.route("/data", methods=['POST'])
def data():
    # check if the post request has the file part
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        # load training data
        train_data = pd.read_csv("aircon_train.csv")
        train_cols_with_nonempty = train_data.columns[train_data.notna().any()].tolist()[
            1:]

        # load testing data and remove empty columns in training data
        test_data = pd.read_csv(file)
        test_cols_with_nonempty = test_data.columns[test_data.notna().any()].tolist()[
            1:]
        train_cols_with_nonempty = [
            col for col in train_cols_with_nonempty if col in test_cols_with_nonempty]

        # extract non-empty columns from training data
        train_X = train_data[train_cols_with_nonempty]

        # train HMM model
        train_model = hmm.GaussianHMM(n_components=2, covariance_type='diag')
        train_model.fit(train_X)

        # load testing data
        test_timestamp_str = test_data['Timestamp'].values
        # convert timestamp strings to datetime objects
        test_timestamp = pd.to_datetime(test_timestamp_str)
        test_voltage = test_data['v'].values
        test_current = test_data['i'].values
        # calculate power from voltage and current data
        test_power = test_voltage * test_current

        # reshape and tile
        # test_power = np.nan_to_num(
        #     test_power, nan=np.nan, posinf=np.nan, neginf=np.nan)
        # test_power = test_power[np.isfinite(test_power)]
        # if test_power.size > 0:
        #     test_power = np.tile(test_power.reshape(-1, 1),
        #                          (1, len(train_cols_with_nonempty)))
        #     test_power = test_power.reshape(test_power.shape[0], -1)
        #     test_power = test_power.squeeze()

        # remove columns with all missing values
        test_data = test_data.dropna(axis=1, how='all')

        # replace missing values with mean value
        test_data = test_data.fillna(test_data.mean(numeric_only=True))

        # convert infinite values to NaN
        test_data = test_data.replace([np.inf, -np.inf], np.nan)

        # drop rows with NaN values
        test_data = test_data.dropna()

        # test HMM model
        test_X = test_data[train_cols_with_nonempty]
        if test_X.shape[0] > 0:
            test_probabilities = train_model.predict_proba(test_X)
        else:
            print("Error: test_X is empty")

        # detect on periods
        threshold = 0.5
        test_states = (test_probabilities[:, 0] > threshold).astype(int)
        test_start_indices = np.where(np.diff(test_states) == 1)[0] + 1
        test_end_indices = np.where(np.diff(test_states) == -1)[0]

        if len(test_start_indices) > len(test_end_indices):
            test_start_indices = test_start_indices[:-1]

        if len(test_start_indices) < len(test_end_indices):
            test_end_indices = test_end_indices[1:]

        data_dict = {
            "timestamp": test_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ').tolist(),
            "power": test_power.tolist(),
            "states": test_states.tolist()
        }

        return json.dumps(data_dict)


@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)


@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


if __name__ == "__main__":
    app.run(debug=True)
