from statistics import mean, stdev

import numpy as np
from scipy.stats import skew

from data_objects.raw_session import RawSession
from preparation_system.prepared_session import PreparedSession


class PreparedSessionGenerator:

    def __init__(self, raw_session: RawSession):
        self.raw_session = raw_session
        self.prepared_session = None
        self.time_diff = None
        self.norm_amount = []

    def generate_time_diff(self):
        transactions = self.raw_session.transactions
        time = []
        for transaction in transactions:
            # converto time (str) in long int
            hour, minute, sec = transaction.commercial.time.split(':')
            time_int = int(hour) * 3600 + int(minute) * 60 + int(sec)
            time.append(time_int)
        time_array = np.array(time)
        self.time_diff = list(np.diff(time_array))

    def generate_time_mean(self):
        return mean(self.time_diff)

    def generate_time_std(self):
        return stdev(self.time_diff)

    def generate_time_skew(self):
        return skew(np.array(self.time_diff))

    def generate_norm_amount(self):
        transactions = self.raw_session.transactions
        amount = []
        for transaction in transactions:
            amount.append(float(transaction.commercial.amount))
        amount_min, amount_max = min(amount), max(amount)
        for val in amount:
            temp = (val - amount_min) / (amount_max - amount_min)
            self.norm_amount.append(temp)

    def extract_features(self):
        self.generate_time_diff()
        time_mean = self.generate_time_mean()
        time_std = self.generate_time_std()
        time_skew = self.generate_time_skew()
        self.generate_norm_amount()

        self.prepared_session = PreparedSession(self.raw_session.session_id, time_mean,
                                                time_std, time_skew, self.norm_amount,
                                                self.raw_session.attack_risk_label)

        return self.prepared_session.to_dict()