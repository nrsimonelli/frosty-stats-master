import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations


class HeatMapGraphMaker:
    def __init__(self, fn, tie_breakers=False):
        self.df = pd.read_csv(fn)
        self.tie_breakers = tie_breakers

        self._create_features()
        self._handle_tiebreakers()
        self.df_stacked = self._stack_data()
        plt.style.use('ggplot')

    def _create_features(self):
        self.df['tiebreaker'] = self.df['tiebreaker'].fillna(0)
        self.df['t1_win'] = np.where(self.df['t1_points'] > self.df['t2_points'], 1, 0)
        self.df['t2_win'] = np.where(self.df['t1_win'] == 0, 1, 0)
        self.df['t1'] = self.df[['t1_player1', 't1_player2', 't1_player3', 't1_player4']].values.tolist()
        self.df['t2'] = self.df[['t2_player1', 't2_player2', 't2_player3', 't2_player4']].values.tolist()

    def _handle_tiebreakers(self):
        self.df = self.df[self.df['tiebreaker'] == 0].copy()

    def _stack_data(self):
        dfs = []
        # iterate all games & the two teams rosters, create all possible combinations of 2
        # create "win" 1/0 indicator attribute
        for data in self.df[['t1', 't1_win']].values:
            row = pd.DataFrame(list(combinations(data[0], 2)))
            row['win'] = data[1]
            dfs.append(row)

        for data in self.df[['t2', 't2_win']].values:
            row = pd.DataFrame(list(combinations(data[0], 2)))
            row['win'] = data[1]
            dfs.append(row)

        df_stacked = pd.concat([pd.concat(dfs)[[0, 1, 'win']],
                                pd.concat(dfs)[[1, 0, 'win']].rename({1: 0, 0: 1}, axis=1)])

        return df_stacked.dropna().reset_index(drop=True)

    def create_count_heatmap(self):
        return pd.crosstab(self.df_stacked[0], self.df_stacked[1]).astype(float)

    def create_wr_heatmap(self):
        return pd.crosstab(self.df_stacked[0], self.df_stacked[1], aggfunc='mean', values=self.df_stacked['win'])

