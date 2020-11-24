from src.request_manager import RequestManager
from src.diagram import Diagram
from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator, QIntValidator
import src.design as design
import sys


class ComputerSimulationModelApp(QtWidgets.QMainWindow, design.UiDesign):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.request_manager = None
        self.n = 0
        self.p_cur = 2
        self.p_prev = 0

        self.double_validator = QDoubleValidator(bottom=0)
        self.int_validator = QIntValidator(bottom=0)

        self.producer_count_edit.setValidator(self.int_validator)
        self.producer_count_edit.textChanged.connect(self.__check_configuration_params_button)

        self.alpha_edit.setValidator(self.double_validator)
        self.alpha_edit.textChanged.connect(self.__check_configuration_params_button)

        self.beta_edit.setValidator(self.double_validator)
        self.beta_edit.textChanged.connect(self.__check_configuration_params_button)

        self.device_count_edit.setValidator(self.int_validator)
        self.device_count_edit.textChanged.connect(self.__check_configuration_params_button)

        self.lambda_edit.setValidator(self.double_validator)
        self.lambda_edit.textChanged.connect(self.__check_configuration_params_button)

        self.buffer_size_edit.setValidator(self.int_validator)
        self.buffer_size_edit.textChanged.connect(self.__check_configuration_params_button)

        self.n_edit.setValidator(self.int_validator)
        self.n_edit.textChanged.connect(self.__check_configuration_params_button)

        self.configure_button.clicked.connect(self.__configure)
        self.step_button.clicked.connect(self.__step)
        self.finish_button.clicked.connect(self.__finish)
        self.refresh_button.clicked.connect(self.__refresh)

        self.__diagram = Diagram(0, 0, 0, [], [], [], [])
        self.diagram_scroll_area.setWidget(self.__diagram)

    def __check_configuration_params_button(self):
        is_filled = self.producer_count_edit.text() != '' \
                    and self.alpha_edit.text() != '' \
                    and self.beta_edit.text() != '' \
                    and self.device_count_edit.text() != '' \
                    and self.lambda_edit.text() != '' \
                    and self.buffer_size_edit.text() != '' \
                    and self.n_edit.text() != ''
        self.configure_button.setEnabled(is_filled)

    def __configure(self):
        self.request_manager = RequestManager(int(self.producer_count_edit.text()),
                                              float(self.alpha_edit.text().replace(',', '.')),
                                              float(self.beta_edit.text().replace(',', '.')),
                                              int(self.device_count_edit.text()),
                                              float(self.lambda_edit.text().replace(',', '.')),
                                              int(self.buffer_size_edit.text()))
        self.n = int(self.n_edit.text())
        self.p_cur = 2
        self.p_prev = 0

        self.statusbar.showMessage('Configured', 1500)

        self.auto_tab.setEnabled(True)
        self.step_tab.setEnabled(True)

        self.device_table.setRowCount(self.request_manager.get_device_count())
        self.producer_table.setRowCount(self.request_manager.get_producer_count())

        self.__configure_diagram()

    def __refresh(self):
        request_count = self.request_manager.get_request_count()
        stats = self.request_manager.get_statistics()

        self.progress_bar.setValue(round(sum(request_count) / self.n * 100))
        self.__set_values_at_column(request_count, 0, self.producer_table)
        for i in range(6):
            self.__set_values_at_column(stats[i], i + 1, self.producer_table)
        self.__set_values_at_column(stats[6], 0, self.device_table)
        self.n_label.setText('N: ' + str(self.n))

    def __set_values_at_column(self, values, column, table):
        for i, value in enumerate(values):
            table.setItem(i, column, QtWidgets.QTableWidgetItem(str(round(value, 5))))

    def __step(self):
        if sum(self.request_manager.get_request_count()) < self.n:
            self.request_manager.process_next_event()
            self.__update_diagram()
        else:
            self.request_manager.process_remaining_requests()
            self.p_prev = self.p_cur
            self.p_cur = self.request_manager.get_deny_probability()
            if not self.__check_correctness():
                self.__calculate_n()
                self.__restart_request_manager()
            else:
                self.__finish()

    def __finish(self):
        self.__finish_simulation()
        while not self.__check_correctness():
            self.__calculate_n()
            self.__restart_request_manager()
            self.__finish_simulation()

        self.__update_diagram()
        print(self.request_manager.get_utilization_rate(),
              self.request_manager.get_deny_probability(),
              self.request_manager.get_residence_time())
        self.statusbar.showMessage('Finished', 1500)

    def __configure_diagram(self):
        self.__diagram = Diagram(self.request_manager.get_producer_count(),
                                 self.request_manager.get_buffer_size(),
                                 self.request_manager.get_device_count(),
                                 *self.request_manager.get_logs())
        self.diagram_scroll_area.setWidget(self.__diagram)

    def __update_diagram(self):
        self.__diagram.update_data(*self.request_manager.get_logs())
        self.__diagram.update()

    # Если разница |p(n-1) - p(n)| меньше 10 % от значения p(n-1),
    # то N(n-1) удовлетворяет заданной точности результатов
    def __check_correctness(self):
        if self.p_prev != 0:
            return (abs(self.p_cur - self.p_prev) / self.p_prev) < 0.1
        return False

    # t(alpha) = 1.643, alpha = 0.9, delta = 0.1
    def __calculate_n(self):
        if self.p_cur != 0:
            self.n = int(pow(2, 1.643) * (1 - self.p_cur) / (self.p_cur * pow(0.1, 2)))
        else:
            self.n *= 1.5

    def __restart_request_manager(self):
        self.request_manager = RequestManager(self.request_manager.get_producer_count(),
                                              self.request_manager.get_alpha(),
                                              self.request_manager.get_beta(),
                                              self.request_manager.get_device_count(),
                                              self.request_manager.get_lambda(),
                                              self.request_manager.get_buffer_size())

    def __finish_simulation(self):
        while sum(self.request_manager.get_request_count()) < self.n:
            self.request_manager.process_next_event()
        self.request_manager.process_remaining_requests()
        self.p_prev = self.p_cur
        self.p_cur = self.request_manager.get_deny_probability()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ComputerSimulationModelApp()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
