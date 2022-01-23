import base64
import binascii
import os
import sys

from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MyWindow(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        dpi = self.screen().logicalDotsPerInch() / 96
        font_size = 14 if dpi <= 1 else (11 if 1 < dpi <= 1.25 else (9 if 1.25 < dpi <= 1.5 else 8))
        self.setFont(QFont("DengXian", font_size))
        self.resize(480, 800)
        self.setWindowTitle("SHA256 with RSA")
        self.center()

        self.label1 = QLabel(self)
        self.label1.setText("Generate the keypair")
        self.label1.move(10, 10)
        self.label1.setFont(QFont("DengXian", font_size + 1, 75))

        self.button1 = QToolButton(self)
        self.button1.move(10, 40)
        self.button1.setText("Select Folder")
        self.button1.clicked.connect(self.select_base_dir)

        self.label2 = QLabel(self)  # base dir path
        self.label2.move(140, 35)
        self.label2.resize(310, 30)

        self.label3 = QLabel(self)
        self.label3.move(10, 75)
        self.label3.setText("New filename:")

        self.box1 = QLineEdit(self)  # filename form-control
        self.box1.move(140, 70)
        self.box1.resize(160, 30)

        self.label5 = QLabel(self)
        self.label5.move(310, 75)
        self.label5.setText("n (Opt.):")

        self.box2 = QLineEdit(self)  # n form-control
        self.box2.move(380, 70)
        self.box2.resize(70, 30)

        self.button2 = QToolButton(self)
        self.button2.move(10, 110)
        self.button2.setText("Run")
        self.button2.clicked.connect(self.generate_key)

        self.label4 = QLabel(self)  # keypair run status
        self.label4.move(70, 110)
        self.label4.resize(380, 25)

        self.label6 = QLabel(self)
        self.label6.move(10, 140)
        self.label6.setText("Sign")
        self.label6.setFont(QFont("DengXian", font_size + 1, 75))

        self.label7 = QLabel(self)
        self.label7.move(10, 170)
        self.label7.setText("Message:")

        self.box3 = QTextEdit(self)  # message textarea
        self.box3.move(10, 190)
        self.box3.resize(440, 80)

        self.button3 = QToolButton(self)
        self.button3.move(10, 280)
        self.button3.clicked.connect(self.select_private_key)
        self.button3.setText("Private Key")

        self.label8 = QLabel(self)  # private key path
        self.label8.move(120, 280)
        self.label8.resize(330, 20)

        self.button4 = QToolButton(self)
        self.button4.move(10, 420)
        self.button4.setText("Run")
        self.button4.clicked.connect(self.sign)

        self.label9 = QLabel(self)
        self.label9.move(10, 310)
        self.label9.setText("Signature:")

        self.box4 = QTextEdit(self)  # signature textarea
        self.box4.move(10, 330)
        self.box4.resize(440, 80)

        self.label10 = QLabel(self)  # signature run status
        self.label10.move(70, 420)
        self.label10.resize(380, 20)

        self.label11 = QLabel(self)
        self.label11.move(10, 460)
        self.label11.setFont(QFont("DengXian", font_size + 1, 75))
        self.label11.setText("Verify")

        self.label12 = QLabel(self)
        self.label12.move(10, 490)
        self.label12.setText("Message:")

        self.box5 = QTextEdit(self)  # message textarea
        self.box5.move(10, 510)
        self.box5.resize(440, 80)

        self.label14 = QLabel(self)
        self.label14.move(10, 600)
        self.label14.setText("Signature:")

        self.box6 = QTextEdit(self)  # signature textarea
        self.box6.move(10, 620)
        self.box6.resize(440, 80)

        self.button5 = QToolButton(self)
        self.button5.move(10, 710)
        self.button5.clicked.connect(self.select_public_key)
        self.button5.setText("Public Key")

        self.label13 = QLabel(self)  # public key path
        self.label13.move(120, 710)
        self.label13.resize(330, 20)

        self.label15 = QLabel(self)  # verify status
        self.label15.move(120, 740)
        self.label15.resize(330, 20)

        self.button6 = QToolButton(self)
        self.button6.move(10, 740)
        self.button6.setText("Run")
        self.button6.clicked.connect(self.verify)

        self.label16 = QLabel(self)
        self.label16.move(10, 770)
        self.label16.setText("Author: cloudy-sfu @github")

        self.label17 = QLabel(self)  # verification result
        self.label17.move(300, 460)
        self.label17.resize(150, 20)
        self.label17.setFont(QFont("Segoe UI", font_size, 75))

        self.generator = None
        self.signer = None
        self.signature_valid = None

    def display_signature_valid(self, x):
        if x is True:
            self.label17.setStyleSheet("color: green;")
            self.label17.setText("VALID")
        elif x is False:
            self.label17.setStyleSheet("color: red;")
            self.label17.setText("INVALID")
        else:
            self.label17.clear()

    def center(self):
        fg = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

    def select_base_dir(self):
        fp = QFileDialog.getExistingDirectory(self)
        self.label2.setText(fp)

    def select_private_key(self):
        fp, _ = QFileDialog.getOpenFileName(self)
        self.label8.setText(fp)

    def select_public_key(self):
        fp, _ = QFileDialog.getOpenFileName(self)
        self.label13.setText(fp)

    def generate_key(self):
        if not self.label2.text():
            return self.label4.setText("FAIL: BASE DIR REQUIRED")
        elif not self.box1.text():
            return self.label4.setText("FAIL: FILENAME REQUIRED")
        try:
            n = int(self.box2.text())
            self.generator = Generate(self.label2.text(), self.box1.text(), n)
            # the returned value must be a property of MyWindow, otherwise will cause error:
            #  QThread: Destroyed while thread is still running
        except ValueError:
            self.generator = Generate(self.label2.text(), self.box1.text())
        self.generator.start()
        self.generator.signal1.connect(lambda x: self.label4.setText(x))
        self.label4.clear()

    def sign(self):
        if not self.box3.toPlainText():
            return self.label10.setText("FAIL: MESSAGE IS EMPTY")
        if not self.label8.text():
            return self.label10.setText("FAIL: PRIVATE KEY IS EMPTY")
        self.label10.clear()
        self.signer = Sign(self.label8.text(), self.box3.toPlainText())
        self.signer.start()
        self.signer.signal1.connect(lambda x: self.box4.setText(x))
        self.signer.signal2.connect(lambda x: self.label10.setText(x))
        self.box4.clear()

    def verify(self):
        if not self.box5.toPlainText():
            return self.label15.setText("FAIL: MESSAGE IS EMPTY")
        if not self.box6.toPlainText():
            return self.label15.setText("FAIL: SIGNATURE IS EMPTY")
        if not self.label13.text():
            return self.label15.setText("FAIL: PUBLIC KEY IS EMPTY")
        self.label17.clear()
        self.signature_valid = Verify(self.box5.toPlainText(), self.box6.toPlainText(), self.label13.text())
        self.signature_valid.start()
        self.signature_valid.signal1.connect(self.display_signature_valid)
        self.signature_valid.signal2.connect(lambda x: self.label15.setText(x))
        self.label15.clear()


class Verify(QThread):
    signal1 = pyqtSignal(bool)
    signal2 = pyqtSignal(str)

    def __init__(self, data, signature, public_key_filename):
        super(Verify, self).__init__()
        self.data = data
        self.signature = signature
        self.public_key_filename = public_key_filename

    def run(self) -> None:
        with open(self.public_key_filename, "r") as f:
            public_key_string = f.read()
        try:
            public_key = RSA.import_key(public_key_string)
        except ValueError:
            return self.signal2.emit("FAIL: THE PUBLIC KEY IS INVALID")
        verifier = PKCS1_v1_5.new(public_key)
        try:
            valid = verifier.verify(SHA256.new(self.data.encode("utf-8")), base64.b64decode(self.signature))
        except binascii.Error:
            return self.signal2.emit("FAIL: INCORRECT PADDING")
        self.signal1.emit(valid)
        self.signal2.emit("SUCCESS")


class Sign(QThread):
    signal1 = pyqtSignal(str)
    signal2 = pyqtSignal(str)

    def __init__(self, private_key_filename, message):
        super(Sign, self).__init__()
        self.private_key_filename = private_key_filename
        self.message = message

    def run(self) -> None:
        with open(self.private_key_filename, "r") as f:
            private_key_string = f.read()
        try:
            private_key = RSA.import_key(private_key_string)
        except ValueError:
            return self.signal2.emit("FAIL: THE PRIVATE KEY IS INVALID")
        signer = PKCS1_v1_5.new(private_key)
        try:
            signature = signer.sign(SHA256.new(self.message.encode("utf-8")))
        except TypeError:
            return self.signal2.emit("FAIL: THE PRIVATE KEY IS INVALID")
        signature = base64.encodebytes(signature).decode()
        self.signal1.emit(signature)
        self.signal2.emit("SUCCESS")


class Generate(QThread):
    signal1 = pyqtSignal(str)

    def __init__(self, base_directory, filename, n: int = 2048):
        super(Generate, self).__init__()
        self.base_directory = base_directory
        self.filename = filename
        self.n = n

    def run(self) -> None:
        keypair = RSA.generate(self.n)
        private_key = keypair.export_key()
        private_path, public_path = self._get_keypair_filename()
        with open(private_path, "wb") as f:
            f.write(private_key)
        public_key = keypair.public_key().export_key()
        with open(public_path, "wb") as f:
            f.write(public_key)
        self.signal1.emit("SUCCESS")

    def _get_keypair_filename(self):
        return os.path.join(self.base_directory, self.filename), \
               os.path.join(self.base_directory, self.filename + ".pub")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myw = MyWindow()
    myw.show()
    sys.exit(app.exec_())
