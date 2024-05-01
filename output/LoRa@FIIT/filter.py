import pandas as pd


def filter(data, config, enable_filtering=True, operator="OR", debug=False):
    if enable_filtering:
        filtered_data = data.copy()
        filter_condition = None
        for key, value in config.items():
            try:
                if len(config[key]) == 0:
                    if debug:
                        print(f"Skipping {key}")
                    continue
                if key == "recv_time_from" and config["recv_time_from"]:
                    from_time = pd.to_datetime(value)
                    if "recv_time_to" in config and config["recv_time_to"]:
                        to_time = pd.to_datetime(config["recv_time_to"])
                        filtered_data['receive_time'] = pd.to_datetime(filtered_data['receive_time'])
                        condition = (filtered_data['receive_time'] >= from_time) & (filtered_data['receive_time'] <= to_time)
                    else:
                        condition = (pd.to_datetime(filtered_data['receive_time']) >= from_time)
                elif key == "recv_time_to" and config["recv_time_to"]:
                    to_time = pd.to_datetime(value)
                    condition = (pd.to_datetime(filtered_data['receive_time']) <= to_time)
                else:
                    for val in config[key]:
                        condition = (filtered_data[key] == val)
                        if filter_condition is None:
                            filter_condition = condition
                        else:
                            if operator == "AND":
                                filter_condition &= condition
                            else:
                                filter_condition |= condition
                    continue

                if filter_condition is None:
                    filter_condition = condition
                else:
                    if operator == "AND":
                        filter_condition &= condition
                    else:
                        filter_condition |= condition

            except KeyError:
                continue

        if filter_condition is not None:
            filtered_data = filtered_data[filter_condition]

        return filtered_data

    else:
        return data
