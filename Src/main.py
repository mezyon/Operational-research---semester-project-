import random
from copy import deepcopy



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

    def __init__(self):
        self.n_vect_start = []
        self.ni = None
        self.solution = []
        self.t_list = None
        self.quality = None

    def get_random_startpoint(self):
        random_n_vect = [random.randint(0, 20) for _ in range(9)]
        self.n_vect_start = random_n_vect

    def get_test_startpoint(self):
        self.n_vect_start = [2, 1, 2, 1, 2, 1, 2, 1]

    def get_test_solution(self):
        self.solution = [11, 11, 10, 10, 9, 8]

    def calculate_solution_quality(self):
        a_ = 0.2
        b_ = 0.3
        quality = 0
        N = deepcopy(self.n_vect_start)
        n_list = [None for _ in range(len(N) - 1)]
        n_list[0] = N

        # getting ni list
        for i, combination_nr in enumerate(self.solution):
            n_list[i + 1] = [n_list[i][j] - possible_combinations[combination_nr][j] for j in range(len(n_list[0]))]
        n_list.pop(0)
        self.ni = deepcopy(n_list)

        # getting T list:
        t_list = [[0, 0, 0, 0, 0, 0, 0, 0]]
        for i in range(len(self.solution)):
            t_list.append([t_list[i][j] + 1 for j in range(len(t_list[i]))])
            xi = possible_combinations[self.solution[i]]
            indices = [index for index, value in enumerate(xi) if value == 1]
            t_list[i + 1][indices[0]] = 0
            t_list[i + 1][indices[1]] = 0
        t_list.pop(0)
        self.t_list = t_list

        # quality
        for i in range(len(n_list)):
            quality += 1 + a_ * sum([n_list[i][j] * t_list[i][j] for j in range(len(n_list[i]))])

        self.quality = quality
        # print(n_list)


sim = Simulation()
sim.get_test_startpoint()
sim.get_test_solution()

# print(sim.n_vect_start)
# print(sim.solution)

sim.calculate_solution_quality()

print("Ilość przejść:            ", len(sim.ni))
print(sim.ni)
print("Ilość kroków:             ", len(sim.solution))
print(sim.solution)
print("Ilość czasów oczekiwania: ", len(sim.t_list))
print(sim.t_list)
print(sim.quality)


