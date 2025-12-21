(function() {
  'use strict';

  const ThemeManager = {
    STORAGE_KEY: 'theme',
    THEME_LIGHT: 'light',
    THEME_DARK: 'dark',
    ATTR_NAME: 'data-theme',

    init: function() {
      this.loadTheme();
      this.attachToggleListeners();
    },

    loadTheme: function() {
      let savedTheme = localStorage.getItem(this.STORAGE_KEY);
      
      if (!savedTheme) {
        const oldDarkMode = localStorage.getItem('darkMode');
        if (oldDarkMode === 'enabled' || oldDarkMode === 'true') {
          savedTheme = this.THEME_DARK;
          localStorage.removeItem('darkMode');
        } else {
          savedTheme = this.THEME_LIGHT;
        }
      }
      
      this.setTheme(savedTheme);
    },

    setTheme: function(theme) {
      const root = document.documentElement;
      if (theme === this.THEME_DARK) {
        root.setAttribute(this.ATTR_NAME, this.THEME_DARK);
      } else {
        root.setAttribute(this.ATTR_NAME, this.THEME_LIGHT);
      }
      localStorage.setItem(this.STORAGE_KEY, theme);
      this.updateIcons(theme === this.THEME_DARK);
    },

    toggleTheme: function() {
      const currentTheme = document.documentElement.getAttribute(this.ATTR_NAME) || this.THEME_LIGHT;
      const newTheme = currentTheme === this.THEME_DARK ? this.THEME_LIGHT : this.THEME_DARK;
      this.setTheme(newTheme);
    },

    updateIcons: function(isDark) {
      const iconClass = isDark ? 'fa-moon' : 'fa-sun';
      const buttons = document.querySelectorAll('#darkToggleDesktop, #darkToggleMobile');
      
      buttons.forEach(function(btn) {
        if (!btn) return;
        const icon = btn.querySelector('i');
        if (!icon) return;
        icon.classList.remove('fa-moon', 'fa-sun');
        icon.classList.add(iconClass);
      });
    },

    attachToggleListeners: function() {
      const desktopBtn = document.getElementById('darkToggleDesktop');
      const mobileBtn = document.getElementById('darkToggleMobile');
      
      if (desktopBtn) {
        desktopBtn.addEventListener('click', () => this.toggleTheme());
      }
      
      if (mobileBtn) {
        mobileBtn.addEventListener('click', () => this.toggleTheme());
      }
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
  } else {
    ThemeManager.init();
  }
})();

