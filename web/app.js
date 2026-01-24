function app() {
  return {
    API_BASE: 'http://127.0.0.1:8000',

    currentView: localStorage.getItem('lastView') || 'today',
    loading: { tasks: false, weather: false },

    tasks: [],
    overview: {},
    stats: {},
    weather: {
      current: {},
      hourly: [],
      daily: [],
      location: ''
    },

    newTask: { title: '', priority: 'normal', due_date: '', tags: '' },
    editingTask: null,
    filters: {
      q: '',
      tag: '',
      status: '',
      priority: '',
      sort: '-created_at'
    },

    selectedTasks: [],
    toasts: [],
    toastId: 0,

    weatherCodes: {
      0: '☀️ Ciel dégagé', 1: '🌤️ Dégagé', 2: '⛅ Nuageux', 3: '☁️ Couvert',
      45: '🌫️ Brouillard', 48: '🌫️ Brouillard givrant',
      51: '🌦️ Bruine', 53: '🌦️ Bruine modérée', 55: '🌦️ Bruine dense',
      61: '🌧️ Pluie légère', 63: '🌧️ Pluie', 65: '🌧️ Pluie forte',
      66: '🧊 Pluie verglaçante', 67: '🧊 Pluie verglaçante forte',
      71: '🌨️ Neige légère', 73: '🌨️ Neige', 75: '❄️ Neige forte',
      77: '🌨️ Grains de neige',
      80: '🌧️ Averses légères', 81: '🌧️ Averses', 82: '🌧️ Averses violentes',
      85: '🌨️ Averses de neige légères', 86: '🌨️ Averses de neige fortes',
      95: '⛈️ Orage', 96: '⛈️ Orage + grêle légère', 99: '⛈️ Orage + grêle forte'
    },

    hyperplanning: {
      schedule: { display_date: '', courses: [] },
      nextCourses: [],
      stats: [],
      grades: [],
      showImport: false,
      importInput: ''
    },

    email: {
      count: null,
      emails: [],
      error: '',
      showCompose: false,
      sending: false,
      compose: {
        to: '',
        subject: '',
        body: ''
      },
      selectedEmail: null,
      loadingEmail: false
    },

    spotify: {
      connected: false,
      loading: false,
      error: '',
      track: null,
      pollingInterval: null
    },

    theme: localStorage.getItem('theme') || 'auto',
    systemTheme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',

    clock: {
      time: '',
      date: '',
      interval: null
    },

    pomodoro: {
      minutes: 25,
      seconds: 0,
      isRunning: false,
      mode: 'work',
      completedPomodoros: 0,
      interval: null,
      workDuration: 25,
      breakDuration: 5,
      longBreakDuration: 15
    },

    quickNotes: localStorage.getItem('quickNotes') || '',

    favoriteLinks: JSON.parse(localStorage.getItem('favoriteLinks') || '[]'),
    showAddLink: false,
    newLink: { name: '', url: '' },

    countdowns: JSON.parse(localStorage.getItem('countdowns') || '[]'),
    showAddCountdown: false,
    newCountdown: { name: '', date: '' },

    importExport: {
      importing: false,
      exporting: false
    },

    taskViewMode: localStorage.getItem('taskViewMode') || 'list',
    draggingTask: null,

    availableTags: [],

    focusMode: localStorage.getItem('focusMode') === 'true',

    lofiPlayer: {
      show: false
    },

    // Gamification system
    gamification: JSON.parse(localStorage.getItem('gamification') || JSON.stringify({
      xp: 0,
      streak: 0,
      lastActiveDate: null,
      totalTasksCompleted: 0,
      totalPomodorosCompleted: 0,
      unlockedBadges: []
    })),

    badges: [
      { id: 'first_task', name: 'Premier pas', icon: '🎯', desc: 'Compléter sa première tâche', condition: (g) => g.totalTasksCompleted >= 1 },
      { id: 'task_10', name: 'Productif', icon: '⚡', desc: 'Compléter 10 tâches', condition: (g) => g.totalTasksCompleted >= 10 },
      { id: 'task_50', name: 'Machine', icon: '🤖', desc: 'Compléter 50 tâches', condition: (g) => g.totalTasksCompleted >= 50 },
      { id: 'task_100', name: 'Légende', icon: '🏆', desc: 'Compléter 100 tâches', condition: (g) => g.totalTasksCompleted >= 100 },
      { id: 'streak_3', name: 'En forme', icon: '🔥', desc: '3 jours consécutifs', condition: (g) => g.streak >= 3 },
      { id: 'streak_7', name: 'Semaine parfaite', icon: '💪', desc: '7 jours consécutifs', condition: (g) => g.streak >= 7 },
      { id: 'streak_30', name: 'Inarrêtable', icon: '👑', desc: '30 jours consécutifs', condition: (g) => g.streak >= 30 },
      { id: 'pomodoro_10', name: 'Concentré', icon: '🍅', desc: '10 pomodoros complétés', condition: (g) => g.totalPomodorosCompleted >= 10 },
      { id: 'pomodoro_50', name: 'Zen master', icon: '🧘', desc: '50 pomodoros complétés', condition: (g) => g.totalPomodorosCompleted >= 50 },
      { id: 'xp_500', name: 'Niveau up!', icon: '📈', desc: 'Atteindre 500 XP', condition: (g) => g.xp >= 500 },
      { id: 'xp_2000', name: 'Expert', icon: '🎓', desc: 'Atteindre 2000 XP', condition: (g) => g.xp >= 2000 }
    ],

    levels: [
      { level: 1, name: 'Débutant', icon: '🌱', minXp: 0 },
      { level: 2, name: 'Apprenti', icon: '🌿', minXp: 100 },
      { level: 3, name: 'Productif', icon: '🌳', minXp: 300 },
      { level: 4, name: 'Expert', icon: '⭐', minXp: 600 },
      { level: 5, name: 'Maître', icon: '🏆', minXp: 1000 },
      { level: 6, name: 'Légende', icon: '👑', minXp: 2000 }
    ],

    // Habit tracker
    habits: JSON.parse(localStorage.getItem('habits') || '[]'),
    habitHistory: JSON.parse(localStorage.getItem('habitHistory') || '{}'),
    showAddHabit: false,
    newHabit: { name: '', icon: '✅' },

    async init() {
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
          .then(() => console.log('[PWA] Service Worker registered'))
          .catch(err => console.warn('[PWA] Service Worker failed:', err));
      }

      this.loadFiltersFromStorage();
      this.initTheme();
      this.startClock();
      this.initGamification();
      await Promise.all([
        this.loadOverview(),
        this.loadTasks(),
        this.loadWeather(),
        this.loadStats(),
        this.loadHyperplanning(),
        this.loadEmail(),
        this.loadSpotify()
      ]);

      this.$watch('currentView', (view) => {
        localStorage.setItem('lastView', view);
      });

      document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    },

    handleKeyboard(e) {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        if (e.key === 'Escape') {
          document.activeElement.blur();
        }
        return;
      }

      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'n':
          case 'N':
            e.preventDefault();
            this.currentView = 'tasks';
            this.$nextTick(() => {
              document.querySelector('input[x-model="newTask.title"]')?.focus();
            });
            break;
          case '1':
            e.preventDefault();
            this.currentView = 'today';
            break;
          case '2':
            e.preventDefault();
            this.currentView = 'tasks';
            break;
          case '3':
            e.preventDefault();
            this.currentView = 'weather';
            break;
          case '4':
            e.preventDefault();
            this.currentView = 'hyperplanning';
            break;
          case '5':
            e.preventDefault();
            this.currentView = 'mail';
            break;
          case '6':
            e.preventDefault();
            this.currentView = 'settings';
            break;
        }
      }

      switch (e.key) {
        case 'Escape':
          this.selectedTasks = [];
          this.email.showCompose = false;
          this.hyperplanning.showImport = false;
          break;
        case 't':
          this.toggleTheme();
          break;
      }
    },

    async fetchJSON(url, options = {}) {
      try {
        const res = await fetch(url, {
          headers: { 'Accept': 'application/json' },
          ...options
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
      } catch (err) {
        this.showToast(`Erreur: ${err.message}`, 'error');
        throw err;
      }
    },

    async sendJSON(url, data, method = 'POST') {
      return this.fetchJSON(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
    },

    async loadOverview() {
      try {
        this.overview = await this.fetchJSON(`${this.API_BASE}/meta/overview`);
      } catch (err) {
        console.error('Overview error:', err);
      }
    },

    async refreshQuote() {
      try {
        const quote = await this.fetchJSON(`${this.API_BASE}/meta/quote`);
        this.overview.quote = quote.content;
        this.overview.quote_author = quote.author;
      } catch (err) {
        console.error('Quote refresh error:', err);
      }
    },

    async loadStats() {
      try {
        this.stats = await this.fetchJSON(`${this.API_BASE}/tasks/stats/summary`);
      } catch (err) {
        console.error('Stats error:', err);
      }
    },

    async loadTasks() {
      this.loading.tasks = true;
      try {
        const params = new URLSearchParams({
          ...this.filters,
          limit: 50,
          offset: 0
        });
        if (!this.filters.tag) params.delete('tag');
        this.tasks = await this.fetchJSON(`${this.API_BASE}/tasks?${params}`);
        this.extractTags();
        this.saveFiltersToStorage();
      } catch (err) {
        console.error('Tasks error:', err);
      } finally {
        this.loading.tasks = false;
      }
    },

    debouncedLoadTasks() {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => this.loadTasks(), 300);
    },

    async addTask() {
      if (!this.newTask.title.trim()) return;

      try {
        const payload = { ...this.newTask };
        if (payload.due_date) {
          payload.due_date = new Date(payload.due_date).toISOString();
        } else {
          delete payload.due_date;
        }
        if (!payload.tags?.trim()) {
          delete payload.tags;
        }
        await this.sendJSON(`${this.API_BASE}/tasks`, payload);
        this.newTask = { title: '', priority: 'normal', due_date: '', tags: '' };
        await this.loadTasks();
        await this.loadStats();
        this.showToast('Tâche ajoutée !', 'success');
      } catch (err) {
        this.showToast('Erreur lors de l\'ajout', 'error');
      }
    },

    extractTags() {
      const allTags = new Set();
      this.tasks.forEach(task => {
        if (task.tags) {
          task.tags.split(',').forEach(tag => {
            const trimmed = tag.trim();
            if (trimmed) allTags.add(trimmed);
          });
        }
      });
      this.availableTags = Array.from(allTags).sort();
    },

    getTaskTags(task) {
      if (!task.tags) return [];
      return task.tags.split(',').map(t => t.trim()).filter(t => t);
    },

    openEditTask(task) {
      this.editingTask = {
        ...task,
        due_date: task.due_date ? task.due_date.slice(0, 16) : '',
        _originalStatus: task.status // Store original status for gamification
      };
    },

    closeEditTask() {
      this.editingTask = null;
    },

    async saveEditTask() {
      if (!this.editingTask || !this.editingTask.title.trim()) return;

      try {
        const payload = {
          title: this.editingTask.title,
          description: this.editingTask.description,
          priority: this.editingTask.priority,
          status: this.editingTask.status,
          tags: this.editingTask.tags || null
        };
        if (this.editingTask.due_date) {
          payload.due_date = new Date(this.editingTask.due_date).toISOString();
        }
        // Check if task was completed (status changed to done)
        const wasCompleted = this.editingTask._originalStatus !== 'done' && this.editingTask.status === 'done';
        const taskForXP = { priority: this.editingTask.priority };

        await this.fetchJSON(`${this.API_BASE}/tasks/${this.editingTask.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        this.editingTask = null;
        await this.loadTasks();
        await this.loadStats();

        if (wasCompleted) {
          this.onTaskCompleted(taskForXP);
        } else {
          this.showToast('Tâche modifiée !', 'success');
        }
      } catch (err) {
        this.showToast('Erreur lors de la modification', 'error');
      }
    },

    async deleteTask(id) {
      if (!confirm('Supprimer cette tâche ?')) return;

      try {
        await fetch(`${this.API_BASE}/tasks/${id}`, { method: 'DELETE' });
        await this.loadTasks();
        await this.loadStats();
        this.showToast('Tâche supprimée', 'success');
      } catch (err) {
        this.showToast('Erreur lors de la suppression', 'error');
      }
    },

    addingSubtaskTo: null,
    newSubtaskTitle: '',

    openAddSubtask(task) {
      this.addingSubtaskTo = task.id;
      this.newSubtaskTitle = '';
    },

    closeAddSubtask() {
      this.addingSubtaskTo = null;
      this.newSubtaskTitle = '';
    },

    async addSubtask(parentId) {
      if (!this.newSubtaskTitle.trim()) return;

      try {
        await this.sendJSON(`${this.API_BASE}/tasks`, {
          title: this.newSubtaskTitle.trim(),
          parent_id: parentId,
          priority: 'normal'
        });
        this.closeAddSubtask();
        await this.loadTasks();
        this.showToast('Sous-tâche ajoutée !', 'success');
      } catch (err) {
        this.showToast('Erreur lors de l\'ajout', 'error');
      }
    },

    async toggleSubtaskStatus(subtask) {
      const newStatus = subtask.status === 'done' ? 'todo' : 'done';
      try {
        await this.fetchJSON(`${this.API_BASE}/tasks/${subtask.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        });
        await this.loadTasks();
      } catch (err) {
        this.showToast('Erreur lors de la mise à jour', 'error');
      }
    },

    async bulkDelete() {
      if (this.selectedTasks.length === 0) return;
      if (!confirm(`Supprimer ${this.selectedTasks.length} tâche(s) ?`)) return;

      try {
        await this.sendJSON(`${this.API_BASE}/tasks/bulk-delete`, { ids: this.selectedTasks }, 'POST');
        this.selectedTasks = [];
        await this.loadTasks();
        await this.loadStats();
        this.showToast('Tâches supprimées', 'success');
      } catch (err) {
        this.showToast('Erreur lors de la suppression groupée', 'error');
      }
    },

    toggleTaskSelection(id) {
      const index = this.selectedTasks.indexOf(id);
      if (index > -1) {
        this.selectedTasks.splice(index, 1);
      } else {
        this.selectedTasks.push(id);
      }
    },

    async loadWeather() {
      this.loading.weather = true;

      if (!('geolocation' in navigator)) {
        this.showToast('Géolocalisation non disponible', 'error');
        this.loading.weather = false;
        return;
      }

      try {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: false,
            timeout: 8000
          });
        });

        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const params = `lat=${lat}&lon=${lon}`;

        const [current, forecast, place] = await Promise.all([
          this.fetchJSON(`${this.API_BASE}/external/weather?${params}`),
          this.fetchJSON(`${this.API_BASE}/external/forecast?${params}`),
          this.fetchJSON(`${this.API_BASE}/external/reverse-geocode?${params}`).catch(() => null)
        ]);

        this.weather.current = current;
        this.weather.hourly = forecast.hourly || [];
        this.weather.daily = forecast.daily || [];
        this.weather.location = place ? `(${place.city || place.label})` : '';

      } catch (err) {
        console.error('Weather error:', err);
        this.showToast('Impossible de charger la météo', 'error');
      } finally {
        this.loading.weather = false;
      }
    },

    getWeatherDesc(code) {
      return this.weatherCodes[code] || `Code ${code}`;
    },

    async loadHyperplanning() {
      try {
        const [schedule, stats, nextCourses, grades] = await Promise.all([
          this.fetchJSON(`${this.API_BASE}/hyperplanning/courses`),
          this.fetchJSON(`${this.API_BASE}/hyperplanning/stats`),
          this.fetchJSON(`${this.API_BASE}/hyperplanning/next-courses`),
          this.fetchJSON(`${this.API_BASE}/hyperplanning/grades`)
        ]);

        if (Array.isArray(schedule)) {
             this.hyperplanning.schedule = { display_date: "Aujourd'hui", courses: schedule };
        } else {
             this.hyperplanning.schedule = schedule;
        }

        this.hyperplanning.stats = stats;
        this.hyperplanning.nextCourses = nextCourses;
        this.hyperplanning.grades = grades;
      } catch (err) {
        console.error('Hyperplanning error:', err);
        this.showToast('Erreur chargement emploi du temps', 'error');
      }
    },

    async loadEmail() {
      try {
        const data = await this.fetchJSON(`${this.API_BASE}/email/proton/unread`);
        this.email.count = data.count_unread;
        this.email.emails = data.emails || [];
        this.email.error = data.error || '';
      } catch (err) {
        console.error('Email error:', err);
        this.email.error = 'Impossible de charger';
      }
    },

    async sendEmail() {
      if (!this.email.compose.to || !this.email.compose.subject) {
        this.showToast('Veuillez remplir le destinataire et le sujet', 'warning');
        return;
      }

      this.email.sending = true;
      try {
        const result = await this.sendJSON(`${this.API_BASE}/email/proton/send`, {
          to: this.email.compose.to,
          subject: this.email.compose.subject,
          body: this.email.compose.body
        });

        if (result.success) {
          this.showToast('Email envoyé avec succès !', 'success');
          this.email.showCompose = false;
          this.email.compose = { to: '', subject: '', body: '' };
        } else {
          this.showToast(result.error || 'Erreur lors de l\'envoi', 'error');
        }
      } catch (err) {
        console.error('Send email error:', err);
        this.showToast('Erreur lors de l\'envoi de l\'email', 'error');
      } finally {
        this.email.sending = false;
      }
    },

    async openEmail(mail) {
      this.email.loadingEmail = true;
      this.email.selectedEmail = {
        id: mail.id,
        subject: mail.subject,
        sender: mail.sender,
        date: mail.date,
        body: '',
        html_body: null
      };

      try {
        const data = await this.fetchJSON(`${this.API_BASE}/email/proton/message/${mail.id}`);
        this.email.selectedEmail = data;
      } catch (err) {
        console.error('Error loading email:', err);
        this.email.selectedEmail.body = 'Erreur lors du chargement de l\'email';
      } finally {
        this.email.loadingEmail = false;
      }
    },

    closeEmail() {
      this.email.selectedEmail = null;
    },

    async importGrades() {
      try {
        const input = this.hyperplanning.importInput.trim();
        if (!input) {
          this.showToast('Veuillez entrer des notes au format JSON', 'warning');
          return;
        }

        let grades;
        try {
          grades = JSON.parse(input);
        } catch (e) {
          this.showToast('Format JSON invalide', 'error');
          return;
        }

        if (!Array.isArray(grades)) {
          this.showToast('Le JSON doit être un tableau de notes', 'error');
          return;
        }

        const result = await this.sendJSON(`${this.API_BASE}/hyperplanning/grades/import`, { grades });
        this.showToast(result.message, 'success');
        this.hyperplanning.showImport = false;
        this.hyperplanning.importInput = '';
        await this.loadHyperplanning();
      } catch (err) {
        console.error('Import grades error:', err);
        this.showToast('Erreur import notes', 'error');
      }
    },

    async clearGrades() {
      if (!confirm('Voulez-vous vraiment supprimer toutes les notes ?')) return;

      try {
        const result = await fetch(`${this.API_BASE}/hyperplanning/grades/clear`, { method: 'DELETE' });
        const data = await result.json();
        this.showToast(data.message, 'success');
        await this.loadHyperplanning();
      } catch (err) {
        console.error('Clear grades error:', err);
        this.showToast('Erreur suppression notes', 'error');
      }
    },

    async loadSpotify() {
      try {
        const status = await this.fetchJSON(`${this.API_BASE}/spotify/status`);
        this.spotify.connected = status.connected;
        this.spotify.error = status.error || '';

        if (status.connected) {
          await this.loadNowPlaying();
          this.startSpotifyPolling();
        }
      } catch (err) {
        console.error('Spotify status error:', err);
        this.spotify.error = 'Impossible de vérifier Spotify';
      }
    },

    async loadNowPlaying() {
      if (!this.spotify.connected) return;

      try {
        const data = await this.fetchJSON(`${this.API_BASE}/spotify/now-playing`);
        if (data.error && data.error !== 'Nothing playing') {
          this.spotify.error = data.error;
          this.spotify.track = null;
        } else if (data.track_name) {
          this.spotify.track = data;
          this.spotify.error = '';
        } else {
          this.spotify.track = null;
          this.spotify.error = '';
        }
      } catch (err) {
        console.error('Now playing error:', err);
      }
    },

    startSpotifyPolling() {
      if (this.spotify.pollingInterval) return;
      this.spotify.pollingInterval = setInterval(() => this.loadNowPlaying(), 5000);
    },

    stopSpotifyPolling() {
      if (this.spotify.pollingInterval) {
        clearInterval(this.spotify.pollingInterval);
        this.spotify.pollingInterval = null;
      }
    },

    spotifyLogin() {
      window.location.href = `${this.API_BASE}/spotify/login`;
    },

    async spotifyLogout() {
      try {
        await this.sendJSON(`${this.API_BASE}/spotify/logout`, {});
        this.spotify.connected = false;
        this.spotify.track = null;
        this.stopSpotifyPolling();
        this.showToast('Déconnecté de Spotify', 'success');
      } catch (err) {
        console.error('Spotify logout error:', err);
      }
    },

    async spotifyPlay() {
      try {
        await this.sendJSON(`${this.API_BASE}/spotify/play`, {});
        await this.loadNowPlaying();
      } catch (err) {
        console.error('Spotify play error:', err);
      }
    },

    async spotifyPause() {
      try {
        await this.sendJSON(`${this.API_BASE}/spotify/pause`, {});
        await this.loadNowPlaying();
      } catch (err) {
        console.error('Spotify pause error:', err);
      }
    },

    async spotifyNext() {
      try {
        await this.sendJSON(`${this.API_BASE}/spotify/next`, {});
        setTimeout(() => this.loadNowPlaying(), 300);
      } catch (err) {
        console.error('Spotify next error:', err);
      }
    },

    async spotifyPrevious() {
      try {
        await this.sendJSON(`${this.API_BASE}/spotify/previous`, {});
        setTimeout(() => this.loadNowPlaying(), 300);
      } catch (err) {
        console.error('Spotify previous error:', err);
      }
    },

    formatTime(ms) {
      if (!ms) return '0:00';
      const seconds = Math.floor(ms / 1000);
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    initTheme() {
      // Listen for system theme changes
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        this.systemTheme = e.matches ? 'dark' : 'light';
        if (this.theme === 'auto') {
          this.applyTheme();
        }
      });
      this.applyTheme();
    },

    applyTheme() {
      const effectiveTheme = this.theme === 'auto' ? this.systemTheme : this.theme;
      document.documentElement.setAttribute('data-theme', effectiveTheme);
    },

    toggleTheme() {
      // Cycle: dark -> light -> auto
      const themes = ['dark', 'light', 'auto'];
      const currentIndex = themes.indexOf(this.theme);
      this.theme = themes[(currentIndex + 1) % themes.length];
      localStorage.setItem('theme', this.theme);
      this.applyTheme();

      const labels = { dark: 'Sombre', light: 'Clair', auto: 'Automatique' };
      this.showToast(`Thème: ${labels[this.theme]}`, 'info');
    },

    getThemeIcon() {
      if (this.theme === 'auto') return '🔄';
      if (this.theme === 'dark') return '🌙';
      return '☀️';
    },

    toggleFocusMode() {
      this.focusMode = !this.focusMode;
      localStorage.setItem('focusMode', this.focusMode);
      if (this.focusMode) {
        this.showToast('Mode Focus activé - Concentre-toi ! 🎯', 'success');
      } else {
        this.showToast('Mode Focus désactivé', 'info');
      }
    },

    toggleLofiPlayer() {
      this.lofiPlayer.show = !this.lofiPlayer.show;
    },

    saveQuickNotes() {
      localStorage.setItem('quickNotes', this.quickNotes);
    },

    saveFavoriteLinks() {
      localStorage.setItem('favoriteLinks', JSON.stringify(this.favoriteLinks));
    },

    addFavoriteLink() {
      if (!this.newLink.name.trim() || !this.newLink.url.trim()) return;
      let url = this.newLink.url.trim();
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }
      this.favoriteLinks.push({
        id: Date.now(),
        name: this.newLink.name.trim(),
        url: url
      });
      this.saveFavoriteLinks();
      this.newLink = { name: '', url: '' };
      this.showAddLink = false;
    },

    removeFavoriteLink(id) {
      this.favoriteLinks = this.favoriteLinks.filter(link => link.id !== id);
      this.saveFavoriteLinks();
    },

    saveCountdowns() {
      localStorage.setItem('countdowns', JSON.stringify(this.countdowns));
    },

    addCountdown() {
      if (!this.newCountdown.name.trim() || !this.newCountdown.date) return;
      this.countdowns.push({
        id: Date.now(),
        name: this.newCountdown.name.trim(),
        date: this.newCountdown.date
      });
      this.saveCountdowns();
      this.newCountdown = { name: '', date: '' };
      this.showAddCountdown = false;
    },

    removeCountdown(id) {
      this.countdowns = this.countdowns.filter(c => c.id !== id);
      this.saveCountdowns();
    },

    getDaysRemaining(dateStr) {
      const target = new Date(dateStr);
      const now = new Date();
      now.setHours(0, 0, 0, 0);
      target.setHours(0, 0, 0, 0);
      const diff = target - now;
      return Math.ceil(diff / (1000 * 60 * 60 * 24));
    },

    formatCountdownDate(dateStr) {
      return new Date(dateStr).toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    },

    async exportData() {
      this.importExport.exporting = true;
      try {
        const data = {
          version: '1.0',
          exportedAt: new Date().toISOString(),
          tasks: this.tasks,
          quickNotes: this.quickNotes,
          favoriteLinks: this.favoriteLinks,
          countdowns: this.countdowns,
          theme: this.theme,
          filters: this.filters
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `autodesk-kiwi-backup-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('Données exportées avec succès', 'success');
      } catch (err) {
        console.error('Export error:', err);
        this.showToast('Erreur lors de l\'export', 'error');
      } finally {
        this.importExport.exporting = false;
      }
    },

    toggleTaskViewMode() {
      this.taskViewMode = this.taskViewMode === 'list' ? 'kanban' : 'list';
      localStorage.setItem('taskViewMode', this.taskViewMode);
    },

    onDragStart(event, task) {
      this.draggingTask = task;
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', task.id);
      event.target.classList.add('dragging');
    },

    onDragEnd(event) {
      event.target.classList.remove('dragging');
      this.draggingTask = null;
    },

    onDragOver(event) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
    },

    onDragEnter(event) {
      event.target.closest('.kanban-column')?.classList.add('drag-over');
    },

    onDragLeave(event) {
      if (!event.relatedTarget?.closest('.kanban-column')) {
        event.target.closest('.kanban-column')?.classList.remove('drag-over');
      }
    },

    async onDrop(event, newStatus) {
      event.preventDefault();
      event.target.closest('.kanban-column')?.classList.remove('drag-over');

      if (!this.draggingTask || this.draggingTask.status === newStatus) return;

      const wasCompleted = this.draggingTask.status !== 'done' && newStatus === 'done';
      const taskForXP = { priority: this.draggingTask.priority };

      try {
        await fetch(`${this.API_BASE}/tasks/${this.draggingTask.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        });

        this.draggingTask.status = newStatus;

        if (wasCompleted) {
          this.onTaskCompleted(taskForXP);
        } else {
          this.showToast(`Tâche déplacée vers "${this.mapStatus(newStatus)}"`, 'success');
        }
      } catch (err) {
        console.error('Drop error:', err);
        this.showToast('Erreur lors du déplacement', 'error');
      }
    },

    getTasksByStatus(status) {
      return this.tasks.filter(t => t.status === status);
    },

    async importData(event) {
      const file = event.target.files?.[0];
      if (!file) return;

      this.importExport.importing = true;
      try {
        const text = await file.text();
        const data = JSON.parse(text);

        if (!data.version) {
          throw new Error('Format de fichier invalide');
        }

        if (data.quickNotes !== undefined) {
          this.quickNotes = data.quickNotes;
          localStorage.setItem('quickNotes', data.quickNotes);
        }
        if (data.favoriteLinks) {
          this.favoriteLinks = data.favoriteLinks;
          localStorage.setItem('favoriteLinks', JSON.stringify(data.favoriteLinks));
        }
        if (data.countdowns) {
          this.countdowns = data.countdowns;
          localStorage.setItem('countdowns', JSON.stringify(data.countdowns));
        }
        if (data.theme) {
          this.theme = data.theme;
          localStorage.setItem('theme', data.theme);
          this.applyTheme();
        }
        if (data.filters) {
          this.filters = data.filters;
          this.saveFiltersToStorage();
        }

        if (data.tasks && data.tasks.length > 0) {
          for (const task of data.tasks) {
            try {
              await fetch(`${this.API_BASE}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  title: task.title,
                  description: task.description,
                  priority: task.priority,
                  due_date: task.due_date
                })
              });
            } catch (e) {
              console.warn('Could not import task:', task.title);
            }
          }
          await this.loadTasks();
        }

        this.showToast('Données importées avec succès', 'success');
        event.target.value = '';
      } catch (err) {
        console.error('Import error:', err);
        this.showToast('Erreur lors de l\'import: ' + err.message, 'error');
      } finally {
        this.importExport.importing = false;
      }
    },

    startClock() {
      this.updateClock();
      this.clock.interval = setInterval(() => this.updateClock(), 1000);
    },

    updateClock() {
      const now = new Date();
      this.clock.time = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      this.clock.date = now.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    },

    startPomodoro() {
      if (this.pomodoro.isRunning) return;
      this.pomodoro.isRunning = true;
      this.pomodoro.interval = setInterval(() => this.tickPomodoro(), 1000);
    },

    pausePomodoro() {
      this.pomodoro.isRunning = false;
      if (this.pomodoro.interval) {
        clearInterval(this.pomodoro.interval);
        this.pomodoro.interval = null;
      }
    },

    resetPomodoro() {
      this.pausePomodoro();
      if (this.pomodoro.mode === 'work') {
        this.pomodoro.minutes = this.pomodoro.workDuration;
      } else if (this.pomodoro.mode === 'break') {
        this.pomodoro.minutes = this.pomodoro.breakDuration;
      } else {
        this.pomodoro.minutes = this.pomodoro.longBreakDuration;
      }
      this.pomodoro.seconds = 0;
    },

    tickPomodoro() {
      if (this.pomodoro.seconds === 0) {
        if (this.pomodoro.minutes === 0) {
          this.pomodoroComplete();
          return;
        }
        this.pomodoro.minutes--;
        this.pomodoro.seconds = 59;
      } else {
        this.pomodoro.seconds--;
      }
    },

    pomodoroComplete() {
      this.pausePomodoro();
      this.playNotificationSound();

      if (this.pomodoro.mode === 'work') {
        this.pomodoro.completedPomodoros++;
        this.onPomodoroCompleted(); // Add XP for completing pomodoro

        if (this.pomodoro.completedPomodoros % 4 === 0) {
          this.pomodoro.mode = 'longBreak';
          this.pomodoro.minutes = this.pomodoro.longBreakDuration;
          this.showToast('Pomodoro terminé ! Longue pause de 15 min.', 'success');
        } else {
          this.pomodoro.mode = 'break';
          this.pomodoro.minutes = this.pomodoro.breakDuration;
          this.showToast('Pomodoro terminé ! Pause de 5 min.', 'success');
        }
      } else {
        this.pomodoro.mode = 'work';
        this.pomodoro.minutes = this.pomodoro.workDuration;
        this.showToast('Pause terminée ! Au travail !', 'info');
      }
      this.pomodoro.seconds = 0;
    },

    skipPomodoro() {
      this.pomodoroComplete();
    },

    playNotificationSound() {
      try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdH2Onp6Xkol7cGRbU09OSUlKS01RWF9nbXN4fYKGiYuMjIuKiIaDf3t2cWxnYl5aVlNRT05NS0pJSUlKS01QVFheZGpwdnx/g4aIiYqKiYiFgn55dXBqZmFdWVVSUE5NTExMTU5QVFleY2lundHl+goaIiYqKiYiFgX14c29qZWBcWFVSTk1MTExNTlBUWF1iZ21yd3uAhIeJioqJiIWBfXl0cGtmYV1ZVlJPTUxLTE1OUVVZXmNobXJ3fIGFiImKiomIhYF9eXRwbGdj');
        audio.volume = 0.5;
        audio.play();
      } catch (e) {
        console.log('Audio not supported');
      }
    },

    formatPomodoro() {
      const mins = String(this.pomodoro.minutes).padStart(2, '0');
      const secs = String(this.pomodoro.seconds).padStart(2, '0');
      return `${mins}:${secs}`;
    },

    getPomodoroLabel() {
      const labels = {
        work: 'Travail',
        break: 'Pause',
        longBreak: 'Longue pause'
      };
      return labels[this.pomodoro.mode];
    },

    mapStatus(status) {
      const map = {
        'todo': 'À faire',
        'doing': 'En cours',
        'done': 'Terminée',
        'archived': 'Archivée'
      };
      return map[status] || status;
    },

    loadFiltersFromStorage() {
      const saved = localStorage.getItem('taskFilters');
      if (saved) {
        try {
          this.filters = { ...this.filters, ...JSON.parse(saved) };
        } catch (e) {
          console.error('Error loading filters:', e);
        }
      }
    },

    saveFiltersToStorage() {
      localStorage.setItem('taskFilters', JSON.stringify(this.filters));
    },

    showToast(message, type = 'info') {
      const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
      };

      const toast = {
        id: this.toastId++,
        message,
        type,
        icon: icons[type] || icons.info,
        show: true
      };

      this.toasts.push(toast);

      setTimeout(() => {
        this.removeToast(toast.id);
      }, 4000);
    },

    removeToast(id) {
      const index = this.toasts.findIndex(t => t.id === id);
      if (index > -1) {
        this.toasts[index].show = false;
        setTimeout(() => {
          this.toasts.splice(index, 1);
        }, 300);
      }
    },

    isCurrentCourse(course) {
      const now = new Date();
      const currentHour = now.getHours();
      const currentMinute = now.getMinutes();
      const currentTime = currentHour * 60 + currentMinute;

      const [startH, startM] = course.start.split(':').map(Number);
      const [endH, endM] = course.end.split(':').map(Number);
      const startTime = startH * 60 + startM;
      const endTime = endH * 60 + endM;

      return currentTime >= startTime && currentTime < endTime;
    },

    getGradeColor(value) {
      if (value >= 16) return 'text-success';
      if (value >= 10) return 'text-warning';
      return 'text-danger';
    },

    formatDueDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
    },

    isOverdue(task) {
      if (!task.due_date || task.status === 'done' || task.status === 'archived') return false;
      return new Date(task.due_date) < new Date();
    },

    isDueSoon(task) {
      if (!task.due_date || task.status === 'done' || task.status === 'archived') return false;
      const dueDate = new Date(task.due_date);
      const now = new Date();
      const diff = dueDate - now;
      return diff > 0 && diff < 24 * 60 * 60 * 1000;
    },

    // ============ GAMIFICATION ============

    initGamification() {
      this.updateStreak();
      this.checkBadges();
    },

    saveGamification() {
      localStorage.setItem('gamification', JSON.stringify(this.gamification));
    },

    getToday() {
      return new Date().toISOString().split('T')[0];
    },

    updateStreak() {
      const today = this.getToday();
      const lastActive = this.gamification.lastActiveDate;

      if (!lastActive) return;

      const lastDate = new Date(lastActive);
      const todayDate = new Date(today);
      const diffDays = Math.floor((todayDate - lastDate) / (1000 * 60 * 60 * 24));

      if (diffDays > 1) {
        // Streak broken
        this.gamification.streak = 0;
        this.saveGamification();
      }
    },

    addXP(amount, reason) {
      const today = this.getToday();
      const wasActiveToday = this.gamification.lastActiveDate === today;

      this.gamification.xp += amount;

      if (!wasActiveToday) {
        // New day activity
        const lastActive = this.gamification.lastActiveDate;
        if (lastActive) {
          const lastDate = new Date(lastActive);
          const todayDate = new Date(today);
          const diffDays = Math.floor((todayDate - lastDate) / (1000 * 60 * 60 * 24));
          if (diffDays === 1) {
            this.gamification.streak++;
          } else {
            this.gamification.streak = 1;
          }
        } else {
          this.gamification.streak = 1;
        }
      }

      this.gamification.lastActiveDate = today;
      this.saveGamification();
      this.checkBadges();

      if (reason) {
        this.showToast(`+${amount} XP - ${reason}`, 'success');
      }
    },

    onTaskCompleted(task) {
      const xpAmount = task.priority === 'high' ? 20 : task.priority === 'low' ? 5 : 10;
      this.gamification.totalTasksCompleted++;
      this.addXP(xpAmount, 'Tâche complétée');
    },

    onPomodoroCompleted() {
      this.gamification.totalPomodorosCompleted++;
      this.addXP(5, 'Pomodoro terminé');
    },

    getCurrentLevel() {
      let currentLevel = this.levels[0];
      for (const level of this.levels) {
        if (this.gamification.xp >= level.minXp) {
          currentLevel = level;
        }
      }
      return currentLevel;
    },

    getNextLevel() {
      const current = this.getCurrentLevel();
      const nextIndex = this.levels.findIndex(l => l.level === current.level) + 1;
      return this.levels[nextIndex] || null;
    },

    getLevelProgress() {
      const current = this.getCurrentLevel();
      const next = this.getNextLevel();
      if (!next) return 100;

      const xpInLevel = this.gamification.xp - current.minXp;
      const xpNeeded = next.minXp - current.minXp;
      return Math.floor((xpInLevel / xpNeeded) * 100);
    },

    checkBadges() {
      let newBadges = [];
      for (const badge of this.badges) {
        if (!this.gamification.unlockedBadges.includes(badge.id) && badge.condition(this.gamification)) {
          this.gamification.unlockedBadges.push(badge.id);
          newBadges.push(badge);
        }
      }
      if (newBadges.length > 0) {
        this.saveGamification();
        for (const badge of newBadges) {
          this.showToast(`🏅 Badge débloqué: ${badge.icon} ${badge.name}!`, 'success');
        }
      }
    },

    isBadgeUnlocked(badgeId) {
      return this.gamification.unlockedBadges.includes(badgeId);
    },

    // ============ HABIT TRACKER ============

    saveHabits() {
      localStorage.setItem('habits', JSON.stringify(this.habits));
    },

    saveHabitHistory() {
      localStorage.setItem('habitHistory', JSON.stringify(this.habitHistory));
    },

    addHabit() {
      if (!this.newHabit.name.trim()) return;

      const habit = {
        id: Date.now(),
        name: this.newHabit.name.trim(),
        icon: this.newHabit.icon || '✅',
        createdAt: new Date().toISOString()
      };

      this.habits.push(habit);
      this.saveHabits();
      this.newHabit = { name: '', icon: '✅' };
      this.showAddHabit = false;
      this.showToast('Habitude ajoutée !', 'success');
    },

    removeHabit(id) {
      if (!confirm('Supprimer cette habitude ?')) return;
      this.habits = this.habits.filter(h => h.id !== id);
      this.saveHabits();
      this.showToast('Habitude supprimée', 'info');
    },

    toggleHabitDay(habitId, date) {
      const key = `${habitId}_${date}`;
      if (this.habitHistory[key]) {
        delete this.habitHistory[key];
      } else {
        this.habitHistory[key] = true;
        // Give XP for completing habit
        this.addXP(3, 'Habitude complétée');
      }
      this.saveHabitHistory();
    },

    isHabitDone(habitId, date) {
      return !!this.habitHistory[`${habitId}_${date}`];
    },

    getHabitStreak(habitId) {
      let streak = 0;
      const today = new Date();

      for (let i = 0; i < 365; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];

        if (this.isHabitDone(habitId, dateStr)) {
          streak++;
        } else if (i > 0) {
          break;
        }
      }
      return streak;
    },

    getHabitCompletionRate(habitId) {
      const last30Days = [];
      const today = new Date();

      for (let i = 0; i < 30; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        if (this.isHabitDone(habitId, dateStr)) {
          last30Days.push(true);
        }
      }

      return Math.round((last30Days.length / 30) * 100);
    },

    getLast7Days() {
      const days = [];
      const today = new Date();

      for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        days.push({
          date: date.toISOString().split('T')[0],
          dayName: date.toLocaleDateString('fr-FR', { weekday: 'short' }),
          dayNum: date.getDate(),
          isToday: i === 0
        });
      }
      return days;
    }
  };
}
