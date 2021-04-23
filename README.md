# Vive Accuracy Experiment

This is a refactor or probably better described as a rewrite of another git repo of mine. 

## Architecture

Essentially, the pipeline goes as follows:

1. Read raw data using `utils.read_measurement_files.py`
2. Use `pre_process_data.py` to average/check for corrupted (aka moved the tripod during measurement)
3. Use `build_data.py` to construct the data point objects
4. Use `analysis.py` to calculate the distance between points to get the evaluation of the relative error
5. Use `plot.py` to plot the data