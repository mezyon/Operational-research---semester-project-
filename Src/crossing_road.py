import random
from copy import deepcopy
from math import inf

possible_combinations = {
    0: [1, 1, 0, 0, 0, 0, 0, 0],
    1: [0, 0, 1, 1, 0, 0, 0, 0],
    2: [0, 0, 0, 0, 1, 1, 0, 0],
    3: [0, 0, 0, 0, 0, 0, 1, 1],
    4: [0, 1, 0, 0, 0, 0, 1, 0],
    5: [1, 0, 0, 1, 0, 0, 0, 0],
    6: [0, 0, 1, 0, 0, 1, 0, 0],
    7: [0, 0, 0, 0, 1, 0, 0, 1],
    8: [0, 1, 0, 0, 0, 1, 0, 0],
    9: [0, 0, 0, 1, 0, 0, 0, 1],
    10: [0, 0, 1, 0, 0, 0, 1, 0],
    11: [1, 0, 0, 0, 1, 0, 0, 0]
}


class Simulation:

    def __init__(self, n_vect_start=[]):
        self.n_vect_start = n_vect_start
        self.ni = None
        self.t_list = None
        # self.quality = None
        self.population = list()

    def get_random_startpoint(self):
        random_n_vect = [random.randint(0, 20) for _ in range(9)]
        self.n_vect_start = random_n_vect

    def get_test_startpoint(self):
        self.n_vect_start = [2, 1, 2, 1, 2, 1, 2, 1]

    def get_population(self, quantity, length=12):
        self.population = [Solution(length) for _ in range(quantity)]

    def calculate_solution_quality(self, solution):
        a_ = 0.2
        b_ = 0.3
        c_ = 30
        quality = 0
        N = deepcopy(self.n_vect_start)
        n_matrix = [[] for _ in range(len(solution.solution) + 1)]
        n_matrix[0] = N
        prev_comb = solution.solution[0]

        # getting ni list
        for i, combination_nr in enumerate(solution.solution):
            # print(f"i: {i}, Combination nr: {combination_nr}")
            if i == 0:
                # print("combination_nr:", combination_nr)
                # print("Len n_matrix:", len(n_matrix))
                n_matrix[i + 1] = [n_matrix[i][j] - possible_combinations[combination_nr][j]
                                   for j in range(8)]
            else:
                # print("combination_nr:", combination_nr)
                # print("Len n_matrix:", len(n_matrix))
                n_matrix[i + 1] = [n_matrix[i][j] - possible_combinations[combination_nr][j]
                                 - possible_combinations[prev_comb][j] for j in range(8)]

            prev_comb = combination_nr
            # print("\n")

        for i in range(len(n_matrix)):
            for j in range(8):
                if n_matrix[i][j] < 0:
                    n_matrix[i][j] = 0


        n_matrix.pop(0)
        self.ni = deepcopy(n_matrix)

        # getting T list (lista czasu oczekiwań na poszczegónych sygalizatorach w danej iteracji):
        t_list = [[0, 0, 0, 0, 0, 0, 0, 0]]
        for i in range(len(solution.solution)):
            t_list.append([t_list[i][j] + 1 for j in range(len(t_list[i]))])
            xi = possible_combinations[solution.solution[i]]
            indices = [index for index, value in enumerate(xi) if value == 1]
            t_list[i + 1][indices[0]] = 0
            t_list[i + 1][indices[1]] = 0
        t_list.pop(0)
        self.t_list = t_list

        # quality
        for i in range(len(n_matrix)):
            if sum(n_matrix[i]) == 0:
                break
            quality += 1 + a_ * sum([n_matrix[i][j] * t_list[i][j] for j in range(len(n_matrix[i]))])

        quality += sum(n_matrix[-1]) * c_

        solution.quality = quality
        # print(n_list)


class Solution:

    def __init__(self, length=12):
        self.solution = [random.randint(0, 11) for _ in range(length)]
        self.quality = inf

    def make_it_test_solution(self):
        self.solution = [11, 11, 10, 10, 9, 8]

    def permutation(self, type=0):
        """
        Metoda dokonująca permutacji w obrębie jednego rozwiązania
        :param type: w zależności od typu:
        0) losuje dwie liczby a, b i podmienia wartości na tych indeksach
        1) losuje dwie liczby a, b i w tym zakresie odwraca kolejność
        ... można chyba do woli tworzyć możliwe permutacje
        :return: nic nie zwraca, modyfikuje to rozwiązanie
        """
        length = len(self.solution)

        if type == 0:
            a = random.randint(0, length)
            b = random.randint(0, length)
            self.solution[a], self.solution[b] = self.solution[b], self.solution[a]

        if type == 1:
            a = random.randint(0, length)
            b = random.randint(0, length)
            if a > b:
                a, b = b, a

            self.solution[a:b] = self.solution[a:b:-1]

    def mutation(self, type=0):
        """
        Metoda mutująca
        0) jedna podmianka
        1) podmiana 1/4 losowych indeksów na losowe weartości
        :return: podmienia w rozwiązaniu wartości na określonych indeksach na inne losowe
        """
        length = len(self.solution)
        if type == 0:
            idx = random.randint(0, length)
            self.solution[idx] = random.randint(0, 11)  # bo 11 jest kombinacji świateł jak coś
        if type == 1:
            number_of_changes = length // 4
            for _ in range(number_of_changes):
                idx = random.randint(0, length)
                self.solution[idx] = random.randint(0, 11)



if __name__ == '__main__':
    sim = Simulation()
    sim.get_random_startpoint()
    sim.get_population(100, 15)

    # for i in range(8):
    #     print(i)
    #
    # print("\n\n")

    # for sol in sim.population:
    #     print(sol.solution)

    best_sol = None
    best_quality = inf

    for sol in sim.population:
        sim.calculate_solution_quality(sol)
        if sol.quality < best_quality:
            best_sol = sol
            best_quality = sol.quality

print(best_sol.solution)
print(best_sol.quality)
