import pandas as pd
import re
import locale
import numpy as np

locale.setlocale(locale.LC_NUMERIC, 'en_US.utf8')


class CarTransformer:
    # __df: pd.DataFrame
    #
    # def __init__(self, df: pd.DataFrame):
    #     self.__df = df

    @staticmethod
    def __parse_mileage(mileage_str):
        if pd.isnull(mileage_str):
            return np.NaN
        res = re.findall(r"(\d+[\.|,]?\d*)[\s]?((?:km\/kg)|(?:kmpl))*", mileage_str)
        mileage = locale.atof(res[0][0])
        torque_meas = res[0][1]
        if torque_meas == 'km/kg':
            mileage = round(mileage * 1.4, 2)
        return mileage

    @staticmethod
    def __parse_torque(torque_str):
        if pd.isnull(torque_str):
            return pd.Series([np.NaN, np.NaN])
        res = re.findall(r"(\d+[\.|,]?\d*)[\s|\(]?((?:Nm)|(?:kgm))*", torque_str)
        torque = locale.atof(res[0][0])
        torque_max = locale.atoi(res[-1][0])
        torque_meas = max(res[0][1], res[-1][1])
        if torque_meas == 'kgm':
            torque = round(torque * 9.80665, 2)
        return pd.Series([torque, torque_max])

    @staticmethod
    def __rem_measure_and_cast_float(__df: pd.DataFrame, column_name):
        # self.__df[column_name] = self.__df[column_name].replace(to_replace="(\d+.?\d*).*", value=r"\1", regex=True).astype(float)
        __df[column_name] = __df[column_name].replace(to_replace="(\d+.?\d*).*", value=r"\1",
                                                                regex=True).astype(float)

    @staticmethod
    def transform_value_columns(__x_df: pd.DataFrame) -> pd.DataFrame:
        CarTransformer.__rem_measure_and_cast_float(__x_df, 'engine')
        __x_df.loc[__x_df['max_power'] == ' bhp', 'max_power'] = np.nan
        CarTransformer.__rem_measure_and_cast_float(__x_df, 'max_power')
        __x_df[['torque', 'max_torque_rpm']] = __x_df.loc[:, 'torque'].apply(CarTransformer.__parse_torque)
        __x_df['mileage'] = __x_df.loc[:, 'mileage'].apply(CarTransformer.__parse_mileage)
        return __x_df

    @staticmethod
    def convert_values_to_int(__x_df: pd.DataFrame) -> pd.DataFrame:
        __x_df['engine'] = __x_df['engine'].astype(int)
        __x_df['max_torque_rpm'] = __x_df['max_torque_rpm'].astype(int)
        __x_df['seats'] = __x_df['seats'].astype(int).astype(object)
        return __x_df

    @staticmethod
    def split_dataset(__df: pd.DataFrame) -> (pd.DataFrame, pd.Series):
        x = __df.drop('selling_price', axis=1)
        y = __df['selling_price']
        return x, y

    @staticmethod
    def drop_columns(__x_df: pd.DataFrame) -> (pd.DataFrame, pd.Series):
        __x_df = __x_df.drop(['name'], axis=1)
        return __x_df

    @staticmethod
    def drop_duplicates(__x_df: pd.DataFrame) -> pd.DataFrame:
        features_columns = [x for x in __x_df.columns.values if x != 'selling_price']
        __x_df[__x_df.duplicated(subset=features_columns, keep=False)].sort_values(
            features_columns + ['selling_price'])
        __x_df.drop_duplicates(subset=features_columns, inplace=True)
        __x_df.reset_index(drop=True, inplace=True)
        return __x_df

    @staticmethod
    def covert_year_to_centered_square(__x_df: pd.DataFrame) -> pd.DataFrame:
        __x_df['year'] = (__x_df['year'] - 1995) ** 2
        return __x_df
