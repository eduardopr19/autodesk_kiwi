function app() {
  return {
    // Config
    API_BASE: 'http://127.0.0.1:8000',
    
    // State
    currentView: localStorage.getItem('lastView') || 'today',
    loading: { tasks: false, weather: false },
    
    // Data
    tasks: [],
    overview: {},
    stats: {},
    weather: {
      current: {},
      hourly: [],
      daily: [],
      location: ''
    },
    
    // Forms
    newTask: { title: '', priority: 'normal' },
    filters: {
      q: '',
      status: '',
      priority: '',
      sort: '-created_at'
    },
    
    // UI
    selectedTasks: [],
    toasts: [],
    toastId: 0,
    
    // Weather codes
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

    // Hyperplanning Data
    hyperplanning: {
      schedule: { display_date: '', courses: [] },
      nextCourses: [],
      stats: [],
      grades: [],
      showImport: false,
      importInput: ''
    },
    
    // Init
    async init() {
      this.loadFiltersFromStorage();
      await Promise.all([
        this.loadOverview(),
        this.loadTasks(),
        this.loadWeather(),
        this.loadStats(),
        this.loadHyperplanning()
      ]);
      
      // Watch view changes
      this.$watch('currentView', (view) => {
        localStorage.setItem('lastView', view);
      });
    },
    
    // HTTP Helpers
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
    
    // Overview
    async loadOverview() {
      try {
        this.overview = await this.fetchJSON(`${this.API_BASE}/meta/overview`);
      } catch (err) {
        console.error('Overview error:', err);
      }
    },
    
    // Stats
    async loadStats() {
      try {
        this.stats = await this.fetchJSON(`${this.API_BASE}/tasks/stats/summary`);
      } catch (err) {
        console.error('Stats error:', err);
      }
    },
    
    // Tasks
    async loadTasks() {
      this.loading.tasks = true;
      try {
        const params = new URLSearchParams({
          ...this.filters,
          limit: 50,
          offset: 0
        });
        this.tasks = await this.fetchJSON(`${this.API_BASE}/tasks?${params}`);
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
        await this.sendJSON(`${this.API_BASE}/tasks`, this.newTask);
        this.newTask = { title: '', priority: 'normal' };
        await this.loadTasks();
        await this.loadStats();
        this.showToast('Tâche ajoutée !', 'success');
      } catch (err) {
        this.showToast('Erreur lors de l\'ajout', 'error');
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
    
    // Weather
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

    // Hyperplanning
    async loadHyperplanning() {
      try {
        const [schedule, stats, nextCourses, grades] = await Promise.all([
          this.fetchJSON(`${this.API_BASE}/hyperplanning/courses`),
          this.fetchJSON(`${this.API_BASE}/hyperplanning/stats`),
          this.fetchJSON(`${this.API_BASE}/hyperplanning/next-courses`),
          this.fetchJSON(`${this.API_BASE}/hyperplanning/grades`)
        ]);

        // Handle legacy array response if backend not updated yet (safety check)
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

    // Import/Clear Grades
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
    // Utilities
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
    
    // Toast notifications
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

    // Hyperplanning Helpers
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
    }
  };
}
