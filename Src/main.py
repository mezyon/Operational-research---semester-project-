from crossing_road import przeprowadzenie_symulacji

import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QRadioButton, QButtonGroup, QCheckBox, QFrame
)

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

class GraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph with List Input")
        self.setGeometry(100, 100, 1600, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        input_wektor_layout = QHBoxLayout()
        input_layout = QHBoxLayout()
        input_layout2 = QHBoxLayout()

        wektor_label = QLabel("9 elementowy wektor początkowy:")
        self.wektor_poczatkowy = QLineEdit()
        self.wektor_poczatkowy.setPlaceholderText("np. 13, 20, 21, 17, 18, 13, 14, 24, 15")
        self.wektor_poczatkowy.setText("13, 20, 21, 17, 18, 13, 14, 24, 15")

        populacja_label = QLabel("Rozmiar populacji:")
        self.populacja = QLineEdit()
        self.populacja.setPlaceholderText("np. 50")
        self.populacja.setText("50")

        iteracje_label = QLabel("Liczba iteracji:")
        self.iteracje = QLineEdit()
        self.iteracje.setPlaceholderText("np. 1000")
        self.iteracje.setText("1000")

        progowa_label = QLabel("Wartość progowa:")
        self.wartosc_progowa = QLineEdit()
        self.wartosc_progowa.setText("0")

        mutacja_label = QLabel("Prawdopodobieństwo mutacji:")
        self.mutacja = QLineEdit()
        self.mutacja.setText("0.5")
        
        permutacja_label = QLabel("Prawdopodobieństwo permutacji:")
        self.permutacja = QLineEdit()
        self.permutacja.setText("0.5")

        self.dodawanie = QCheckBox("Losowe dodawanie")
        self.dodawanie.setChecked(False)
        
        self.karanie = QCheckBox("Karanie")
        self.karanie.setChecked(True)
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)
                
        input_wektor_layout.addWidget(wektor_label)
        input_wektor_layout.addWidget(self.wektor_poczatkowy)
        input_layout.addWidget(populacja_label)
        input_layout.addWidget(self.populacja)
        input_layout.addWidget(iteracje_label)
        input_layout.addWidget(self.iteracje)
        input_layout.addWidget(progowa_label)
        input_layout.addWidget(self.wartosc_progowa)
        input_layout.addWidget(mutacja_label)
        input_layout.addWidget(self.mutacja)
        input_layout.addWidget(permutacja_label)
        input_layout.addWidget(self.permutacja)
        input_layout2.addWidget(self.dodawanie)
        input_layout2.addWidget(self.karanie)
        input_layout2.addWidget(self.start_button)
        main_layout.addLayout(input_wektor_layout)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(input_layout2)
        
        output_layout = QHBoxLayout()

        f_celu_label = QLabel("Funkcja celu najlepszego rozwiązania:")
        self.f_celu = QLineEdit()
        self.f_celu.setReadOnly(True)

        rozw_label = QLabel("Najlepsze rozwiązanie:")
        self.rozw = QLineEdit()
        self.rozw.setReadOnly(True)


        output_layout.addWidget(f_celu_label)
        output_layout.addWidget(self.f_celu)
        output_layout.addWidget(rozw_label)
        output_layout.addWidget(self.rozw)

        main_layout.addLayout(output_layout)

        graph_layout = QHBoxLayout()

        self.canvas1 = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax1 = self.canvas1.figure.add_subplot(111)
        self.ax1.set_title("WYKRES PRZEBIEGU FUNKCJI CELU\n NAJLEPSZEGO ROZWIĄZANIA")
        graph_layout.addWidget(self.canvas1)

        self.canvas2 = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax2 = self.canvas2.figure.add_subplot(111)
        self.ax2.set_title("WYKRES PRZEBIEGU FUNKCJI CELU\n NAJLEPSZEGO ROZWIĄZANIA W DANEJ ITERACJI")
        graph_layout.addWidget(self.canvas2)

        self.canvas3 = FigureCanvas(Figure(figsize=(5, 3)))
        self.ax3 = self.canvas3.figure.add_subplot(111)
        self.ax3.set_title("WYKRES NADMIARU")
        graph_layout.addWidget(self.canvas3)
        
        main_layout.addLayout(graph_layout)

    def start(self):
        wektor_poczatkowy = self.parse_list_input(self.wektor_poczatkowy.text().strip())
        if len(wektor_poczatkowy) != 9:
            raise ValueError("Zła długość")
        
        populacja = int(self.populacja.text())
        iteracje = int(self.iteracje.text())
        progowa = int(self.wartosc_progowa.text())
        mutacja = float(self.mutacja.text())
        permutacja = float(self.permutacja.text())
        dodawanie = self.dodawanie.isChecked()
        karanie = self.karanie.isChecked()
        
        n_vect_start, population0_solution, przebieg_najlepszej_f_celu, przebieg_f_celu, przebieg_nadmiaru, dlugosc_rozwiazania = przeprowadzenie_symulacji(wektor_poczatkowy=wektor_poczatkowy, rozmiar_populacji=populacja, liczba_iteracji=iteracje, wartosc_progowa=progowa, mut=mutacja, perm=permutacja, add=dodawanie, karanie=karanie)

        self.update_output_values(przebieg_najlepszej_f_celu, population0_solution)
        self.plot_graphs(przebieg_najlepszej_f_celu, przebieg_f_celu, przebieg_nadmiaru, n_vect_start, dlugosc_rozwiazania)
        
    def plot_graphs(self, przebieg_najlepszej_f_celu, przebieg_f_celu, przebieg_nadmiaru, n_vect_start, dlugosc_rozwiazania):
        try:
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()

            # Wykres 1
            self.ax1.plot(range(len(przebieg_najlepszej_f_celu)), przebieg_najlepszej_f_celu)
            #self.ax1.set_title(f"{n_vect_start}, rozwiązanie dł. {dlugosc_rozwiazania}")
            self.ax1.set_title("WYKRES PRZEBIEGU FUNKCJI CELU\n NAJLEPSZEGO ROZWIĄZANIA")
            self.ax1.set_xlabel("Iteracja")
            self.ax1.set_ylabel("Wartość Funkcji celu")
            self.ax1.legend()

            # Wykres 2
            self.ax2.plot(range(len(przebieg_f_celu)), przebieg_f_celu)
            #self.ax2.set_title(f"{n_vect_start}, rozwiązanie dł. {dlugosc_rozwiazania}")
            self.ax2.set_title("WYKRES PRZEBIEGU FUNKCJI CELU\n NAJLEPSZEGO ROZWIĄZANIA W DANEJ ITERACJI")
            self.ax2.set_xlabel("Iteracja")
            self.ax2.set_ylabel("Wartość Funkcji celu")
            self.ax2.legend()

            # Wykres 3
            self.ax3.plot(range(len(przebieg_nadmiaru)), przebieg_nadmiaru)
            #self.ax3.set_title(f"{n_vect_start}, rozwiązanie dł. {dlugosc_rozwiazania}")
            self.ax3.set_title("WYKRES NADMIARU")
            self.ax3.set_xlabel("Iteracja")
            self.ax3.set_ylabel("Wartość nadmiaru")
            self.ax3.legend()

            # Refresh canvases
            self.canvas1.draw()
            self.canvas2.draw()
            self.canvas3.draw()

        except ValueError as e:
            self.list_input.setText(f"Error: {str(e)}")

    def parse_list_input(self, list_input):
        try:
            return [float(num.strip()) for num in list_input.split(",") if num.strip()]
        except ValueError:
            raise ValueError("Nieprawidłowe dane wejściowe, liczby muszą być oddzielone przecinkami")

    def update_output_values(self, a, b):
        self.f_celu.setText(f"{min(a)}")
        self.rozw.setText(f"{b}")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec())