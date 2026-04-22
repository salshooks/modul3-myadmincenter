
from PyQt6.QtWidgets import (
    QWidget, QMessageBox )
    
class EditADUserWindow(QWidget):

    def __init__(self, caption, userid):
        super().__init__()
        self.setWindowTitle = caption
        QMessageBox.information(self, "Note", f"Userid:{userid}")