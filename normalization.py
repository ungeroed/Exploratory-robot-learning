def normalize(sensor_state):
    def _norm(min_value, max_value):
        return (lambda value: float(value + min_value) / float(max_value - min_value))

    prox = [0.0, 4500.0]
    ground = [0.0, 1000.0]
    acc = [-32.0, 32.0]
    mic = [0.0, 255.0]

    values = []

    values += map(_norm(*prox), sensor_state["frontSensors"])
    values += map(_norm(*prox), sensor_state["rearSensors"])
    values += map(_norm(*ground), sensor_state["groundSensors"][-1:])
    #values += map(_norm(*acc), sensor_state["accelerometer"])
    #values += map(_norm(*mic), [sensor_state["micIntensity"]])

    if sensor_state["lassoState"] == 'down':
        values.append(1.0)
    else:
        values.append(0.0)

    return values

# Application entry point
if __name__ == '__main__':
    data = {
        "frontSensors": [0, 0, 4400, 2500, 100],
        "groundSensors": [5, 800, 795],
        "rearSensors": [3300, 0],
        "accelerometer": [-17, 29, 2],
        "micIntensity": 95,
        "lassoState": True
    }
    print(data)
    print(normalize(data))
