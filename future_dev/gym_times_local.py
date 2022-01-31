import openpyxl
import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta
import matplotlib.pyplot as plt
from matplotlib.dates import date2num


def main():
    gym_times_raw = pd.read_excel("test_dillon_data.xlsx")
    first_of_day = pd.notnull(gym_times_raw["Day"])
    gym_times_raw["First of Day"] = first_of_day
    gym_times_raw["Time of Day"] = gym_times_raw["Time of Day"].apply(
        func=lambda x: x.upper()
    )
    gym_times_raw["Stephen's Fitness Center"].replace(
        "-", np.NaN, inplace=True
    )
    custom_imputer(gym_times_raw)

    date_list = [
        datetime(2017, 5, 9, 6, 30, 0),
        datetime(2017, 5, 9, 7, 0, 0),
        datetime(2017, 5, 9, 7, 30, 0),
        datetime(2017, 5, 9, 8, 0, 0),
        datetime(2017, 5, 9, 8, 30, 0),
        datetime(2017, 5, 9, 9, 0, 0),
    ]
    start = date_list[0]
    end = date_list[-1]
    total_minutes = (end - start).total_seconds() / 60
    number_of_half_hours = int(total_minutes / 30)
    print(number_of_half_hours)

    half_hour = timedelta(minutes=30)
    day = []
    for i in range(number_of_half_hours):
        day.append(start + (i) * half_hour)

    numweek = date2num(day)

    plt.hist(date_list, bins=numweek, ec="k")
    plt.gcf().autofmt_xdate()
    plt.show()


# performs all imputations for datetime column, and patron #
def custom_imputer(df):
    helper_patron_imputer(df)
    helper_datetime_imputer(df)


#! Just forward-fills and backwards-fills (handles corner cases where
#! missing values are at start and end)
def helper_patron_imputer(df):

    df["Stephen's Fitness Center"].ffill(inplace=True)
    df["Stephen's Fitness Center"].bfill(inplace=True)
    print(df["Stephen's Fitness Center"])


def helper_datetime_imputer(df):
    missing_datetimes = df["Timestamp"].index[
        df["Timestamp"].apply(np.isnan)
    ]
    # 3 cases
    #! 1. NaN datetime entry is between 2 entries on same day
    #   - Read datetime of above + below and use the given time of day

    #! 2. NaN datetime between above entry on earlier day, and below entry on next day
    #   - Corresponds to NaN value being @ start of day
    #   - Use datetime from below

    #! 3. NaN value between above date same day, below date on next day
    #   - Corresponds to NaN value being @ end of day
    #   - Below date is start of next day, use above datetime

    for miss_index in missing_datetimes:
        #! Case 1
        # check explicitly for same day
        if (
            df.loc[miss_index - 1, "Timestamp"].day
            == df.loc[miss_index + 1, "Timestamp"].day
        ):
            # use previous day, (either prev or after works)
            prev_day_datetime_raw = df.loc[miss_index - 1, "Timestamp"]
            current_time_of_day_raw = df.loc[miss_index, "Time of Day"]
            combined_time = datetime_builder(
                prev_day_datetime_raw, current_time_of_day_raw
            )
            df.loc[miss_index, "Timestamp"] = combined_time

        #! Case 2
        if df.loc[miss_index, "First of Day"] == True:
            next_day_datetime_raw = df.loc[miss_index + 1, "Timestamp"]
            current_time_of_day_raw = df.loc[miss_index, "Time of Day"]
            combined_time = datetime_builder(
                next_day_datetime_raw, current_time_of_day_raw
            )
            df.loc[miss_index, "Timestamp"] = combined_time
        #! Case 3
        # miss_index + 1 is the day following missing entry
        if df.loc[miss_index + 1, "First of Day"] == True:
            prev_day_datetime_raw = df.loc[miss_index - 1, "Timestamp"]
            current_time_of_day_raw = df.loc[miss_index, "Time of Day"]
            combined_time = datetime_builder(
                prev_day_datetime_raw, current_time_of_day_raw
            )
            df.loc[miss_index, "Timestamp"] = combined_time


def datetime_builder(date_raw, time_raw):
    time_parsed = datetime.strptime(time_raw, "%I:%M%p")
    imputed_datetime_date = date(
        date_raw.year, date_raw.month, date_raw.day
    )
    imputed_datetime_time = time(time_parsed.hour, time_parsed.minute)
    combined_time = datetime.combine(
        imputed_datetime_date, imputed_datetime_time
    )
    return combined_time


if __name__ == "__main__":
    main()
