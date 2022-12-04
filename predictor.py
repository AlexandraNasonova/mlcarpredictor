import pandas as pd
import joblib
from cartransformer import CarTransformer


class Predictor:

    @staticmethod
    def __prepare_data(df: pd.DataFrame):
        df = CarTransformer.transform_value_columns(df)
        df = CarTransformer.drop_columns(df)
        df = CarTransformer.covert_year_to_centered_square(df)
        return df

    @staticmethod
    def predict(df: pd.DataFrame) -> pd.Series:
        df = Predictor.__prepare_data(df)
        pipeline = joblib.load('pipeline.pkl')
        prices = pipeline.predict(df)
        return prices
