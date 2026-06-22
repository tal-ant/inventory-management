<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="close">
        <div class="modal-panel" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">{{ t('profileDetails.title') }}</h3>
            <button class="modal-close" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="profile-section">
            <div class="avatar-section">
              <div class="avatar-xl">
                {{ getInitials(currentUser.name) }}
              </div>
              <h4 class="profile-name">{{ currentUser.name }}</h4>
              <p class="profile-job-title">{{ currentUser.jobTitle }}</p>
            </div>

            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">{{ t('profileDetails.email') }}</div>
                <div class="info-value">{{ currentUser.email }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">{{ t('profileDetails.department') }}</div>
                <div class="info-value">{{ currentUser.department }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">{{ t('profileDetails.location') }}</div>
                <div class="info-value">{{ currentUser.location }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">{{ t('profileDetails.phone') }}</div>
                <div class="info-value">{{ currentUser.phone }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">{{ t('profileDetails.joinDate') }}</div>
                <div class="info-value">{{ formatDate(currentUser.joinDate) }}</div>
              </div>

              <div class="info-item">
                <div class="info-label">{{ t('profileDetails.employeeId') }}</div>
                <div class="info-value">CC-{{ currentUser.id.toString().padStart(5, '0') }}</div>
              </div>
            </div>
          </div>

          <div class="modal-footer-row">
            <button class="btn btn-secondary btn-sm" @click="close">{{ t('profileDetails.close') }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'

const { currentUser, getInitials } = useAuth()
const { t, currentLocale } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
  return date.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.profile-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding-bottom: var(--space-6);
  border-bottom: var(--border-width) solid var(--color-border);
}

.avatar-xl {
  width: 96px;
  height: 96px;
  border-radius: var(--radius-full);
  background: var(--color-accent);
  color: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--weight-semibold);
  font-size: var(--text-xl);
  letter-spacing: var(--tracking-wide);
}

.profile-name {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  margin: 0;
}

.profile-job-title {
  font-size: var(--text-md);
  color: var(--color-text-muted);
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-6);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.info-label {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  color: var(--color-text-muted);
}

.info-value {
  font-size: var(--text-base);
  color: var(--color-text);
  font-weight: var(--weight-medium);
}

/* Footer */
.modal-footer-row {
  border-top: var(--border-width) solid var(--color-border);
  padding-top: var(--space-4);
  margin-top: var(--space-6);
  display: flex;
  justify-content: flex-end;
}

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-panel,
.modal-leave-active .modal-panel {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-panel,
.modal-leave-to .modal-panel {
  transform: scale(0.95);
}
</style>
