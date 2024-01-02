import sys
import cv2
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QComboBox, QMessageBox, \
    QColorDialog, QFontDialog, QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
import cv2
import numpy as np

class PhotoEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Pencere ayarları
        self.setWindowTitle("Photo Editor")
        self.setGeometry(100, 100, 850, 500)

        # Görüntü etiketi
        self.label_image = QLabel(self)
        self.label_image.setGeometry(50, 50, 540, 340)

        # "Open Image" düğmesi
        self.button_open = QPushButton("Open Image", self)
        self.button_open.setGeometry(680, 50, 120, 30)
        self.button_open.clicked.connect(self.open_image)

        # Filtre seçimi için açılır menü
        self.combo_filter = QComboBox(self)
        self.combo_filter.setGeometry(20, 410, 150, 30)
        self.combo_filter.addItems(["None", "Salt and Pepper", "Blurring", "Sepia", "Black and White", "Sharpening", "Brightness","Brightness Reduction"])

        # Filtre uygulama düğmesi
        self.button_apply_filter = QPushButton("Apply Filter", self)
        self.button_apply_filter.setGeometry(680, 130, 120, 30)
        self.button_apply_filter.clicked.connect(self.apply_filter)

        # İleri filtre düğmesi
        self.button_forward = QPushButton("Forward", self)
        self.button_forward.setGeometry(680, 290, 120, 30)
        self.button_forward.clicked.connect(self.forward_filter)

        # Geri filtre düğmesi
        self.button_backward = QPushButton("Backward", self)
        self.button_backward.setGeometry(680, 330, 120, 30)
        self.button_backward.clicked.connect(self.backward_filter)

        # Kırpma düğmesi
        self.button_crop = QPushButton("Crop", self)
        self.button_crop.setGeometry(680, 250, 120, 30)
        self.button_crop.clicked.connect(self.start_crop)

        # Çizim düğmesi
        self.button_draw = QPushButton("Draw", self)
        self.button_draw.setGeometry(680, 170, 120, 30)
        self.button_draw.clicked.connect(self.start_drawing)

        # Çizim rengi seçme düğmesi
        self.button_color = QPushButton("Select Color", self)
        self.button_color.setGeometry(680, 210, 120, 30)
        self.button_color.clicked.connect(self.select_drawing_color)

        # Şekil seçimi için açılır menü
        self.combo_shape = QComboBox(self)
        self.combo_shape.setGeometry(180, 410, 150, 30)
        self.combo_shape.addItems(["None", "Rectangle", "Ellipse", "Line"])

        # Şekil çizme düğmesi
        self.button_draw_shape = QPushButton("Draw Shape", self)
        self.button_draw_shape.setGeometry(680, 370, 120, 30)
        self.button_draw_shape.clicked.connect(self.draw_shape)

        # Temizleme düğmesi
        self.button_clear = QPushButton("Delete", self)
        self.button_clear.setGeometry(420, 410, 120, 30)
        self.button_clear.clicked.connect(self.clear_all2)

        # "Save Image" düğmesi
        self.button_save_image = QPushButton("Save Image", self)
        self.button_save_image.setGeometry(680, 410, 120, 30)
        self.button_save_image.clicked.connect(self.save_image)

        # "Reset" düğmesi
        self.button_clear_image = QPushButton("Reset", self)
        self.button_clear_image.setGeometry(550, 410, 120, 30)
        self.button_clear_image.clicked.connect(self.clear_image)

        # Metin ekleme düğmesi
        self.button_add_text = QPushButton("Add Text", self)
        self.button_add_text.setGeometry(680, 90, 120, 30)
        self.button_add_text.clicked.connect(self.open_text_input_dialog)

        # İlgili değişkenlerin tanımlanması
        self.image_path = ""
        self.drawing_mode = False
        self.drawing_start_point = QPoint()
        self.drawing_end_point = QPoint()

        self.image_path = ""
        self.dragging = False
        self.drag_position = QPoint()
        self.dragged_text = ""

        self.image_path = ""
        self.drawing = False
        self.last_point = None
        self.drawing_color = QColor(255, 0, 0)  # Varsayılan renk: kırmızı

        self.image_path = ""
        self.image = None
        self.is_cropping = False
        self.crop_start = None
        self.crop_end = None

        self.image_path = ""
        self.applied_filters = []
        self.filtered_images = []
        self.current_index = -1

        self.text = ""
        self.point = None

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.point is not None:
            # Metni çizmek için boyama işlemcisi oluşturulması
            painter = QPainter(self)
            painter.setPen(QColor(255, 0, 0))  # Kırmızı renk
            painter.setFont(QFont("Arial", 10))  # Arial 10 punto
            painter.drawText(self.point, self.text)

    def open_image(self):
        # Dosya seçme iletişim kutusunu açma
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if image_path:
            self.image_path = image_path
            self.display_image(image_path)

    def display_image(self, image_path):
        # Görüntüyü etikete ekleme
        self.image = cv2.imread(image_path)
        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.label_image.setPixmap(pixmap.scaled(self.label_image.width(), self.label_image.height()))

    def open_text_input_dialog(self):
        if self.image_path:
            self.label_image.mousePressEvent1 = self.get_mouse_position1

    def get_mouse_position1(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            self.open_text_input_dialog_at_position(x, y)

    def open_text_input_dialog_at_position(self, x, y):
        # Metin giriş iletişim kutusunu açma
        text, ok = QInputDialog.getText(self, "Enter Text", "Enter the text:")
        if ok and text:
            # Yazı tipi seçme iletişim kutusunu açma
            font, ok = QFontDialog.getFont(self.font(), self, "Select Font")
            if ok:
                # Renk seçme iletişim kutusunu açma
                color = QColorDialog.getColor(Qt.black, self, "Select Color")
                if color.isValid():
                    # Metni görüntüye ekleme
                    self.add_text_to_image(text, font, color, (x, y))

    def add_text_to_image(self, text, font, color, position):
        # Metni görüntüye ekleme
        painter = QPainter(self.label_image.pixmap())
        painter.setPen(QColor(color))
        painter.setFont(font)
        painter.drawText(position[0], position[1], text)
        self.label_image.setPixmap(self.label_image.pixmap())

    def mousePressEvent1(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.pos()

    def mouseMoveEvent1(self, event):
        if self.dragging:
            # Metni taşıma işlemi
            self.label_image.move(self.mapToParent(event.pos() - self.drag_position))

    def mouseReleaseEvent1(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_position = QPoint()

            # Eğer taşınan metin varsa, metni görüntüye ekleyin
            if self.dragged_text:
                self.add_text_to_image(self.dragged_text, self.font(), Qt.black, self.label_image.pos())
                self.dragged_text = ""  # Taşınan metni sıfırla

    def keyPressEvent1(self, event):
        # ESC tuşuna basıldığında sürükleme durumunu ve sürüklenen metni sıfırla
        if event.key() == Qt.Key_Escape:
            self.dragging = False
            self.drag_position = QPoint()
            self.dragged_text = ""

        # BACKSPACE tuşuna basıldığında sürüklenen metinden son karakteri sil
        if event.key() == Qt.Key_Backspace:
            if self.dragged_text:
                self.dragged_text = self.dragged_text[:-1]

        # Herhangi bir metin karakterine basıldığında sürüklenen metine ekle ve güncelle
        if event.text():
            self.dragged_text += event.text()
            self.update_dragged_text()

    def update_dragged_text(self):
        # Sürüklenen metni etiket resmi üzerinde güncelle
        painter = QPainter(self.label_image.pixmap())
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(self.font())
        painter.drawText(self.label_image.rect(), Qt.AlignCenter, self.dragged_text)
        self.label_image.setPixmap(self.label_image.pixmap())

    def draw_text_on_image(self, text, font, color, x, y):
        # Metni resim üzerine çizmek için QPainter kullan
        image = cv2.imread(self.image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # QPainter için BGR'yi RGB'ye dönüştür
        q_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        painter = QPainter(pixmap)
        painter.setFont(font)
        painter.setPen(QPen(color))
        painter.drawText(QPoint(x, y), text)
        painter.end()

        self.label_image.setPixmap(pixmap.scaled(self.label_image.width(), self.label_image.height()))

    def apply_filter(self):
        if self.image_path:
            # Resmi oku
            image = cv2.imread(self.image_path)
            # Seçilen filtre tipini al
            filter_type = self.combo_filter.currentText()
            # Filtrelenmiş resim değişkenini başlangıçta boş olarak tanımla
            filtered_image = None

            # Filtre tipine göre ilgili işlemleri yap
            if filter_type == "Salt and Pepper":
                # Tuz ve biber gürültü miktarını ayarla
                salt_pepper_amount = 0.2
                # Resmi kopyala
                filtered_image = np.copy(image)
                rows, cols, _ = filtered_image.shape
                # Rastgele tuz ve biber pikselleri oluştur
                salt_pepper_pixels = np.random.rand(rows, cols)
                # Tuz piksellerini siyah yap
                filtered_image[salt_pepper_pixels < salt_pepper_amount / 2] = 0
                # Biber piksellerini beyaz yap
                filtered_image[salt_pepper_pixels > 1 - salt_pepper_amount / 2] = 255
            elif filter_type == "Blurring":
                # Bulanıklık filtresini uygula (çekirdek boyutunu ihtiyaca göre ayarla)
                filtered_image = cv2.GaussianBlur(image, (15, 15), 0)
            elif filter_type == "Sepia":
                # Sepia filtresini uygula
                filtered_image = self.apply_sepia(image)
            elif filter_type == "Black and White":
                # Resmi gri tonlamaya çevir
                filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            elif filter_type == "Sharpening":
                # Keskinleştirme filtresini uygula
                sharpening_kernel = np.array([[-1, -1, -1],
                                              [-1, 9, -1],
                                              [-1, -1, -1]])
                filtered_image = cv2.filter2D(image, -1, sharpening_kernel)
            elif filter_type == "Brightness":
                # Parlaklık faktörünü ayarla
                brightness_factor = 1.5
                # Parlaklık filtresini uygula
                filtered_image = self.apply_brightness(image, brightness_factor)
            elif filter_type == "Brightness Reduction":
                # Azaltma değerini ayarla
                reduction_value = 50
                # Parlaklık azaltma filtresini uygula
                filtered_image = self.apply_brightness_reduction(image, reduction_value)
            else:
                # Filtre yoksa orijinal resmi kullan
                filtered_image = image

            # Filtrelenmiş resim başarılı bir şekilde oluşturulduysa
            if filtered_image is not None:
                # Uygulanan filtrenin adını ve filtreyi listelere ekle
                self.applied_filters.append(filter_type)
                self.filtered_images.append(filtered_image)
                # Güncel indeksi ayarla
                self.current_index = len(self.filtered_images) - 1

                # Filtrelenmiş resmi ekranda göster
                if filter_type == "Black and White":
                    # Gri tonlamalı resim için QImage formatını ayarla
                    q_image = QImage(filtered_image.data, filtered_image.shape[1], filtered_image.shape[0],
                                     QImage.Format_Grayscale8)
                else:
                    # Diğer filtreler için QImage formatını ayarla
                    filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB)
                    q_image = QImage(filtered_image.data, filtered_image.shape[1], filtered_image.shape[0],
                                     QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.label_image.setPixmap(pixmap.scaled(self.label_image.width(), self.label_image.height()))

    def forward_filter(self): #bir adım ileri gitmeyi sağlar
        if self.current_index < len(self.filtered_images) - 1:
            self.current_index += 1
            filtered_image = self.filtered_images[self.current_index]
            filter_type = self.applied_filters[self.current_index]
            self.display_filtered_image(filtered_image, filter_type)

    def backward_filter(self): #bir adım geriye dönmeyi sağlar
        if self.current_index > 0:
            self.current_index -= 1
            filtered_image = self.filtered_images[self.current_index]
            filter_type = self.applied_filters[self.current_index]
            self.display_filtered_image(filtered_image, filter_type)

    def display_filtered_image(self, filtered_image, filter_type):
        if filter_type == "Black and White":
            q_image = QImage(filtered_image.data, filtered_image.shape[1], filtered_image.shape[0], QImage.Format_Grayscale8)
        else:
            filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for display
            q_image = QImage(filtered_image.data, filtered_image.shape[1], filtered_image.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.label_image.setPixmap(pixmap.scaled(self.label_image.width(), self.label_image.height()))

    def apply_sepia(self, image):
        # Apply Sepia filter to the image
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        sepia_image = cv2.transform(image, kernel)
        return sepia_image

    def apply_brightness(self, image, brightness_factor):
        # Apply brightness adjustment to the image
        adjusted_image = cv2.convertScaleAbs(image, alpha=brightness_factor, beta=0)
        return adjusted_image

    def apply_brightness_reduction(self, image, reduction_value):
        # Apply brightness reduction filter to the image
        adjusted_image = np.int16(image) - reduction_value
        adjusted_image = np.clip(adjusted_image, 0, 255)
        adjusted_image = np.uint8(adjusted_image)
        return adjusted_image

    def start_crop(self):
        if not self.is_cropping:
            self.is_cropping = True
            self.crop_start = None
            self.crop_end = None
            self.label_image.mousePressEvent = self.crop_mouse_press_event
            self.label_image.mouseMoveEvent = self.crop_mouse_move_event
            self.label_image.mouseReleaseEvent = self.crop_mouse_release_event

    def crop_mouse_press_event(self, event):
        if self.is_cropping:
            x = event.x()
            y = event.y()
            self.crop_start = (x, y)

    def crop_mouse_move_event(self, event):
        if self.is_cropping and self.crop_start is not None:
            x = event.x()
            y = event.y()
            self.crop_end = (x, y)
            self.display_image_with_crop()

    def crop_mouse_release_event(self, event):
        if self.is_cropping and self.crop_start is not None and self.crop_end is not None:
            x = event.x()
            y = event.y()
            self.crop_end = (x, y)
            self.is_cropping = False
            self.label_image.mousePressEvent = None
            self.label_image.mouseMoveEvent = None
            self.label_image.mouseReleaseEvent = None

            # Crop işlemini tamamlamak için bir mesaj kutusu göster
            reply = QMessageBox.question(self, 'Crop İşlemi Tamamlansın Mı?',
                                         'Crop işlemini tamamlamak istiyor musunuz?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.apply_crop()
            else:
                self.crop_start = None
                self.crop_end = None
                self.display_image_with_crop()

    def display_image_with_crop(self):
        if self.crop_start is not None and self.crop_end is not None:
            image = self.image.copy()
            cv2.rectangle(image, self.crop_start, self.crop_end, (0, 255, 0), 2)
        else:
            image = self.image.copy()

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.label_image.setPixmap(pixmap.scaled(self.label_image.width(), self.label_image.height()))

    def apply_crop(self):
        if self.crop_start is not None and self.crop_end is not None:
            image_cropped = self.image[self.crop_start[1]:self.crop_end[1], self.crop_start[0]:self.crop_end[0]]
            image_cropped = cv2.cvtColor(image_cropped, cv2.COLOR_BGR2RGB)
            height, width, channel = image_cropped.shape
            bytes_per_line = 3 * width
            q_image = QImage(image_cropped.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.label_image.setPixmap(pixmap.scaled(self.label_image.width(), self.label_image.height()))

            # Sonraki crop işlemleri için koordinatları sıfırla
            self.crop_start = None
            self.crop_end = None

    def start_drawing(self):
        # Çizim modunu başlatır
        self.drawing = True

    def mousePressEvent(self, event):
        # Sol fare düğmesine basıldığında ve çizim modu aktifken son noktayı kaydeder
        if self.drawing and event.button() == 1:  # Sol fare düğmesi
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        # Sol fare düğmesi basılı tutuluyorsa çizim yapar
        if self.drawing and event.buttons() & 1:  # Sol fare düğmesi basılı tutuluyor
            painter = QPainter(self.label_image.pixmap())
            pen = QPen(self.drawing_color)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()
            self.last_point = event.pos()
            self.label_image.update()

    def mouseReleaseEvent(self, event):
        # Sol fare düğmesi bırakıldığında çizim modunu kapatır
        if self.drawing and event.button() == 1:  # Sol fare düğmesi
            self.drawing = False

    def select_drawing_color(self):
        # Kullanıcıya renk seçme iletişim kutusu gösterir ve seçilen rengi kaydeder
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            self.drawing_color = color

    def draw_shape(self):
        # Şekil çizme işlevini etkinleştirir
        if self.image_path:
            shape_type = self.combo_shape.currentText()
            if shape_type == "None":
                return
            elif shape_type == "Rectangle":
                # Dikdörtgen çizme işlevini ayarlar
                self.label_image.mousePressEvent = self.start_drawing_rectangle
                self.label_image.mouseMoveEvent = self.update_drawing_rectangle
                self.label_image.mouseReleaseEvent = self.finish_drawing_rectangle
            elif shape_type == "Ellipse":
                # Elips çizme işlevini ayarlar
                self.label_image.mousePressEvent = self.start_drawing_ellipse
                self.label_image.mouseMoveEvent = self.update_drawing_ellipse
                self.label_image.mouseReleaseEvent = self.finish_drawing_ellipse
            elif shape_type == "Line":
                # Çizgi çizme işlevini ayarlar
                self.label_image.mousePressEvent = self.start_drawing_line
                self.label_image.mouseMoveEvent = self.update_drawing_line
                self.label_image.mouseReleaseEvent = self.finish_drawing_line

    def start_drawing_rectangle(self, event):
        # Sol fare düğmesine basıldığında çizim modunu başlatır
        if event.button() == Qt.LeftButton:
            self.drawing_mode = True
            self.drawing_start_point = event.pos()

    def update_drawing_rectangle(self, event):
        # Çizim modu açıksa dikdörtgenin güncellenmiş son noktasını kaydeder ve etikette gösterir
        if self.drawing_mode:
            self.drawing_end_point = event.pos()
            self.display_image(self.image_path)
            painter = QPainter(self.label_image.pixmap())
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            # Çizim başlangıç noktasından çizim son noktasına kadar bir dikdörtgen çizer
            painter.drawRect(self.drawing_start_point.x(), self.drawing_start_point.y(),
                             self.drawing_end_point.x() - self.drawing_start_point.x(),
                             self.drawing_end_point.y() - self.drawing_start_point.y())
            painter.end()

    def finish_drawing_rectangle(self, event):
        if event.button() == Qt.LeftButton and self.drawing_mode:
            self.drawing_mode = False  # Çizim modunu sonlandırır
            self.drawing_end_point = event.pos()  # Çizimin son noktasını alır
            self.display_image(self.image_path)  # Resmi etikete gösterir
            painter = QPainter(self.label_image.pixmap())  # QPainter nesnesi oluşturur
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))  # Kırmızı renkte ve 2 kalınlığında bir kalem kullanır
            painter.drawRect(self.drawing_start_point.x(), self.drawing_start_point.y(),
                             self.drawing_end_point.x() - self.drawing_start_point.x(),
                             self.drawing_end_point.y() - self.drawing_start_point.y())  # Dikdörtgeni çizer
            painter.end()  # QPainter nesnesini sonlandırır

    def start_drawing_ellipse(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing_mode = True  # Çizim modunu başlatır
            self.drawing_start_point = event.pos()  # Çizimin başlangıç noktasını alır

    def update_drawing_ellipse(self, event):
        if self.drawing_mode:
            self.drawing_end_point = event.pos()  # Çizimin son noktasını günceller
            self.display_image(self.image_path)  # Resmi etikete gösterir
            painter = QPainter(self.label_image.pixmap())  # QPainter nesnesi oluşturur
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))  # Kırmızı renkte ve 2 kalınlığında bir kalem kullanır
            painter.drawEllipse(self.drawing_start_point.x(), self.drawing_start_point.y(),
                                self.drawing_end_point.x() - self.drawing_start_point.x(),
                                self.drawing_end_point.y() - self.drawing_start_point.y())  # Elipsi çizer
            painter.end()  # QPainter nesnesini sonlandırır

    def finish_drawing_ellipse(self, event):
        if event.button() == Qt.LeftButton and self.drawing_mode:
            self.drawing_mode = False  # Çizim modunu sonlandırır
            self.drawing_end_point = event.pos()  # Çizimin son noktasını alır
            self.display_image(self.image_path)  # Resmi etikete gösterir
            painter = QPainter(self.label_image.pixmap())  # QPainter nesnesi oluşturur
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))  # Kırmızı renkte ve 2 kalınlığında bir kalem kullanır
            painter.drawEllipse(self.drawing_start_point.x(), self.drawing_start_point.y(),
                                self.drawing_end_point.x() - self.drawing_start_point.x(),
                                self.drawing_end_point.y() - self.drawing_start_point.y())  # Elipsi çizer
            painter.end()  # QPainter nesnesini sonlandırır

    def start_drawing_line(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing_mode = True  # Çizim modunu başlatır
            self.drawing_start_point = event.pos()  # Çizimin başlangıç noktasını alır

    def update_drawing_line(self, event):
        if self.drawing_mode:
            self.drawing_end_point = event.pos()  # Çizimin son noktasını günceller
            self.display_image(self.image_path)  # Resmi etikete gösterir
            painter = QPainter(self.label_image.pixmap())  # QPainter nesnesi oluşturur
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))  # Kırmızı renkte ve 2 kalınlığında bir kalem kullanır
            painter.drawLine(self.drawing_start_point, self.drawing_end_point)  # Çizgiyi çizer
            painter.end()  # QPainter nesnesini sonlandırır

    def clear_all2(self):
        self.current_filter = None  # Geçerli filtreyi temizler
        self.filter_history = []  # Filtre geçmişini temizler
        self.label_image.clear()  # Etiketteki görüntüyü temizler
        if self.image_path:
            image = cv2.imread(self.image_path)  # Resmi yeniden yükler
            self.display_image(image)  # Resmi etikete gösterir

    def finish_drawing_line(self, event):
        if event.button() == Qt.LeftButton and self.drawing_mode:
            self.drawing_mode = False  # Çizim modunu kapatır
            self.drawing_end_point = event.pos()  # Çizimin son noktasını alır
            self.display_image(self.image_path)  # Resmi etikete gösterir
            painter = QPainter(self.label_image.pixmap())  # QPainter nesnesi oluşturur
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))  # Kırmızı renkte ve 2 kalınlığında bir kalem kullanır
            painter.drawLine(self.drawing_start_point, self.drawing_end_point)  # Çizgiyi çizer
            painter.end()  # QPainter nesnesini sonlandırır

    def save_image(self):
        if self.image_path:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "JPEG Files (*.jpg)")
            if save_path:
                pixmap = self.label_image.pixmap()  # Etiketteki pixmap'i alır
                pixmap.save(save_path, "JPEG")  # Pixmap'i belirtilen yola JPEG formatında kaydeder
                print("Image saved successfully.")  # Başarıyla kaydedildiğini bildirir

    def clear_image(self):
        if self.image_path:
            self.display_image(self.image_path)  # Resmi başlangıçtaki haline geri getirir
            self.crop_start = None  # Kesme işlemi başlangıç noktasını sıfırlar
            self.crop_end = None  # Kesme işlemi bitiş noktasını sıfırlar


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoEditor()
    window.show()
    sys.exit(app.exec_())