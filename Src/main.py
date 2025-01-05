from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QRadioButton, QButtonGroup, QCheckBox, 
    QFrame, QGridLayout, QScrollArea, QGroupBox, QSpinBox, QDoubleSpinBox,
    QSlider, QMessageBox
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import sys

from crossing_road import przeprowadzenie_symulacji

class SliderWithInput(QWidget):
    def __init__(self, minimum, maximum, decimals=1):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(minimum * 10**decimals))
        self.slider.setMaximum(int(maximum * 10**decimals))
        
        # Spin box
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(minimum, maximum)
        self.spinbox.setDecimals(decimals)
        self.spinbox.setSingleStep(0.1)
        
        # Connect signals
        self.slider.valueChanged.connect(
            lambda: self.spinbox.setValue(self.slider.value() / 10**decimals))
        self.spinbox.valueChanged.connect(
            lambda: self.slider.setValue(int(self.spinbox.value() * 10**decimals)))
        
        layout.addWidget(self.slider, stretch=7)
        layout.addWidget(self.spinbox, stretch=3)
        
    def value(self):
        return self.spinbox.value()
        
    def setValue(self, value):
        self.spinbox.setValue(value)

class InputGroup(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.row = 0

    def add_input(self, label_text, widget, tooltip=""):
        label = QLabel(label_text)
        if tooltip:
            label.setToolTip(tooltip)
            widget.setToolTip(tooltip)
        self.layout.addWidget(label, self.row, 0)
        self.layout.addWidget(widget, self.row, 1)
        self.row += 1
        return widget

class GraphApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wizualizacja algorytmu genetycznego")
        self.setGeometry(100, 100, 1800, 900)

        # Create main widget with scroll support
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Create a horizontal layout for input panels
        input_panels_layout = QHBoxLayout()

        # Initial Vector Input Group
        vector_group = InputGroup("Warunki początkowe")
        self.wektor_poczatkowy = vector_group.add_input(
            "Wektor początkowy (8 elementów):",
            QLineEdit("13, 20, 21, 17, 18, 13, 14, 24"),
            "Wprowadź 8 liczb oddzielonych przecinkami"
        )
        
        # losowy wektor początkowy
        self.random_wektor_checkbox = vector_group.add_input(
            "Losowy wektor początkowy?",
            QCheckBox()
        )
        self.random_wektor_checkbox.stateChanged.connect(
            lambda state: self.wektor_poczatkowy.setEnabled(not state)
        )
        # TODO jedna uniwersalna funkcja?
        self.random_wektor_checkbox.stateChanged.connect(
            lambda state: self.random_wektor_min.setEnabled(state)
        )
        self.random_wektor_checkbox.stateChanged.connect(
            lambda state: self.random_wektor_max.setEnabled(state)
        )
        
        self.random_wektor_min = vector_group.add_input(
            "Min",
            QSpinBox()
        )
        
        self.random_wektor_min.setRange(0,20)
        self.random_wektor_min.setValue(4)
        self.random_wektor_min.setEnabled(False)
        
        self.random_wektor_max = vector_group.add_input(
            "Max",
            QSpinBox()
        )
        self.random_wektor_max.setRange(0,20)
        self.random_wektor_max.setValue(12)
        self.random_wektor_max.setEnabled(False)

        # Algorithm Parameters Group
        algo_group = InputGroup("Parametry algorytmu")
        self.populacja = algo_group.add_input(
            "Rozmiar populacji:",
            QSpinBox(),
            "Wielkość populacji w algorytmie genetycznym"
        )
        self.populacja.setRange(10, 1000)
        self.populacja.setValue(50)
        
        
        self.iteracje = algo_group.add_input(
            "Liczba iteracji:",
            QSpinBox(),
            "Liczba iteracji do wykonania"
        )
        self.iteracje.setRange(100, 10000)
        self.iteracje.setValue(1000)
        
        self.wartosc_progowa = algo_group.add_input(
            "Wartość progowa:",
            QSpinBox(),
            "Minimalna wartość progowa"
        )
        self.wartosc_progowa.setValue(0)
        
        self.dlugosc_rozwiazania = algo_group.add_input(
            "Długość rozwiązania:",
            QSpinBox(),
            "Długość rozwiązania"
        )
        self.dlugosc_rozwiazania.setValue(0)
        self.dlugosc_rozwiazania.setEnabled(False)
        
        # Probability Parameters Group
        prob_group = InputGroup("Ustawienia prawdopodobieństwa")
        self.mutacja = prob_group.add_input(
            "Prawdopodobieństwo mutacji:",
            SliderWithInput(0, 1),
            "Prawdopodobieństwo wystąpienia mutacji"
        )
        self.mutacja.setValue(0.5)
        
        self.permutacja = prob_group.add_input(
            "Prawdopodobieństwo permutacji:",
            SliderWithInput(0, 1),
            "Prawdopodobieństwo wystąpienia permutacji"
        )
        self.permutacja.setValue(0.5)

        # Options Group
        options_group = InputGroup("Dodatkowe opcje")
        self.dodawanie = QCheckBox("Losowe dodawanie")
        self.karanie = QCheckBox("Włącz kary")
        self.karanie.setChecked(True)
        self.dummy = QCheckBox("Dummy")
        self.dummy.setChecked(False)
        self.dummy.setToolTip("""
        <b>Parametr dummy – decyduje, w jaki sposób będą inicjowane poszczególne rozwiązania:</b> 
        <ul>
            <li>Jeśli dummy = 1, każde rozwiązanie będzie ”dummy”, tj. wszystkie elementy w
            rozwiązaniu będą ustawione na 0. Tego typu rozwiązania są traktowane jako puste
            lub domyślne.</li>
            <li>Jeśli dummy = 0, każde rozwiązanie jest inicjowane losowo, dzięki czemu w populacji
            będą znajdować się różnorodne rozwiązania.</li>
        </ul>              
        """)
        self.checkbox_dlugosc_rozwiazania = QCheckBox("Długość rozwiązania")
        self.checkbox_dlugosc_rozwiazania.setChecked(False)
        self.checkbox_dlugosc_rozwiazania.stateChanged.connect(
            lambda state: self.dlugosc_rozwiazania.setEnabled(state)
        )
        self.checkbox_dlugosc_rozwiazania.setToolTip("""
        Długość rozwiązania (length) – ustala liczbę elementów, które składają się na każde
        rozwiązanie. Można narzucić tę długość, lecz w przypadku braku takiego działania,
        algorytm dobiera ją samodzielnie w sposób umożliwiający opuszczenie skrzyżowania
        przez niemal wszystkie auta.                                             
        """)
        options_group.layout.addWidget(self.dodawanie)
        options_group.layout.addWidget(self.karanie)
        options_group.layout.addWidget(self.dummy)
        options_group.layout.addWidget(self.checkbox_dlugosc_rozwiazania)

        # Add control button
        self.start_button = QPushButton("Rozpocznij symulację")
        self.start_button.clicked.connect(self.start)
        self.start_button.setStyleSheet("padding: 10px;")
        options_group.layout.addWidget(self.start_button)

        # Add all input groups to the panel layout
        input_panels_layout.addWidget(vector_group)
        input_panels_layout.addWidget(algo_group)
        input_panels_layout.addWidget(prob_group)
        input_panels_layout.addWidget(options_group)
        main_layout.addLayout(input_panels_layout)

        # Results Group
        results_group = QGroupBox("Wyniki")
        results_layout = QGridLayout()
        results_group.setLayout(results_layout)

        # Add result fields
        self.f_celu = QLineEdit()
        self.f_celu.setReadOnly(True)
        results_layout.addWidget(QLabel("Funkcja celu najlepszego rozwiązania:"), 0, 0)
        results_layout.addWidget(self.f_celu, 0, 1)

        self.rozw = QLineEdit()
        self.rozw.setReadOnly(True)
        results_layout.addWidget(QLabel("Najlepsze rozwiązanie:"), 1, 0)
        results_layout.addWidget(self.rozw, 1, 1)

        main_layout.addWidget(results_group)

        # Create plots layout
        plots_widget = QWidget()
        plots_layout = QHBoxLayout()
        plots_widget.setLayout(plots_layout)

        # Configure plot style
        sns.set_style("whitegrid")
        sns.set_palette("husl")

        # Create plots with vertical arrangement
        self.figures = []
        self.canvases = []
        self.axes = []
        plot_titles = [
            "PRZEBIEG FUNKCJI CELU NAJLEPSZEGO ROZWIĄZANIA",
            "PRZEBIEG FUNKCJI CELU NAJLEPSZEGO ROZWIĄZANIA W DANEJ ITERACJI",
            "WYKRES NADMIARU"
        ]
        
        for title in plot_titles:
            fig = Figure(figsize=(4, 16))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.set_title(title)
            
            # Add to vertical layout
            plots_layout.addWidget(canvas)
            
            self.figures.append(fig)
            self.canvases.append(canvas)
            self.axes.append(ax)

        # Add plots to scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(plots_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        

    def start(self):
        try:
            wektor_poczatkowy = self.parse_list_input(self.wektor_poczatkowy.text().strip())
            if len(wektor_poczatkowy) != 8:
                raise ValueError("Wektor musi mieć dokładnie 8 elementów")
            
            params = {
                'wektor_poczatkowy': wektor_poczatkowy if not self.random_wektor_checkbox.isChecked() else None,
                'dlugosc_rozwiazania': self.dlugosc_rozwiazania.value() if self.checkbox_dlugosc_rozwiazania.isChecked() else None,
                'rozmiar_populacji': self.populacja.value(),
                'liczba_iteracji': self.iteracje.value(),
                'wartosc_progowa': self.wartosc_progowa.value(),
                'a': self.random_wektor_min.value(),
                'b': self.random_wektor_max.value(),
                'mut': self.mutacja.value(),
                'perm': self.permutacja.value(),
                'add': self.dodawanie.isChecked(),
                'dummy': 1 if self.dummy.isChecked() else 0,
                'karanie': self.karanie.isChecked()
            }
            
            n_vect_start, population0_solution, przebieg_najlepszej_f_celu, przebieg_f_celu, przebieg_nadmiaru, dlugosc_rozwiazania = przeprowadzenie_symulacji(**params)

            self.update_output_values(przebieg_najlepszej_f_celu, population0_solution)
            self.plot_graphs(przebieg_najlepszej_f_celu, przebieg_f_celu, przebieg_nadmiaru)
            
            QMessageBox.information(self, "Sukces", "Wartość funkcji celu najlepszego rozwiązania: " + str(min(przebieg_najlepszej_f_celu)))

        except ValueError as e:
            print(f"Błąd: {str(e)}")

    def plot_graphs(self, przebieg_najlepszej_f_celu, przebieg_f_celu, przebieg_nadmiaru):
        plot_data = [
            (przebieg_najlepszej_f_celu, "Iteracja", "Wartość funkcji celu"),
            (przebieg_f_celu, "Iteracja", "Wartość funkcji celu"),
            (przebieg_nadmiaru, "Iteracja", "Wartość nadmiaru")
        ]

        for ax, canvas, (data, xlabel, ylabel) in zip(self.axes, self.canvases, plot_data):
            ax.clear()
            
            sns.lineplot(x=range(len(data)), y=data, ax=ax)
            
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.3)
            
            canvas.figure.tight_layout()
            canvas.draw()

    def parse_list_input(self, list_input):
        try:
            return [float(num.strip()) for num in list_input.split(",") if num.strip()]
        except ValueError:
            QMessageBox.warning(self, "Błąd", "Nieprawidłowy format danych. Liczby muszą być oddzielone przecinkami.")
            raise ValueError("Nieprawidłowy format danych. Liczby muszą być oddzielone przecinkami.")

    def update_output_values(self, objective_values, best_solution):
        self.f_celu.setText(f"{min(objective_values)}")
        self.rozw.setText(f"{best_solution}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphApp()
    window.show()
    sys.exit(app.exec())