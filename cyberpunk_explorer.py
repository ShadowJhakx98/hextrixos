#!/usr/bin/env python3

import os
import sys
import time
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTreeView, QFileSystemModel, QLabel, 
                           QPushButton, QLineEdit, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QSize, QDir
from PyQt5.QtGui import QPalette, QColor, QPainter, QLinearGradient, QFont, QIcon

class GlowingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(40, 40)
        
        # Initialize glow value
        self._glow = 0.0
        
        # Create timer for glow animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_glow)
        self.timer.start(16)  # ~60 FPS
        self.glow_phase = 0.0
        
        # Cyberpunk style
        self.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: #00FFFF;
                border: 2px solid #00FFFF;
                border-radius: 20px;
                font-family: 'Segoe UI';
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00FFFF;
                color: #000000;
            }
        """)
    
    def _update_glow(self):
        # Update glow phase
        self.glow_phase += 0.02
        if self.glow_phase >= 2 * 3.14159:
            self.glow_phase = 0.0
        
        # Calculate new glow value using sine wave
        self._glow = (math.sin(self.glow_phase) + 1) / 2
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._glow > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create glow effect
            glow_size = 20
            gradient = QLinearGradient(0, 0, 0, self.height())
            glow_color = QColor(0, 255, 255, int(255 * self._glow))
            gradient.setColorAt(0, glow_color)
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(self.rect().adjusted(-glow_size, -glow_size, 
                                                       glow_size, glow_size), 
                                  20 + glow_size, 20 + glow_size)

class CyberPathBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        
        # Path input
        self.path_input = QLineEdit()
        self.path_input.setStyleSheet("""
            QLineEdit {
                background-color: #000000;
                color: #00FFFF;
                border: 2px solid #00FFFF;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
        """)
        
        # Navigation buttons
        self.back_btn = GlowingButton("⬅")
        self.forward_btn = GlowingButton("➡")
        self.up_btn = GlowingButton("⬆")
        self.refresh_btn = GlowingButton("⟳")
        
        layout.addWidget(self.back_btn)
        layout.addWidget(self.forward_btn)
        layout.addWidget(self.up_btn)
        layout.addWidget(self.path_input)
        layout.addWidget(self.refresh_btn)
        
        # Cyberpunk style
        self.setStyleSheet("""
            CyberPathBar {
                background-color: #000000;
                border-bottom: 2px solid #00FFFF;
            }
        """)

class CyberExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk File Explorer")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create path bar
        self.path_bar = CyberPathBar()
        layout.addWidget(self.path_bar)
        
        # Create splitter for file system view
        splitter = QSplitter(Qt.Horizontal)
        
        # Create tree view for folders
        self.folder_model = QFileSystemModel()
        self.folder_model.setRootPath("")
        self.folder_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        
        self.folder_view = QTreeView()
        self.folder_view.setModel(self.folder_model)
        self.folder_view.setHeaderHidden(True)
        self.folder_view.setAnimated(True)
        for i in range(1, self.folder_model.columnCount()):
            self.folder_view.hideColumn(i)
            
        # Create tree view for files
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        
        self.file_view = QTreeView()
        self.file_view.setModel(self.file_model)
        self.file_view.setRootIndex(self.file_model.index(""))
        self.file_view.setAnimated(True)
        
        # Add views to splitter
        splitter.addWidget(self.folder_view)
        splitter.addWidget(self.file_view)
        layout.addWidget(splitter)
        
        # Cyberpunk styling for views
        view_style = """
            QTreeView {
                background-color: #000000;
                color: #00FFFF;
                border: 2px solid #00FFFF;
                border-radius: 5px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QTreeView::item {
                padding: 5px;
            }
            QTreeView::item:selected {
                background-color: #00FFFF;
                color: #000000;
            }
            QTreeView::item:hover {
                background-color: #004444;
            }
            QTreeView::branch {
                background-color: #000000;
            }
            QTreeView::branch:has-siblings:!adjoins-item {
                border-image: url(vline.png) 0;
            }
            QTreeView::branch:has-siblings:adjoins-item {
                border-image: url(branch-more.png) 0;
            }
            QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                border-image: url(branch-end.png) 0;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(branch-closed.png);
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(branch-open.png);
            }
        """
        self.folder_view.setStyleSheet(view_style)
        self.file_view.setStyleSheet(view_style)
        
        # Connect signals
        self.folder_view.clicked.connect(self.folder_clicked)
        self.path_bar.path_input.returnPressed.connect(self.path_changed)
        self.path_bar.back_btn.clicked.connect(self.go_back)
        self.path_bar.forward_btn.clicked.connect(self.go_forward)
        self.path_bar.up_btn.clicked.connect(self.go_up)
        self.path_bar.refresh_btn.clicked.connect(self.refresh)
        
        # Initialize history
        self.history = []
        self.current_index = -1
        
        # Set initial directory
        self.set_path(os.path.expanduser("~"))
        
        # Window properties
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def set_path(self, path):
        if os.path.exists(path):
            self.path_bar.path_input.setText(path)
            self.folder_view.setRootIndex(self.folder_model.index(path))
            self.file_view.setRootIndex(self.file_model.index(path))
            
            # Update history
            if self.current_index == -1 or path != self.history[self.current_index]:
                self.current_index += 1
                self.history = self.history[:self.current_index]
                self.history.append(path)
    
    def folder_clicked(self, index):
        path = self.folder_model.filePath(index)
        self.set_path(path)
    
    def path_changed(self):
        new_path = self.path_bar.path_input.text()
        self.set_path(new_path)
    
    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.set_path(self.history[self.current_index])
    
    def go_forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.set_path(self.history[self.current_index])
    
    def go_up(self):
        current_path = self.path_bar.path_input.text()
        parent_path = os.path.dirname(current_path)
        if parent_path != current_path:
            self.set_path(parent_path)
    
    def refresh(self):
        current_path = self.path_bar.path_input.text()
        self.folder_model.setRootPath("")
        self.file_model.setRootPath("")
        self.set_path(current_path)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show the explorer
    explorer = CyberExplorer()
    explorer.show()
    
    sys.exit(app.exec_()) 