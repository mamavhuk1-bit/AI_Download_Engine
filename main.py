import os
import time
import threading
import requests
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
    DOWNLOAD_DIR = os.path.join(primary_external_storage_path(), 'Download', 'AIDownloadEngine')
else:
    DOWNLOAD_DIR = os.path.join(os.path.expanduser('~'), 'Downloads', 'AIDownloadEngine')

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

THEMES = {
    "1. Cyber Neon": {"bg": [0.05, 0.07, 0.14, 1], "glass": [0.12, 0.16, 0.28, 0.65], "accent": [0.0, 0.95, 0.85, 1]},
    "2. Royal Purple": {"bg": [0.10, 0.04, 0.18, 1], "glass": [0.20, 0.10, 0.35, 0.65], "accent": [0.75, 0.35, 1.0, 1]},
    "3. Emerald Glass": {"bg": [0.03, 0.12, 0.10, 1], "glass": [0.08, 0.25, 0.20, 0.65], "accent": [0.15, 0.95, 0.55, 1]},
    "4. Sunset Amber": {"bg": [0.16, 0.06, 0.04, 1], "glass": [0.30, 0.14, 0.10, 0.65], "accent": [1.0, 0.55, 0.15, 1]},
    "5. Ocean Deep": {"bg": [0.02, 0.09, 0.16, 1], "glass": [0.06, 0.20, 0.34, 0.65], "accent": [0.20, 0.70, 1.0, 1]},
    "6. Crimson Dark": {"bg": [0.14, 0.02, 0.05, 1], "glass": [0.28, 0.06, 0.12, 0.65], "accent": [1.0, 0.22, 0.38, 1]},
    "7. Midnight Gold": {"bg": [0.08, 0.08, 0.08, 1], "glass": [0.18, 0.17, 0.14, 0.70], "accent": [1.0, 0.80, 0.20, 1]},
    "8. Arctic Frost": {"bg": [0.12, 0.16, 0.22, 1], "glass": [0.25, 0.32, 0.42, 0.65], "accent": [0.55, 0.88, 1.0, 1]},
    "9. Matrix Green": {"bg": [0.02, 0.06, 0.02, 1], "glass": [0.06, 0.16, 0.06, 0.65], "accent": [0.20, 1.0, 0.20, 1]},
    "10. Rose Quartz": {"bg": [0.15, 0.07, 0.12, 1], "glass": [0.28, 0.15, 0.23, 0.65], "accent": [1.0, 0.45, 0.72, 1]},
}

KV = '''
<GlassCard@BoxLayout>:
    orientation: 'vertical'
    padding: dp(14)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: app.glass_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(18),]
        Color:
            rgba: [1, 1, 1, 0.18]
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(18))
            width: 1.1

<DownloadItemWidget>:
    size_hint_y: None
    height: dp(135)
    GlassCard:
        BoxLayout:
            size_hint_y: None
            height: dp(28)
            Label:
                text: root.filename
                bold: True
                font_size: '15sp'
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                shorten: True
                color: [1, 1, 1, 1]
            Label:
                text: root.speed_text
                bold: True
                font_size: '13sp'
                size_hint_x: None
                width: dp(95)
                halign: 'right'
                color: app.accent_color

        Widget:
            size_hint_y: None
            height: dp(10)
            canvas:
                Color:
                    rgba: [1, 1, 1, 0.12]
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(5),]
                Color:
                    rgba: app.accent_color
                RoundedRectangle:
                    pos: self.pos
                    size: (self.width * (root.progress / 100.0), self.height)
                    radius: [dp(5),]

        BoxLayout:
            size_hint_y: None
            height: dp(14)
            spacing: dp(3)
            Label:
                text: "8-Chunks:"
                font_size: '11sp'
                size_hint_x: None
                width: dp(58)
                color: [0.8, 0.8, 0.8, 0.9]
            ProgressBar:
                max: 100
                value: root.c1
            ProgressBar:
                max: 100
                value: root.c2
            ProgressBar:
                max: 100
                value: root.c3
            ProgressBar:
                max: 100
                value: root.c4
            ProgressBar:
                max: 100
                value: root.c5
            ProgressBar:
                max: 100
                value: root.c6
            ProgressBar:
                max: 100
                value: root.c7
            ProgressBar:
                max: 100
                value: root.c8

        BoxLayout:
            size_hint_y: None
            height: dp(26)
            Label:
                text: root.status_text
                font_size: '12sp'
                halign: 'left'
                text_size: self.size
                color: [0.85, 0.9, 0.95, 0.85]
            Button:
                text: "Pause" if not root.is_paused else "Resume"
                size_hint_x: None
                width: dp(70)
                font_size: '12sp'
                background_normal: ''
                background_color: [1, 1, 1, 0.15]
                on_release: root.toggle_pause()

ScreenManager:
    MainScreen:
    AboutScreen:

<MainScreen>:
    name: 'main'
    canvas.before:
        Color:
            rgba: app.bg_color
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: dp(14)
        spacing: dp(12)

        GlassCard:
            size_hint_y: None
            height: dp(76)
            orientation: 'horizontal'
            spacing: dp(12)

            Widget:
                size_hint: None, None
                size: dp(46), dp(46)
                pos_hint: {'center_y': 0.5}
                canvas:
                    Color:
                        rgba: app.accent_color
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(14),]
                    Color:
                        rgba: app.bg_color
                    Triangle:
                        points: [self.x + dp(14), self.y + dp(26), self.x + dp(32), self.y + dp(26), self.x + dp(23), self.y + dp(12)]
                    Rectangle:
                        pos: (self.x + dp(20), self.y + dp(26))
                        size: (dp(6), dp(10))

            BoxLayout:
                orientation: 'vertical'
                pos_hint: {'center_y': 0.5}
                Label:
                    text: "AI Download Engine"
                    bold: True
                    font_size: '18sp'
                    halign: 'left'
                    text_size: self.size
                Label:
                    text: "Multi-Thread Turbo Accelerator"
                    font_size: '11sp'
                    halign: 'left'
                    text_size: self.size
                    color: app.accent_color

            Button:
                text: "About"
                size_hint: None, None
                size: dp(68), dp(36)
                pos_hint: {'center_y': 0.5}
                background_normal: ''
                background_color: app.accent_color
                color: [0, 0, 0, 1]
                bold: True
                on_release: root.manager.current = 'about'

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(8)
            Label:
                text: "Glass Theme:"
                size_hint_x: None
                width: dp(95)
                font_size: '13sp'
                bold: True
            Spinner:
                id: theme_spinner
                text: "1. Cyber Neon"
                values: app.theme_names
                background_normal: ''
                background_color: app.glass_color
                on_text: app.change_theme(self.text)

        GlassCard:
            size_hint_y: None
            height: dp(112)
            TextInput:
                id: url_input
                hint_text: "Paste direct download link (URL) here..."
                multiline: False
                background_normal: ''
                background_color: [0, 0, 0, 0.35]
                foreground_color: [1, 1, 1, 1]
                hint_text_color: [0.7, 0.7, 0.7, 0.8]
                padding: [dp(12), dp(10)]
                font_size: '14sp'

            BoxLayout:
                spacing: dp(10)
                Button:
                    text: "START TURBO DOWNLOAD (8X)"
                    bold: True
                    background_normal: ''
                    background_color: app.accent_color
                    color: [0, 0, 0, 1]
                    on_release: root.start_download(url_input.text)
                Button:
                    text: "Clear"
                    size_hint_x: 0.3
                    background_normal: ''
                    background_color: [1, 1, 1, 0.15]
                    on_release: url_input.text = ""

        ScrollView:
            BoxLayout:
                id: download_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)

<AboutScreen>:
    name: 'about'
    canvas.before:
        Color:
            rgba: app.bg_color
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(16)

        GlassCard:
            Label:
                text: "AI Download Engine"
                font_size: '24sp'
                bold: True
                color: app.accent_color
            Label:
                text: "Version 1.0 Pro • 8-Thread Segmented Engine"
                font_size: '13sp'
                color: [0.85, 0.85, 0.85, 1]
            Widget:
                size_hint_y: None
                height: dp(10)
            Label:
                text: "Developed & Architected By:"
                font_size: '14sp'
                color: [0.75, 0.8, 0.85, 1]
            Label:
                text: "Akter Hossain & Gemini AI"
                font_size: '20sp'
                bold: True
                color: [1, 1, 1, 1]
            Label:
                text: "Features:\n• IDM-Style 8-Part Parallel Chunk Downloader\n• Real-Time Speedometer & Segment Monitor\n• Smooth Glassmorphism UI with 10 Live Themes\n• Automatic File Merging & Resume Support"
                halign: 'center'
                font_size: '13sp'
                color: [0.9, 0.92, 0.95, 0.9]

        Button:
            text: "BACK TO DOWNLOADS"
            size_hint_y: None
            height: dp(48)
            bold: True
            background_normal: ''
            background_color: app.accent_color
            color: [0, 0, 0, 1]
            on_release: root.manager.current = 'main'
'''

class DownloadItemWidget(BoxLayout):
    filename = StringProperty("Preparing...")
    speed_text = StringProperty("0.00 MB/s")
    status_text = StringProperty("Connecting...")
    progress = NumericProperty(0)
    c1 = NumericProperty(0)
    c2 = NumericProperty(0)
    c3 = NumericProperty(0)
    c4 = NumericProperty(0)
    c5 = NumericProperty(0)
    c6 = NumericProperty(0)
    c7 = NumericProperty(0)
    c8 = NumericProperty(0)
    is_paused = BooleanProperty(False)

    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.url = url.strip()
        self.num_threads = 8
        self.chunk_downloaded = [0] * self.num_threads
        self.chunk_sizes = [1] * self.num_threads
        self.total_size = 0
        self.last_bytes = 0
        self.last_time = time.time()
        self.active = True

        threading.Thread(target=self.prepare_and_download, daemon=True).start()
        Clock.schedule_interval(self.update_stats, 0.4)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.status_text = "Paused" if self.is_paused else "Downloading..."

    def format_size(self, b):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if b < 1024:
                return f"{b:.2f} {unit}"
            b /= 1024
        return f"{b:.2f} TB"

    def prepare_and_download(self):
        try:
            head = requests.head(self.url, allow_redirects=True, timeout=15)
            self.total_size = int(head.headers.get('content-length', 0))
            accept_ranges = head.headers.get('accept-ranges', 'none')

            fname = self.url.split('/')[-1].split('?')[0] or f"file_{int(time.time())}.bin"
            self.set_filename(fname)
            filepath = os.path.join(DOWNLOAD_DIR, fname)

            if self.total_size > 0 and accept_ranges == 'bytes':
                part_size = self.total_size // self.num_threads
                threads = []
                for i in range(self.num_threads):
                    start = i * part_size
                    end = self.total_size - 1 if i == self.num_threads - 1 else (start + part_size - 1)
                    self.chunk_sizes[i] = (end - start) + 1
                    t = threading.Thread(target=self.download_chunk, args=(i, start, end, filepath))
                    threads.append(t)
                    t.start()

                for t in threads:
                    t.join()

                if self.active:
                    self.merge_files(filepath)
            else:
                self.chunk_sizes = [max(self.total_size, 1)] + [1]*7
                self.download_chunk(0, 0, self.total_size - 1 if self.total_size else None, filepath, single=True)
                if self.active:
                    os.rename(f"{filepath}.part0", filepath)
                    self.finish_download()

        except Exception as e:
            self.set_error(str(e))

    def download_chunk(self, idx, start, end, filepath, single=False):
        headers = {'Range': f'bytes={start}-{end}'} if not single else {}
        part_file = f"{filepath}.part{idx}"
        try:
            with requests.get(self.url, headers=headers, stream=True, timeout=20) as r:
                r.raise_for_status()
                with open(part_file, 'wb') as f:
                    for data in r.iter_content(chunk_size=65536):
                        while self.is_paused and self.active:
                            time.sleep(0.2)
                        if not self.active:
                            return
                        if data:
                            f.write(data)
                            self.chunk_downloaded[idx] += len(data)
        except Exception as e:
            self.set_error(f"Thread {idx+1} error: {e}")

    def merge_files(self, filepath):
        self.update_status("Merging 8 segments...")
        with open(filepath, 'wb') as outfile:
            for i in range(self.num_threads):
                part_file = f"{filepath}.part{i}"
                if os.path.exists(part_file):
                    with open(part_file, 'rb') as infile:
                        outfile.write(infile.read())
                    os.remove(part_file)
        self.finish_download()

    @mainthread
    def set_filename(self, name):
        self.filename = name

    @mainthread
    def update_status(self, text):
        self.status_text = text

    @mainthread
    def set_error(self, err):
        self.active = False
        self.status_text = f"Error: {err[:35]}"
        self.speed_text = "0.00 MB/s"

    @mainthread
    def finish_download(self):
        self.active = False
        self.progress = 100
        self.c1 = self.c2 = self.c3 = self.c4 = self.c5 = self.c6 = self.c7 = self.c8 = 100
        self.speed_text = "Completed"
        self.status_text = f"Saved ({self.format_size(self.total_size)})"

    def update_stats(self, dt):
        if not self.active:
            return False
        total_dl = sum(self.chunk_downloaded)
        now = time.time()
        elapsed = max(now - self.last_time, 0.01)
        speed = (total_dl - self.last_bytes) / elapsed
        self.last_bytes = total_dl
        self.last_time = now

        self.speed_text = f"{self.format_size(speed)}/s"
        if self.total_size > 0:
            self.progress = min((total_dl / self.total_size) * 100, 99.9)
            self.status_text = f"{self.format_size(total_dl)} / {self.format_size(self.total_size)} ({self.progress:.1f}%)"
        else:
            self.status_text = f"Downloaded: {self.format_size(total_dl)}"

        for i in range(8):
            pct = min((self.chunk_downloaded[i] / max(self.chunk_sizes[i], 1)) * 100, 100)
            setattr(self, f"c{i+1}", pct)

class MainScreen(Screen):
    def start_download(self, url):
        if url.strip().startswith("http"):
            item = DownloadItemWidget(url)
            self.ids.download_list.add_widget(item, index=0)
            self.ids.url_input.text = ""

class AboutScreen(Screen):
    pass

class AIDownloadEngineApp(App):
    bg_color = ListProperty(THEMES["1. Cyber Neon"]["bg"])
    glass_color = ListProperty(THEMES["1. Cyber Neon"]["glass"])
    accent_color = ListProperty(THEMES["1. Cyber Neon"]["accent"])
    theme_names = ListProperty(list(THEMES.keys()))

    def build(self):
        self.title = "AI Download Engine"
        return Builder.load_string(KV)

    def change_theme(self, theme_name):
        if theme_name in THEMES:
            self.bg_color = THEMES[theme_name]["bg"]
            self.glass_color = THEMES[theme_name]["glass"]
            self.accent_color = THEMES[theme_name]["accent"]

if __name__ == '__main__':
    AIDownloadEngineApp().run()
