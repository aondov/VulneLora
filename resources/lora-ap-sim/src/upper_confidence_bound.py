import math


class UpperConfidenceBound:
    def __init__(self, net_data):
        """
        UCB constructor
        :param net_data: list, list of all arms
        """
        self.arms_selected = []
        self.net_data = net_data
        self.num_of_arms = len(net_data)
        self.num_of_selections = [0] * self.num_of_arms
        self.sums_of_rewards = [0] * self.num_of_arms
        self.total_reward = 0
        self.num_tries = 0

    def select_arm(self):
        """
        Selects the best arm from net_data.
        :return dict, returns selected arm
        """
        arm = 0
        max_upper_bound = 0

        for i in range(0, self.num_of_arms):
            if self.num_of_selections[i] > 0:
                avg_reward = self.sums_of_rewards[i] / self.num_of_selections[i]
                upper_bound = self._factor_importance_each_arm(self.num_of_selections[i], avg_reward)
            else:
                upper_bound = 1e400

            if upper_bound > max_upper_bound:
                max_upper_bound = upper_bound
                arm = i
        self.num_tries += 1
        self.arms_selected.append(arm)
        self.num_of_selections[arm] += 1
        chosen_arm = self.net_data[arm]
        reward = chosen_arm['rw']
        self.sums_of_rewards[arm] += reward
        self.total_reward += reward
        return chosen_arm

    def _factor_importance_each_arm(self, num_selections, avg_reward):
        """
        This method represents the core of the UCB algorithm.
        :param num_selections: int, number of selections for given arms
        :param avg_reward: float, average reward calculated from all previous rewards
        :return float, number of importance
        """
        exploration_factor = math.sqrt(2 * math.log(self.num_tries + 1) / num_selections)
        print(f'AVG_RW: {avg_reward} EXPL_FACTOR: {exploration_factor}')
        return avg_reward + exploration_factor

    def update_reward(self, sf, pw, rw):
        """
        This method updates a reward for a given arm.
        :param sf: int, spreading factor
        :param pw: int, power
        :param rw: int, reward
        """
        i = 0
        for data in self.net_data:
            if data.sf == sf and data.pw == pw:
                self.net_data[i]['rw'] = rw
                print(f'Reward updated to SF={sf},TP={pw},RW={rw}')
            i += 1

    def increment_reward(self, sf, pw, inc=1):
        """
        This method updates a reward for a given arm.
        :param inc: int, increment
        :param sf: int, spreading factor
        :param pw: int, power
        """
        i = 0
        for data in self.net_data:
            if data.sf == sf and data.pw == pw:
                self.net_data[i]['rw'] += inc
                print(f'Reward incremented to SF={sf},TP={pw},RW={self.net_data[i]["rw"]}')
            i += 1

    def decrement_reward(self, sf, pw, dec=1):
        """
        This method updates a reward for a given arm.
        :param dec: int, decrement
        :param sf: int, spreading factor
        :param pw: int, power
        """
        i = 0
        for data in self.net_data:
            if data.sf == sf and data.pw == pw:
                self.net_data[i]['rw'] -= dec
                print(f'Reward decremented to SF={sf},TP={pw},RW={self.net_data[i]["rw"]}')
            i += 1

    def update_arms(self, net_data):
        """
        Replace old model with new one
        :param net_data: dict, arms as a dictionary
        :return void
        """
        self.net_data = net_data
