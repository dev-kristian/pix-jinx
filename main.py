# Import necessary modules
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QCheckBox, QLineEdit, QFileDialog, QLabel, QMessageBox, QProgressBar, QGroupBox, QHBoxLayout, QTextEdit, QTabWidget, QGridLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from file_organizer import organize_files_by_date
import logging
import os 

# Custom logging handler that emits logs to a QTextEdit widget
class QTextEditLogger(logging.Handler, QObject):
    append_signal = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)
        self.append_signal.connect(self.widget.append)

    # Emit log messages as signals that can be received by the QTextEdit widget
    def emit(self, record):
        msg = self.format(record)
        self.append_signal.emit(msg)

# Thread to handle file organization without blocking the GUI
class OrganizerThread(QThread):
    progress_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    # Initialize thread with all necessary parameters for file organization
    def __init__(self, source_folder, dest_folder, move_files, delete_files, dry_run, year_only, day_only, month_only, rename_files, skip_existing, maintain_metadata, organize_by_type, ignore_types, organize_by_size, organize_by_name, eliminate_duplicates):
        QThread.__init__(self)
        # Assign parameters to instance variables
        self.source_folder = source_folder
        self.dest_folder = dest_folder
        self.move_files = move_files
        self.delete_files = delete_files
        self.dry_run = dry_run
        self.year_only = year_only
        self.day_only = day_only
        self.month_only = month_only
        self.rename_files = rename_files
        self.skip_existing = skip_existing
        self.maintain_metadata = maintain_metadata
        self.organize_by_type = organize_by_type
        self.ignore_types = ignore_types
        self.organize_by_size = organize_by_size
        self.organize_by_name = organize_by_name
        self.eliminate_duplicates = eliminate_duplicates

    # Run the file organization process in the thread
    def run(self):
        self.start_time = time.time()
        
        # Callback function to update progress
        def progress_callback():
            self.progress += 1
            progress_percentage = (self.progress / self.total_files) * 100
            elapsed_time = time.time() - self.start_time
            estimated_total_time = elapsed_time / (self.progress / self.total_files)
            remaining_time = estimated_total_time - elapsed_time
            it_per_s = self.progress / elapsed_time
            progress_str = f"{progress_percentage:.1f}%|{'█' * int(progress_percentage // 10)}{' ' * (10 - int(progress_percentage // 10))}| {self.progress}/{self.total_files} [{elapsed_time:.0f}s<{remaining_time:.0f}s, {it_per_s:.2f}it/s]"
            self.progress_signal.emit(progress_str)

        self.progress = 0
        self.total_files = sum([len(files) for r, d, files in os.walk(self.source_folder)])

        # Call the file organization function with all parameters
        result = organize_files_by_date(
            self.source_folder,
            self.dest_folder,
            self.move_files,
            self.delete_files,
            self.dry_run,
            self.year_only,
            self.day_only,
            self.month_only,
            self.rename_files,
            self.skip_existing,
            self.maintain_metadata,
            self.organize_by_type,
            self.ignore_types,
            self.organize_by_size,
            self.organize_by_name,
            self.eliminate_duplicates,
            progress_callback
        )

        # Emit log messages for each operation
        for operation, count in result.items():
            self.log_signal.emit(f"Total files {operation}: {count}")

# Main application window
class App(QWidget):
    def __init__(self):
        super().__init__()
        # Set window title and icon
        self.title = 'Pix-Jinx'
        self.setWindowIcon(QIcon('icon.png')) 
        # Set minimum window width
        self.setMinimumWidth(800) 

        # Initialize logger
        self.logTextBox = QTextEditLogger(self)
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.INFO)

        # Initialize user interface
        self.initUI()

    # Initialize user interface
    def initUI(self):
        # Set window title
        self.setWindowTitle(self.title)
        # Set application styles
        self.setStyleSheet("""
            QWidget {
                background-color: #232F34;
            }
            QLabel, QCheckBox {
                color: #D2D7D3;
                font-size: 16px;
            }
            QPushButton {
                background-color: #1E88E5;
                color: #FFFFFF;
                border: none;
                padding: 10px 20px;
                margin: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0D47A1;
            }
            QLineEdit {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #707070;
                padding: 10px;
                margin: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QProgressBar {
                border: 2px solid #1E88E5;
                border-radius: 5px;
                text-align: center;
                color: white; 
            }
            QProgressBar::chunk {
                background-color: #1E88E5;
                width: 20px;
            }
            QGroupBox {
                border: 1px solid #1E88E5;
                border-radius: 5px;
                margin-top: 20px;
                font-size: 18px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #707070;
                padding: 10px;
                margin: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
        """)

        # Initialize main layout
        layout = QVBoxLayout()

        # Initialize tab widget
        self.tab_widget = QTabWidget()

        # Initialize options tab
        self.options_tab = QWidget()
        options_layout = QGridLayout()

        # Initialize progress bar
        self.progress = QProgressBar(self)

        # Initialize folder group box
        folder_group = QGroupBox("Folders")
        folder_layout = QVBoxLayout()

        # Initialize source folder button
        self.source_folder_button = QPushButton('Select Source Folder', self)
        self.source_folder_button.clicked.connect(self.select_source_folder)
        folder_layout.addWidget(self.source_folder_button)

        # Initialize destination folder button
        self.dest_folder_button = QPushButton('Select Destination Folder', self)
        self.dest_folder_button.clicked.connect(self.select_dest_folder)
        folder_layout.addWidget(self.dest_folder_button)

        # Set layout for folder group box
        folder_group.setLayout(folder_layout)

        # Initialize source and destination folder labels
        self.source_folder_label = QLabel(self)
        self.dest_folder_label = QLabel(self)

        # Initialize basic options group box
        basic_options_group = QGroupBox("Basic Options")
        basic_options_layout = QVBoxLayout()

        # Initialize basic option check boxes
        self.move_files_check = QCheckBox('Move files', self)
        basic_options_layout.addWidget(self.move_files_check)

        self.delete_files_check = QCheckBox('Delete files', self)
        basic_options_layout.addWidget(self.delete_files_check)

        self.dry_run_check = QCheckBox('Dry run', self)
        basic_options_layout.addWidget(self.dry_run_check)

        # Set layout for basic options group box
        basic_options_group.setLayout(basic_options_layout)

        # Initialize advanced options group box
        advanced_options_group = QGroupBox("Advanced Options")
        advanced_options_layout = QVBoxLayout()

        # Initialize advanced option check boxes and line edit
        self.rename_files_check = QCheckBox('Rename files', self)
        advanced_options_layout.addWidget(self.rename_files_check)

        self.skip_existing_check = QCheckBox('Skip existing', self)
        advanced_options_layout.addWidget(self.skip_existing_check)

        self.maintain_metadata_check = QCheckBox('Maintain metadata', self)
        advanced_options_layout.addWidget(self.maintain_metadata_check)

        self.ignore_types_entry = QLineEdit(self)
        advanced_options_layout.addWidget(QLabel("Ignore types:"))
        advanced_options_layout.addWidget(self.ignore_types_entry)

        self.eliminate_duplicates_check = QCheckBox('Eliminate duplicates', self)
        advanced_options_layout.addWidget(self.eliminate_duplicates_check)

        # Set layout for advanced options group box
        advanced_options_group.setLayout(advanced_options_layout)

        # Add widgets to options layout
        options_layout.addWidget(folder_group, 0, 0)
        options_layout.addWidget(self.source_folder_label, 1, 0)
        options_layout.addWidget(self.dest_folder_label, 2, 0)
        options_layout.addWidget(basic_options_group, 3, 0)
        options_layout.addWidget(advanced_options_group, 4, 0)

        # Initialize organizing options group box
        organizing_options_group = QGroupBox("Organizing Options")
        organizing_options_layout = QVBoxLayout()

        # Initialize organizing option check boxes
        self.year_only_check = QCheckBox('Year only', self)
        organizing_options_layout.addWidget(self.year_only_check)

        self.day_only_check = QCheckBox('Day only', self)
        organizing_options_layout.addWidget(self.day_only_check)

        self.month_only_check = QCheckBox('Month only', self)
        organizing_options_layout.addWidget(self.month_only_check)

        self.organize_by_type_check = QCheckBox('Organize by type', self)
        organizing_options_layout.addWidget(self.organize_by_type_check)

        self.organize_by_size_check = QCheckBox('Organize by size', self)
        organizing_options_layout.addWidget(self.organize_by_size_check)

        self.organize_by_name_check = QCheckBox('Organize by name', self)
        organizing_options_layout.addWidget(self.organize_by_name_check)

        # Set layout for organizing options group box
        organizing_options_group.setLayout(organizing_options_layout)

        # Add widgets to options layout
        options_layout.addWidget(organizing_options_group, 0, 1, 5, 1)
        options_layout.addWidget(self.progress, 5, 0, 1, 2)

        # Initialize organize button
        self.organize_button = QPushButton('Organize', self)
        self.organize_button.clicked.connect(self.organize_files)
        options_layout.addWidget(self.organize_button, 6, 0, 1, 2)

        # Add spacer to options layout
        options_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 7, 0, 1, 2)

        # Set layout for options tab
        self.options_tab.setLayout(options_layout)
        self.tab_widget.addTab(self.options_tab, "Options")

        # Initialize log tab
        self.log_tab = QWidget()
        log_layout = QVBoxLayout()

        # Initialize log screen
        self.log_screen = QTextEdit(self)
        self.log_screen.setReadOnly(True)
        log_layout.addWidget(QLabel("Log:"))
        log_layout.addWidget(self.logTextBox.widget)

        # Set layout for log tab
        self.log_tab.setLayout(log_layout)
        self.tab_widget.addTab(self.log_tab, "Log")

        # Add tab widget to main layout
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    # Function to select source folder
    def select_source_folder(self):
        self.source_folder = QFileDialog.getExistingDirectory(self, 'Select Source Folder')
        self.source_folder_label.setText(f"Selected source folder: {self.source_folder}")

    # Function to select destination folder
    def select_dest_folder(self):
        self.dest_folder = QFileDialog.getExistingDirectory(self, 'Select Destination Folder')
        self.dest_folder_label.setText(f"Selected destination folder: {self.dest_folder}")

    # Function to start file organization
    def organize_files(self):
        # Check if source and destination folders have been selected
        if not hasattr(self, 'source_folder'):
            QMessageBox.critical(self, "Error", "Please select a source folder.")
            return
        if not hasattr(self, 'dest_folder'):
            QMessageBox.critical(self, "Error", "Please select a destination folder.")
            return

        # Get ignore types from line edit
        ignore_types = self.ignore_types_entry.text().split()
        self.progress.setValue(0)
        # Initialize and start organizer thread
        self.organizer_thread = OrganizerThread(
            self.source_folder,
            self.dest_folder,
            self.move_files_check.isChecked(),
            self.delete_files_check.isChecked(),
            self.dry_run_check.isChecked(),
            self.year_only_check.isChecked(),
            self.day_only_check.isChecked(),
            self.month_only_check.isChecked(),
            self.rename_files_check.isChecked(),
            self.skip_existing_check.isChecked(),
            self.maintain_metadata_check.isChecked(),
            self.organize_by_type_check.isChecked(),
            ignore_types,
            self.organize_by_size_check.isChecked(),
            self.organize_by_name_check.isChecked(),
            self.eliminate_duplicates_check.isChecked()
        )
        self.organizer_thread.progress_signal.connect(self.progress.setFormat)
        self.organizer_thread.log_signal.connect(self.logTextBox.append_signal.emit)
        self.organizer_thread.start()

# Main function to start the application
def main():
    app = QApplication([])
    ex = App()
    ex.show()
    app.exec_()

# Start the application if the script is run directly
if __name__ == "__main__":
    main()
