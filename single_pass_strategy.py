from itertools import product
from functools import partial
from typing import Tuple

import multiprocessing as mp
import numpy as np
import pandas as pd
from tqdm import tqdm

from utils import guess_result, filter


class SinglePassStrategy():
    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df
        self._num_choices = len(df)

        self.guess_row = self.guess()

    def guess(self):
        indices = [p for p in product(*[range(self._num_choices), range(self._num_choices)])]
        with mp.Pool(mp.cpu_count()) as pool:
            possibilities_after_guess_table = list(tqdm(pool.imap(
                partial(mp_function, df=self._df),
                indices
            )))

        information_arr = np.array(possibilities_after_guess_table)
        information_arr = information_arr[:,2].reshape((self._num_choices, self._num_choices))
        min_index = np.argmin(np.sum(information_arr, axis=1))
        return self._df.iloc[min_index].to_dict()


def mp_function(indices: Tuple[int, int], df: pd.DataFrame): 
    guess_idx: int = indices[0]
    actual_idx: int = indices[1]

    filtered_df = df.copy()

    res = guess_result(df.iloc[guess_idx], df.iloc[actual_idx])

    filtered_df = filter(
        filtered_df,
        df.iloc[guess_idx],
        res
    )

    return (guess_idx, actual_idx, len(filtered_df))