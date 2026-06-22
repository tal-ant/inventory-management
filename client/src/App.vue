<template>
  <div class="app-shell">
    <div
      v-if="sidebarOpen"
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    ></div>

    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-brand">
        <span class="brand-name">{{ t('nav.companyName') }}</span>
        <span class="brand-sub">{{ t('nav.subtitle') }}</span>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" :class="{ active: $route.path === '/' }">{{ t('nav.overview') }}</router-link>
        <router-link to="/inventory" :class="{ active: $route.path === '/inventory' }">{{ t('nav.inventory') }}</router-link>
        <router-link to="/orders" :class="{ active: $route.path === '/orders' }">{{ t('nav.orders') }}</router-link>
        <router-link to="/spending" :class="{ active: $route.path === '/spending' }">{{ t('nav.finance') }}</router-link>
        <router-link to="/demand" :class="{ active: $route.path === '/demand' }">{{ t('nav.demandForecast') }}</router-link>
        <router-link to="/restocking" :class="{ active: $route.path === '/restocking' }">{{ t('nav.restocking') }}</router-link>
        <router-link to="/reports" :class="{ active: $route.path === '/reports' }">Reports</router-link>
      </nav>

      <div class="sidebar-footer">
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
      </div>
    </aside>

    <div class="main-column">
      <header class="topbar">
        <button
          class="sidebar-toggle"
          @click="sidebarOpen = !sidebarOpen"
          aria-label="Toggle navigation"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 5H17M3 10H17M3 15H17" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
        <FilterBar />
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const sidebarOpen = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      sidebarOpen,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
/* ── App shell ───────────────────────────────────────────────────── */
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

/* ── Sidebar ─────────────────────────────────────────────────────── */
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: var(--border-width) solid var(--color-border);
  padding: var(--space-5) var(--space-3);
  z-index: 60;
}

.sidebar-brand {
  padding: 0 var(--space-3) var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.brand-name {
  font-size: var(--text-md);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  letter-spacing: var(--tracking-tight);
}

.brand-sub {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.sidebar-nav a {
  display: block;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.sidebar-nav a:hover {
  background: var(--color-surface-sunken);
  color: var(--color-text);
}

.sidebar-nav a.active {
  background: var(--color-accent-soft);
  color: var(--color-accent-text);
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding-top: var(--space-4);
  border-top: var(--border-width) solid var(--color-border);
}

/* ── Main column ─────────────────────────────────────────────────── */
.main-column {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  min-height: var(--topbar-height);
  display: flex;
  align-items: center;
  background: var(--color-surface);
  border-bottom: var(--border-width) solid var(--color-border);
  padding: 0 var(--content-padding);
  gap: var(--space-3);
}

.sidebar-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  padding: var(--space-2);
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  flex-shrink: 0;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.sidebar-toggle:hover {
  background: var(--color-surface-sunken);
  color: var(--color-text);
}

.content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-6) var(--content-padding) var(--space-12);
}

/* ── Mobile sidebar overlay ──────────────────────────────────────── */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  z-index: 55;
  background: rgba(31, 29, 26, 0.4);
}

/* ── Responsive collapse (keep in sync with --breakpoint-collapse) ── */
@media (max-width: 1024px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform var(--transition-base);
  }

  .sidebar.open {
    transform: translateX(0);
    box-shadow: var(--shadow-overlay);
  }

  .main-column {
    margin-left: 0;
  }

  .sidebar-toggle {
    display: flex;
  }
}
</style>
