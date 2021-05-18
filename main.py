import cv2
import numpy as np
import json
import time
import telegram


def nothing(x):
    pass


class Color_cv:
    """
        Класс для цветового маскирования изображений
    """
    settings_default = {
                         "low - hue": 0,
                         "low - sat": 0,
                         "low - val": 0,
                         "upp - hue": 255,
                         "upp - sat": 255,
                         "upp - val": 255
                       }

    def __init__(self, color_name: str):
        """
            Создает окно с скроллами для настройки цвета маскирования
        """
        self.hsv_fname = f"hsv_{color_name}.json"
        self.w_name_trackbars = f"{color_name} trackbars"
        self.mask_name = f"{color_name} mask"
        self.recognized = False  # Флаг распознавания

        # Создание окна с скроллами для настройки цвета маскирования
        hsv_json = self.load_settings()
        cv2.namedWindow(self.w_name_trackbars)
        cv2.createTrackbar("low - hue", self.w_name_trackbars,
                           hsv_json["low - hue"], 179, nothing)
        cv2.createTrackbar("low - sat", self.w_name_trackbars,
                           hsv_json["low - sat"], 255, nothing)
        cv2.createTrackbar("low - val", self.w_name_trackbars,
                           hsv_json["low - val"], 255, nothing)
        cv2.createTrackbar("upp - hue", self.w_name_trackbars,
                           hsv_json["upp - hue"], 179, nothing)
        cv2.createTrackbar("upp - sat", self.w_name_trackbars,
                           hsv_json["upp - sat"], 255, nothing)
        cv2.createTrackbar("upp - val", self.w_name_trackbars,
                           hsv_json["upp - val"], 255, nothing)

    def get_color_diaposones(self) -> dict:
        """
            Возвращает цветовые диапозоны в формате HSV для маскирования
        """
        l_h = cv2.getTrackbarPos("low - hue", self.w_name_trackbars)
        l_s = cv2.getTrackbarPos("low - sat", self.w_name_trackbars)
        l_v = cv2.getTrackbarPos("low - val", self.w_name_trackbars)
        u_h = cv2.getTrackbarPos("upp - hue", self.w_name_trackbars)
        u_s = cv2.getTrackbarPos("upp - sat", self.w_name_trackbars)
        u_v = cv2.getTrackbarPos("upp - val", self.w_name_trackbars)

        return {
                 "lower": np.array([l_h, l_s, l_v]),
                 "upper": np.array([u_h, u_s, u_v])
               }

    def show_mask(self, frame):
        """
            Маскирует изображение и выводит его в отдельное окно.
            Устанавливает флаг распознавания
        """
        diaposones = self.get_color_diaposones()
        self.mask = cv2.inRange(frame, diaposones["lower"],
                                       diaposones["upper"])
        cv2.imshow(self.mask_name, self.mask)

#        self.recognized = self.recognize(cv2.moments(self.mask, 1))
        result_frame = cv2.bitwise_and(frame, frame, mask=self.mask)
        blocks = []
        i = 0
        j = 0

    def recognize(self, moments: dict) -> bool:
        """
            Вычисляет и возвращает флаг распознавания объекта
            В случае, если объект распознан, то вычисляет и устанавливает точку
        его центра
            :return: True, если moments["m00"] > 35
                     False в иных случаях
        """
        moments = cv2.moments(self.mask, 1)
        dM01 = moments["m01"]
        dM10 = moments["m10"]
        dArea = moments["m00"]
        if dArea > 35:
            self.x_center = int(dM10 / dArea)
            self.y_center = int(dM01 / dArea)
            return True
        else:
            return False

    def save_settings(self):
        """
            Сохраняет настройки маскирования из трэкбара
        """
        with open(self.hsv_fname, "w") as write_file:
            data = {
                     "low - hue": cv2.getTrackbarPos("low - hue",
                                                     self.w_name_trackbars),
                     "low - sat": cv2.getTrackbarPos("low - sat",
                                                     self.w_name_trackbars),
                     "low - val": cv2.getTrackbarPos("low - val",
                                                     self.w_name_trackbars),
                     "upp - hue": cv2.getTrackbarPos("upp - hue",
                                                     self.w_name_trackbars),
                     "upp - sat": cv2.getTrackbarPos("upp - sat",
                                                     self.w_name_trackbars),
                     "upp - val": cv2.getTrackbarPos("upp - val",
                                                     self.w_name_trackbars)
            }
            json.dump(data, write_file)

    def load_settings(self) -> dict:
        """
            Загружает настройки маскирования. Если файл не найден, то
        возвращает стандартные настройки
        """
        try:
            with open(self.hsv_fname, "r") as read_file:
                return json.load(read_file)
        except FileNotFoundError:
            return self.settings_default


def write_info(frame, text: str) -> "Frame":
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (39, 28)
    fontScale = 0.75
    color = (255, 0, 0)
    thickness = 2
    return cv2.putText(frame, text, org, font,
                       fontScale, color, thickness, cv2.LINE_AA)


def calc_lenght(p1: tuple, p2: tuple) -> int:
    """
        Расчет расстояния между двумя точками
        :param p1: точка 1 (x;y)
        :param p2: точка 2 (x;y)
        :return: расстояние между точками
    """
    max_x = max(p1[0], p2[0])
    min_x = min(p1[0], p2[0])
    len_x = max_x - min_x

    # Расчет длины между точками по y
    max_y = max(p1[1], p2[1])
    min_y = min(p1[1], p2[1])
    len_y = max_y - min_y

    # Расчет длины между точками
    return int(round((len_x**2 + len_y**2)**0.5))

def show_information(frame):
    """
        Отображает состояние двух объектов: то, распознаны ли они (и какие
    не распознаны), расстояние между ними. Так же отображает круг, цвет
    которого означает диапозон расстояний, в котором сейчас находится объект.
    Рисует круг на распознаном объекте.
    """

    # Отображение круга на опознанных объектах
    if cv_yellow.recognized:
       cv2.circle(frame, (cv_yellow.x_center, cv_yellow.y_center),
                  10, (255, 255, 255), -1)
    if cv_red.recognized:
       cv2.circle(frame, (cv_red.x_center, cv_red.y_center),
                  10, (0, 0, 255), -1)

    if cv_yellow.recognized & cv_red.recognized:
        lenght = calc_lenght((cv_yellow.x_center, cv_red.y_center),
                             (cv_red.x_center, cv_yellow.y_center))
        print(lenght)
        if lenght > 200:
            text = f"Lenght: {lenght}, Green"
            cv2.line(frame, (cv_yellow.x_center, cv_yellow.y_center),
                            (cv_red.x_center, cv_red.y_center), (0, 255, 0), 3)
            cv2.circle(frame, (16, 20), 14, (0, 255, 0), -1)
            telegram.bot.mailing = -1
        elif lenght > 50:
            text = f"Lenght: {lenght}, Orange"
            cv2.line(frame, (cv_yellow.x_center, cv_yellow.y_center),
                            (cv_red.x_center, cv_red.y_center), (0, 165, 255), 3)
            cv2.circle(frame, (16, 20), 14, (0, 165, 255), -1)
            if telegram.bot.mailing == -1:
                telegram.bot.send_message(f"Внимание! До айсберга {lenght}")
            telegram.bot.mailing += 1
            if telegram.bot.mailing == 150:
                telegram.bot.mailing = -1
        elif lenght <= 50:
            text = f"Lenght: {lenght}, Red"
            cv2.line(frame, (cv_yellow.x_center, cv_yellow.y_center),
                            (cv_red.x_center, cv_red.y_center), (0, 0, 255), 3)
            cv2.circle(frame, (16, 20), 14, (0, 0, 255), -1)
            if telegram.bot.mailing == -1:
                telegram.bot.send_message(f"Внимание! До столкновения с айсбергом {lenght}")
            telegram.bot.mailing += 1
            if telegram.bot.mailing == 150:
                telegram.bot.mailing = -1
    else:
        if (not cv_yellow.recognized) & (cv_red.recognized):
            text = "white not recognized"
        elif (cv_yellow.recognized) & (not cv_red.recognized):
            text = "red not recognized"
        else:
            text = "red & white not recognized"
    write_info(frame, text)


cap = cv2.VideoCapture(1)
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

cv_yellow = Color_cv("white")
cv_red = Color_cv("red")

while True:
    _, frame = cap.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    cv_yellow.show_mask(hsv)
    cv_red.show_mask(hsv)
    result_red = cv2.bitwise_and(frame, frame, mask=cv_yellow.mask)
    result = result_red

    result_white = cv2.bitwise_and(frame, frame, mask=cv_red.mask)
    result = cv2.bitwise_or(result, result_white)

    show_information(frame)

    cv2.imshow("Frame", frame)
    cv2.imshow("Result", result)

    key = cv2.waitKey(1)
    if key == 27:
        break
    time.sleep(1 / 30)

cv_yellow.save_settings()
cv_red.save_settings()

cap.release()
cv2.destroyAllWindows()
