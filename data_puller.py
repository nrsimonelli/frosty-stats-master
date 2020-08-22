import psycopg2
import pandas as pd
import numpy as np
from itertools import combinations


class DBConnector:
    def __init__(self, user, pw, host, port, db_name):
        self.user = user
        self.pw = pw
        self.host = host
        self.port = port
        self.db_name = db_name

    def connect_to_db(self):
        connection = psycopg2.connect(user=self.user,
                                      password=self.pw,
                                      host=self.host,
                                      port=self.port,
                                      database=self.db_name)

        return connection.cursor()


class DBPuller:
    def __init__(self, user, pw, host, port, db_name):
        self.db_connector = DBConnector(user, pw, host, port, db_name)

    def fetch_all_games(self):
        cursor = self.db_connector.connect_to_db()
        cursor.execute("select * from games")
        games = cursor.fetchall()
        df = pd.DataFrame(games, columns=[desc[0] for desc in cursor.description])

        cursor.execute("select * from players")
        players = dict(cursor.fetchall())

        df.loc[:, [x for x in df.columns if 'player' in x]] = df.loc[:, [x for x in df.columns if 'player' in x]].apply(lambda x: x.map(players))

        return df


class DataFormatter:
    def __init__(self, user, pw, host, port, db_name):
        self.df = DBPuller(user, pw, host, port, db_name).fetch_all_games()
        self._create_features()

        self.df_per_player = self._stack_per_player_data()
        self.df_player_pairs = self._stack_pair_data()
        self.df_player_vs_opponent = self._create_player_vs_opponent_table()

    def _create_features(self):
        self.df['tiebreaker'] = self.df['tiebreaker'].fillna(0)
        self.df['t1_win'] = np.where(self.df['t1_score'] > self.df['t2_score'], 1, 0)
        self.df['t2_win'] = np.where(self.df['t1_win'] == 0, 1, 0)
        self.df['t1'] = self.df[['t1_player1', 't1_player2', 't1_player3', 't1_player4', 't1_player5']].values.tolist()
        self.df['t2'] = self.df[['t2_player1', 't2_player2', 't2_player3', 't2_player4', 't2_player5']].values.tolist()
        self.df['total_points'] = self.df['t1_score'] + self.df['t2_score']

    def _stack_pair_data(self):
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

    def _stack_per_player_data(self):

        total_wins = pd.concat([self.df.groupby('t1_player1')['t1_win'].sum(),
                                self.df.groupby('t1_player2')['t1_win'].sum(),
                                self.df.groupby('t1_player3')['t1_win'].sum(),
                                self.df.groupby('t1_player4')['t1_win'].sum(),
                                self.df.groupby('t1_player5')['t1_win'].sum(),
                                self.df.groupby('t2_player1')['t2_win'].sum(),
                                self.df.groupby('t2_player2')['t2_win'].sum(),
                                self.df.groupby('t2_player3')['t2_win'].sum(),
                                self.df.groupby('t2_player4')['t2_win'].sum(),
                                self.df.groupby('t2_player5')['t2_win'].sum()], axis=1).sum(axis=1)

        total_points = pd.concat([self.df.groupby('t1_player1')['t1_score'].sum(),
                                  self.df.groupby('t1_player2')['t1_score'].sum(),
                                  self.df.groupby('t1_player3')['t1_score'].sum(),
                                  self.df.groupby('t1_player4')['t1_score'].sum(),
                                  self.df.groupby('t1_player5')['t1_score'].sum(),
                                  self.df.groupby('t2_player1')['t2_score'].sum(),
                                  self.df.groupby('t2_player2')['t2_score'].sum(),
                                  self.df.groupby('t2_player3')['t2_score'].sum(),
                                  self.df.groupby('t2_player4')['t2_score'].sum(),
                                  self.df.groupby('t2_player5')['t2_score'].sum()], axis=1).sum(axis=1)

        total_points_played = pd.concat([self.df.groupby('t1_player1')['total_points'].sum(),
                                         self.df.groupby('t1_player2')['total_points'].sum(),
                                         self.df.groupby('t1_player3')['total_points'].sum(),
                                         self.df.groupby('t1_player4')['total_points'].sum(),
                                         self.df.groupby('t1_player5')['total_points'].sum(),
                                         self.df.groupby('t2_player1')['total_points'].sum(),
                                         self.df.groupby('t2_player2')['total_points'].sum(),
                                         self.df.groupby('t2_player3')['total_points'].sum(),
                                         self.df.groupby('t2_player4')['total_points'].sum(),
                                         self.df.groupby('t2_player5')['total_points'].sum()], axis=1).sum(axis=1)

        total_games = pd.concat([self.df.groupby('t1_player1').size(),
                                 self.df.groupby('t1_player2').size(),
                                 self.df.groupby('t1_player3').size(),
                                 self.df.groupby('t1_player4').size(),
                                 self.df.groupby('t1_player5').size(),
                                 self.df.groupby('t2_player1').size(),
                                 self.df.groupby('t2_player2').size(),
                                 self.df.groupby('t2_player3').size(),
                                 self.df.groupby('t2_player4').size(),
                                 self.df.groupby('t2_player5').size()], axis=1).sum(axis=1)

        tbl = pd.concat([total_wins, total_points, total_points_played, total_games], axis=1)
        tbl.columns = ['tot_wins', 'total_points_scored', 'total_points_played', 'tot_games']
        tbl['win_perc'] = tbl['tot_wins'] / tbl['tot_games']
        tbl['ppg'] = tbl['total_points_scored'] / tbl['tot_games']
        tbl['point_score_perc'] = tbl['total_points_scored'] / tbl['total_points_played']
        return tbl

    def _create_player_vs_opponent_table(self):
        t1_1 = self.df[['t1_player1', 't2_player1', 't2_player2', 't2_player3', 't2_player4', 't2_player5', 't1_win']].melt(['t1_player1', 't1_win'])
        t1_2 = self.df[['t1_player2', 't2_player1', 't2_player2', 't2_player3', 't2_player4', 't2_player5', 't1_win']].melt(['t1_player2', 't1_win'])
        t1_3 = self.df[['t1_player3', 't2_player1', 't2_player2', 't2_player3', 't2_player4', 't2_player5', 't1_win']].melt(['t1_player3', 't1_win'])
        t1_4 = self.df[['t1_player4', 't2_player1', 't2_player2', 't2_player3', 't2_player4', 't2_player5', 't1_win']].melt(['t1_player4', 't1_win'])

        t2_1 = self.df[['t2_player1', 't1_player1', 't1_player2', 't1_player3', 't1_player4', 't1_player5', 't2_win']].melt(['t2_player1', 't2_win'])
        t2_2 = self.df[['t2_player2', 't1_player1', 't1_player2', 't1_player3', 't1_player4', 't1_player5',  't2_win']].melt(['t2_player2', 't2_win'])
        t2_3 = self.df[['t2_player3', 't1_player1', 't1_player2', 't1_player3', 't1_player4', 't1_player5',  't2_win']].melt(['t2_player3', 't2_win'])
        t2_4 = self.df[['t2_player4', 't1_player1', 't1_player2', 't1_player3', 't1_player4', 't1_player5',  't2_win']].melt(['t2_player4', 't2_win'])

        tbls = [t1_1, t1_2, t1_3, t1_4, t2_1, t2_2, t2_3, t2_4]

        for tbl in tbls:
            tbl.columns = ['player', 'win', 'variable', 'opponent', ]

        tbls = [tbl[['player', 'opponent', 'win']] for tbl in tbls]
        return pd.concat(tbls)

    def create_count_heatmap(self):
        return pd.crosstab(self.df_player_pairs[0], self.df_player_pairs[1]).astype(float)

    def create_wr_heatmap(self):
        return pd.crosstab(self.df_player_pairs[0], self.df_player_pairs[1], aggfunc='mean', values=self.df_player_pairs['win'])

