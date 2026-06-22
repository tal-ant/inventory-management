<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-panel modal-lg" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Inventory Shortage Details</h3>
            <button class="modal-close" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="shortage-header">
            <div class="shortage-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <path d="M24 8L24 28M24 34L24 36" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                <circle cx="24" cy="24" r="18" stroke="currentColor" stroke-width="3"/>
              </svg>
            </div>
            <div class="shortage-title-section">
              <h4 class="item-name">{{ translateProductName(backlogItem.item_name) }}</h4>
              <div class="item-sku">SKU: {{ backlogItem.item_sku }}</div>
            </div>
            <span class="badge" :class="backlogItem.priority">
              {{ backlogItem.priority }} Priority
            </span>
          </div>

          <div class="shortage-summary">
            <div class="summary-card danger-card">
              <div class="summary-label">Shortage Amount</div>
              <div class="summary-value tabular-nums">{{ shortage }} units</div>
            </div>
            <div class="summary-card warning-card">
              <div class="summary-label">Days Delayed</div>
              <div class="summary-value tabular-nums">{{ backlogItem.days_delayed }} days</div>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Order ID</div>
              <div class="info-value info-code">{{ backlogItem.order_id }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Item SKU</div>
              <div class="info-value info-code">{{ backlogItem.item_sku }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Quantity Needed</div>
              <div class="info-value tabular-nums">{{ backlogItem.quantity_needed }} units</div>
            </div>

            <div class="info-item">
              <div class="info-label">Quantity Available</div>
              <div class="info-value tabular-nums">{{ backlogItem.quantity_available }} units</div>
            </div>

            <div class="info-item">
              <div class="info-label">Expected Date</div>
              <div class="info-value">{{ formatDate(backlogItem.expected_date) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Status</div>
              <div class="info-value">
                <span class="badge danger">Backordered</span>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary btn-sm" @click="close">Close</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const { translateProductName } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  backlogItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return props.backlogItem.quantity_needed - props.backlogItem.quantity_available
})

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.shortage-header {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding-bottom: var(--space-5);
  border-bottom: var(--border-width) solid var(--color-border);
  margin-bottom: var(--space-5);
}

.shortage-icon {
  width: var(--space-12);
  height: var(--space-12);
  background: var(--color-danger);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-surface);
  flex-shrink: 0;
}

.shortage-title-section {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  margin: 0 0 var(--space-1) 0;
}

.item-sku {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.shortage-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.summary-card {
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: var(--border-width) solid var(--color-border);
}

.summary-card.danger-card {
  border-color: var(--color-danger);
  background: var(--color-danger-bg);
}

.summary-card.warning-card {
  border-color: var(--color-warning);
  background: var(--color-warning-bg);
}

.summary-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}

.summary-value {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
}

.summary-card.danger-card .summary-value { color: var(--color-danger); }
.summary-card.warning-card .summary-value { color: var(--color-warning); }

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-5);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.info-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  color: var(--color-text-secondary);
}

.info-value {
  font-size: var(--text-base);
  color: var(--color-text);
  font-weight: var(--weight-medium);
}

.info-value.info-code {
  color: var(--color-accent);
}

.modal-footer {
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: var(--border-width) solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition-base);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-panel,
.modal-leave-active .modal-panel {
  transition: transform var(--transition-base);
}

.modal-enter-from .modal-panel,
.modal-leave-to .modal-panel {
  transform: scale(0.95);
}
</style>
