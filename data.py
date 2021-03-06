import pandas as pd

from enum import Enum

from datetime import datetime

POSITIVE_KEYWORD = 'Positiu'
NEGATIVE_STR = 'Sospitós'


class DataColumn(Enum):

    date = 'TipusCasData'
    abs_code = 'ABSCodi'
    abs_text = 'ABSDescripcio'
    diagnose = 'TipusCasDescripcio'
    cases = 'NumCasos'


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """ Rename columns to the expected names """

    def column(df: pd.DataFrame, column: DataColumn) -> str:
        return [col for col in df.columns.values if column.value in col][0]

    return df.rename(columns={
        column(df, DataColumn.date): 'Date',
        column(df, DataColumn.abs_code): 'ABSCode',
        column(df, DataColumn.abs_text): 'ABSText',
        column(df, DataColumn.diagnose): 'Diagnose',
        column(df, DataColumn.cases): 'Cases',
    })


def latest_data():
    df = pd.read_csv('rows.csv')
    # Rename columns, as column names usually change
    df = rename_columns(df)
    df = df.dropna(subset=['Date', 'Diagnose', 'Cases'])
    # Parse date into DateTime
    df.Date = df.Date.apply(
        lambda x: datetime.strptime(x, '%d/%m/%Y')
    )
    return df



def tests_per_abs(df: pd.DataFrame) -> pd.DataFrame:
    return df \
        .groupby(['ABSCode', 'ABSText'])['Cases'] \
        .sum() \
        .reset_index(name='TotalTests')


def daily_tests(df: pd.DataFrame) -> pd.DataFrame:
    return df \
        .groupby(['Date']).Cases \
        .sum() \
        .reset_index(name='Tests') \
        .fillna(0)


def daily_positive_rates(df: pd.DataFrame) -> pd.DataFrame:

    def _get_positive_perc(df: pd.DataFrame) -> float:
        positives = df[df.Diagnose.str.contains(POSITIVE_KEYWORD)].Cases.sum()
        return round(positives / df.Cases.sum() * 100, 2)

    return df \
        .groupby(['Date']) \
        .apply(_get_positive_perc) \
        .reset_index(name='Percentatge positius') \
        .fillna(0)


def total_tests_num(df: pd.DataFrame) -> int:
    return df.Cases.sum()
