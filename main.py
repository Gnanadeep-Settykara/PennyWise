# Add dependencies
import sys
import sqlite3
from matplotlib import cm
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QPainter, QBrush, QColor
from PySide6.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget, QMessageBox, QFormLayout)
from PySide6.QtCharts import QChartView, QPieSeries, QChart


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.items = 0

        # Database connection
        self.connect_to_sqlite()

        # Left Widget
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Description", "Price ($)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        colormap = cm.get_cmap("tab20c", 40)  # You can choose a different colormap
        self.colors = [QColor.fromRgbF(*colormap(i)[:3]) for i in range(0, 40, 2)]

        # Right Widget
        self.description = QLineEdit()
        self.price = QLineEdit()
        self.add = QPushButton("Add")
        self.delete = QPushButton("Delete")
        self.clear = QPushButton("Clear")
        self.quit = QPushButton("Quit")
        self.plot = QPushButton("Plot")

        # Disabling 'Add' button initially
        self.add.setEnabled(False)
        self.delete.setEnabled(False)

        self.right = QVBoxLayout()
        self.right.addWidget(QLabel("Description"))
        self.right.addWidget(self.description)
        self.right.addWidget(QLabel("Price"))
        self.right.addWidget(self.price)
        self.right.addWidget(self.add)
        self.right.addWidget(self.delete)
        self.right.addWidget(self.plot)
        self.right.addWidget(self.chart_view)
        self.right.addWidget(self.clear)
        self.right.addWidget(self.quit)

        # QWidget Layout
        self.layout = QHBoxLayout()

        # self.table_view.setSizePolicy(size)
        self.layout.addWidget(self.table)
        self.layout.addLayout(self.right)

        # Set the layout to the QWidget
        self.setLayout(self.layout)

        # Signals and Slots
        self.add.clicked.connect(self.add_element)
        self.delete.clicked.connect(self.delete_element)
        self.quit.clicked.connect(self.quit_application)
        self.plot.clicked.connect(self.plot_data)
        self.clear.clicked.connect(self.clear_table)
        self.description.textChanged[str].connect(self.check_disable)
        self.price.textChanged[str].connect(self.check_disable)

        # Table selection change signal
        self.table.itemSelectionChanged.connect(self.enable_disable_buttons)

        # Fill example data
        self.fill_table()
        # Fetch data from the database and update the table
        self.fetch_data_from_database()

    def connect_to_sqlite(self):
        self.connection = sqlite3.connect("expenses.db")
        self.cursor = self.connection.cursor()

        # Create expenses table if not exists
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)
        self.connection.commit()

        # Add dummy data if the table is empty
        self.cursor.execute("SELECT COUNT(*) FROM expenses")
        count = self.cursor.fetchone()[0]
        if count == 0:
            dummy_data = [
                ("Rent", 1600),
                ("Grocery", 300),
                ("Water", 50),
                ("Coffee", 45),
                ("Phone", 30),
                ("Internet", 60)
            ]
            self.cursor.executemany("INSERT INTO expenses (description, price) VALUES (?, ?)", dummy_data)
            self.connection.commit()

    def fetch_data_from_database(self):
        self.cursor.execute("SELECT * FROM expenses")
        rows = self.cursor.fetchall()
        return rows

    def update_table(self):
        self.table.setRowCount(0)
        self.items = 0
        self.fetch_data_from_database()
        self.fill_table()

    @Slot()
    def add_element(self):
        des = self.description.text()
        price = self.price.text()

        try:
            price_value = float(price)
            self.cursor.execute("INSERT INTO expenses (description, price) VALUES (?, ?)", (des, price_value))
            self.connection.commit()

            self.update_table()

            self.description.setText("")
            self.price.setText("")
        except ValueError as e:
            # Display an error message box with the ValueError information
            error_message = f"Invalid input: {price}\nPlease enter a valid Price!"
            QMessageBox.critical(self, "Error", error_message)

    @Slot()
    def delete_element(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            expense_id = self._get_expense_id(selected_row)
            self.cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
            self.connection.commit()

            self.update_table()

            self.description.setText("")
            self.price.setText("")

    def _get_expense_id(self, row_index):
        return self.table.item(row_index, 0).data(Qt.UserRole)

    @Slot()
    def clear_table(self):
        self.cursor.execute("DELETE FROM expenses")
        self.connection.commit()
        self.update_table()

    @Slot()
    def check_disable(self, x):
        if not self.description.text() or not self.price.text():
            self.add.setEnabled(False)
            self.delete.setEnabled(False)
        else:
            self.add.setEnabled(True)
            self.delete.setEnabled(True)

    @Slot()
    def plot_data(self):
        # Get table information
        series = QPieSeries()

        for i in range(self.table.rowCount()):
            text = self.table.item(i, 0).text()
            number = float(self.table.item(i, 1).text())

            color = self.colors[i % len(self.colors)]
            slice_item = series.append(text, number)
            slice_item.setBrush(QBrush(color))

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignLeft)
        self.chart_view.setChart(chart)

    @Slot()
    def quit_application(self):
        QApplication.quit()

    def fill_table(self, data=None):
        data = self.fetch_data_from_database() if not data else data
        for row in data:
            description_item = QTableWidgetItem(row[1])

            price_item = QTableWidgetItem(f"{row[2]:.2f}")

            price_item.setTextAlignment(Qt.AlignRight)
            description_item.setData(Qt.UserRole, row[0])

            self.table.insertRow(self.items)
            self.table.setItem(self.items, 0, description_item)
            self.table.setItem(self.items, 1, price_item)
            self.items += 1

    @Slot()
    def enable_disable_buttons(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            self.delete.setEnabled(True)
        else:
            self.delete.setEnabled(False)


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("PennyWise")

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)
        self.setCentralWidget(widget)

    @Slot()
    def exit_app(self, checked):
        QApplication.quit()


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec())