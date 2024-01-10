# Inspired by Thompson Bernoulli Example: https://github.com/JussiM01/ThompsonSampling/blob/master/thompsonbernoulli.py
# and https://github.com/alison-carrera/mabalgs/blob/master/mab/algs.py

import random


class ThompsonSampling:
    def __init__(self, net_data):
        """
        Thompson Sampling Constructor
        :param net_data: list, list of bandit arms
        """
        self.net_data = net_data
        self.num_arms = len(net_data)
        self.alphas = [1] * self.num_arms
        self.betas = [1] * self.num_arms
        self.successes = [0] * self.num_arms
        self.failures = [0] * self.num_arms

    def setup(self, alphas, betas, successes, failures):
        """
        Thompson Sampling Constructor
        :param failures:
        :param successes:
        :param betas:
        :param alphas:
        """
        self.alphas = alphas
        self.betas = betas
        self.successes = successes
        self.failures = failures

    def select_arm(self):
        """
        Select an arm base on alpha and bate values
        :return dict, selected arm as a dictionary
        """
        thetas = []

        for i in range(len(self.alphas)):
            thetas.append(random.betavariate(self.successes[i] + self.alphas[i], self.failures[i] + self.betas[i]))

        return self.net_data[thetas.index(max(thetas))]

    def update_reward(self, arm, reward):
        """
        Update reward in arm
        :param arm: int, selected arm
        :param reward: int, reward increment or decrement
        :return void
        """
        index = self.net_data.index(arm)

        if reward == 1:
            self.successes[index] += 1
        else:
            self.failures[index] += 1

