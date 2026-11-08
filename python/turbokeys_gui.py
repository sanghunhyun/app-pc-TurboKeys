#!/usr/bin/env python3
"""
Turbo Keys GUI - Modern Cross-Platform Keypad Configurator
Powered by PyQt6 & turbokeys HID engine.
"""

import sys
import json
import os
from typing import Dict, Optional, Tuple

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QCheckBox, QTabWidget,
    QGroupBox, QDialog, QMessageBox, QFileDialog, QFrame, QScrollArea,
    QStackedLayout, QGraphicsDropShadowEffect, QSizePolicy
)

# Import backend engine
try:
    from turbokeys import (
        MiniKeyboard, KeyType, Modifier, KEYCODES, MEDIA_KEYCODES,
        PHYSICAL_KEYS, parse_key_combo, VENDOR_ID, PRODUCT_IDS
    )
except ImportError:
    # If running from script directory directly
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from turbokeys import (
        MiniKeyboard, KeyType, Modifier, KEYCODES, MEDIA_KEYCODES,
        PHYSICAL_KEYS, parse_key_combo, VENDOR_ID, PRODUCT_IDS
    )

# High Contrast Modern Dark Theme Stylesheet
STYLESHEET = """
QMainWindow, QDialog, QMessageBox {
    background-color: #0E1017;
    color: #F8FAFC;
}

QWidget {
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    color: #F8FAFC;
}

QFrame#card {
    background-color: #171925;
    border: 1px solid #2D3248;
    border-radius: 12px;
}

QFrame#subcard {
    background-color: #1E2235;
    border: 1px solid #2D3248;
    border-radius: 8px;
}

QLabel {
    color: #F8FAFC;
}

QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #FFFFFF;
}

QLabel#subtitleLabel {
    font-size: 13px;
    color: #CBD5E1;
    font-weight: 500;
}

QLabel#statusText {
    font-size: 13px;
    font-weight: 700;
}

/* Tab Widget Styling */
QTabWidget::pane {
    border: 1px solid #3B4262;
    background-color: #171925;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
    border-top-right-radius: 12px;
}

QTabBar::tab {
    background-color: #1E2235;
    color: #CBD5E1;
    padding: 10px 24px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    font-weight: 600;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #171925;
    color: #00F0FF;
    border: 1px solid #3B4262;
    border-bottom: 2px solid #00F0FF;
}

QTabBar::tab:hover:!selected {
    background-color: #282E47;
    color: #FFFFFF;
}

/* Key Buttons */
QPushButton.keyBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #252A40, stop:1 #1A1D2C);
    border: 2px solid #3B4262;
    border-radius: 12px;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: bold;
    padding: 8px;
}

QPushButton.keyBtn:hover {
    border: 2px solid #00F0FF;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2E3552, stop:1 #202438);
    color: #FFFFFF;
}

QPushButton.keyBtn:pressed {
    background-color: #00F0FF;
    color: #0E1017;
}

QPushButton.knobBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #32264D, stop:1 #1E1B30);
    border: 2px solid #7C3AED;
    border-radius: 10px;
    color: #F3E8FF;
    font-size: 12px;
    font-weight: bold;
}

QPushButton.knobBtn:hover {
    border: 2px solid #C084FC;
    background: #4C3775;
    color: #FFFFFF;
}

/* Action Buttons */
QPushButton.primaryBtn {
    background-color: #00F0FF;
    color: #0B0E14;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-size: 13px;
}

QPushButton.primaryBtn:hover {
    background-color: #33F3FF;
    color: #000000;
}

QPushButton.primaryBtn:disabled {
    background-color: #2D3248;
    color: #94A3B8;
}

QPushButton.secondaryBtn {
    background-color: #252A40;
    color: #FFFFFF;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton.secondaryBtn:hover {
    background-color: #323854;
    border: 1px solid #00F0FF;
    color: #00F0FF;
}

/* Form Controls (ComboBox, LineEdit, CheckBox) */
QComboBox, QLineEdit {
    background-color: #1E2235;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 8px 12px;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 500;
}

QComboBox:hover, QLineEdit:hover {
    border-color: #00F0FF;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* QComboBox Popup List (Crucial for Contrast & Zero Truncation) */
QComboBox QAbstractItemView {
    background-color: #1E2235;
    color: #FFFFFF;
    border: 1.5px solid #00F0FF;
    selection-background-color: #00F0FF;
    selection-color: #0E1017;
    outline: none;
    padding: 6px;
    border-radius: 6px;
    min-width: 420px;
}

QComboBox QAbstractItemView::item {
    min-height: 32px;
    color: #F8FAFC;
    padding-left: 8px;
}

QComboBox QAbstractItemView::item:hover,
QComboBox QAbstractItemView::item:selected {
    background-color: #00F0FF;
    color: #0E1017;
    font-weight: bold;
}

QCheckBox {
    spacing: 8px;
    color: #F1F5F9;
    font-weight: 600;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1.5px solid #64748B;
    background-color: #1E2235;
}

QCheckBox::indicator:hover {
    border-color: #00F0FF;
}

QCheckBox::indicator:checked {
    background-color: #00F0FF;
    border-color: #00F0FF;
}

QGroupBox {
    border: 1px solid #3B4262;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: bold;
    color: #00F0FF;
    font-size: 13px;
}

/* Scrollbar Styling */
QScrollBar:vertical {
    background: #171925;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #3B4262;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #00F0FF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

REVERSE_KEYCODES = {v: k.upper() for k, v in KEYCODES.items()}
REVERSE_MEDIA = {v: k.upper() for k, v in MEDIA_KEYCODES.items()}


class KeyConfigDialog(QDialog):
    """Dialog for configuring a physical key mapping"""

    def __init__(self, key_id: int, key_name: str, current_config: dict, parent=None):
        super().__init__(parent)
        self.key_id = key_id
        self.key_name = key_name
        self.current_config = current_config or {}
        self.result_config = self.current_config.copy()

        self.setWindowTitle(f"Configure {key_name} (Physical Key {key_id})")
        self.setMinimumWidth(480)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Header
        header = QLabel(f"⚙️ Key Configuration: {self.key_name}")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00F0FF;")
        layout.addWidget(header)

        # Tabs for key types
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 1. Basic Key Tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)

        # Modifiers Group
        mod_group = QGroupBox("Modifiers")
        mod_layout = QGridLayout(mod_group)
        self.cb_ctrl = QCheckBox("Ctrl")
        self.cb_shift = QCheckBox("Shift")
        self.cb_alt = QCheckBox("Alt")
        self.cb_win = QCheckBox("Win / Super")

        mod_layout.addWidget(self.cb_ctrl, 0, 0)
        mod_layout.addWidget(self.cb_shift, 0, 1)
        mod_layout.addWidget(self.cb_alt, 1, 0)
        mod_layout.addWidget(self.cb_win, 1, 1)
        basic_layout.addWidget(mod_group)

        # Keycode selector
        key_select_layout = QHBoxLayout()
        key_select_layout.addWidget(QLabel("Primary Key:"))
        self.key_combo = QComboBox()
        self.key_combo.addItems(sorted([k.upper() for k in KEYCODES.keys()]))
        key_select_layout.addWidget(self.key_combo)
        basic_layout.addLayout(key_select_layout)

        self.tabs.addTab(basic_tab, "⌨️ Keyboard Key")

        # 2. Media Key Tab
        media_tab = QWidget()
        media_layout = QVBoxLayout(media_tab)
        media_layout.addWidget(QLabel("Select Media Function:"))
        self.media_combo = QComboBox()
        self.media_combo.addItems([
            "VOLUMEUP", "VOLUMEDOWN", "MUTE",
            "PLAYPAUSE", "NEXT", "PREVIOUS", "STOP"
        ])
        media_layout.addWidget(self.media_combo)
        media_layout.addStretch()
        self.tabs.addTab(media_tab, "🎵 Media Key")

        # Load Current Config into UI
        cfg_type = self.current_config.get("type", "basic")
        if cfg_type == "media":
            self.tabs.setCurrentIndex(1)
            med_name = self.current_config.get("name", "VOLUMEUP")
            idx = self.media_combo.findText(med_name.upper())
            if idx >= 0:
                self.media_combo.setCurrentIndex(idx)
        else:
            self.tabs.setCurrentIndex(0)
            mods = self.current_config.get("modifiers", 0)
            self.cb_ctrl.setChecked(bool(mods & Modifier.CTRL))
            self.cb_shift.setChecked(bool(mods & Modifier.SHIFT))
            self.cb_alt.setChecked(bool(mods & Modifier.ALT))
            self.cb_win.setChecked(bool(mods & Modifier.WIN))

            key_name = self.current_config.get("key_name", "A")
            idx = self.key_combo.findText(key_name.upper())
            if idx >= 0:
                self.key_combo.setCurrentIndex(idx)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Apply Mapping")
        save_btn.setProperty("class", "primaryBtn")
        save_btn.clicked.connect(self.on_save)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def on_save(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            # Basic Key
            mods = 0
            if self.cb_ctrl.isChecked(): mods |= Modifier.CTRL
            if self.cb_shift.isChecked(): mods |= Modifier.SHIFT
            if self.cb_alt.isChecked(): mods |= Modifier.ALT
            if self.cb_win.isChecked(): mods |= Modifier.WIN

            key_name = self.key_combo.currentText().lower()
            keycode = KEYCODES.get(key_name, 4)

            # Format display label
            mod_strs = []
            if mods & Modifier.CTRL: mod_strs.append("Ctrl")
            if mods & Modifier.SHIFT: mod_strs.append("Shift")
            if mods & Modifier.ALT: mod_strs.append("Alt")
            if mods & Modifier.WIN: mod_strs.append("Win")
            
            label_parts = mod_strs + [key_name.upper()]
            display_label = "+".join(label_parts)

            self.result_config = {
                "type": "basic",
                "keycode": keycode,
                "modifiers": mods,
                "key_name": key_name.upper(),
                "display": display_label
            }
        else:
            # Media Key
            media_name = self.media_combo.currentText().lower()
            media_code = MEDIA_KEYCODES.get(media_name, 233)

            self.result_config = {
                "type": "media",
                "media_code": media_code,
                "name": media_name.upper(),
                "display": f"🎵 {media_name.upper()}"
            }

        self.accept()


class MainWindow(QMainWindow):
    """Main Application Window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DIY Keys - Macro Keypad Manager")
        self.setMinimumSize(840, 540)
        self.setStyleSheet(STYLESHEET)
        self.kb = MiniKeyboard()

        # Configuration state: { key_id: config_dict }
        self.mappings: Dict[int, dict] = {}

        self.init_ui()

        # Timer for non-blocking HID connection monitoring
        self.conn_timer = QTimer(self)
        self.conn_timer.setInterval(2000)
        self.conn_timer.timeout.connect(self.check_device_connection)
        self.conn_timer.start()

        self.check_device_connection()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        # 1. Top Header Bar
        header_card = QFrame()
        header_card.setObjectName("card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_vbox = QVBoxLayout()
        title = QLabel("⚡ DIY Keys Configurator")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Cross-Platform Custom Keypad Manager")
        subtitle.setObjectName("subtitleLabel")
        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        header_layout.addLayout(title_vbox)

        header_layout.addStretch()

        # Connection status badge
        self.status_badge = QFrame()
        self.status_badge.setObjectName("subcard")
        badge_layout = QHBoxLayout(self.status_badge)
        badge_layout.setContentsMargins(12, 6, 12, 6)

        self.status_icon = QLabel("🔴")
        self.status_label = QLabel("Device Disconnected")
        self.status_label.setObjectName("statusText")
        
        self.connect_btn = QPushButton("Refresh")
        self.connect_btn.setProperty("class", "secondaryBtn")
        self.connect_btn.clicked.connect(self.check_device_connection)

        badge_layout.addWidget(self.status_icon)
        badge_layout.addWidget(self.status_label)
        badge_layout.addWidget(self.connect_btn)

        header_layout.addWidget(self.status_badge)
        main_layout.addWidget(header_card)

        # 2. Main Content Split: Product Visual (Left) & Controls (Right)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # 2A. Left Card: Product Visual Preview
        left_card = QFrame()
        left_card.setObjectName("card")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)

        visual_title = QLabel("🖼️ Hardware Preview")
        visual_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #00F0FF;")
        left_layout.addWidget(visual_title)

        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setStyleSheet("border-radius: 8px; background-color: #0B0E14; padding: 6px;")

        # Load clean product image
        prod_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "diy_keys_product.jpg")
        if os.path.exists(prod_img_path):
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(prod_img_path)
            scaled = pixmap.scaledToWidth(250, Qt.TransformationMode.SmoothTransformation)
            self.img_label.setPixmap(scaled)
        else:
            self.img_label.setText("DIY Keys Hardware")

        left_layout.addWidget(self.img_label)
        left_layout.addStretch()

        content_layout.addWidget(left_card, stretch=1)

        # 2B. Right Card: Interactive Keys (Key 1..3 & Knob 1)
        right_card = QFrame()
        right_card.setObjectName("card")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(12)

        # Keys Grid
        keypad_group = QGroupBox("⌨️ Mechanical Keys (1 - 3)")
        keypad_grid = QGridLayout(keypad_group)
        keypad_grid.setSpacing(10)

        self.key_buttons: Dict[int, QPushButton] = {}

        # 3 Physical Keys
        for i in range(3):
            key_id = i + 1
            btn = QPushButton(f"Key {key_id}\n(Empty)")
            btn.setProperty("class", "keyBtn")
            btn.setFixedSize(115, 80)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, k=key_id: self.open_key_config(k))

            keypad_grid.addWidget(btn, 0, i)
            self.key_buttons[key_id] = btn

        right_layout.addWidget(keypad_group)

        # Knob Group
        knob_group = QGroupBox("🎛️ Rotary Knob 1 Controls")
        knob_layout = QVBoxLayout(knob_group)
        knob_layout.setSpacing(8)
        knob_layout.setContentsMargins(12, 12, 12, 12)

        knob_definitions = [
            ("Knob 1 ↺ (Counter-Clockwise)", 13, "#C084FC"),
            ("Knob 1 🔘 (Press / Click)", 14, "#00F0FF"),
            ("Knob 1 ↻ (Clockwise)", 15, "#38BDF8"),
        ]

        for label_text, key_id, color_code in knob_definitions:
            k_row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"font-weight: 600; font-size: 12px; color: {color_code};")
            btn = QPushButton("Not Configured")
            btn.setProperty("class", "knobBtn")
            btn.setFixedHeight(36)
            btn.setMinimumWidth(160)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, k=key_id: self.open_key_config(k))

            k_row.addWidget(lbl, stretch=1)
            k_row.addWidget(btn, stretch=1)
            knob_layout.addLayout(k_row)
            self.key_buttons[key_id] = btn

        right_layout.addWidget(knob_group)
        content_layout.addWidget(right_card, stretch=2)

        main_layout.addLayout(content_layout)

        # 3. Global Device Controls Bar (LED, Presets, Profiles, Flashing)
        bottom_card = QFrame()
        bottom_card.setObjectName("subcard")
        bottom_layout = QHBoxLayout(bottom_card)
        bottom_layout.setContentsMargins(14, 10, 14, 10)
        bottom_layout.setSpacing(10)

        # Presets Selector
        preset_lbl = QLabel("🎯 Presets:")
        preset_lbl.setStyleSheet("font-weight: bold; color: #00F0FF; font-size: 12px;")
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(260)
        self.preset_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.preset_combo.addItems([
            "⚡ Select 3-Key Preset...",
            "📋 Office: [Ctrl+C] [Ctrl+V] [Win+Shift+S] | Knob: Vol",
            "🎵 Media: [Play/Pause] [Mute] [Next] | Knob: Vol",
            "🎨 Graphics: [Ctrl+Z Undo] [Ctrl+Y Redo] [Ctrl+J Dup] | Knob: Vol",
            "💻 Developer: [F5 Run] [F10 Step] [Ctrl+/ Comment] | Knob: Vol"
        ])
        # Ensure dropdown popup list is wide enough so text is never truncated
        self.preset_combo.view().setMinimumWidth(420)
        self.preset_combo.currentIndexChanged.connect(self.apply_preset)

        bottom_layout.addWidget(preset_lbl)
        bottom_layout.addWidget(self.preset_combo)

        # LED Control
        led_lbl = QLabel("💡 LED:")
        led_lbl.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.led_combo = QComboBox()
        self.led_combo.addItems(["0: Off", "1: Static", "2: Breathing", "3: Reactive"])
        apply_led_btn = QPushButton("Set LED")
        apply_led_btn.setProperty("class", "secondaryBtn")
        apply_led_btn.clicked.connect(self.apply_led_mode)

        bottom_layout.addWidget(led_lbl)
        bottom_layout.addWidget(self.led_combo)
        bottom_layout.addWidget(apply_led_btn)

        bottom_layout.addStretch()

        # Preset Save / Load Buttons
        load_btn = QPushButton("📂 Load")
        load_btn.setProperty("class", "secondaryBtn")
        load_btn.clicked.connect(self.load_profile)

        save_btn = QPushButton("💾 Save")
        save_btn.setProperty("class", "secondaryBtn")
        save_btn.clicked.connect(self.save_profile)

        bottom_layout.addWidget(load_btn)
        bottom_layout.addWidget(save_btn)

        # Flash Button
        write_all_btn = QPushButton("🚀 Flash to Hardware")
        write_all_btn.setProperty("class", "primaryBtn")
        write_all_btn.setFixedHeight(36)
        write_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        write_all_btn.clicked.connect(self.write_all_to_device)
        bottom_layout.addWidget(write_all_btn)

        main_layout.addWidget(bottom_card)

    def create_layer_page(self, layer_id: int) -> QWidget:
        """Create an integrated page layout for a single layer"""
        page = QWidget()
        page_layout = QHBoxLayout(page)
        page_layout.setContentsMargins(16, 16, 16, 16)
        page_layout.setSpacing(20)

        # Left Box: Keypad Matrix (1 - 12)
        keypad_group = QGroupBox(f"⌨️ Layer {layer_id} Key Matrix (Keys 1 - 12)")
        keypad_grid = QGridLayout(keypad_group)
        keypad_grid.setSpacing(10)

        if not hasattr(self, 'layer_key_buttons'):
            self.layer_key_buttons = {1: {}, 2: {}, 3: {}}

        # 3x4 Grid for Keys 1-12
        for i in range(12):
            key_id = i + 1
            btn = QPushButton(f"Key {key_id}\n(Empty)")
            btn.setProperty("class", "keyBtn")
            btn.setFixedSize(110, 80)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, k=key_id: self.open_key_config(k))

            row = i // 3
            col = i % 3
            keypad_grid.addWidget(btn, row, col)
            self.layer_key_buttons[layer_id][key_id] = btn

        page_layout.addWidget(keypad_group, stretch=2)

        # Right Box: Compact Tabbed Knob Controls (Knob 1, 2, 3)
        knob_group = QGroupBox(f"🎛️ Layer {layer_id} Knob Controls")
        knob_group_layout = QVBoxLayout(knob_group)
        knob_group_layout.setContentsMargins(10, 14, 10, 10)

        knob_subtabs = QTabWidget()
        knob_subtabs.setStyleSheet("""
            QTabBar::tab { padding: 6px 14px; font-size: 11px; }
            QTabWidget::pane { border: 1px solid #3B4262; background-color: #1E2235; border-radius: 6px; }
        """)

        # Helper to populate a knob tab page
        def populate_knob_page(defs: list, color_code: str) -> QWidget:
            k_page = QWidget()
            k_layout = QVBoxLayout(k_page)
            k_layout.setContentsMargins(12, 12, 12, 12)
            k_layout.setSpacing(8)

            for label_text, key_id in defs:
                k_row = QHBoxLayout()
                lbl = QLabel(label_text)
                lbl.setStyleSheet(f"font-weight: 600; font-size: 11px; color: {color_code};")
                btn = QPushButton("Not Configured")
                btn.setProperty("class", "knobBtn")
                btn.setFixedHeight(34)
                btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn.clicked.connect(lambda checked, k=key_id: self.open_key_config(k))

                k_row.addWidget(lbl, stretch=1)
                k_row.addWidget(btn, stretch=1)
                k_layout.addLayout(k_row)
                self.layer_key_buttons[layer_id][key_id] = btn

            k_layout.addStretch()
            return k_page

        knob1_defs = [("↺ CCW", 13), ("🔘 Click", 14), ("↻ CW", 15)]
        knob2_defs = [("↺ CCW", 16), ("🔘 Click", 17), ("↻ CW", 18)]
        knob3_defs = [("↺ CCW", 19), ("🔘 Click", 20), ("↻ CW", 21)]

        knob_subtabs.addTab(populate_knob_page(knob1_defs, "#C084FC"), "Knob 1")
        knob_subtabs.addTab(populate_knob_page(knob2_defs, "#F472B6"), "Knob 2")
        knob_subtabs.addTab(populate_knob_page(knob3_defs, "#38BDF8"), "Knob 3")

        knob_group_layout.addWidget(knob_subtabs)
        page_layout.addWidget(knob_group, stretch=1)

        return page

    def check_device_connection(self):
        """Poll and update device status badge"""
        if self.kb.is_connected():
            return

        connected = self.kb.connect()
        if connected:
            self.status_icon.setText("🟢")
            self.status_label.setText(f"Connected (Report ID: {self.kb.report_id})")
            self.status_label.setStyleSheet("color: #4ADE80;")
        else:
            self.status_icon.setText("🔴")
            self.status_label.setText("Keypad Not Found")
            self.status_label.setStyleSheet("color: #F87171;")

    def update_key_buttons_ui(self):
        """Update display labels of 3 keys and Knob 1 controls"""
        if not hasattr(self, 'key_buttons'):
            return

        for key_id, btn in self.key_buttons.items():
            cfg = self.mappings.get(key_id)
            if cfg:
                display_txt = cfg.get("display", "Configured")
                if key_id <= 3:
                    btn.setText(f"Key {key_id}\n[{display_txt}]")
                    btn.setStyleSheet("border-color: #00F0FF; background-color: #1E293B; color: #00F0FF;")
                else:
                    btn.setText(f"[{display_txt}]")
                    btn.setStyleSheet("border: 1.5px solid #00F0FF; background-color: #2E1B4E; color: #FFFFFF; font-weight: bold;")
            else:
                if key_id <= 3:
                    btn.setText(f"Key {key_id}\n(Empty)")
                    btn.setStyleSheet("")
                else:
                    btn.setText("Not Configured")
                    btn.setStyleSheet("")

    def open_key_config(self, key_id: int):
        knob_names = {
            13: "Knob 1 CCW ↺", 14: "Knob 1 Click 🔘", 15: "Knob 1 CW ↻"
        }
        key_name = f"Key {key_id}" if key_id <= 3 else knob_names.get(key_id, f"Knob ({key_id})")
        cur_cfg = self.mappings.get(key_id, {})

        dlg = KeyConfigDialog(key_id, key_name, cur_cfg, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            config = dlg.result_config
            self.mappings[key_id] = config
            self.update_key_buttons_ui()

            # Instantly write single key if connected
            self.write_single_key_to_device(key_id, config)

    def write_single_key_to_device(self, key_id: int, config: dict):
        if not self.kb.is_connected():
            return

        cfg_type = config.get("type", "basic")
        if cfg_type == "basic":
            self.kb.set_basic_key(
                physical_key=key_id,
                keycode=config.get("keycode", 4),
                modifiers=config.get("modifiers", 0),
                layer=1
            )
        elif cfg_type == "media":
            self.kb.set_media_key(
                physical_key=key_id,
                media_keycode=config.get("media_code", 233),
                layer=1
            )

    def write_all_to_device(self):
        if not self.kb.is_connected():
            if not self.kb.connect():
                QMessageBox.critical(self, "Error", "No macro keypad device detected. Please connect your USB keypad.")
                return

        written_count = 0
        for key_id, config in self.mappings.items():
            cfg_type = config.get("type", "basic")
            if cfg_type == "basic":
                self.kb.set_basic_key(
                    physical_key=key_id,
                    keycode=config.get("keycode", 4),
                    modifiers=config.get("modifiers", 0),
                    layer=1
                )
                written_count += 1
            elif cfg_type == "media":
                self.kb.set_media_key(
                    physical_key=key_id,
                    media_keycode=config.get("media_code", 233),
                    layer=1
                )
                written_count += 1

        QMessageBox.information(self, "Success", f"Successfully flashed {written_count} key mapping(s) to 3-Key keypad memory!")

    def apply_preset(self, index: int):
        if index == 0:
            return

        if index == 1:
            # 📋 Office Work (Copy, Paste, Capture + Vol)
            self.mappings = {
                1: {"type": "basic", "keycode": KEYCODES['c'], "modifiers": Modifier.CTRL, "key_name": "C", "display": "Ctrl+C"},
                2: {"type": "basic", "keycode": KEYCODES['v'], "modifiers": Modifier.CTRL, "key_name": "V", "display": "Ctrl+V"},
                3: {"type": "basic", "keycode": KEYCODES['s'], "modifiers": Modifier.WIN | Modifier.SHIFT, "key_name": "S", "display": "Win+Shift+S"},
                13: {"type": "media", "media_code": MEDIA_KEYCODES['voldown'], "name": "VOLDOWN", "display": "🎵 VOLDOWN"},
                14: {"type": "media", "media_code": MEDIA_KEYCODES['mute'], "name": "MUTE", "display": "🎵 MUTE"},
                15: {"type": "media", "media_code": MEDIA_KEYCODES['volup'], "name": "VOLUP", "display": "🎵 VOLUP"},
            }
        elif index == 2:
            # 🎵 Media Player (Play/Pause, Mute, Next + Vol)
            self.mappings = {
                1: {"type": "media", "media_code": MEDIA_KEYCODES['playpause'], "name": "PLAYPAUSE", "display": "🎵 PLAYPAUSE"},
                2: {"type": "media", "media_code": MEDIA_KEYCODES['mute'], "name": "MUTE", "display": "🎵 MUTE"},
                3: {"type": "media", "media_code": MEDIA_KEYCODES['next'], "name": "NEXT", "display": "🎵 NEXT"},
                13: {"type": "media", "media_code": MEDIA_KEYCODES['voldown'], "name": "VOLDOWN", "display": "🎵 VOLDOWN"},
                14: {"type": "media", "media_code": MEDIA_KEYCODES['playpause'], "name": "PLAYPAUSE", "display": "🎵 PLAYPAUSE"},
                15: {"type": "media", "media_code": MEDIA_KEYCODES['volup'], "name": "VOLUP", "display": "🎵 VOLUP"},
            }
        elif index == 3:
            # 🎨 Graphics/Design (Undo, Redo, Duplicate)
            self.mappings = {
                1: {"type": "basic", "keycode": KEYCODES['z'], "modifiers": Modifier.CTRL, "key_name": "Z", "display": "Ctrl+Z"},
                2: {"type": "basic", "keycode": KEYCODES['y'], "modifiers": Modifier.CTRL, "key_name": "Y", "display": "Ctrl+Y"},
                3: {"type": "basic", "keycode": KEYCODES['j'], "modifiers": Modifier.CTRL, "key_name": "J", "display": "Ctrl+J"},
                13: {"type": "media", "media_code": MEDIA_KEYCODES['voldown'], "name": "VOLDOWN", "display": "🎵 VOLDOWN"},
                14: {"type": "basic", "keycode": KEYCODES['0'], "modifiers": Modifier.CTRL, "key_name": "0", "display": "Ctrl+0"},
                15: {"type": "media", "media_code": MEDIA_KEYCODES['volup'], "name": "VOLUP", "display": "🎵 VOLUP"},
            }
        elif index == 4:
            # 💻 Developer/IDE (Run F5, Step F10, Comment)
            self.mappings = {
                1: {"type": "basic", "keycode": KEYCODES['f5'], "modifiers": 0, "key_name": "F5", "display": "F5"},
                2: {"type": "basic", "keycode": KEYCODES['f10'], "modifiers": 0, "key_name": "F10", "display": "F10"},
                3: {"type": "basic", "keycode": KEYCODES['slash'], "modifiers": Modifier.CTRL, "key_name": "/", "display": "Ctrl+/"},
                13: {"type": "media", "media_code": MEDIA_KEYCODES['voldown'], "name": "VOLDOWN", "display": "🎵 VOLDOWN"},
                14: {"type": "basic", "keycode": KEYCODES['f5'], "modifiers": 0, "key_name": "F5", "display": "F5"},
                15: {"type": "media", "media_code": MEDIA_KEYCODES['volup'], "name": "VOLUP", "display": "🎵 VOLUP"},
            }

        self.update_key_buttons_ui()

    def apply_led_mode(self):
        if not self.kb.is_connected():
            if not self.kb.connect():
                QMessageBox.critical(self, "Error", "No keypad device connected.")
                return

        mode_idx = self.led_combo.currentIndex()
        if self.kb.set_led_mode(mode_idx):
            QMessageBox.information(self, "LED Updated", f"LED mode set to Mode {mode_idx}.")

    def save_profile(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Keypad Profile", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.mappings, f, indent=2)
                QMessageBox.information(self, "Saved", f"Profile saved to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save profile: {e}")

    def load_profile(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Keypad Profile", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Convert string keys back to ints
                if isinstance(list(data.keys())[0], str) and isinstance(list(data.values())[0], dict) and 'type' in list(data.values())[0]:
                    self.mappings = {int(k): v for k, v in data.items()}
                elif '1' in data and isinstance(data['1'], dict) and 'type' not in data['1']:
                    # Support legacy multi-layer profiles
                    self.mappings = {int(k): v for k, v in data['1'].items()}
                else:
                    self.mappings = {int(k): v for k, v in data.items()}
                self.update_key_buttons_ui()
                QMessageBox.information(self, "Loaded", f"Profile loaded from {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load profile: {e}")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
