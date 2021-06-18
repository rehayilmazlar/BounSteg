import sys
import base64
import os
import math
import re
from PIL import Image, UnidentifiedImageError
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox
import Ui_bounsteg_embed
import Ui_bounsteg_retrieve

image = None
new_image = None
image_rgb = None
width, height = 0, 0
magic_word = "$Reh@$"
magic_file = "$ß0UN$"
stopper_word = "#Reh@#"
has_space = True
is_rgba = False


class ImageProcess:
    @staticmethod
    def get_image_attributes(filename):
        # file to pass
        size = os.path.getsize(filename)
        size_kilobytes = ImageProcess.convert_to_kilobyte(size)

        global width, height

        return f"Image resolution: {width}x{height} File size: {size} bytes ({size_kilobytes} kb)"

    @staticmethod
    def is_corrupt(filename):
        try:
            global image
            global image_rgb
            global is_rgba

            image = Image.open(filename)
            if image.format == 'PNG':
                image_rgb = image.convert("RGBA")
                is_rgba = True
            else:
                image_rgb = image.convert("RGB")
                is_rgba = False

            global width, height
            width, height = image.size
            return False

        except (UnidentifiedImageError):
            MessageBox.error("UnidentifiedImageError",
                             "Image file you are trying to open is not valid, check the image and try again.")
            width, height = 0, 0
            return True

    @staticmethod
    def check_space(pixels, secret_binary):
        global has_space
        secret_length = len(secret_binary)
        try:
            for i in range(secret_length):
                pixels[i] = pixels[i][:-1] + secret_binary[i]
            has_space = True
            return pixels
        except IndexError:
            MessageBox.error(
                "Too Big!", "The data you try to embed is too big for this image.")
            has_space = False

    @staticmethod
    def convert_to_kilobyte(size):
        '''Converts bytes to kilobytes with precision of 2 decimal points'''
        return math.floor(size/1024 * 10 ** 2) / 10 ** 2

    @staticmethod
    def convert_to_binary(text):
        if(type(text) == str):
            converted = ''
            for char in text:
                converted += (''.join(format(ord(char), "08b")))
            return converted

        elif(type(text) == int):
            text = format(text, "08b")
            return text

    @staticmethod
    def convert_to_pixels():
        global image_rgb
        pixels = []
        for x in range(height):
            for y in range(width):
                rgb_value = image_rgb.getpixel((y, x))
                for i in rgb_value:
                    pixels.append(ImageProcess.convert_to_binary(i))
        return pixels

    @staticmethod
    def add_secret_message(secret, pixels, filename=''):
        result_message = ''
        if filename == '':
            result_message = ImageProcess.add_magic_word(secret)
        else:
            result_message = ImageProcess.add_magic_word(secret, filename)

        secret_binary = ImageProcess.convert_to_binary(result_message)

        length = len(secret_binary)
        # print("Length: ", length)
        # print("Pixels: ", len(pixels))

        new_pixels = ImageProcess.check_space(pixels, secret_binary)

        return new_pixels

    @staticmethod
    def convert_to_image(pixels):
        new_pixels = []
        if pixels is not None:
            for pixel in pixels:
                pixel = int(pixel, 2)
                new_pixels.append(pixel)

            img_bytes = bytes(new_pixels)
            if image.format == 'PNG':
                img = Image.frombytes('RGBA', (width, height), img_bytes)
            else:
                img = Image.frombytes('RGB', (width, height), img_bytes)
            return img
        else:
            return False

    @staticmethod
    def add_magic_word(secret, filename=''):
        if filename == '':
            # append # at the end of text to mark where the text ends.
            result = magic_word + secret + stopper_word
            return result
        else:
            # append ## at the end of filename to mark where the file name ends.
            result = magic_file + filename + stopper_word + secret + stopper_word
            return result

    @staticmethod
    def hide_text(message):
        pixels = ImageProcess.convert_to_pixels()
        base64encoded_message = ImageProcess.base64_encode(message)
        new_pixels = ImageProcess.add_secret_message(
            base64encoded_message, pixels)
        global new_image
        new_image = ImageProcess.convert_to_image(new_pixels)

    @staticmethod
    def hide_file(filename):
        filename_only = filename.rsplit('/', 1)[-1]
        pixels = ImageProcess.convert_to_pixels()
        base64encoded_message = ImageProcess.base64_encode_file(filename)
        new_pixels = ImageProcess.add_secret_message(
            base64encoded_message, pixels, filename_only)
        global new_image
        new_image = ImageProcess.convert_to_image(new_pixels)
        if not new_image:
            return False
        else:
            return True

    @staticmethod
    def save_image(name):
        # not to lose any pixel value.
        new_image.save(name, quality=100, subsampling=0)
        # print("image saved")

    @staticmethod
    def show_message():
        if ImageProcess.has_magic() == 'Text':
            # print("has hidden text")
            magic_word_binary = ImageProcess.convert_to_binary(magic_word)
            pixel_string = ''
            for x in range(height):
                for y in range(width):
                    # use global image_rgb
                    rgb_value = image_rgb.getpixel((y, x))
                    for i in rgb_value:
                        # get pixel's every 8th to be able to extract data
                        pixel_string += ImageProcess.convert_to_binary(i)[7]

            marker = ImageProcess.convert_to_binary(stopper_word)
            where = pixel_string.find(marker)
            # print("Where: ", where)
            message_binary = pixel_string[:where]

            secret_message = ''
            for i in range(0, len(message_binary), 8):
                secret_message += chr(int((message_binary[i:i+8]), 2))

            if magic_word in secret_message:
                secret_message = secret_message.lstrip(magic_word)
            else:
                MessageBox.error("Error", "Something went wrong, try again.")

            base64decoded_message = ImageProcess.base64_decode(secret_message)
            # print(base64decoded_message)
            return base64decoded_message

        elif ImageProcess.has_magic() == 'File':
            # print("has hidden file")
            marker = ImageProcess.convert_to_binary(stopper_word)
            pixel_string = ''
            for x in range(height):
                for y in range(width):
                    rgb_value = image_rgb.getpixel((y, x))
                    for i in rgb_value:
                        # get pixel's every 8th to be able to extract data
                        pixel_string += ImageProcess.convert_to_binary(i)[7]

            first_marker = pixel_string.find(marker)
            # print("First marker: ", first_marker)
            message_binary = pixel_string[:first_marker]

            file_name = ''
            for i in range(0, len(message_binary), 8):
                file_name += chr(int((message_binary[i:i+8]), 2))

            second_marker = pixel_string.find(marker, first_marker + 1)
            # print("Second marker: ", second_marker)

            file_binary = pixel_string[first_marker:second_marker]

            if magic_file in file_name:
                file_name = file_name.lstrip(magic_file)
            else:
                MessageBox.error("Error", "Something went wrong, try again.")

            # print(file_name)

            file = ''
            for i in range(0, len(file_binary), 8):
                file += chr(int((file_binary[i:i+8]), 2))

            # strip the ## at the beginning
            file = file.lstrip(stopper_word)
            # print(len(file))

            return (file, file_name)

    @staticmethod
    def has_magic():
        global image_rgb
        global is_rgba
        magic_word_binary = ImageProcess.convert_to_binary(magic_word)
        magic_file_binary = ImageProcess.convert_to_binary(magic_file)

        pixels = []

        # if rgb get 16, if rgba get 12 : 16 * 3 =  12 * 4
        if is_rgba:
            rgb_range = 12
        else:
            rgb_range = 16

        for y in range(rgb_range):
            rgb_value = image_rgb.getpixel((y, 0))
            for i in rgb_value:
                pixels.append(ImageProcess.convert_to_binary(i))

        pixel_string = ''

        for pixel in pixels:
            # get pixel's every 8th bit to check if it has stego data
            pixel_string += pixel[7]

        if magic_word_binary in pixel_string:
            return "Text"
        elif magic_file_binary in pixel_string:
            return "File"
        else:
            return None

    @staticmethod
    def base64_encode(text):
        text_bytes = text.encode("utf-8")

        base64_bytes = base64.b64encode(text_bytes)
        base64_string = base64_bytes.decode("utf-8")

        return base64_string

    @staticmethod
    def base64_decode(text):
        base64_bytes = text.encode("utf-8")

        text_bytes = base64.b64decode(base64_bytes)
        decoded_string = text_bytes.decode("utf-8")

        return decoded_string

    @staticmethod
    def base64_encode_file(filename):

        with open(filename, "rb") as file:
            b64_encoded_bytes = base64.b64encode(file.read())

        base64_string = b64_encoded_bytes.decode("utf-8")

        # print("base64 len: ", len(base64_string))
        return base64_string

    @staticmethod
    def base64_decode_file(string, filename):
        string_bytes = string

        print(len(string_bytes))
        with open(filename, 'wb') as file:
            file.write(base64.b64decode((string_bytes)))

        # print(f"{filename} has been extracted")


class EmbedDialog(QMainWindow, Ui_bounsteg_embed.Ui_embedData):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # toggles check buttons, if one is checked other is unchecked
        self.radioFile.toggled.connect(self.toggle_radioFile)
        self.radioText.toggled.connect(self.toggle_radioText)

        self.radioRetrieve1.toggled.connect(self.switch_dialogue)
        self.radioEmbed1.toggled.connect(self.switch_dialogue)
        self.browseImage1.clicked.connect(self.browse_image)

        self.saveNewImage.clicked.connect(self.save_file)
        self.browseFile.clicked.connect(self.browse_file)
        self.embed.clicked.connect(self.embed_data)

    def browse_image(self):
        file_dialog = QFileDialog(self)
        fileName = QFileDialog.getOpenFileName(
            self, "Open File", "", "Images (*.bmp *.png )")

        # if user didn't cancel click on browse file dialogue, then proceed
        if not fileName == ('', ''):
            filePath = fileName[0]
            self.filePath1.setText(fileName[0]),
            if ImageProcess.is_corrupt(filePath):
                self.filePath1.setText("1) Choose an image to start...")
                self.imageInfo1.setText("")

            else:
                if ImageProcess.has_magic():
                    self.imageInfo1.setText(
                        "The file you chose has already embedded data, please choose another file.")
                    self.embed.setEnabled(False)
                else:
                    image_info = ImageProcess.get_image_attributes(filePath)
                    self.imageInfo1.setText(image_info)
                    self.embed.setEnabled(True)

    def check_filePath(self, file_path):
        if os.path.exists(file_path):
            # print("file exists")
            return True
        else:
            return False

    def save_file(self):
        options = QFileDialog.Options()
        fileName = ''
        image_path = self.filePath1.text()

        if self.check_filePath(image_path):
            file_extension = image_path[-3:]
            if file_extension.lower() == 'bmp':
                fileName, _ = QFileDialog.getSaveFileName(
                    self, "QFileDialog.getSaveFileName()", "", "BMP (*.bmp)", options=options)
            elif file_extension.lower() == 'png':
                fileName, _ = QFileDialog.getSaveFileName(
                    self, "QFileDialog.getSaveFileName()", "", "PNG (*.png)", options=options)
                # print(fileName)

            if not image_path == '' and fileName == '':
                # print("name")
                MessageBox.warning(
                    "Name the new file!", "You should name your new image file in order to save.")

            # check file name if it has inappropriate characters
            elif not re.match(r"^[\w\-.]+$", fileName.rsplit('/', 1)[-1]):
                MessageBox.error("Characters not permitted!",
                                 "You cannot use those characters in a file name.")
            else:
                # save the file and append the file extension.
                ImageProcess.save_image(
                    fileName)
                MessageBox.information(
                    "File saved!", "New image file succesfully saved.")

    def browse_file(self):
        file_dialog = QFileDialog(self)
        fileName = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*.*)")

        # if user didn't cancel click on browse file dialogue, then proceed
        if not fileName == ('', ''):
            filePath = fileName[0]
            self.secretFile1.setText(fileName[0])
            size = os.path.getsize(filePath)
            size_kilobytes = math.floor(size/1024 * 10 ** 2) / 10 ** 2
            size_info = f"File size: {size} bytes ({size_kilobytes} kb)"
            self.secretFileInfo.setText(size_info)

    def embed_data(self):
        # print("embed data!")
        image_path = self.filePath1.text()
        file_path = self.secretFile1.text()
        if self.radioFile.isChecked():
            # print("radioFile.isChecked")
            if self.check_filePath(image_path) and self.check_filePath(file_path):
                # print("PATH: ", file_path)
                if ImageProcess.hide_file(file_path):
                    # print("returns trueee")
                    self.saveNewImage.setEnabled(True)
                    MessageBox.information(
                        "Save the new image", "Now you can save your new stego image.")
            else:
                MessageBox.warning("No Image or File Chosen!",
                                   "You should browse an image and a file to embed.")
        else:
            # print("Text is checked")
            if self.check_filePath(image_path):
                if ImageProcess.has_magic():
                    MessageBox.error(
                        "Error!", "Image has already secret data embedded, please choose another image.")
                else:
                    message = self.secretText1.toPlainText()
                    if message == '':
                        MessageBox.warning(
                            "Type something to hide inside the image.", "")
                    else:
                        ImageProcess.hide_text(message)
                        self.saveNewImage.setEnabled(True)
                        MessageBox.information(
                            "Save the new image", "Now you can save your new stego image.")
                        self.embed.setEnabled(False)
            else:
                MessageBox.error("File does not exist!",
                                 "Please browse a file.")

    def toggle_radioFile(self):
        if self.radioFile.isChecked():
            self.radioText.setChecked(False)
            self.secretText1.setEnabled(False)
            # print("switched")
            self.secretText1.setPlaceholderText("")
            self.secretFile1.setText("2) Choose a file to embed...")
        else:
            self.radioText.setChecked(True)

    def toggle_radioText(self):
        if self.radioText.isChecked():
            self.radioFile.setChecked(False)
            self.browseFile.setEnabled(False)
            self.secretText1.setEnabled(True)
            self.secretFile1.setEnabled(False)
            self.secretText1.setPlaceholderText(
                "2) Type your text here that you want to hide into the image...")
            self.secretFile1.setText("")
        else:
            self.radioFile.setChecked(True)
            self.browseFile.setEnabled(True)

    # this method shows the other dialogue (rerieve dialog) and closes this one.
    def switch_dialogue(self):
        # print("retrieve clicked")
        retrieve_dialogue = RetrieveDialog()
        widget.addWidget(retrieve_dialogue)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setWindowTitle = 'Boun Steg - Embed Data'
        widget.show()


class RetrieveDialog(QMainWindow, Ui_bounsteg_retrieve.Ui_retrieveData):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.radioembed2.toggled.connect(self.switch_dialogue)
        self.browseImage2.clicked.connect(self.browse_image)
        self.saveAsText.clicked.connect(self.save_as_text)
        self.copyText.clicked.connect(self.copy_text)
        self.extractFile.clicked.connect(self.save_as_file)

    def switch_dialogue(self):
        # print("embed clicked")
        embed_dialogue = EmbedDialog()
        widget.addWidget(embed_dialogue)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.show()

    def browse_image(self):
        # reset everything when browsing a new image
        self.copyText.setEnabled(False)
        self.saveAsText.setEnabled(False)
        self.extractFile.setEnabled(False)
        self.secretFileName.setEnabled(False)
        self.secretFileName.setText("")
        self.secretText2.setEnabled(False)
        self.secretText2.setText("")
        self.imageInfo2.setText("")

        file_dialog = QFileDialog(self)
        fileName = QFileDialog.getOpenFileName(
            self, "Open File", "", "Images (*.bmp *.png )")

        # if user didn't cancel click on browse file dialogue, then proceed
        if not fileName == ('', ''):
            filePath = fileName[0]
            self.filePath2.setText(fileName[0])
            self.secretText2.setText("")
            if not ImageProcess.is_corrupt(filePath):
                image_info = ImageProcess.has_magic()
                if image_info == 'File':
                    self.imageInfo2.setText(
                        "Image seems to have an embedded file.")
                    self.secretFileName.setEnabled(True)
                    self.extractFile.setEnabled(True)
                    file_name = ImageProcess.show_message()[1]
                    self.secretFileName.setText(file_name)
                elif image_info == 'Text':
                    self.imageInfo2.setText(
                        "Image seems to have a hidden text.")
                    self.secretText2.setEnabled(True)
                    self.saveAsText.setEnabled(True)
                    self.copyText.setEnabled(True)
                    hidden_text = ImageProcess.show_message()
                    self.secretText2.setText(hidden_text)
                else:
                    self.imageInfo2.setText(
                        "Image does not seem to have any hidden data.")
            else:
                self.filePath2.setText("1) Choose an image to start...")
                self.imageInfo2.setText("")

    def check_filePath(self, file_path):
        if os.path.exists(file_path):
            # print("file exists")
            return True
        else:
            return False

    def save_as_text(self):
        self.save_file()

    def save_as_file(self):
        self.save_file("file")

    def save_file(self, file="text"):
        if file == "text":
            file_types = "Text Documents (*.txt)"
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getSaveFileName(
                self, 'Save As', 'secret_message', filter=file_types, options=options)
        else:
            file_types = "All Files (*.*)"
            options = QFileDialog.Options()
            secret_file = self.secretFileName.text()
            fileName, _ = QFileDialog.getSaveFileName(
                self, 'Save As', secret_file, options=options)

        if fileName == '':
            # print("name")
            MessageBox.warning(
                "Name the new file!", "You should name your new image file in order to save.")

        # check file name if it has inappropriate characters
        elif not re.match(r"^[\w\-.]+$", fileName.rsplit('/', 1)[-1]):
            MessageBox.error("Characters not permitted!",
                             "You cannot use those characters in a file name.")
        else:
            if file == "text":
                text = self.secretText2.toPlainText()
                # save the file and append the file extension.
                with open(fileName, 'w', encoding='utf8') as file:
                    file.write(text)
                MessageBox.information(
                    "File saved!", "New image file succesfully saved.")

            else:
                file = ImageProcess.show_message()[0]
                result = ImageProcess.base64_decode_file(file, fileName)
                MessageBox.information(
                    "File saved!", "File extracted successfully.")

    def copy_text(self):
        text = self.secretText2.toPlainText()
        clipboard.setText(text)
        MessageBox.information("Content copied to clipboard.", "", "Copied!")


class MessageBox:

    @staticmethod
    def error(exception_type, exception_message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(exception_type)
        msg.setInformativeText(exception_message)
        msg.setWindowTitle("Error")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./stego.ico"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
        msg.setWindowIcon(icon)
        msg.exec_()

    @staticmethod
    def warning(warning_type, warning_message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(warning_type)
        msg.setInformativeText(warning_message)
        msg.setWindowTitle("Warning")
        msg.setWindowIcon(icon)
        msg.exec_()

    @staticmethod
    def information(warning_type, warning_message, *title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(warning_type)
        msg.setInformativeText(warning_message)
        msg.setWindowIcon(icon)

        if len(title) > 0:
            title = title[0]
            msg.setWindowTitle(title)
        else:
            msg.setWindowTitle("Information")

        msg.exec_()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    clipboard = app.clipboard()
    embed_dialogue = EmbedDialog()
    widget = QtWidgets.QStackedWidget()
    widget.setFixedHeight(341)
    widget.setFixedWidth(488)
    widget.addWidget(embed_dialogue)
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("./stego.ico"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
    widget.setWindowIcon(icon)
    if widget.windowTitleChanged:
        widget.setWindowTitle("Boun Steg")
    widget.show()
    # main()
    sys.exit(app.exec_())
