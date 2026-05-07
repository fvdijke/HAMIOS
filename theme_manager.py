THEMES = {
    "Midnight": {
        "BG_ROOT": "#1A1C1F",
        "BG_PANEL": "#22252A",
        "BG_SURFACE": "#2A2E35",
        "BG_HOVER": "#32373F",
        "ACCENT": "#C8A84B",
        "TEXT_H1": "#F0E6C8",
        "TEXT_BODY": "#B0B8C4",
        "TEXT_DIM": "#606870",
        "BORDER": "#383E47",
    },
    "DeepOcean": {
        "BG_ROOT": "#0A1A2A",
        "BG_PANEL": "#12253A",
        "BG_SURFACE": "#1B3550",
        "BG_HOVER": "#254568",
        "ACCENT": "#4BACC8",
        "TEXT_H1": "#E0F0F5",
        "TEXT_BODY": "#B0C8D4",
        "TEXT_DIM": "#608090",
        "BORDER": "#2A4A60",
    },
    "HighContrast": {
        "BG_ROOT": "#000000",
        "BG_PANEL": "#111111",
        "BG_SURFACE": "#222222",
        "BG_HOVER": "#444444",
        "ACCENT": "#FFFF00",
        "TEXT_H1": "#FFFFFF",
        "TEXT_BODY": "#EEEEEE",
        "TEXT_DIM": "#AAAAAA",
        "BORDER": "#FFFFFF",
    }
}

class ThemeManager:
    def __init__(self, settings):
        self.themes = THEMES
        self.current_theme_name = settings.get("theme", "Midnight")
        if self.current_theme_name not in self.themes:
            self.current_theme_name = "Midnight"

    def get_color(self, key):
        return self.themes[self.current_theme_name].get(key, "#000000")

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            return True
        return False
