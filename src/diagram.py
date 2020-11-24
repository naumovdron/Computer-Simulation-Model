from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from src.event import *
import math


class Diagram(QtWidgets.QWidget):
    def __init__(self, producer_count, buffer_size, device_count,
                 event_log, release_log, deny_log, buffer_log):
        super(Diagram, self).__init__()

        self.__device_count = device_count
        self.__producer_count = producer_count
        self.__buffer_size = buffer_size

        self.__event_log = event_log
        self.__release_log = release_log
        self.__deny_log = deny_log
        self.__buffer_log = buffer_log

        self.__axes_gap = 40
        self.__group_gap = 70
        self.__top_padding = 50
        self.__down_padding = 50
        self.__left_padding = 40
        self.__label_padding = 10

        self.__producers_axes_heights, self.__buffer_axes_heights, self.__device_axes_heights\
            = self.__calculate_axes_heights()
        if len(self.__device_axes_heights) > 0:
            self.setFixedHeight(self.__device_axes_heights[-1] + self.__group_gap + self.__down_padding)
            self.__labels = self.__generate_labels()

    def update_data(self, event_log, release_log, deny_log, buffer_log):
        self.__event_log = event_log
        self.__release_log = release_log
        self.__deny_log = deny_log
        self.__buffer_log = buffer_log

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        self.__draw_axes(qp)
        self.__draw_events(qp)

        qp.end()

    def __draw_events(self, qp):
        for i, e in enumerate(self.__event_log):
            if isinstance(e, CreationEvent):
                qp.drawLine(self.__left_padding + 30 * i, self.__producers_axes_heights[e.producer_id] - 15,
                            self.__left_padding + 30 * i, self.__producers_axes_heights[e.producer_id])
                qp.drawText(self.__left_padding + 30 * i + 3, self.__producers_axes_heights[e.producer_id] - 3,
                            str(e.producer_id + 1) + '.' + str(e.id + 1))
            elif isinstance(e, SettingEvent):
                qp.drawLine(self.__left_padding + 30 * i, self.__device_axes_heights[e.device_index] - 15,
                            self.__left_padding + 30 * i, self.__device_axes_heights[e.device_index])
                qp.drawText(self.__left_padding + 30 * i + 3, self.__device_axes_heights[e.device_index] - 3,
                            str(e.request.producer_id + 1) + '.' + str(e.request.id + 1))
                j = min(i + 1, len(self.__release_log))
                while j < len(self.__release_log) and (self.__release_log[j] is None
                                                       or self.__release_log[j].device_index != e.device_index):
                    j += 1
                qp.drawLine(self.__left_padding + 30 * i, self.__device_axes_heights[e.device_index] - 15,
                            self.__left_padding + 30 * j, self.__device_axes_heights[e.device_index] - 15)

        for i, e in enumerate(self.__release_log):
            if e is not None and e.request is not None:
                j = max(i - 1, 0)
                while (j >= 0 and (not isinstance(self.__event_log[j], SettingEvent)
                                   or self.__event_log[j].device_index != e.device_index)):
                    j -= 1
                if j == -1:
                    if i != 0:
                        qp.drawText(self.__left_padding + 3, self.__device_axes_heights[e.device_index] - 3,
                                    str(e.request.producer_id + 1) + '.' + str(e.request.id + 1))
                    j = 0
                qp.drawLine(self.__left_padding + 30 * j, self.__device_axes_heights[e.device_index] - 15,
                            self.__left_padding + 30 * i, self.__device_axes_heights[e.device_index] - 15)
                qp.drawLine(self.__left_padding + 30 * i, self.__device_axes_heights[e.device_index] - 15,
                            self.__left_padding + 30 * i, self.__device_axes_heights[e.device_index])

        for i, state in enumerate(self.__buffer_log):
            for j, value in enumerate(state):
                if value is not None:
                    qp.drawLine(self.__left_padding + 30 * i, self.__buffer_axes_heights[j] - 15,
                                self.__left_padding + 30 * (i + 1), self.__buffer_axes_heights[j] - 15)

                    if (i == 0
                        or self.__buffer_log[i - 1][j] is None
                        or self.__buffer_log[i - 1][j].id != self.__buffer_log[i][j].id
                            or self.__buffer_log[i - 1][j].producer_id != self.__buffer_log[i][j].producer_id):
                        qp.drawText(self.__left_padding + 30 * i + 3, self.__buffer_axes_heights[j] - 3,
                                    str(value.producer_id + 1) + '.' + str(value.id + 1))
                        qp.drawLine(self.__left_padding + 30 * i, self.__buffer_axes_heights[j] - 15,
                                    self.__left_padding + 30 * i, self.__buffer_axes_heights[j])
                    if i == len(self.__buffer_log) - 1 and i != 9:
                        qp.drawLine(self.__left_padding + 30 * (i + 1), self.__buffer_axes_heights[j] - 15,
                                    self.__left_padding + 30 * (i + 1), self.__buffer_axes_heights[j])
                elif i != 0 and self.__buffer_log[i - 1][j] is not None:
                    qp.drawLine(self.__left_padding + 30 * i, self.__buffer_axes_heights[j] - 15,
                                self.__left_padding + 30 * i, self.__buffer_axes_heights[j])

        for i, e in enumerate(self.__deny_log):
            if e is not None:
                qp.drawLine(self.__left_padding + 30 * i, self.__device_axes_heights[-1] + self.__group_gap - 10,
                            self.__left_padding + 30 * i, self.__device_axes_heights[-1] + self.__group_gap)
                qp.drawText(self.__left_padding + 30 * i + 3, self.__device_axes_heights[-1] + self.__group_gap - 3,
                            str(e.request.producer_id + 1) + '.' + str(e.request.id + 1))

    def __draw_axes(self, qp):
        for i in range(self.__producer_count):
            qp.drawLine(self.__left_padding, self.__producers_axes_heights[i],
                        self.__left_padding + 300, self.__producers_axes_heights[i])

        for i in range(self.__buffer_size):
            qp.drawLine(self.__left_padding, self.__buffer_axes_heights[i],
                        self.__left_padding + 300, self.__buffer_axes_heights[i])

        for i in range(self.__device_count):
            qp.drawLine(self.__left_padding, self.__device_axes_heights[i],
                        self.__left_padding + 300, self.__device_axes_heights[i])

        if len(self.__device_axes_heights) > 0:
            qp.drawLine(self.__left_padding, self.__device_axes_heights[-1] + self.__group_gap,
                        self.__left_padding + 300, self.__device_axes_heights[-1] + self.__group_gap)

    def __calculate_axes_heights(self):
        producers_axes_heights = []
        for i in range(self.__producer_count):
            if i == 0:
                producers_axes_heights.append(self.__top_padding)
            else:
                producers_axes_heights.append(producers_axes_heights[-1] + self.__axes_gap)

        buffer_axes_heights = []
        for i in range(self.__buffer_size):
            if i == 0:
                buffer_axes_heights.append(producers_axes_heights[-1] + self.__group_gap)
            else:
                buffer_axes_heights.append(buffer_axes_heights[-1] + self.__axes_gap)

        device_axes_heights = []
        for i in range(self.__device_count):
            if i == 0:
                device_axes_heights.append(buffer_axes_heights[-1] + self.__group_gap)
            else:
                device_axes_heights.append(device_axes_heights[-1] + self.__axes_gap)
        return producers_axes_heights, buffer_axes_heights, device_axes_heights

    def __generate_labels(self):
        labels = []

        for i in range(self.__producer_count):
            labels.append(self.__generate_label('P' + str(i + 1) + ':', self.__producers_axes_heights[i]))

        for i in range(self.__buffer_size):
            labels.append(self.__generate_label('B' + str(i + 1) + ':', self.__buffer_axes_heights[i]))

        for i in range(self.__device_count):
            labels.append(self.__generate_label('D' + str(i + 1) + ':', self.__device_axes_heights[i]))

        labels.append(self.__generate_label('DENY:', self.__device_axes_heights[-1] + self.__group_gap))

        return labels

    def __generate_label(self, text, height):
        label = QtWidgets.QLabel(text, self)
        label.move(self.__label_padding, height - 10)
        label.show()
        return label
