<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && costData" class="modal-overlay" @click="close">
        <div class="modal-panel" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">{{ costData.month }} Cost Breakdown</h3>
            <button class="modal-close" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="cost-summary">
            <div class="summary-card total">
              <div class="summary-label">Total Costs</div>
              <div class="summary-value tabular-nums">{{ currencySymbol }}{{ totalCosts.toLocaleString() }}</div>
            </div>
          </div>

          <div class="cost-breakdown">
            <div class="cost-item procurement">
              <div class="cost-header">
                <div class="cost-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect x="4" y="6" width="16" height="14" rx="2" stroke="currentColor" stroke-width="2"/>
                    <path d="M8 6V4M16 6V4M4 10H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </div>
                <div class="cost-info">
                  <div class="cost-name">Procurement</div>
                  <div class="cost-amount tabular-nums">{{ currencySymbol }}{{ costData.procurement.toLocaleString() }}</div>
                </div>
              </div>
              <div class="cost-percentage tabular-nums">{{ getProcurementPercentage() }}% of total</div>
            </div>

            <div class="cost-item operational">
              <div class="cost-header">
                <div class="cost-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </div>
                <div class="cost-info">
                  <div class="cost-name">Operational</div>
                  <div class="cost-amount tabular-nums">{{ currencySymbol }}{{ costData.operational.toLocaleString() }}</div>
                </div>
              </div>
              <div class="cost-percentage tabular-nums">{{ getOperationalPercentage() }}% of total</div>
            </div>

            <div class="cost-item labor">
              <div class="cost-header">
                <div class="cost-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2"/>
                    <path d="M6 20C6 16.6863 8.68629 14 12 14C15.3137 14 18 16.6863 18 20" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
                <div class="cost-info">
                  <div class="cost-name">Labor</div>
                  <div class="cost-amount tabular-nums">{{ currencySymbol }}{{ costData.labor.toLocaleString() }}</div>
                </div>
              </div>
              <div class="cost-percentage tabular-nums">{{ getLaborPercentage() }}% of total</div>
            </div>

            <div class="cost-item overhead">
              <div class="cost-header">
                <div class="cost-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M3 12L5 10M5 10L12 3L19 10M5 10V20C5 20.5523 5.44772 21 6 21H9M19 10L21 12M19 10V20C19 20.5523 18.5523 21 18 21H15M9 21C9 21 9 18 9 16C9 14 10 14 12 14C14 14 15 14 15 16C15 18 15 21 15 21M9 21H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </div>
                <div class="cost-info">
                  <div class="cost-name">Overhead</div>
                  <div class="cost-amount tabular-nums">{{ currencySymbol }}{{ costData.overhead.toLocaleString() }}</div>
                </div>
              </div>
              <div class="cost-percentage tabular-nums">{{ getOverheadPercentage() }}% of total</div>
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

const { currentCurrency } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  costData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalCosts = computed(() => {
  if (!props.costData) return 0
  return props.costData.procurement + props.costData.operational +
         props.costData.labor + props.costData.overhead
})

const getProcurementPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.procurement / totalCosts.value) * 100).toFixed(1)
}

const getOperationalPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.operational / totalCosts.value) * 100).toFixed(1)
}

const getLaborPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.labor / totalCosts.value) * 100).toFixed(1)
}

const getOverheadPercentage = () => {
  if (!props.costData || totalCosts.value === 0) return 0
  return ((props.costData.overhead / totalCosts.value) * 100).toFixed(1)
}

const close = () => {
  emit('close')
}
</script>

<style scoped>
.cost-summary {
  margin-bottom: var(--space-5);
}

.summary-card.total {
  background: var(--color-accent);
  color: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  text-align: center;
}

.summary-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  opacity: 0.85;
  margin-bottom: var(--space-2);
}

.summary-value {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
}

.cost-breakdown {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.cost-item {
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: var(--border-width) solid var(--color-border);
}

.cost-item.procurement {
  border-color: var(--color-info);
  background: var(--color-info-bg);
}

.cost-item.operational {
  border-color: var(--color-border-strong);
  background: var(--color-surface-sunken);
}

.cost-item.labor {
  border-color: var(--color-success);
  background: var(--color-success-bg);
}

.cost-item.overhead {
  border-color: var(--color-warning);
  background: var(--color-warning-bg);
}

.cost-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-2);
}

.cost-icon {
  width: var(--space-8);
  height: var(--space-8);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-surface);
  flex-shrink: 0;
}

.cost-item.procurement .cost-icon  { background: var(--color-info); }
.cost-item.operational .cost-icon  { background: var(--color-text-secondary); }
.cost-item.labor .cost-icon        { background: var(--color-success); }
.cost-item.overhead .cost-icon     { background: var(--color-warning); }

.cost-info {
  flex: 1;
}

.cost-name {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  margin-bottom: var(--space-1);
}

.cost-amount {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
}

.cost-percentage {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  font-weight: var(--weight-medium);
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
