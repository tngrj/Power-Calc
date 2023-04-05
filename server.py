from flask import Flask, request, send_from_directory
import numpy as np
import pandas as pd
from hmmlearn import hmm
import json

app = Flask(__name__)


@app.route("/aircon", methods=['POST'])
def aircon():
    # check if the post request has the file part
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        train_data = pd.read_csv("aircon_train.csv")
        test_data = pd.read_csv(file)
        return json.dumps(data_processing(train_data, test_data))


@app.route("/oven", methods=['POST'])
def oven():
    # check if the post request has the file part
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        train_data = pd.read_csv("oven_train.csv")
        test_data = pd.read_csv(file)
        return json.dumps(data_processing(train_data, test_data))


@app.route("/heater", methods=['POST'])
def heater():
    # check if the post request has the file part
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        train_data = pd.read_csv("heater_train.csv")
        test_data = pd.read_csv(file)
        return json.dumps(data_processing(train_data, test_data))


def data_processing(train_data, test_data):
    train_cols_with_nonempty = train_data.columns[train_data.notna().any()].tolist()[
        1:]

    # load testing data and remove empty columns in training data
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
    power_consump = np.nan_to_num(
        test_power, nan=np.nan, posinf=np.nan, neginf=np.nan)
    power_consump = power_consump[np.isfinite(power_consump)]
    if power_consump.size > 0:
        power_consump = np.tile(power_consump.reshape(-1, 1),
                                (1, len(train_cols_with_nonempty)))
        power_consump = power_consump.reshape(power_consump.shape[0], -1)
        power_consump = power_consump.squeeze()

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

    # calculate power consumption during on periods
    test_power_consumption = []
    for start, end in zip(test_start_indices, test_end_indices):
        # power data during on period
        test_power_on = power_consump[start:end+1]
        # energy consumed during on period in Wh
        test_energy_on = np.trapz(test_power_on, dx=1) / 3600
        test_power_consumption.append(test_energy_on)

    period_info_list = []

    # calculate and print total energy consumption during on periods
    for i, energy in enumerate(test_power_consumption):
        start = test_timestamp[test_start_indices[i]]
        end = test_timestamp[test_end_indices[i]]
        total_energy = sum(energy)
        duration = (end - start).total_seconds() / 3600  # in hours
        avg_power = total_energy / duration
        cost = (avg_power/1000 * 27.43)/100
        period_info = f"On period {i+1}: From {start} to {end}, Total Power Consumption: {total_energy:.1f} Wh. Average power of {avg_power:.1f} W. Cost of ${cost:.2f}"
        period_info_list.append(period_info)

    data_dict = {
        "timestamp": test_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ').tolist(),
        "power": test_power.tolist(),
        "states": test_states.tolist(),
        "period_info": period_info_list
    }

    return data_dict


@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)


@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


if __name__ == "__main__":
    app.run(debug=True)
