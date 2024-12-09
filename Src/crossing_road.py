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
        self.population = list()
        self.ni = None
        self.t_list = None
        self.best_solution_history = []
        self.best_quality = None

    def get_random_startpoint(self):
        random_n_vect = [random.randint(2, 5) for _ in range(9)]
        self.n_vect_start = random_n_vect

    def get_test_startpoint(self):
        self.n_vect_start = [2, 1, 2, 1, 2, 1, 2, 1]

    def get_population(self, quantity, length=12):
        self.population = [Solution(length) for _ in range(quantity)]
        for el in self.population:
            el.randomize()

    def calculate_solution_quality(self, solution):
        a_ = 0.2
        b_ = 0.3
        c_ = inf
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

        # print(n_matrix[-1])

        if sum(n_matrix[-1]) != 0:
            quality += sum(n_matrix[-1]) * c_

        solution.quality = quality
        # print(n_list)

    def genetic_algorithm(self, quantity=100, length=7, iterations=100):
        # stwórz pierwszą populację
        self.get_population(quantity, length)
        counter = 0
        while counter < iterations:
            counter += 1

            # oblicz jakość w populacji
            for one_sol in self.population:
                self.calculate_solution_quality(one_sol)

            if len(self.population) > quantity:
                self.population = self.population[:quantity]

            # posortuj rozwiązania względem jakości
            self.population.sort(key=lambda x: x.quality, reverse=False)

            self.best_solution_history.append(self.population[0].quality)

            TOP_25 = deepcopy(self.population[:quantity//4])

            crossing = []
            for el in TOP_25:
                for _ in range(2): # wykonaj dwa razy
                    one, two = el.crossing(random.choice(TOP_25))
                    crossing.append(one)
                    crossing.append(two)

            # 1/4 ilości populacji razy wykonaj mutacje
            for _ in range(quantity//4):
                idx = random.randint(0, len(crossing) - 1)
                crossing[idx].mutation(random.choice([0, 1]))
                idx = random.randint(0, len(crossing) - 1)
                crossing[idx].permutation(random.choice([0, 1]))

            self.population = crossing

        for one_sol in self.population:
            self.calculate_solution_quality(one_sol)

        # posortuj rozwiązania względem jakości
        self.population.sort(key=lambda x: x.quality, reverse=False)

        for el in self.population[:5]:
            print(el.quality)


class Solution:

    def __init__(self, length=12):
        # Długość pojedynczego rozwiązania powinna wynosić sumę wszystkich
        # jendostek samochodowych na początku przez 2 -> wówczas na pewno
        # będzie istaniało rozwiązanie, które umożliwy przejazd wszystkim pojazdom
        self.solution = [None for _ in range(length)]  # lista do przechowywania roziązania
        self.quality = 999999999  # duża i charakterystyczna liczba, ale nie nieskończoność dla lepszej diagnostyki
        self.length = length

    def randomize(self):
        self.solution = [random.randint(0, 11) for _ in range(len(self.solution))]

    def make_it_test_solution(self):
        self.solution = [11, 11, 10, 10, 9, 8]

    def permutation(self, typ=0):
        """
        Metoda dokonująca permutacji w obrębie jednego rozwiązania
        :param typ: w zależności od typu:
        0) losuje dwie liczby a, b i podmienia wartości na tych indeksach
        1) losuje dwie liczby a, b i w tym zakresie odwraca kolejność
        ... można chyba do woli tworzyć możliwe permutacje
        :return: nic nie zwraca, modyfikuje to rozwiązanie
        """

        if typ == 0:
            a = random.randint(0, self.length - 1)
            b = random.randint(0, self.length - 1)
            x = self.solution[a]
            self.solution[a] = self.solution[b]
            self.solution[b] = x

        if typ == 1:
            a = random.randint(0, self.length)
            b = random.randint(0, self.length)
            if a > b:
                a, b = b, a

            self.solution[a:b] = self.solution[a:b][::-1]

    def mutation(self, typ=0):
        """
        Metoda mutująca
        0) jedna podmianka
        1) podmiana 1/4 losowych indeksów na losowe weartości
        :return: podmienia w rozwiązaniu wartości na określonych indeksach na inne losowe
        """
        length = len(self.solution)
        if typ == 0:
            idx = random.randint(0, length - 1)
            self.solution[idx] = random.randint(0, 11)  # bo 11 jest kombinacji świateł jak coś
        if typ == 1:
            number_of_changes = length // 4
            for _ in range(number_of_changes):
                idx = random.randint(0, length - 1)
                self.solution[idx] = random.randint(0, 11)

    def crossing(self, other, typ=0):
        """
        metoda krzyżująca, przyjmuje inne rozwiązanie i krzyżuje je z tym
        :param other: inne rozwiązanie
        :return: (new_sol1, new_sol2)
        """
        new_sol1 = Solution(self.length)
        new_sol2 = Solution(self.length)

        if typ == 0:
            bound = random.randint(1, self.length - 1)
            new_sol1.solution = self.solution[:bound] + other.solution[bound:]
            new_sol2.solution = other.solution[:bound] + self.solution[bound:]

        return new_sol1, new_sol2


if __name__ == '__main__':

    test_start = [2, 5, 2, 2, 4, 4, 2, 2, 2]

    sim = Simulation()
    sim.n_vect_start = deepcopy([2, 5, 2, 2, 4, 4, 2, 2, 2])

    sim.genetic_algorithm(100, 12)
    print(sim.best_solution_history)
    print(min(sim.best_solution_history))
