from sys import stderr, exit, argv
import socket
import argparse
from PySide6.QtWidgets import *
import dialog

def create_line_edit():
    """
    create QLineEdit objects
    """
    lineedit = QLineEdit()
    lineedit.setFixedSize(250, 20)
    return lineedit


def create_windows():
    """
    create a GUI window to receive user input
    """
    app = QApplication(argv)

    # create line edit
    dept_line_edit = create_line_edit()
    course_line_edit = create_line_edit()
    sub_line_edit = create_line_edit()
    title_line_edit = create_line_edit()

    h_layout = QHBoxLayout()
    form_layout1 = QFormLayout()
    form_layout2 = QFormLayout()
    form_layout1.addRow('Department', dept_line_edit)
    form_layout1.addRow('Subject', sub_line_edit)
    form_layout2.addRow('Course Number', course_line_edit)
    form_layout2.addRow('Title', title_line_edit)
    h_layout.addLayout(form_layout1)
    h_layout.addLayout(form_layout2)

    def button_click():
        query = ""
        check = False
        if dept_line_edit.text():
            check = True
            query += "dept:" + str(dept_line_edit.text()) + "##"

        if course_line_edit.text():
            check = True
            query += "coursenum:" + str(course_line_edit.text()) + "##"

        if sub_line_edit.text():
            check = True
            query += "subject:" + str(sub_line_edit.text()) + "##"

        if title_line_edit.text():
            check = True
            query += "title:" + str(title_line_edit.text()) + "##"

        query += "\n"

        if not check:
            query = " \n"

        output = connection(query, window)
        if output is not None:
            listwidget.clear()
            for i in range(2, len(output)):
                output[i] = output[i].replace("\n", "")
                listwidget.insertItem(i-2, output[i])
        else:
            listwidget.clear()

    def on_double_clicked(item):
        """
        handles double click for course detail
        """

        item_text = item.text()
        query = "crn:"
        query += str(item_text).split(' ', maxsplit=1)[0] + "\n"

        result = connection(query, window)
        message = "".join(result)

        dialog_box = dialog.FixedWidthMessageDialog(
            "Details for class ", message)
        dialog_box.exec()

    button = QPushButton('Submit Query')
    button.clicked.connect(button_click)

    listwidget = QListWidget()
    listwidget.setFont(dialog.FW_FONT)
    listwidget.itemActivated.connect(on_double_clicked)

    v_layout = QVBoxLayout()
    v_layout.addLayout(h_layout)
    v_layout.addWidget(button)
    v_layout.addWidget(listwidget)

    frame = QFrame()
    frame.setLayout(v_layout)

    window = QMainWindow()
    window.setWindowTitle('Registrar Application')
    window.setCentralWidget(frame)
    screen_size = app.primaryScreen().availableGeometry()
    window.resize(screen_size.width()//2, screen_size.height()//2)
    window.show()
    exit(app.exec())

reconnect = 0

def connection(query, window):
    """
    handles user input
    """

    global reconnect

    host = str(argv[1])
    port = int(argv[2])

    try:
        client_socket = socket.socket()
        client_socket.connect((host, port))

        out_flo = client_socket.makefile(mode='w', encoding='utf-8')
        out_flo.write(query)
        out_flo.flush()

        flo = client_socket.makefile(mode='r', encoding='utf-8')
        res = flo.readlines()
        reconnect = 0

        return res

    except Exception as ex:
        reconnect += 1
        error_message = QErrorMessage(window)
        error_message.showMessage(str(ex))

        print(ex, file=stderr)
        if reconnect == 5:
            exit(1)


def main():
    """
    main function to initiate GUI
    """

    parser = argparse.ArgumentParser(
        allow_abbrev=False, description='Server for the registrar application')

    parser.add_argument('host',
                        type=str,
                        nargs=1,
                        help='the host on which the server is running')
    parser.add_argument('port',
                        type=int,
                        nargs=1,
                        help='the port at which the server should listen')

    parser.parse_args()
    create_windows()


if __name__ == "__main__":
    main()
