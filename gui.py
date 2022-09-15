from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from ui import Ui_SamgovBot
from main import search_by_keyword, search_by_filters, search_by_all


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowTitle("Samgov Bot")
        self.setGeometry(50, 50, 300, 300)
        self.ui = Ui_SamgovBot()

        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.ui.start_btn.clicked.connect(self.start_scraping)




    def start_scraping(self):
        try:
            domain = None
            notice = None
            aside = None
            start_date = None
            end_date = None
            specified_naics = self.ui.custom_naics.text() if self.ui.specify_naics.isChecked() else None
            keyword = self.ui.keyword_input.text()
            if self.ui.filters__checkbox.isChecked() and self.ui.keyword__checkbox.isChecked():
                domain = self.ui.domain_select.currentText()
                aside = self.ui.aside_select.currentText()
                notice = self.ui.notice_select.currentText()
                if self.ui.date_filter.isChecked():
                    start_date = self.ui.start_date.selectedDate().getDate()
                    end_date = self.ui.end_date.selectedDate().getDate()
                if not start_date:
                    search_by_all(custom_naics=specified_naics, keyword=keyword, domain=domain, aside=aside, notice=notice, start_date=None, end_date=None)
                else:
                    search_by_all(custom_naics=specified_naics, keyword=keyword, domain=domain, aside=aside, notice=notice, start_date=f"{start_date[0]}-{start_date[1]:02d}-{start_date[2]:02d}", end_date=f"{end_date[0]}-{end_date[1]:02d}-{end_date[2]:02d}")

            elif self.ui.filters__checkbox.isChecked():
                domain = self.ui.domain_select.currentText()
                aside = self.ui.aside_select.currentText()
                notice = self.ui.notice_select.currentText()
                if self.ui.date_filter.isChecked():
                    start_date = self.ui.start_date.selectedDate().getDate()
                    end_date = self.ui.end_date.selectedDate().getDate()
                if not start_date:
                    search_by_filters(domain=domain, aside=aside, notice=notice, start_date=None, end_date=None)
                else:
                    search_by_filters(domain=domain, aside=aside, notice=notice, start_date=f"{start_date[0]}-{start_date[1]:02d}-{start_date[2]:02d}", end_date=f"{end_date[0]}-{end_date[1]:02d}-{end_date[2]:02d}")

            elif self.ui.keyword__checkbox.isChecked():
                keyword = self.ui.keyword_input.text()
                search_by_keyword(keyword)
        except Exception as e:
            print(e)



def window():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    window()
