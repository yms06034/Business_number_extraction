from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui import Ui_MainWindow
from datetime import datetime

import logic_code as api
import sys
import os
import time

def resource_path(relativa_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relativa_path)

main_ui = Ui_MainWindow()
NAME = "Business Number Extraction"

class SeleniumThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal() 

    def __init__(self, main_window, keyword_list=None):
        super().__init__()
        self.keyword_list = keyword_list
        self.main_window = main_window
        self._running = True

    def run(self):
        if self.keyword_list == []:
            self.log_signal.emit("키워드를 넣어주세요.")

        if all([self.keyword_list]):
            total_iterations = len(self.keyword_list)
            progress_count = 0
            progress = 100 / total_iterations
            self.progress_signal.emit(progress_count)
            try:
                self.log_signal.emit("프로그램을 시작합니다.")
                self.browser = api.open_browser()

                for ka_kw in self.keyword_list:
                    self.log_signal.emit(f"{ka_kw} 키워드로 전화번호 추출을 시작합니다.")
                    result = api.final_logic(self.browser, ka_kw)
                    print("result : ", result)

                    if result == 1:
                        self.log_signal.emit(f"{ka_kw} 키워드로 추출이 완료되었습니다.")
                        self.log_signal.emit(f"{ka_kw} 키워드로 엑셀 저장이 완료되었습니다.")
                        self.log_signal.emit(f"----------------------------")
                        progress_count += progress
                        self.progress_signal.emit(progress_count)
                    elif result == 2:
                        self.log_signal.emit(f"{ka_kw}에서 오류가 발생하였습니다. \t\n프로그램을 다시 돌려주세요.")
                        self.log_signal.emit(f"----------------------------")
                    elif result == 0:
                        self.log_signal.emit(f"{ka_kw}는 검색 결과가 없습니다. 다음 키워드로 넘어갑니다.")
                        progress_count += progress
                        self.progress_signal.emit(progress_count)
                        self.log_signal.emit(f"----------------------------")

                self.browser.quit()

                self.log_signal.emit(f"모든 작업이 완료되었습니다.")
                self.log_signal.emit(f"----------------------------")
            except Exception as e:
                self.log_signal.emit(f"{ka_kw}에서 오류가 발생하였습니다. \t\n{str(e)}")
            finally:
                self.finished_signal.emit()
                    
    def stop(self):
        self._running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        main_ui.setupUi(self)
        self.setWindowTitle(NAME)

        window_ico = resource_path('favicon.ico')
        self.setWindowIcon(QIcon(window_ico))
        self.timer = QTimer(self)
        self.browser = None

        self.keyword_list = []
        self.selenium_thread = None

        main_ui.btn_get_hashtags.clicked.connect(self.btn_get_hashtagsClicked)
        main_ui.btn_clear_hashtags.clicked.connect(self.btn_clear_hashtagsClicked)

        main_ui.btn_add.clicked.connect(self.btn_addClicked) # Txt file Import button
        main_ui.btn_del.clicked.connect(self.btn_delClicked) # Txt file Delete button
        main_ui.hashtag.returnPressed.connect(self.addKeyword)

        main_ui.btn_start.clicked.connect(self.start_btn) # Login Start button

        main_ui.textEdit.setReadOnly(True)

    def addKeyword(self):
        if main_ui.hashtag.text():
            if main_ui.hashtag.text() in self.keyword_list:
                main_ui.hashtag.clear()
                return
            self.keyword_list.append(main_ui.hashtag.text())
            main_ui.hashtags.addItem(main_ui.hashtag.text())
            main_ui.hashtag.clear()
        return

    def btn_addClicked(self):
        self.addKeyword()
        return
    
    def btn_delClicked(self):
        if main_ui.hashtags.currentItem():
            self.keyword_list.remove(self.keyword_list[main_ui.hashtags.currentRow()])
            main_ui.hashtags.takeItem(main_ui.hashtags.currentRow())
        return 

    def btn_get_hashtagsClicked(self):
        path = QFileDialog.getOpenFileNames(self)
        for p in path[0]:
            try:
                if p == '':
                    return
                
                if not p.lower().endswith('.txt'):
                    QMessageBox.information(self, NAME, ".txt 확장자만 넣을 수 있습니다. \t\n파일 확장자를 다시 확인해주세요.")
                
                file = open(p, 'rt', encoding='UTF8')
                while True:
                    line = file.readline()
                    if not line:
                        break
                    elif line == '\n':
                        continue
                    elif line.replace('\n', '') in self.keyword_list:
                        continue
                    main_ui.hashtags.addItem(line.replace('\n', ''))
                    self.keyword_list.append(line.replace('\n', ''))

                file.close()
            except:
                j = p.split('/')[-1]
                QMessageBox.information(self, NAME, f'{j}파일 내용이 잘못되었습니다.')
                return
        return

    def btn_clear_hashtagsClicked(self):
        option = QMessageBox.warning(self, NAME, "정말로 초기화 하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if option == QMessageBox.Yes:
            main_ui.hashtags.clear()
            self.keyword_list.clear()
        return
    
    def start_btn(self):
        try:
            self.selenium_thread = SeleniumThread(self, self.keyword_list)
            self.selenium_thread.log_signal.connect(self.update_log)
            self.selenium_thread.progress_signal.connect(self.update_progress)
            self.selenium_thread.finished_signal.connect(self.thread_finished)
            self.selenium_thread.start()
        except Exception as e:
            print(e)

    def thread_finished(self):  
        self.selenium_thread = None  
    
    def closeEvent(self, event):
        if self.selenium_thread is not None and self.selenium_thread.isRunning():
            self.selenium_thread.stop()
            self.selenium_thread.wait()

    def update_log(self, message):
        main_ui.textEdit.append(message)

    def update_progress(self, value):
        main_ui.progressBar.setValue(value)


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())