def to_dict(obj):
    """
    Convert object to dictionary, source:

    https://stackoverflow.com/questions/1036409/recursively-convert-python-object-graph-to-dictionary

    :param obj: Instance of a class
    :return: Object serialized to a dictionary
    """
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict(v)
        return data
    elif hasattr(obj, "_ast"):
        return to_dict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [to_dict(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, to_dict(value))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        return data
    else:
        return obj
