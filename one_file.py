import sys
import json
import os
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QListWidget, QLineEdit, QPushButton, 
                             QLabel, QDialog, QListWidgetItem, QFrame, 
                             QMessageBox, QFileDialog, QScrollArea, 
                             QComboBox, QGroupBox, QSlider, QSizePolicy, 
                             QGraphicsDropShadowEffect, QAbstractItemView, QMenu,
                             QAction, QTextEdit)
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, pyqtProperty, 
                          QSize, QSettings, QThread, pyqtSignal, QMutex, QUrl,
                          QPropertyAnimation, QEasingCurve, QRect, QPoint)
from PyQt5.QtGui import (QFont, QPixmap, QPainter, QColor, QBrush, 
                         QPalette, QIcon, QDesktopServices, QImage, QMouseEvent,
                         QCursor)

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


STYLES = {
    'Light': {
        'bg': '#FFFFFF',
        'chat_bg': '#F0F0F0',
        'text': '#000000',
        'text_secondary': '#707579',
        'input_bg': '#FFFFFF',
        'list_bg': '#FFFFFF',
        'list_hover': '#F5F5F5',
        'list_sel': '#E3F2FD',
        'msg_in': '#FFFFFF',
        'msg_out': '#3390EC',
        'time_in': '#A1AAB3',
        'time_out': '#BBDEFB',
        'border': '#E0E0E0',
        'accent': '#3390EC',
        'online': '#4CAF50'
    },
    'Dark': {
        'bg': '#17212B',
        'chat_bg': '#0E1621',
        'text': '#FFFFFF',
        'text_secondary': '#8A8D91',
        'input_bg': '#242F3D',
        'list_bg': '#17212B',
        'list_hover': '#202B36',
        'list_sel': '#2B5278',
        'msg_in': '#182533',
        'msg_out': '#2B5278',
        'time_in': '#758392',
        'time_out': '#779ABB',
        'border': '#2F3B4B',
        'accent': '#3390EC',
        'online': '#4CAF50'
    },
    'Blue': {
        'bg': '#0F2639',
        'chat_bg': '#0A1E2E',
        'text': '#FFFFFF',
        'text_secondary': '#8A8D91',
        'input_bg': '#1C3548',
        'list_bg': '#0F2639',
        'list_hover': '#1C3548',
        'list_sel': '#2B5278',
        'msg_in': '#182533',
        'msg_out': '#2B5278',
        'time_in': '#779ABB',
        'time_out': '#779ABB',
        'border': '#1C3548',
        'accent': '#3390EC',
        'online': '#4CAF50'
    }
}

db_mutex = QMutex()

class Database:
    def __init__(self, db_path="telegram_bot_data"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        self.init_database()
    
    def init_database(self):
        for file in ["messages.json", "chats.json", "processed.json", "photos_cache"]:
            path = os.path.join(self.db_path, file)
            if file == "photos_cache":
                if not os.path.exists(path):
                    os.makedirs(path)
            else:
                if not os.path.exists(path):
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
    
    def save_message(self, chat_id, message, is_outgoing, msg_type="text", file_path=None, file_name=None, photo_data=None):
        db_mutex.lock()
        try:
            path = os.path.join(self.db_path, "messages.json")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chat_id = str(chat_id)
            if chat_id not in data:
                data[chat_id] = []
            
            current_time = datetime.now()
            msg_obj = {
                'id': int(current_time.timestamp() * 1000),
                'text': message,
                'out': is_outgoing,
                'time': current_time.strftime("%H:%M"),
                'type': msg_type,
                'timestamp': current_time.timestamp()
            }
            
            if not message and msg_type == 'photo':
                msg_obj['text'] = "🖼️ Photo"
            elif not message and msg_type == 'document':
                msg_obj['text'] = "📎 File"
            
            if file_path: 
                msg_obj['file_path'] = file_path
            if file_name: 
                msg_obj['file_name'] = file_name
            if photo_data:
                # Сохраняем фото в кэш
                photo_id = f"photo_{int(current_time.timestamp() * 1000)}"
                photo_path = os.path.join(self.db_path, "photos_cache", f"{photo_id}.jpg")
                with open(photo_path, 'wb') as f:
                    f.write(photo_data)
                msg_obj['photo_id'] = photo_id
                msg_obj['photo_path'] = photo_path
            
            data[chat_id].append(msg_obj)

            if len(data[chat_id]) > 500:
                data[chat_id] = data[chat_id][-500:]

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving message: {e}")
        finally:
            db_mutex.unlock()

    def get_messages(self, chat_id):
        db_mutex.lock()
        try:
            path = os.path.join(self.db_path, "messages.json")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            messages = data.get(str(chat_id), [])
            for msg in messages:
                if 'type' not in msg:
                    msg['type'] = 'text'
                if 'text' not in msg:
                    msg['text'] = ''
                if 'time' not in msg:
                    if 'timestamp' in msg:
                        try:
                            dt = datetime.fromtimestamp(msg['timestamp'])
                            msg['time'] = dt.strftime("%H:%M")
                        except:
                            msg['time'] = '00:00'
                    else:
                        msg['time'] = '00:00'
                if 'out' not in msg:
                    msg['out'] = False
            return messages
        except:
            return []
        finally:
            db_mutex.unlock()

    def delete_message(self, chat_id, message_id):
        db_mutex.lock()
        try:
            path = os.path.join(self.db_path, "messages.json")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chat_id = str(chat_id)
            if chat_id in data:
                data[chat_id] = [msg for msg in data[chat_id] if msg['id'] != message_id]
                
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                return True
            return False
        except:
            return False
        finally:
            db_mutex.unlock()

    def clear_chat(self, chat_id):
        db_mutex.lock()
        try:
            path = os.path.join(self.db_path, "messages.json")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chat_id = str(chat_id)
            if chat_id in data:
                data[chat_id] = []
                
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                return True
            return False
        except:
            return False
        finally:
            db_mutex.unlock()

    def save_chat(self, chat_data):
        db_mutex.lock()
        try:
            path = os.path.join(self.db_path, "chats.json")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cid = str(chat_data['id'])
            if cid not in data:
                data[cid] = chat_data
            else:
                for key, value in chat_data.items():
                    if key not in data[cid] or not data[cid][key]:
                        data[cid][key] = value
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving chat: {e}")
        finally:
            db_mutex.unlock()
            
    def get_chats(self):
        db_mutex.lock()
        try:
            with open(os.path.join(self.db_path, "chats.json"), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for cid, chat_data in data.items():
                if 'id' not in chat_data:
                    chat_data['id'] = cid
            return data
        except:
            return {}
        finally:
            db_mutex.unlock()

    def is_processed(self, update_id):
        try:
            with open(os.path.join(self.db_path, "processed.json"), 'r') as f:
                data = json.load(f)
            return str(update_id) in data
        except: 
            return False

    def mark_processed(self, update_id):
        try:
            path = os.path.join(self.db_path, "processed.json")
            with open(path, 'r') as f:
                data = json.load(f)
            data[str(update_id)] = True
            if len(data) > 1000:
                keys = list(data.keys())[-500:]
                data = {k: data[k] for k in keys}
            with open(path, 'w') as f:
                json.dump(data, f)
        except: 
            pass

    def clear_all_data(self):
        """Очистка всех данных при выходе из аккаунта"""
        db_mutex.lock()
        try:

            for file in ["messages.json", "chats.json", "processed.json"]:
                path = os.path.join(self.db_path, file)
                if os.path.exists(path):
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
            

            photos_cache = os.path.join(self.db_path, "photos_cache")
            if os.path.exists(photos_cache):
                for file in os.listdir(photos_cache):
                    file_path = os.path.join(photos_cache, file)
                    try:
                        os.remove(file_path)
                    except:
                        pass
        finally:
            db_mutex.unlock()


class BotWorker(QThread):
    new_message = pyqtSignal(dict)
    connection_status = pyqtSignal(bool)
    photo_received = pyqtSignal(str, bytes)  # chat_id, photo_data

    def __init__(self, token):
        super().__init__()
        self.token = token
        self.running = True
        self.offset = 0
        self.db = Database()
        self.mutex = QMutex()

    def run(self):
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        while self.running:
            try:
                params = {'offset': self.offset + 1, 'timeout': 10}
                resp = requests.get(url, params=params, timeout=15)
                
                if resp.status_code == 200:
                    self.connection_status.emit(True)
                    data = resp.json()
                    if data['ok']:
                        for update in data['result']:
                            self.offset = max(self.offset, update['update_id'])
                            if not self.db.is_processed(update['update_id']):
                                self.process_update(update)
                                self.db.mark_processed(update['update_id'])
                else:
                    self.connection_status.emit(False)
            except:
                self.connection_status.emit(False)
            
            self.msleep(500)

    def process_update(self, update):
        if 'message' in update:
            msg = update['message']
            chat = msg['chat']
            
            if 'id' not in chat:
                return
            
            chat_info = {
                'id': chat['id'],
                'first_name': chat.get('first_name', ''),
                'last_name': chat.get('last_name', ''),
                'username': chat.get('username', ''),
                'type': chat.get('type', 'private')
            }
            self.db.save_chat(chat_info)

            content = ""
            msg_type = "text"
            photo_data = None
            
            if 'text' in msg:
                content = msg['text']
            elif 'photo' in msg:
                msg_type = "photo"
                content = "🖼️ Photo"
                photos = msg['photo']
                if photos:
                    largest_photo = photos[-1]
                    file_id = largest_photo.get('file_id')
                    if file_id:
                        photo_data = self.download_photo(file_id)
                        if photo_data:
                            self.photo_received.emit(str(chat['id']), photo_data)
            elif 'document' in msg:
                msg_type = "document"
                doc = msg['document']
                file_name = doc.get('file_name', 'Document')
                content = f"📎 {file_name}"
            
            if content:
                self.db.save_message(chat['id'], content, False, msg_type, photo_data=photo_data)
                self.new_message.emit({'chat_id': chat['id'], 'type': msg_type})

    def download_photo(self, file_id):
        """Скачивает фото по file_id"""
        try:

            url = f"https://api.telegram.org/bot{self.token}/getFile"
            resp = requests.post(url, data={'file_id': file_id})
            if resp.status_code == 200:
                file_data = resp.json()
                if file_data['ok']:
                    file_path = file_data['result']['file_path']
                    

                    download_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
                    photo_resp = requests.get(download_url, timeout=15)
                    
                    if photo_resp.status_code == 200:
                        return photo_resp.content
        except Exception as e:
            print(f"Error downloading photo: {e}")
        return None

    def stop(self):
        self.running = False
        self.wait()

class SendWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, token, chat_id, text=None, file_path=None):
        super().__init__()
        self.token = token
        self.chat_id = chat_id
        self.text = text
        self.file_path = file_path

    def run(self):
        try:
            url = f"https://api.telegram.org/bot{self.token}/"
            
            if self.file_path:
                ext = os.path.splitext(self.file_path)[1].lower()
                if ext in ['.jpg', '.png', '.jpeg']:
                    method = "sendPhoto"
                    with open(self.file_path, 'rb') as f:
                        files = {'photo': f}
                        resp = requests.post(url + method, data={'chat_id': self.chat_id}, files=files)
                else:
                    method = "sendDocument"
                    with open(self.file_path, 'rb') as f:
                        files = {'document': f}
                        resp = requests.post(url + method, data={'chat_id': self.chat_id}, files=files)
            else:
                resp = requests.post(url + "sendMessage", data={'chat_id': self.chat_id, 'text': self.text})
            
            if resp.status_code == 200 and resp.json().get('ok'):
                self.finished.emit(True, "")
            else:
                error_msg = resp.json().get('description', 'API Error') if resp.status_code == 200 else f"HTTP {resp.status_code}"
                self.finished.emit(False, error_msg)
        except Exception as e:
            self.finished.emit(False, str(e))


class AvatarLabel(QLabel):
    def __init__(self, text="", size=40, parent=None):
        super().__init__(parent)
        self.text = text
        self.size = size
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        
        if text:
            try:
                first_char = str(text).strip()[0].upper()
                self.setText(first_char if first_char.isprintable() else "?")
            except:
                self.setText("?")
        
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            border-radius: {self.size//2}px; 
            background: #3390EC; 
            color: white; 
            font-weight: bold;
            border: 2px solid rgba(255, 255, 255, 0.3);
            font-size: {self.size//2}px;
        """)

class PhotoMessageWidget(QWidget):
    """Виджет для отображения фото в чате"""
    def __init__(self, photo_path, theme_dict, scale=1.0, parent=None):
        super().__init__(parent)
        self.photo_path = photo_path
        self.theme = theme_dict
        self.scale = scale
        self.is_outgoing = False
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(int(300 * self.scale), int(200 * self.scale))
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setStyleSheet("""
            QLabel {
                border-radius: 10px;
                border: 1px solid rgba(0,0,0,0.1);
                background: rgba(0,0,0,0.05);
            }
        """)

        self.load_photo()
        

        self.time_label = QLabel(datetime.now().strftime("%H:%M"))
        self.time_label.setFont(QFont("Segoe UI", int(10 * self.scale)))
        self.time_label.setAlignment(Qt.AlignRight)
        
        layout.addWidget(self.photo_label)
        layout.addWidget(self.time_label)
        
        self.setLayout(layout)
        
    def load_photo(self):
        if os.path.exists(self.photo_path):
            pixmap = QPixmap(self.photo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.photo_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.photo_label.setPixmap(scaled_pixmap)
            else:
                self.photo_label.setText("🖼️")
        else:
            self.photo_label.setText("🖼️")
    
    def set_outgoing(self, is_outgoing):
        self.is_outgoing = is_outgoing
        time_color = self.theme['time_out'] if is_outgoing else self.theme['time_in']
        self.time_label.setStyleSheet(f"color: {time_color}; background: transparent;")

class MessageBubble(QWidget):
    def __init__(self, message_data, theme_dict, scale=1.0, parent=None):
        super().__init__(parent)
        self.data = message_data
        self.theme = theme_dict
        self.scale = scale
        self.is_photo = message_data.get('type') == 'photo' and 'photo_path' in message_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        if self.is_photo:

            self.photo_widget = PhotoMessageWidget(
                self.data['photo_path'], 
                self.theme, 
                self.scale
            )
            self.photo_widget.set_outgoing(self.data.get('out', False))
            layout.addWidget(self.photo_widget)
        else:
            self.content_frame = QFrame()
            self.content_frame.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
            
            content_layout = QHBoxLayout(self.content_frame)
            content_layout.setContentsMargins(
                int(12 * self.scale), 
                int(8 * self.scale), 
                int(12 * self.scale), 
                int(8 * self.scale)
            )
            
            self.content_label = QLabel()
            self.content_label.setFont(QFont("Segoe UI", int(14 * self.scale)))
            self.content_label.setWordWrap(True)
            self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
            msg_text = self.data.get('text', '')
            if not msg_text:
                msg_type = self.data.get('type', 'text')
                if msg_type == 'photo':
                    msg_text = "🖼️ Photo"
                elif msg_type == 'document':
                    msg_text = "📎 File"
                else:
                    msg_text = "Message"
            
            self.content_label.setText(msg_text)
            
            content_layout.addWidget(self.content_label)
            time_layout = QVBoxLayout()
            time_layout.setAlignment(Qt.AlignBottom)
            
            time_text = self.data.get('time', '')
            if not time_text and 'timestamp' in self.data:
                try:
                    dt = datetime.fromtimestamp(self.data['timestamp'])
                    time_text = dt.strftime("%H:%M")
                except:
                    time_text = ""
            
            self.time_label = QLabel(time_text)
            self.time_label.setFont(QFont("Segoe UI", int(11 * self.scale)))
            
            time_layout.addWidget(self.time_label)
            content_layout.addLayout(time_layout)
            
            layout.addWidget(self.content_frame)
        
        self.setLayout(layout)
        self.update_style()
        
    def update_style(self):
        if not self.is_photo:
            radius = int(12 * self.scale)
            is_outgoing = self.data.get('out', False)
            
            if is_outgoing:
                bg_color = self.theme['msg_out']
                text_color = '#FFFFFF'
                time_color = self.theme['time_out']
                border_radius = f"{radius}px {radius}px 4px {radius}px"
            else:
                bg_color = self.theme['msg_in']
                text_color = self.theme['text']
                time_color = self.theme['time_in']
                border_radius = f"{radius}px {radius}px {radius}px 4px"
            
            self.content_frame.setStyleSheet(f"""
                QFrame {{
                    background: {bg_color};
                    border: 1px solid {bg_color};
                    border-radius: {border_radius};
                    padding: 0px;
                }}
            """)
            
            self.content_label.setStyleSheet(f"color: {text_color}; background: transparent; border: none;")
            self.time_label.setStyleSheet(f"color: {time_color}; background: transparent; border: none;")

class ChatListItem(QWidget):
    def __init__(self, chat_id, chat_data, theme_dict, scale=1.0, parent=None):
        super().__init__(parent)
        self.chat_id = chat_id
        self.chat_data = chat_data
        self.theme = theme_dict
        self.scale = scale
        self.isSelected = False
        self.setFixedHeight(int(72 * scale))
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(int(15 * self.scale), int(8 * self.scale), int(15 * self.scale), int(8 * self.scale))
        layout.setSpacing(int(12 * self.scale))

        first_name = self.chat_data.get('first_name', '')
        last_name = self.chat_data.get('last_name', '')
        username = self.chat_data.get('username', '')
        
        name = f"{first_name} {last_name}".strip()
        if not name:
            name = username if username else str(self.chat_id)
        
        self.avatar = AvatarLabel(name, int(54 * self.scale))
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(int(4 * self.scale))
        self.name_label = QLabel(name)
        self.name_label.setFont(QFont("Segoe UI", int(14 * self.scale), QFont.DemiBold))
        
        db = Database()
        messages = db.get_messages(self.chat_id)
        last_msg = ""
        last_msg_time = ""
        unread_count = 0
        
        if messages:
            unread_count = sum(1 for msg in messages if not msg.get('out', False) and not msg.get('read', False))
            
            last_msg_data = messages[-1]
            msg_text = last_msg_data.get('text', '')
            if msg_text:
                if len(msg_text) > 30:
                    last_msg = msg_text[:27] + "..."
                else:
                    last_msg = msg_text
            else:
                msg_type = last_msg_data.get('type', 'text')
                if msg_type == 'photo':
                    last_msg = "🖼️ Photo"
                elif msg_type == 'document':
                    last_msg = "📎 File"
            
            last_msg_time = last_msg_data.get('time', '')
            if not last_msg_time and 'timestamp' in last_msg_data:
                try:
                    dt = datetime.fromtimestamp(last_msg_data['timestamp'])
                    last_msg_time = dt.strftime("%H:%M")
                except:
                    last_msg_time = ""
        
        self.last_msg_label = QLabel(last_msg)
        self.last_msg_label.setFont(QFont("Segoe UI", int(12 * self.scale)))
        
        text_layout.addWidget(self.name_label)
        text_layout.addWidget(self.last_msg_label)
        
        layout.addWidget(self.avatar)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)
        right_layout.setSpacing(3)
        
        if last_msg_time:
            time_label = QLabel(last_msg_time)
            time_label.setFont(QFont("Segoe UI", int(10 * self.scale)))
            right_layout.addWidget(time_label)
        
        if unread_count > 0:
            unread_label = QLabel(str(unread_count))
            unread_label.setFont(QFont("Segoe UI", int(9 * self.scale), QFont.Bold))
            unread_label.setStyleSheet("""
                QLabel {
                    background: #3390EC;
                    color: white;
                    border-radius: 10px;
                    padding: 2px 6px;
                    min-width: 20px;
                }
            """)
            unread_label.setAlignment(Qt.AlignCenter)
            right_layout.addWidget(unread_label)
        
        layout.addLayout(right_layout)
        
        self.setLayout(layout)
        self.update_style(False)
        
    def update_style(self, selected):
        self.isSelected = selected
        palette = self.palette()
        if selected:
            palette.setColor(QPalette.Window, QColor(self.theme['list_sel']))
            self.name_label.setStyleSheet(f"color: {self.theme['text']}; font-weight: bold;")
            self.last_msg_label.setStyleSheet(f"color: {self.theme['text']};")
        else:
            palette.setColor(QPalette.Window, QColor(self.theme['list_bg']))
            self.name_label.setStyleSheet(f"color: {self.theme['text']};")
            self.last_msg_label.setStyleSheet(f"color: {self.theme['text_secondary']};")
        
        self.setPalette(palette)

    def enterEvent(self, event):
        if not self.isSelected:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(self.theme['list_hover']))
            self.setPalette(palette)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.isSelected:
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(self.theme['list_bg']))
            self.setPalette(palette)
        super().leaveEvent(event)

class SmoothScrollArea(QScrollArea):
    """Плавная прокрутка с автоскроллом"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border: none;")
        self.verticalScrollBar().setSingleStep(10)
        self.auto_scroll_enabled = True
        
    def enable_auto_scroll(self):
        """Включить автоскролл"""
        self.auto_scroll_enabled = True
        
    def disable_auto_scroll(self):
        """Выключить автоскролл (когда пользователь прокручивает вверх)"""
        self.auto_scroll_enabled = False
        
    def scroll_to_bottom_animated(self):
        """Плавная прокрутка вниз"""
        if self.auto_scroll_enabled:
            sb = self.verticalScrollBar()
            target_value = sb.maximum()
            
            animation = QPropertyAnimation(sb, b"value")
            animation.setDuration(300)
            animation.setStartValue(sb.value())
            animation.setEndValue(target_value)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()
    
    def wheelEvent(self, event):
        """Обработка прокрутки колесиком мыши"""
        super().wheelEvent(event)
        
        if event.angleDelta().y() > 0:
            self.disable_auto_scroll()
        elif self.verticalScrollBar().value() >= self.verticalScrollBar().maximum() - 50:
            self.enable_auto_scroll()


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telegram Login")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3390EC, stop:1 #2B5278);
                border-radius: 10px;
            }
            QLabel { 
                color: white; 
                font-family: 'Segoe UI'; 
            }
            QLineEdit { 
                padding: 12px; 
                border-radius: 8px; 
                background: rgba(255, 255, 255, 0.9); 
                color: #000000; 
                border: 1px solid rgba(255, 255, 255, 0.3); 
                font-size: 14px; 
            }
            QPushButton { 
                background: white; 
                color: #3390EC; 
                border-radius: 8px; 
                padding: 12px; 
                font-weight: bold; 
                font-size: 15px; 
            }
            QPushButton:hover { 
                background: #F0F0F0; 
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        icon = QLabel("✈️")
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Telegram Bot")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Connect your bot to start messaging")
        subtitle.setStyleSheet("font-size: 14px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Bot Token from @BotFather")
        
        self.btn = QPushButton("▶ Start Messaging")
        self.btn.clicked.connect(self.accept)
        
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(QLabel("Bot Token:"))
        layout.addWidget(self.token_input)
        layout.addSpacing(20)
        layout.addWidget(self.btn)
        layout.addStretch()
        
        self.setLayout(layout)

    def get_token(self):
        return self.token_input.text().strip()

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings")
        self.setFixedSize(400, 400)
        self.settings_data = current_settings or {}
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        theme_grp = QGroupBox("🎨 Appearance")
        t_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Blue"])
        self.theme_combo.setCurrentText(self.settings_data.get('theme', 'Light'))
        t_layout.addWidget(QLabel("Theme:"))
        t_layout.addWidget(self.theme_combo)
        
        t_layout.addWidget(QLabel("🔍 Interface Scale:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(80, 150)
        self.scale_slider.setValue(int(self.settings_data.get('scale', 1.0) * 100))
        self.scale_lbl = QLabel(f"{self.scale_slider.value()}%")
        self.scale_slider.valueChanged.connect(lambda v: self.scale_lbl.setText(f"{v}%"))
        
        scale_h = QHBoxLayout()
        scale_h.addWidget(self.scale_slider)
        scale_h.addWidget(self.scale_lbl)
        t_layout.addLayout(scale_h)
        theme_grp.setLayout(t_layout)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addWidget(theme_grp)
        layout.addStretch()
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        self.apply_theme()

    def apply_theme(self):
        theme_name = self.settings_data.get('theme', 'Light')
        theme = STYLES.get(theme_name, STYLES['Light'])
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {theme['bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme['border']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: {theme['text']};
                background: {theme['list_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {theme['text']};
            }}
            QComboBox {{
                background: {theme['input_bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 3px;
                padding: 5px;
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QPushButton {{
                background: {theme['accent']};
                color: white;
                border: 1px solid {theme['accent']};
                border-radius: 5px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background: #44A0FC;
            }}
            QPushButton#cancel_btn {{
                background: {theme['border']};
                border: 1px solid {theme['border']};
            }}
            QPushButton#cancel_btn:hover {{
                background: {theme['text_secondary']};
            }}
        """)

    def get_data(self):
        return {
            'theme': self.theme_combo.currentText(),
            'scale': self.scale_slider.value() / 100.0
        }


class TelegramClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.settings = QSettings("PyTelegram", "Config")
        self.load_settings()
        
        self.bot_token = ""
        self.current_chat_id = None
        self.worker = None
        self.is_logged_in = False
        
        self.check_login()
            
    def check_login(self):
        token = self.settings.value("bot_token", "")
        if not token:
            self.show_login_dialog()
        else:
            self.bot_token = token
            self.is_logged_in = True
            self.setup_ui()
            self.apply_theme()
            self.start_bot_worker()
    
    def show_login_dialog(self):
        dlg = LoginDialog()
        if dlg.exec_() == QDialog.Accepted:
            token = dlg.get_token()
            if token:
                self.settings.setValue("bot_token", token)
                self.bot_token = token
                self.is_logged_in = True
                self.setup_ui()
                self.apply_theme()
                self.start_bot_worker()
            else:
                sys.exit(0)
        else:
            sys.exit(0)
    
    def logout(self):
        """Выход из аккаунта"""
        reply = QMessageBox.question(self, "🚪 Logout", 
                                   "Are you sure you want to logout?\nAll local data will be cleared.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.worker:
                self.worker.stop()
                self.worker = None
            
            self.db.clear_all_data()
            
            self.settings.remove("bot_token")
            
            self.close()
            
            app = QApplication.instance()
            new_window = TelegramClient()
            new_window.show()
    
    def load_settings(self):
        self.app_scale = float(self.settings.value("scale", 1.0))
        self.current_theme = self.settings.value("theme", "Light")
        if self.current_theme not in STYLES:
            self.current_theme = "Light"
        self.theme_data = STYLES[self.current_theme]

    def setup_ui(self):
        self.setWindowTitle("Telegram Client")
        self.resize(int(1200 * self.app_scale), int(800 * self.app_scale))
        
        self.create_menu()
        
        self.central = QWidget()
        self.setCentralWidget(self.central)
        main_layout = QHBoxLayout(self.central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
        
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(int(380 * self.app_scale))
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0,0,0,0)
        
        self.left_header = QFrame()
        self.left_header.setFixedHeight(int(60 * self.app_scale))
        h_layout = QHBoxLayout(self.left_header)
        h_layout.setContentsMargins(15, 0, 15, 0)
        
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.clicked.connect(self.open_settings)
        
        self.left_title = QLabel("Telegram")
        self.left_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
        self.new_chat_btn = QPushButton("✏️")
        self.new_chat_btn.setFixedSize(40, 40)
        self.new_chat_btn.setToolTip("New chat")
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedSize(40, 40)
        self.search_btn.setToolTip("Search")
        
        h_layout.addWidget(self.menu_btn)
        h_layout.addWidget(self.left_title)
        h_layout.addStretch()
        h_layout.addWidget(self.new_chat_btn)
        h_layout.addWidget(self.search_btn)
        
        self.chat_list = QListWidget()
        self.chat_list.setFrameShape(QFrame.NoFrame)
        self.chat_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.chat_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_list.itemClicked.connect(self.load_chat)
        
        left_layout.addWidget(self.left_header)
        left_layout.addWidget(self.chat_list)
        

        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0,0,0,0)
        
        self.chat_header = QFrame()
        self.chat_header.setFixedHeight(int(60 * self.app_scale))
        ch_layout = QHBoxLayout(self.chat_header)
        ch_layout.setContentsMargins(15, 0, 15, 0)
        
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(40, 40)
        
        self.chat_avatar = AvatarLabel("", int(40 * self.app_scale))
        
        self.chat_title = QLabel("Select a chat")
        self.chat_title.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        
        self.chat_menu_btn = QPushButton("⋮")
        self.chat_menu_btn.setFixedSize(40, 40)
        self.chat_menu_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_menu_btn.customContextMenuRequested.connect(self.show_chat_menu)
        
        ch_layout.addWidget(self.back_btn)
        ch_layout.addWidget(self.chat_avatar)
        ch_layout.addWidget(self.chat_title)
        ch_layout.addStretch()
        ch_layout.addWidget(self.chat_menu_btn)
        

        self.scroll_area = SmoothScrollArea()
        self.msg_container = QWidget()
        self.msg_layout = QVBoxLayout(self.msg_container)
        self.msg_layout.addStretch()
        self.scroll_area.setWidget(self.msg_container)

        self.input_area = QFrame()
        self.input_area.setFixedHeight(int(70 * self.app_scale))
        in_layout = QHBoxLayout(self.input_area)
        in_layout.setContentsMargins(15, 10, 15, 10)
        
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setFixedSize(40, 40)
        self.attach_btn.clicked.connect(self.attach_file)
        self.attach_btn.setToolTip("Attach file")
        
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Write a message...")
        self.msg_input.returnPressed.connect(self.send_text)
        
        self.emoji_btn = QPushButton("😊")
        self.emoji_btn.setFixedSize(40, 40)
        self.emoji_btn.setToolTip("Emoji")
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.clicked.connect(self.send_text)
        self.send_btn.setToolTip("Send message")
        
        in_layout.addWidget(self.attach_btn)
        in_layout.addWidget(self.msg_input)
        in_layout.addWidget(self.emoji_btn)
        in_layout.addWidget(self.send_btn)
        
        right_layout.addWidget(self.chat_header)
        right_layout.addWidget(self.scroll_area)
        right_layout.addWidget(self.input_area)
        
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.right_panel)

        self.refresh_chats()

    def create_menu(self):
        """Создает главное меню"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu('📁 File')
        
        logout_action = QAction('🚪 Logout', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction('❌ Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu('✏️ Edit')
        
        settings_action = QAction('⚙️ Settings', self)
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)

        view_menu = menubar.addMenu('👁️ View')
        
        refresh_action = QAction('🔄 Refresh', self)
        refresh_action.triggered.connect(self.refresh_chats)
        view_menu.addAction(refresh_action)

        help_menu = menubar.addMenu('❓ Help')
        
        about_action = QAction('ℹ️ About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def apply_theme(self):
        t = self.theme_data

        self.setStyleSheet(f"""
            QMainWindow {{
                background: {t['bg']};
            }}
            QMenuBar {{
                background: {t['bg']};
                color: {t['text']};
                border-bottom: 1px solid {t['border']};
            }}
            QMenuBar::item:selected {{
                background: {t['list_hover']};
            }}
            QMenu {{
                background: {t['list_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
            QMenu::item:selected {{
                background: {t['list_hover']};
            }}
        """)

        self.left_panel.setStyleSheet(f"background: {t['list_bg']};")

        self.left_header.setStyleSheet(f"""
            QFrame {{
                background: {t['accent']};
                border: none;
            }}
            QPushButton {{
                background: transparent;
                border: none;
                color: white;
                font-size: 18px;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.1);
            }}
        """)

        self.chat_list.setStyleSheet(f"""
            QListWidget {{
                background: {t['list_bg']};
                color: {t['text']};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                border: none;
                background: transparent;
            }}
            QListWidget::item:hover {{
                background: {t['list_hover']};
            }}
            QListWidget::item:selected {{
                background: {t['list_sel']};
            }}
            QScrollBar:vertical {{
                background: {t['list_bg']};
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['border']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['text_secondary']};
            }}
        """)

        self.chat_header.setStyleSheet(f"""
            QFrame {{
                background: {t['bg']};
                border-bottom: 1px solid {t['border']};
            }}
            QPushButton {{
                background: transparent;
                border: none;
                color: {t['text']};
                font-size: 18px;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background: rgba(0,0,0,0.1);
            }}
        """)

        self.input_area.setStyleSheet(f"""
            QFrame {{
                background: {t['bg']};
                border-top: 1px solid {t['border']};
            }}
            QPushButton {{
                background: transparent;
                border: none;
                color: {t['text']};
                font-size: 18px;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background: rgba(0,0,0,0.1);
            }}
            QPushButton#send_btn {{
                background: {t['accent']};
                color: white;
            }}
            QPushButton#send_btn:hover {{
                background: #44A0FC;
            }}
            QLineEdit {{
                background: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 14px;
            }}
        """)
        
        self.send_btn.setObjectName("send_btn")

        self.right_panel.setStyleSheet(f"background: {t['chat_bg']};")
        self.chat_title.setStyleSheet(f"color: {t['text']};")

        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            widget = self.chat_list.itemWidget(item)
            if widget:
                widget.update_style(item.isSelected())

    def start_bot_worker(self):
        """Запускает worker для получения сообщений"""
        if self.worker:
            self.worker.stop()
        
        self.worker = BotWorker(self.bot_token)
        self.worker.new_message.connect(self.on_new_message)
        self.worker.connection_status.connect(self.update_status)
        self.worker.photo_received.connect(self.on_photo_received)
        self.worker.start()

    def refresh_chats(self):
        self.chat_list.clear()
        chats = self.db.get_chats()
        for cid, data in chats.items():
            widget = ChatListItem(cid, data, self.theme_data, self.app_scale)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, cid)
            self.chat_list.addItem(item)
            self.chat_list.setItemWidget(item, widget)

    def load_chat(self, item):
        chat_id = item.data(Qt.UserRole)
        self.current_chat_id = chat_id

        chats = self.db.get_chats()
        chat_data = chats.get(chat_id, {})
        
        first_name = chat_data.get('first_name', '')
        last_name = chat_data.get('last_name', '')
        username = chat_data.get('username', '')
        
        name = f"{first_name} {last_name}".strip()
        if not name:
            name = username if username else str(chat_id)
        
        self.chat_title.setText(name)
        self.chat_avatar.setText(name[0].upper() if name else "?")

        self.clear_message_area()

        msgs = self.db.get_messages(chat_id)
        for msg in msgs:
            self.add_message_bubble(msg, animate=False)

        self.scroll_area.enable_auto_scroll()
        QTimer.singleShot(100, self.scroll_area.scroll_to_bottom_animated)

    def clear_message_area(self):
        while self.msg_layout.count() > 1:
            item = self.msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_message_bubble(self, msg_data, animate=True):
        bubble = MessageBubble(msg_data, self.theme_data, self.app_scale)
        bubble.setContextMenuPolicy(Qt.CustomContextMenu)
        bubble.customContextMenuRequested.connect(lambda pos, msg=msg_data: self.show_message_menu(msg, pos))
        
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(int(10 * self.app_scale), int(5 * self.app_scale), 
                                         int(10 * self.app_scale), int(5 * self.app_scale))
        
        if msg_data.get('out', False):
            wrapper_layout.addStretch()
            wrapper_layout.addWidget(bubble)
        else:
            wrapper_layout.addWidget(bubble)
            wrapper_layout.addStretch()
            
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, wrapper)
        
        if animate:
            effect = QGraphicsDropShadowEffect(bubble)
            effect.setBlurRadius(10)
            effect.setColor(QColor(0,0,0,50))
            bubble.setGraphicsEffect(effect)
            
            anim = QPropertyAnimation(wrapper, b"windowOpacity")
            anim.setDuration(300)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.start()

            if self.scroll_area.auto_scroll_enabled:
                QTimer.singleShot(50, self.scroll_area.scroll_to_bottom_animated)

    def send_text(self):
        txt = self.msg_input.text().strip()
        if not txt or not self.current_chat_id: 
            return

        msg_data = {
            'id': int(datetime.now().timestamp() * 1000),
            'text': txt,
            'out': True,
            'time': datetime.now().strftime("%H:%M"),
            'type': 'text',
            'timestamp': datetime.now().timestamp()
        }
        self.db.save_message(self.current_chat_id, txt, True, 'text')
        self.add_message_bubble(msg_data)
        self.msg_input.clear()
        
        # 2. Network Send
        self.sender_thread = SendWorker(self.bot_token, self.current_chat_id, text=txt)
        self.sender_thread.start()

    def attach_file(self):
        if not self.current_chat_id: 
            return
        
        path, _ = QFileDialog.getOpenFileName(self, "📁 Send File", "", 
                                             "All Files (*);;Images (*.png *.jpg *.jpeg);;Documents (*.pdf *.doc *.docx)")
        if path:
            filename = os.path.basename(path)
            ext = os.path.splitext(path)[1].lower()
            
            if ext in ['.png', '.jpg', '.jpeg']:
                msg_type = "photo"
                display_text = "🖼️ Photo"
                with open(path, 'rb') as f:
                    photo_data = f.read()
                self.db.save_message(self.current_chat_id, display_text, True, msg_type, 
                                    file_path=path, file_name=filename, photo_data=photo_data)
            else:
                msg_type = "document"
                display_text = f"📎 {filename}"
                self.db.save_message(self.current_chat_id, display_text, True, msg_type, 
                                    file_path=path, file_name=filename)

            msg_data = {
                'id': int(datetime.now().timestamp() * 1000),
                'text': display_text,
                'out': True,
                'time': datetime.now().strftime("%H:%M"),
                'type': msg_type,
                'timestamp': datetime.now().timestamp(),
                'file_name': filename
            }
            
            if msg_type == 'photo' and 'photo_path' in msg_data:
                msg_data['photo_path'] = os.path.join(self.db.db_path, "photos_cache", 
                                                     f"photo_{msg_data['id']}.jpg")
            
            self.add_message_bubble(msg_data)
            

            self.sender_thread = SendWorker(self.bot_token, self.current_chat_id, file_path=path)
            self.sender_thread.start()

    def on_new_message(self, data):
        self.refresh_chats()
        if str(data.get('chat_id', '')) == str(self.current_chat_id):
            msgs = self.db.get_messages(self.current_chat_id)
            if msgs:
                self.add_message_bubble(msgs[-1])

    def on_photo_received(self, chat_id, photo_data):
        """Обработка полученного фото"""
        if str(chat_id) == str(self.current_chat_id):

            self.refresh_chats()
            msgs = self.db.get_messages(self.current_chat_id)
            if msgs:
                self.add_message_bubble(msgs[-1])

    def update_status(self, connected):
        status = "🟢 Online" if connected else "🔴 Offline"
        self.setWindowTitle(f"Telegram Client - {status}")

    def open_settings(self):
        curr = {
            'theme': self.current_theme,
            'scale': self.app_scale
        }
        dlg = SettingsDialog(self, curr)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            self.settings.setValue("theme", data['theme'])
            self.settings.setValue("scale", data['scale'])
            
            QMessageBox.information(self, "🔄 Restart Required", "Please restart the app to apply changes.")
            self.load_settings()
            self.apply_theme()

    def show_about(self):
        """Показывает информацию о программе"""
        QMessageBox.about(self, "ℹ️ About", 
                         "Telegram Bot Client\n\n"
                         "Version: 2.0\n"
                         "A desktop client for Telegram bots\n\n"
                         "Features:\n"
                         "• Send and receive messages\n"
                         "• Photo sharing with preview\n"
                         "• Multiple themes\n"
                         "• Chat history\n"
                         "• File attachments\n\n"
                         "Created with PyQt5")

    def show_message_menu(self, message_data, pos):
        menu = QMenu(self)
        
        delete_action = QAction("🗑️ Delete Message", self)
        delete_action.triggered.connect(lambda: self.delete_message(message_data))
        menu.addAction(delete_action)
        

        if message_data.get('type') == 'photo' and 'photo_path' in message_data:
            view_photo_action = QAction("👁️ View Photo", self)
            view_photo_action.triggered.connect(lambda: self.view_photo(message_data['photo_path']))
            menu.addAction(view_photo_action)
        
        menu.exec_(self.mapToGlobal(pos))

    def view_photo(self, photo_path):
        """Открывает фото в программе просмотра по умолчанию"""
        if os.path.exists(photo_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(photo_path))

    def show_chat_menu(self, pos):
        if not self.current_chat_id:
            return
            
        menu = QMenu(self)
        
        clear_action = QAction("🧹 Clear History", self)
        clear_action.triggered.connect(self.clear_chat_history)
        menu.addAction(clear_action)
        
        info_action = QAction("ℹ️ Chat Info", self)
        info_action.triggered.connect(self.show_chat_info)
        menu.addAction(info_action)
        
        menu.exec_(self.mapToGlobal(pos))

    def show_chat_info(self):
        """Показывает информацию о чате"""
        if not self.current_chat_id:
            return
            
        chats = self.db.get_chats()
        chat_data = chats.get(str(self.current_chat_id), {})
        
        first_name = chat_data.get('first_name', '')
        last_name = chat_data.get('last_name', '')
        username = chat_data.get('username', '')
        
        name = f"{first_name} {last_name}".strip()
        if not name:
            name = username if username else str(self.current_chat_id)
        
        messages = self.db.get_messages(self.current_chat_id)
        total_messages = len(messages)
        your_messages = sum(1 for msg in messages if msg.get('out', False))
        their_messages = total_messages - your_messages
        
        info_text = f"""
        <h3>{name}</h3>
        <p><b>ID:</b> {self.current_chat_id}</p>
        <p><b>Username:</b> @{username if username else 'N/A'}</p>
        <hr>
        <p><b>Total messages:</b> {total_messages}</p>
        <p><b>Your messages:</b> {your_messages}</p>
        <p><b>Their messages:</b> {their_messages}</p>
        """
        
        QMessageBox.information(self, "ℹ️ Chat Info", info_text)

    def delete_message(self, message_data):
        if not self.current_chat_id:
            return
            
        reply = QMessageBox.question(self, "🗑️ Delete Message", 
                                   "Are you sure you want to delete this message?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.db.delete_message(self.current_chat_id, message_data.get('id', 0))
            if success:
                self.load_chat_by_id(self.current_chat_id)
            else:
                QMessageBox.warning(self, "❌ Error", "Failed to delete message")

    def clear_chat_history(self):
        if not self.current_chat_id:
            return
            
        reply = QMessageBox.question(self, "🧹 Clear History", 
                                   "Are you sure you want to clear all messages in this chat?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.db.clear_chat(self.current_chat_id)
            if success:
                self.clear_message_area()
                self.msg_layout.addStretch()
            else:
                QMessageBox.warning(self, "❌ Error", "Failed to clear chat history")

    def load_chat_by_id(self, chat_id):
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            if item.data(Qt.UserRole) == chat_id:
                self.chat_list.setCurrentItem(item)
                self.load_chat(item)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    w = TelegramClient()
    w.show()
    sys.exit(app.exec_())
