import sys
import json
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QListWidget, QTextEdit, QLineEdit, QPushButton, 
                             QLabel, QSplitter, QDialog, QListWidgetItem,
                             QInputDialog, QFrame, QStatusBar, QMessageBox,
                             QFileDialog, QScrollArea, QCheckBox, QComboBox,
                             QTabWidget, QGroupBox, QTextEdit, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize, QSettings
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QBrush, QPalette
import base64
from io import BytesIO

class LargeLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telegram Bot")
        self.setFixedSize(600, 700)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #37AEE2, stop: 1 #1E96C8);
            }
            QLabel {
                color: white;
                font-size: 16px;
                background: transparent;
            }
            QLineEdit {
                padding: 20px;
                border: 2px solid #E1E1E1;
                border-radius: 12px;
                font-size: 16px;
                background: white;
                margin: 10px 0px;
                min-height: 30px;
            }
            QLineEdit:focus {
                border-color: #37AEE2;
                background: #F8F9FA;
            }
            QPushButton {
                background: #37AEE2;
                color: white;
                border: none;
                padding: 20px;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                margin: 20px 0px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: #2A8FD6;
            }
            QPushButton:pressed {
                background: #1E7BC2;
            }
            QTextEdit {
                padding: 15px;
                border: 2px solid #E1E1E1;
                border-radius: 12px;
                font-size: 14px;
                background: white;
                margin: 10px 0px;
            }
        """)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(50, 50, 50, 50)
        
        logo_label = QLabel("✈️")
        logo_label.setStyleSheet("font-size: 80px; margin-bottom: 30px;")
        logo_label.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Telegram Bot Manager")
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 15px;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Bot Management Platform")
        subtitle.setStyleSheet("font-size: 18px; color: rgba(255,255,255,0.9); margin-bottom: 50px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        token_label = QLabel("Bot Token")
        token_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-top: 20px;")
        
        self.bot_token_input = QLineEdit()
        self.bot_token_input.setPlaceholderText("Enter bot token...")
        self.bot_token_input.setMinimumHeight(60)
        
        info_group = QGroupBox("Information")
        info_group.setStyleSheet("""
            QGroupBox {
                background: rgba(255,255,255,0.2);
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 15px;
                margin-top: 20px;
                color: white;
                font-weight: bold;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: white;
            }
        """)
        
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "1. Create bot via @BotFather\n"
            "2. Copy bot token\n"
            "3. Paste token below\n"
            "4. Send /start to your bot\n"
            "5. Click Start Messaging"
        )
        info_text.setStyleSheet("""
            background: rgba(255,255,255,0.1); 
            padding: 25px; 
            border-radius: 10px;
            margin: 15px 0px;
            line-height: 1.6;
            font-size: 15px;
        """)
        info_text.setWordWrap(True)
        
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        
        self.login_button = QPushButton("Start Messaging")
        self.login_button.setMinimumHeight(60)
        self.login_button.clicked.connect(self.accept)
        
        layout.addWidget(logo_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(token_label)
        layout.addWidget(self.bot_token_input)
        layout.addWidget(info_group)
        layout.addWidget(self.login_button)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_credentials(self):
        return {
            'bot_token': self.bot_token_input.text().strip()
        }

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 600)
        self.settings = QSettings("TelegramBot", "Client")
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Glass"])
        self.theme_combo.setStyleSheet("padding: 10px; font-size: 14px;")
        
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        
        auto_group = QGroupBox("Auto-Reply")
        auto_layout = QVBoxLayout()
        
        self.auto_reply_check = QCheckBox("Enable Auto-Reply")
        self.auto_reply_check.setStyleSheet("font-size: 14px; padding: 5px;")
        
        self.auto_reply_text = QTextEdit()
        self.auto_reply_text.setPlaceholderText("Auto-reply message...")
        self.auto_reply_text.setMaximumHeight(100)
        self.auto_reply_text.setStyleSheet("font-size: 14px; padding: 10px;")
        
        auto_layout.addWidget(self.auto_reply_check)
        auto_layout.addWidget(QLabel("Message:"))
        auto_layout.addWidget(self.auto_reply_text)
        auto_group.setLayout(auto_layout)
        
        msg_group = QGroupBox("Messages")
        msg_layout = QVBoxLayout()
        
        self.msg_delay_spin = QSpinBox()
        self.msg_delay_spin.setRange(1, 60)
        self.msg_delay_spin.setSuffix(" seconds")
        self.msg_delay_spin.setStyleSheet("padding: 10px; font-size: 14px;")
        
        msg_layout.addWidget(QLabel("Check delay:"))
        msg_layout.addWidget(self.msg_delay_spin)
        msg_group.setLayout(msg_layout)
        
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(theme_group)
        layout.addWidget(auto_group)
        layout.addWidget(msg_group)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        theme = self.settings.value("theme", "Light")
        self.theme_combo.setCurrentText(theme)
        
        auto_reply_enabled = self.settings.value("auto_reply_enabled", False, type=bool)
        self.auto_reply_check.setChecked(auto_reply_enabled)
        
        auto_reply_text = self.settings.value("auto_reply_text", "Thanks for your message!")
        self.auto_reply_text.setPlainText(auto_reply_text)
        
        delay = self.settings.value("message_delay", 5, type=int)
        self.msg_delay_spin.setValue(delay)
    
    def save_settings(self):
        self.settings.setValue("theme", self.theme_combo.currentText())
        self.settings.setValue("auto_reply_enabled", self.auto_reply_check.isChecked())
        self.settings.setValue("auto_reply_text", self.auto_reply_text.toPlainText())
        self.settings.setValue("message_delay", self.msg_delay_spin.value())
        self.accept()

class Database:
    def __init__(self, db_path="telegram_bot_data"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        self.init_database()
    
    def init_database(self):
        for file in ["messages.json", "chats.json", "processed_updates.json"]:
            if not os.path.exists(os.path.join(self.db_path, file)):
                with open(os.path.join(self.db_path, file), 'w', encoding='utf-8') as f:
                    json.dump({}, f)
    
    def save_message(self, chat_id, message, is_outgoing, message_type="text", file_data=None):
        try:
            with open(os.path.join(self.db_path, "messages.json"), 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
            
            chat_id_str = str(chat_id)
            if chat_id_str not in messages_data:
                messages_data[chat_id_str] = []
            
            message_obj = {
                'message': message,
                'is_outgoing': is_outgoing,
                'timestamp': datetime.now().strftime("%H:%M"),
                'type': message_type
            }
            
            if file_data and message_type == "photo":
                message_obj['file_data'] = file_data
            
            if message_type == "text":
                existing_messages = [msg for msg in messages_data[chat_id_str] 
                                   if msg.get('type') == 'text' and msg['message'] == message and msg['is_outgoing'] == is_outgoing]
                if existing_messages:
                    return
            
            messages_data[chat_id_str].append(message_obj)
            
            if len(messages_data[chat_id_str]) > 200:
                messages_data[chat_id_str] = messages_data[chat_id_str][-200:]
            
            with open(os.path.join(self.db_path, "messages.json"), 'w', encoding='utf-8') as f:
                json.dump(messages_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Save error: {e}")
    
    def get_messages(self, chat_id, limit=200):
        try:
            with open(os.path.join(self.db_path, "messages.json"), 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
            
            chat_id_str = str(chat_id)
            if chat_id_str in messages_data:
                return messages_data[chat_id_str][-limit:]
            return []
        except Exception as e:
            print(f"Load error: {e}")
            return []
    
    def save_chat(self, chat_id, username="", first_name="", last_name=""):
        try:
            with open(os.path.join(self.db_path, "chats.json"), 'r', encoding='utf-8') as f:
                chats_data = json.load(f)
            
            chat_id_str = str(chat_id)
            chats_data[chat_id_str] = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'last_activity': datetime.now().isoformat()
            }
            
            with open(os.path.join(self.db_path, "chats.json"), 'w', encoding='utf-8') as f:
                json.dump(chats_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Save chat error: {e}")
    
    def get_chats(self):
        try:
            with open(os.path.join(self.db_path, "chats.json"), 'r', encoding='utf-8') as f:
                chats_data = json.load(f)
            return chats_data
        except Exception as e:
            print(f"Load chats error: {e}")
            return {}
    
    def save_processed_update(self, update_id):
        try:
            with open(os.path.join(self.db_path, "processed_updates.json"), 'r', encoding='utf-8') as f:
                processed_data = json.load(f)
            
            processed_data[str(update_id)] = True
            
            if len(processed_data) > 1000:
                all_ids = list(processed_data.keys())
                for old_id in all_ids[:-500]:
                    del processed_data[old_id]
            
            with open(os.path.join(self.db_path, "processed_updates.json"), 'w', encoding='utf-8') as f:
                json.dump(processed_data, f)
                
        except Exception as e:
            print(f"Save update error: {e}")
    
    def is_update_processed(self, update_id):
        try:
            with open(os.path.join(self.db_path, "processed_updates.json"), 'r', encoding='utf-8') as f:
                processed_data = json.load(f)
            
            return str(update_id) in processed_data
        except:
            return False

class TelegramBotManager:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.is_initialized = False
        self.db = Database()
        self.last_update_id = 0
        self.settings = QSettings("TelegramBot", "Client")
        
    def initialize(self):
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    self.is_initialized = True
                    return True
            return False
        except Exception as e:
            return False
    
    def get_updates(self):
        try:
            params = {'offset': self.last_update_id + 1, 'timeout': 3}
            response = requests.get(f"{self.base_url}/getUpdates", params=params, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if data['ok'] and data['result']:
                    self.last_update_id = max(update['update_id'] for update in data['result'])
                    return data['result']
            return []
        except Exception as e:
            return []
    
    def get_chats(self):
        if not self.is_initialized:
            return []
        
        chats = []
        try:
            updates = self.get_updates()
            
            for update in updates:
                if 'message' in update:
                    chat = update['message']['chat']
                    chat_info = {
                        'id': chat['id'],
                        'username': chat.get('username', ''),
                        'first_name': chat.get('first_name', ''),
                        'last_name': chat.get('last_name', ''),
                        'type': 'private'
                    }
                    
                    self.db.save_chat(chat['id'], chat.get('username', ''), 
                                    chat.get('first_name', ''), chat.get('last_name', ''))
                    
                    if 'text' in update['message'] and not self.db.is_update_processed(update['update_id']):
                        message_text = update['message']['text']
                        self.db.save_message(chat['id'], message_text, False, "text")
                        self.db.save_processed_update(update['update_id'])
                        
                        if (self.settings.value("auto_reply_enabled", False, type=bool) and 
                            not message_text.startswith('/')):
                            reply_text = self.settings.value("auto_reply_text", "Thanks for your message!")
                            self.send_message(chat['id'], reply_text)
                    
                    if not any(c['id'] == chat['id'] for c in chats):
                        chats.append(chat_info)
                        
        except Exception as e:
            pass
        
        saved_chats = self.db.get_chats()
        for chat_id, chat_data in saved_chats.items():
            chat_id_int = int(chat_id)
            if not any(c['id'] == chat_id_int for c in chats):
                chats.append({
                    'id': chat_id_int,
                    'username': chat_data.get('username', ''),
                    'first_name': chat_data.get('first_name', ''),
                    'last_name': chat_data.get('last_name', ''),
                    'type': 'saved'
                })
        
        return chats
    
    def get_file(self, file_id):
        try:
            response = requests.get(f"{self.base_url}/getFile", params={'file_id': file_id})
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    return data['result']
        except Exception as e:
            pass
        return None
    
    def download_file(self, file_path):
        try:
            response = requests.get(f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}")
            if response.status_code == 200:
                return response.content
        except Exception as e:
            pass
        return None
    
    def check_new_messages(self):
        if not self.is_initialized:
            return []
        
        new_messages = []
        try:
            updates = self.get_updates()
            
            for update in updates:
                if 'message' in update and not self.db.is_update_processed(update['update_id']):
                    chat = update['message']['chat']
                    
                    if 'text' in update['message']:
                        message_text = update['message']['text']
                        self.db.save_message(chat['id'], message_text, False, "text")
                        self.db.save_processed_update(update['update_id'])
                        
                        new_messages.append({
                            'chat_id': chat['id'],
                            'message': message_text,
                            'type': 'text'
                        })
                    
                    elif 'photo' in update['message']:
                        photo = max(update['message']['photo'], key=lambda x: x['file_size'])
                        file_id = photo['file_id']
                        
                        file_info = self.get_file(file_id)
                        if file_info:
                            photo_data = self.download_file(file_info['file_path'])
                            if photo_data:
                                photo_base64 = base64.b64encode(photo_data).decode('utf-8')
                                self.db.save_message(chat['id'], "📷 Photo", False, "photo", photo_base64)
                                self.db.save_processed_update(update['update_id'])
                                
                                new_messages.append({
                                    'chat_id': chat['id'],
                                    'message': "📷 Photo",
                                    'type': 'photo'
                                })
                        
        except Exception as e:
            pass
        
        return new_messages
    
    def send_message(self, chat_id, message):
        if not self.is_initialized:
            return False
            
        try:
            payload = {
                'chat_id': chat_id,
                'text': message
            }
            
            response = requests.post(f"{self.base_url}/sendMessage", data=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    self.db.save_message(chat_id, message, True, "text")
                    return True
            
            return False
            
        except Exception as e:
            return False
    
    def send_photo(self, chat_id, photo_path):
        if not self.is_initialized:
            return False
            
        try:
            with open(photo_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                data = {'chat_id': chat_id}
                
                response = requests.post(f"{self.base_url}/sendPhoto", files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data['ok']:
                        with open(photo_path, 'rb') as f:
                            photo_data = f.read()
                            photo_base64 = base64.b64encode(photo_data).decode('utf-8')
                            self.db.save_message(chat_id, "📷 Photo", True, "photo", photo_base64)
                        return True
            
            return False
            
        except Exception as e:
            return False

class ChatListItem(QWidget):
    def __init__(self, chat_data, parent=None):
        super().__init__(parent)
        self.chat_data = chat_data
        self.setFixedHeight(70)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        avatar_label = QLabel()
        avatar_label.setFixedSize(48, 48)
        avatar_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #37AEE2, stop:1 #1E96C8);
                border-radius: 24px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        first_letter = "U"
        if self.chat_data.get('first_name'):
            first_letter = self.chat_data['first_name'][0].upper()
        elif self.chat_data.get('username'):
            first_letter = self.chat_data['username'][0].upper()
        
        avatar_label.setText(first_letter)
        avatar_label.setAlignment(Qt.AlignCenter)
        
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        name = self.chat_data.get('first_name', '') + ' ' + self.chat_data.get('last_name', '')
        name = name.strip()
        if not name:
            name = self.chat_data.get('username', f"User {self.chat_data['id']}")
        
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 15px;
                font-weight: 500;
            }
        """)
        
        last_msg_label = QLabel("Start chatting")
        last_msg_label.setStyleSheet("""
            QLabel {
                color: #707579;
                font-size: 13px;
            }
        """)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(last_msg_label)
        info_widget.setLayout(info_layout)
        
        layout.addWidget(avatar_label)
        layout.addWidget(info_widget)
        layout.addStretch()
        
        self.setLayout(layout)

class TelegramClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bot_manager = None
        self.current_chat_id = None
        self.db = Database()
        self.settings = QSettings("TelegramBot", "Client")
        self.setup_ui()
        self.apply_theme()
        self.show_login_dialog()
        
    def setup_ui(self):
        self.setWindowTitle("Telegram Bot")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)
        
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(360)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        self.left_panel.setLayout(left_layout)
        
        chats_header = QWidget()
        chats_header.setFixedHeight(60)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("Telegram")
        title.setStyleSheet("color: #000000; font-size: 20px; font-weight: bold;")
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 18px;
                color: #0088CC;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #F0F0F0;
            }
        """)
        self.settings_btn.clicked.connect(self.show_settings)
        
        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setFixedSize(36, 36)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 18px;
                color: #0088CC;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F0F0F0;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_chats)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.settings_btn)
        header_layout.addWidget(self.refresh_btn)
        chats_header.setLayout(header_layout)
        
        search_widget = QWidget()
        search_widget.setFixedHeight(50)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(12, 8, 12, 8)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search")
        search_input.setStyleSheet("""
            QLineEdit {
                background: #F7F7F7;
                border: none;
                border-radius: 18px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QLineEdit:focus {
                background: #FFFFFF;
                border: 1px solid #0088CC;
            }
        """)
        
        search_layout.addWidget(search_input)
        search_widget.setLayout(search_layout)
        
        self.chats_list = QListWidget()
        self.chats_list.setStyleSheet("""
            QListWidget {
                background: #FFFFFF;
                border: none;
                outline: none;
                border-right: 1px solid #E6E6E6;
            }
            QListWidget::item {
                border: none;
                background: transparent;
            }
            QListWidget::item:selected {
                background: #E3F2FD;
            }
        """)
        self.chats_list.itemClicked.connect(self.on_chat_selected)
        
        left_layout.addWidget(chats_header)
        left_layout.addWidget(search_widget)
        left_layout.addWidget(self.chats_list)
        
        self.right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        self.right_panel.setLayout(right_layout)
        
        self.chat_header = QWidget()
        self.chat_header.setFixedHeight(60)
        self.chat_header_layout = QHBoxLayout()
        self.chat_header_layout.setContentsMargins(20, 10, 20, 10)
        
        self.chat_avatar = QLabel("U")
        self.chat_avatar.setFixedSize(40, 40)
        self.chat_avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #37AEE2, stop:1 #1E96C8);
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.chat_avatar.setAlignment(Qt.AlignCenter)
        
        self.chat_info = QLabel("Select chat")
        self.chat_info.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold;")
        
        self.chat_header_layout.addWidget(self.chat_avatar)
        self.chat_header_layout.addSpacing(12)
        self.chat_header_layout.addWidget(self.chat_info)
        self.chat_header_layout.addStretch()
        self.chat_header.setLayout(self.chat_header_layout)
        
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setStyleSheet("""
            QTextEdit {
                background: #E5EBF1;
                border: none;
                font-size: 14px;
                padding: 0px;
            }
        """)
        
        input_widget = QWidget()
        input_widget.setFixedHeight(70)
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(8)
        
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setFixedSize(40, 40)
        self.attach_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                color: #707579;
            }
            QPushButton:hover {
                background: #F0F0F0;
            }
        """)
        self.attach_btn.clicked.connect(self.send_photo)
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(50)
        self.message_input.setPlaceholderText("Message")
        self.message_input.setStyleSheet("""
            QTextEdit {
                background: #F7F7F7;
                border: none;
                border-radius: 20px;
                padding: 12px 16px;
                font-size: 14px;
                color: #000000;
            }
            QTextEdit:focus {
                background: #FFFFFF;
            }
        """)
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #0088CC;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: #0077B3;
            }
            QPushButton:disabled {
                background: #CCCCCC;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.attach_btn)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)
        input_widget.setLayout(input_layout)
        
        right_layout.addWidget(self.chat_header)
        right_layout.addWidget(self.messages_area)
        right_layout.addWidget(input_widget)
        
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.right_panel)
        
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background: #F8F8F8; color: #707579;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        self.message_check_timer = QTimer()
        self.message_check_timer.timeout.connect(self.check_new_messages)
        
    def apply_theme(self):
        theme = self.settings.value("theme", "Light")
        
        if theme == "Dark":
            self.apply_dark_theme()
        elif theme == "Glass":
            self.apply_glass_theme()
        else:
            self.apply_light_theme()
    
    def apply_light_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #FFFFFF;
            }
            QWidget {
                background: #FFFFFF;
            }
        """)
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #1E1E1E;
            }
            QWidget {
                background: #1E1E1E;
                color: #FFFFFF;
            }
            QTextEdit {
                background: #2D2D2D;
                color: #FFFFFF;
            }
            QLineEdit {
                background: #2D2D2D;
                color: #FFFFFF;
            }
        """)
    
    def apply_glass_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(55, 174, 226, 0.9),
                    stop:1 rgba(30, 150, 200, 0.7));
            }
            QWidget {
                background: rgba(255, 255, 255, 0.1);
                color: white;
            }
            QTextEdit {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QLineEdit {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """)
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.apply_theme()
            if self.message_check_timer.isActive():
                self.message_check_timer.stop()
                delay = self.settings.value("message_delay", 5, type=int) * 1000
                self.message_check_timer.start(delay)
    
    def show_login_dialog(self):
        dialog = LargeLoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            credentials = dialog.get_credentials()
            self.initialize_bot(credentials)
        else:
            sys.exit(0)
    
    def initialize_bot(self, credentials):
        try:
            self.bot_manager = TelegramBotManager(credentials['bot_token'])
            self.status_bar.showMessage("Connecting...")
            
            QTimer.singleShot(100, self.do_initialize)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", "Connection failed")
    
    def do_initialize(self):
        try:
            success = self.bot_manager.initialize()
            if success:
                self.status_bar.showMessage("Connected")
                self.refresh_chats()
                delay = self.settings.value("message_delay", 5, type=int) * 1000
                self.message_check_timer.start(delay)
            else:
                self.status_bar.showMessage("Connection failed")
                QMessageBox.critical(self, "Error", "Check token")
        except Exception as e:
            self.status_bar.showMessage("Connection error")
    
    def check_new_messages(self):
        if not self.bot_manager:
            return
        
        try:
            new_messages = self.bot_manager.check_new_messages()
            if new_messages:
                for msg in new_messages:
                    if self.current_chat_id == msg['chat_id']:
                        self.load_chat_history()
        except:
            pass
    
    def refresh_chats(self):
        if not self.bot_manager:
            return
            
        self.refresh_btn.setEnabled(False)
        self.status_bar.showMessage("Refreshing...")
        
        QTimer.singleShot(100, self.do_refresh_chats)
    
    def do_refresh_chats(self):
        try:
            chats = self.bot_manager.get_chats()
            self.on_chats_loaded(chats)
        except Exception as e:
            self.on_chats_error(str(e))
    
    def on_chats_loaded(self, chats):
        self.chats_list.clear()
        
        for chat in chats:
            item = QListWidgetItem()
            widget = ChatListItem(chat)
            item.setSizeHint(widget.sizeHint())
            self.chats_list.addItem(item)
            self.chats_list.setItemWidget(item, widget)
        
        self.status_bar.showMessage(f"{len(chats)} chats")
        self.refresh_btn.setEnabled(True)
        
        if len(chats) == 0:
            self.status_bar.showMessage("No chats")
    
    def on_chats_error(self, error):
        self.status_bar.showMessage("Error loading")
        self.refresh_btn.setEnabled(True)
    
    def on_chat_selected(self, item):
        widget = self.chats_list.itemWidget(item)
        if widget:
            self.current_chat_id = widget.chat_data['id']
            self.update_chat_header(widget.chat_data)
            self.load_chat_history()
    
    def update_chat_header(self, chat_data):
        name = chat_data.get('first_name', '') + ' ' + chat_data.get('last_name', '')
        name = name.strip()
        if not name:
            name = chat_data.get('username', f"User {chat_data['id']}")
        
        self.chat_info.setText(name)
        
        first_letter = "U"
        if chat_data.get('first_name'):
            first_letter = chat_data['first_name'][0].upper()
        elif chat_data.get('username'):
            first_letter = chat_data['username'][0].upper()
        
        self.chat_avatar.setText(first_letter)
    
    def load_chat_history(self):
        if not self.current_chat_id:
            return
            
        try:
            messages = self.db.get_messages(self.current_chat_id)
            self.messages_area.clear()
            
            if not messages:
                self.messages_area.setHtml("""
                    <div style='text-align: center; color: #707579; margin-top: 50px; font-family: system-ui;'>
                        <h3 style='color: #000000;'>No messages</h3>
                        <p>Start conversation</p>
                    </div>
                """)
                return
            
            html = """
            <div style='
                font-family: system-ui, -apple-system, sans-serif;
                padding: 20px;
                background: #E5EBF1;
            '>
            """
            
            for msg in messages:
                message_type = msg.get('type', 'text')
                
                if message_type == 'text':
                    if msg['is_outgoing']:
                        html += f"""
                        <div style='margin: 8px 0px; text-align: right;'>
                            <div style='
                                display: inline-block;
                                max-width: 70%;
                                background: #0088CC;
                                padding: 8px 12px;
                                border-radius: 12px 12px 0px 12px;
                                color: white;
                                font-size: 14px;
                                line-height: 1.4;
                                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                            '>
                                <div>{msg['message']}</div>
                                <div style='
                                    font-size: 11px;
                                    color: rgba(255,255,255,0.7);
                                    text-align: right;
                                    margin-top: 4px;
                                '>{msg['timestamp']}</div>
                            </div>
                        </div>
                        """
                    else:
                        html += f"""
                        <div style='margin: 8px 0px; text-align: left;'>
                            <div style='
                                display: inline-block;
                                max-width: 70%;
                                background: #FFFFFF;
                                padding: 8px 12px;
                                border-radius: 0px 12px 12px 12px;
                                color: #000000;
                                font-size: 14px;
                                line-height: 1.4;
                                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                            '>
                                <div>{msg['message']}</div>
                                <div style='
                                    font-size: 11px;
                                    color: #707579;
                                    text-align: right;
                                    margin-top: 4px;
                                '>{msg['timestamp']}</div>
                            </div>
                        </div>
                        """
                elif message_type == 'photo':
                    if msg['is_outgoing']:
                        html += f"""
                        <div style='margin: 8px 0px; text-align: right;'>
                            <div style='
                                display: inline-block;
                                max-width: 70%;
                                background: #0088CC;
                                padding: 8px;
                                border-radius: 12px 12px 0px 12px;
                                color: white;
                                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                            '>
                                <div style='margin-bottom: 4px;'>📷 Photo</div>
                                <img src='data:image/jpeg;base64,{msg['file_data']}' 
                                     style='
                                         max-width: 200px; 
                                         max-height: 200px; 
                                         border-radius: 8px;
                                         display: block;
                                     '/>
                                <div style='
                                    font-size: 11px;
                                    color: rgba(255,255,255,0.7);
                                    text-align: right;
                                    margin-top: 4px;
                                '>{msg['timestamp']}</div>
                            </div>
                        </div>
                        """
                    else:
                        html += f"""
                        <div style='margin: 8px 0px; text-align: left;'>
                            <div style='
                                display: inline-block;
                                max-width: 70%;
                                background: #FFFFFF;
                                padding: 8px;
                                border-radius: 0px 12px 12px 12px;
                                color: #000000;
                                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                            '>
                                <div style='margin-bottom: 4px;'>📷 Photo</div>
                                <img src='data:image/jpeg;base64,{msg['file_data']}' 
                                     style='
                                         max-width: 200px; 
                                         max-height: 200px; 
                                         border-radius: 8px;
                                         display: block;
                                     '/>
                                <div style='
                                    font-size: 11px;
                                    color: #707579;
                                    text-align: right;
                                    margin-top: 4px;
                                '>{msg['timestamp']}</div>
                            </div>
                        </div>
                        """
            
            html += "</div>"
            self.messages_area.setHtml(html)
            
            self.messages_area.verticalScrollBar().setValue(
                self.messages_area.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            self.messages_area.setHtml("""
                <div style='text-align: center; color: #707579; margin-top: 50px;'>
                    <h3 style='color: #000000;'>Error</h3>
                </div>
            """)
    
    def send_message(self):
        if not self.current_chat_id or not self.bot_manager:
            QMessageBox.warning(self, "Telegram", "Select chat")
            return
            
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        
        self.send_btn.setEnabled(False)
        self.status_bar.showMessage("Sending...")
        
        QTimer.singleShot(100, lambda: self.do_send_message(message))
    
    def do_send_message(self, message):
        try:
            success = self.bot_manager.send_message(self.current_chat_id, message)
            self.on_message_sent(success)
        except Exception as e:
            self.on_message_error(str(e))
    
    def send_photo(self):
        if not self.current_chat_id or not self.bot_manager:
            QMessageBox.warning(self, "Telegram", "Select chat")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose Photo", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.status_bar.showMessage("Sending...")
            QTimer.singleShot(100, lambda: self.do_send_photo(file_path))
    
    def do_send_photo(self, file_path):
        try:
            success = self.bot_manager.send_photo(self.current_chat_id, file_path)
            if success:
                self.load_chat_history()
                self.status_bar.showMessage("Sent")
            else:
                self.status_bar.showMessage("Failed")
        except Exception as e:
            self.status_bar.showMessage("Error")
    
    def on_message_sent(self, success):
        self.send_btn.setEnabled(True)
        
        if success:
            self.message_input.clear()
            self.load_chat_history()
            self.status_bar.showMessage("Sent")
        else:
            self.status_bar.showMessage("Failed")
    
    def on_message_error(self, error):
        self.send_btn.setEnabled(True)
        self.status_bar.showMessage("Error")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Telegram Bot")
    
    window = TelegramClient()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()