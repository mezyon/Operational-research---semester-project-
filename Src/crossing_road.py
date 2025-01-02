import random
from copy import deepcopy
from math import inf
import matplotlib.pyplot as plt
import numpy as np

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

# ZMIENNE GLOBALNE START

# współczynniki do liczenia funkcji celu
base_glob = 0   # dodawane w każdym kroku
a_glob = 1    # mnożnik kary
b_glob = 1    # wykładnik kary
c_glob = 1      # kara za pozostałe auta


# lista opcji transformacji - w obecnej implementacji można ją zmieniać na [0], [1] oraz [0, 1]
# nie można zrezygnować z operatora krzyżowania
mut_opt = [0, 1]
perm_opt = [0, 1]
cros_opt = [0,  1]

KARA_FULL = 10
KARA_HALF = 5
# ZMIENNE GLOBALNE STOP


class Simulation:

    def __init__(self, n_vect_start=[]):
        self.n_vect_start = n_vect_start
        self.population = list()
        self.ni = None
        self.t_list = None
        self.best_solution_nadmiar_history = []
        self.best_solution_history = []
        self.best_solution_in_population = []
        self.best_quality = 9999999999999999999999999999

    def get_random_startpoint(self, a=2, b=5):
        random_n_vect = [random.randint(a, b) for _ in range(9)]
        self.n_vect_start = random_n_vect

    def get_test_startpoint(self):
        self.n_vect_start = [2, 1, 2, 1, 2, 1, 2, 1]

    def get_population(self, quantity, length=12, dummy=0):
        self.population = [Solution(length) for _ in range(quantity)]
        if dummy == 1:
            for el in self.population:
                el.dummy()
        else:
            for el in self.population:
                el.randomize()

    def calculate_solution_quality(self, solution):
        base_value = base_glob
        a_ = a_glob
        b_ = b_glob
        c_ = c_glob
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
            quality += base_value + a_ * sum([n_matrix[i][j] * t_list[i][j] for j in range(len(n_matrix[i]))]) ** b_

        # print(n_matrix[-1])

        if sum(n_matrix[-1]) != 0:
            quality += sum(n_matrix[-1]) * c_

        zostalo_aut = sum(n_matrix[-1])
        solution.nadmiar = zostalo_aut
        solution.quality = quality
        # print(n_list)

    def genetic_algorithm(self, quantity=100, length=7, iterations=100, desired_solution=0,
                          MUT_=0.5, PERM_=0.5, add_random_5_inside=True,
                          dummy=0, karanie=False, no_improvement=100):


        # stwórz pierwszą populację
        self.get_population(quantity, length, dummy)
        counter = 0
        improvement_flag = True
        while counter < iterations and improvement_flag:
            counter += 1

            # oblicz jakość w populacji
            for one_sol in self.population:
                self.calculate_solution_quality(one_sol)

            if karanie:
                for solution in self.population:
                    solution.pokaraj()

            # posortuj rozwiązania względem jakości
            self.population.sort(key=lambda x: (x.quality + x.kara), reverse=False)

            if len(self.population) > quantity:
                self.population = self.population[:quantity]

            # aktualizacja listy do tej pory najlepszego rozwiąznia
            try:
                self.best_solution_history.append(self.population[0].quality if self.population[0].quality < self.best_solution_history[-1] else self.best_solution_history[-1])
            except IndexError:
                self.best_solution_history.append(self.population[0].quality)
            # aktualizacja listy najlepszego rozwiązania w obecnej populacji
            self.best_solution_in_population.append(self.population[0].quality)

            self.best_solution_nadmiar_history.append(self.population[0].nadmiar)

            # wybierz jakościowo najlepsze 25% populacji do krzyżowania
            crossing_population = deepcopy(self.population[:quantity//4])

            # dodaj pięć losowych rozwiązań
            if add_random_5_inside:
                for _ in range(5):
                    random_solution = Solution(length)
                    random_solution.randomize()
                    crossing_population.append(random_solution)

            new_population = []
            for el in crossing_population:
                for _ in range(2):   # wykonaj dwa razy
                    one, two = el.crossing(random.choice(crossing_population), random.choice(cros_opt))
                    new_population.append(one)
                    new_population.append(two)

            # mutacje w nowo utworzonej populacji
            for idx in range(len(new_population)):
                if random.random() < MUT_:
                    new_population[idx].mutation(random.choice(mut_opt))
                if random.random() < PERM_:
                    new_population[idx].permutation(random.choice(perm_opt))

            self.population = new_population

            # warunki stopu działają niejako dopiero po no_improvement + 10 iteracji
            if len(self.best_solution_history) > (no_improvement + 10):
                if abs(np.mean(self.best_solution_history[-no_improvement:-1]) - self.best_solution_history[-1]) < 0.01:
                    improvement_flag = False
                if desired_solution > self.best_solution_history[-1]:
                    improvement_flag = False

        for one_sol in self.population:
            self.calculate_solution_quality(one_sol)

        # posortuj rozwiązania względem jakości
        self.population.sort(key=lambda x: x.quality, reverse=False)


class Solution:

    def __init__(self, length=12):
        # Długość pojedynczego rozwiązania powinna wynosić sumę wszystkich
        # jendostek samochodowych na początku przez 2 -> wówczas na pewno
        # będzie istaniało rozwiązanie, które umożliwy przejazd wszystkim pojazdom
        self.solution = [None for _ in range(length)]  # lista do przechowywania roziązania
        self.quality = 999999999  # duża i charakterystyczna liczba, ale nie nieskończoność dla lepszej diagnostyki
        self.length = length
        self.kara = 0
        self.nadmiar = -1

    def pokaraj(self):
        tab = self.solution  # Tablica zawierająca sekwencję rozwiązań.
        kara = 0  # Inicjalizacja wartości kary.

        for i in range(len(tab) - 1):  # Iteracja po parach sąsiednich elementów w tablicy.
            current = possible_combinations[tab[i]]  # Obecna kombinacja.
            next_comb = possible_combinations[tab[i + 1]]  # Następna kombinacja.

            if current == next_comb:  # Jeśli kombinacje są identyczne.
                continue  # Brak kary.

            # Obliczamy liczbę zgodnych indeksów między dwiema kombinacjami.
            matching_indices = sum(1 for c, n in zip(current, next_comb) if c == n and c == 1)

            if matching_indices == 0:  # Jeśli żaden indeks się nie zgadza.
                kara += KARA_FULL  # Kara za brak zgodności (ustaw wartość X według potrzeb).
            elif matching_indices == 1:  # Jeśli dokładnie jeden indeks się zgadza.
                kara += KARA_HALF  # Kara za częściową zgodność (ustaw wartość Y według potrzeb).
            else:  # Więcej niż jeden indeks się zgadza (ale kombinacje nie są identyczne).
                pass  # Opcjonalna kara za większą zgodność, jeśli potrzebne.

        self.kara = kara  # dodanie kary

    def dummy(self):
        self.solution = [0 for _ in range(len(self.solution))]

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
        typ1: wybiera losowo miejsce przecięcia i względem niego wykonuje krzyżowanie
        :return: (new_sol1, new_sol2)
        """
        new_sol1 = Solution(self.length)
        new_sol2 = Solution(self.length)

        if typ == 0:
            bound = random.randint(1, self.length - 1)
            new_sol1.solution = self.solution[:bound] + other.solution[bound:]
            new_sol2.solution = other.solution[:bound] + self.solution[bound:]

        elif typ == 1:
            # Krzyżowanie "w kratkę"
            new_sol1.solution = [self.solution[i] if i % 2 == 0 else other.solution[i] for i in range(self.length)]
            new_sol2.solution = [other.solution[i] if i % 2 == 0 else self.solution[i] for i in range(self.length)]

        return new_sol1, new_sol2


def przeprowadzenie_symulacji(wektor_poczatkowy=None,
                              dlugosc_rozwiazania=None,
                              rozmiar_populacji=100,
                              liczba_iteracji=100,
                              wartosc_progowa=0,
                              a=2,
                              b=5,
                              mut=0.5,
                              perm=0.5,
                              add=True,
                              dummy=0,
                              karanie=False,
                              no_improvement=100):
    """

    :param wektor_poczatkowy: sytuacja na skrzyżowaniu do rozważenia
    :param dlugosc_rozwiazania:
    :param rozmiar_populacji: rozmiar populacji w każdym kroku algorytmu
    :param liczba_iteracji: warunek stopu - jest to MAKSYMALNA liczba iteracji
    :param wartosc_progowa: warunek stopu - domyślnie ustawiony na zero, czyli nieaktywny. Działa
                            dopiero po pierwszych dwudziestu wykonanych iteracjach
    :param a: minimalna ilość pojazdów w danej kolejce (jeśli wektor poczatkowy równy None)
    :param b: maksymalna ilość pojazdów w danej kolejce (jeśli wektor poczatkowy równy None)
    prawdop. mutacji
    prawdop. permutacji
    dodawanie lsoowych 5ciu rozwiązań do każdej populacji
    dummy - start nie z punktu losowego, tylko z samych zer
    :return: nie zwraca nic, tylko printuje i rysuje wykresy
    """
    symulka = Simulation()
    if wektor_poczatkowy is None:
        # ustalić losowy wektor początkowy
        symulka.get_random_startpoint(a, b)
    else:
        symulka.n_vect_start = wektor_poczatkowy
    if dlugosc_rozwiazania is None:
        # ustalić (optymalną) długość rozwiązania
        dlugosc_rozwiazania = sum(symulka.n_vect_start) // 4

    print("pozycja początkowa:", symulka.n_vect_start)
    print("Długość rozwiązania", dlugosc_rozwiazania)

    symulka.genetic_algorithm(rozmiar_populacji, dlugosc_rozwiazania, liczba_iteracji, wartosc_progowa, mut, perm, add, dummy, karanie, no_improvement)

    przebieg_najlepszej_f_celu = symulka.best_solution_history
    przebieg_f_celu = symulka.best_solution_in_population
    przebieg_nadmiaru = symulka.best_solution_nadmiar_history
    print("Funkcja celu najlepszego rozwiąznia", min(przebieg_najlepszej_f_celu))
    print("Najlepsze rozwiązanie:", symulka.population[0].solution)


    # WYKRES PRZEBIEGU FUNKCJI CELU NAJLEPSZEGO ROZWIĄZANIA EVER
    plt.plot(range(len(przebieg_najlepszej_f_celu)), przebieg_najlepszej_f_celu)
    plt.title(f"{symulka.n_vect_start}, rozwiązanie dł. {dlugosc_rozwiazania}")
    plt.xlabel("Iteracja")
    plt.ylabel("Wartość Funkcji celu")
    plt.grid()
    plt.show()

    # WYKRES PRZEBIEGU FUNKCJI CELU NAJLEPSZEGO ROZWIĄZANIA W DANEJ ITERACJI
    plt.plot(range(len(przebieg_f_celu)), przebieg_f_celu)
    plt.title(f"{symulka.n_vect_start}, rozwiązanie dł. {dlugosc_rozwiazania}")
    plt.xlabel("Iteracja")
    plt.ylabel("Wartość Funkcji celu")
    plt.grid()
    plt.show()

    # WYKRES NADMIARU
    plt.plot(range(len(przebieg_nadmiaru)), przebieg_nadmiaru)
    plt.title(f"{symulka.n_vect_start}, rozwiązanie dł. {dlugosc_rozwiazania}")
    plt.xlabel("Iteracja")
    plt.ylabel("Wartość nadmiaru")
    plt.grid()
    plt.show()


if __name__ == '__main__':

    test1_start = [2, 5, 2, 2, 4, 4, 2, 2]

    test3_start = [40, 40, 0, 0, 0, 0, 0, 0]
    testing_v = [13, 20, 21, 17, 18, 13, 14, 24]
    len_t = 38
    przeprowadzenie_symulacji(wektor_poczatkowy=test3_start,
                              dlugosc_rozwiazania=None,
                              rozmiar_populacji=50,
                              liczba_iteracji=1000,
                              wartosc_progowa=0,
                              a=12,
                              b=24,
                              mut=0.5,
                              perm=0.5,
                              add=False,
                              dummy=0,
                              karanie=True)
