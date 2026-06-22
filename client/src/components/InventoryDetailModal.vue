<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && inventoryItem" class="modal-overlay" @click="close">
        <div class="modal-panel modal-lg" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Inventory Item Details</h3>
            <button class="modal-close" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="item-header">
            <div class="item-icon" :class="getStockIconClass()">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect x="8" y="12" width="32" height="28" rx="2" stroke="currentColor" stroke-width="2.5"/>
                <path d="M16 8V16M32 8V16M8 20H40" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M16 28H32M16 34H24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="item-title-section">
              <h4 class="item-name">{{ translateProductName(inventoryItem.name) }}</h4>
              <div class="item-sku">SKU: {{ inventoryItem.sku }}</div>
            </div>
            <span class="badge" :class="getStockStatusClass()">
              {{ getStockStatus() }}
            </span>
          </div>

          <div class="stock-summary">
            <div class="summary-card primary">
              <div class="summary-label">Quantity on Hand</div>
              <div class="summary-value tabular-nums">{{ inventoryItem.quantity_on_hand }} units</div>
            </div>
            <div class="summary-card" :class="getSummaryCardClass()">
              <div class="summary-label">Stock Level</div>
              <div class="summary-value tabular-nums">{{ stockPercentage }}%</div>
              <div class="summary-subtitle">vs. reorder point</div>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Category</div>
              <div class="info-value">{{ inventoryItem.category }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Location</div>
              <div class="info-value">{{ inventoryItem.location }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Reorder Point</div>
              <div class="info-value tabular-nums">{{ inventoryItem.reorder_point }} units</div>
            </div>

            <div class="info-item">
              <div class="info-label">Units Remaining</div>
              <div class="info-value">
                <span
                  class="tabular-nums"
                  :class="inventoryItem.quantity_on_hand <= inventoryItem.reorder_point ? 'val-danger' : 'val-success'"
                >
                  {{ inventoryItem.quantity_on_hand - inventoryItem.reorder_point }} units
                </span>
              </div>
            </div>

            <div class="info-item">
              <div class="info-label">Unit Cost</div>
              <div class="info-value tabular-nums">{{ currencySymbol }}{{ inventoryItem.unit_cost.toFixed(2) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Total Value</div>
              <div class="info-value total-value tabular-nums">
                {{ currencySymbol }}{{ totalValue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
              </div>
            </div>

            <div class="info-item">
              <div class="info-label">Warehouse</div>
              <div class="info-value">{{ translateWarehouse(inventoryItem.location) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Status</div>
              <div class="info-value">
                <span class="badge" :class="getStockStatusClass()">
                  {{ getStockStatus() }}
                </span>
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

const { currentCurrency, translateProductName, translateWarehouse } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  inventoryItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const totalValue = computed(() => {
  if (!props.inventoryItem) return 0
  return props.inventoryItem.quantity_on_hand * props.inventoryItem.unit_cost
})

const stockPercentage = computed(() => {
  if (!props.inventoryItem || props.inventoryItem.reorder_point === 0) return 0
  return Math.round((props.inventoryItem.quantity_on_hand / props.inventoryItem.reorder_point) * 100)
})

const close = () => {
  emit('close')
}

const getStockStatus = () => {
  if (!props.inventoryItem) return 'Unknown'
  if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point) {
    return 'Low Stock'
  } else if (props.inventoryItem.quantity_on_hand <= props.inventoryItem.reorder_point * 1.5) {
    return 'Adequate'
  } else {
    return 'In Stock'
  }
}

const getStockStatusClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger'
  if (status === 'Adequate') return 'warning'
  return 'success'
}

const getStockIconClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger-icon'
  if (status === 'Adequate') return 'warning-icon'
  return 'success-icon'
}

const getSummaryCardClass = () => {
  const status = getStockStatus()
  if (status === 'Low Stock') return 'danger-card'
  if (status === 'Adequate') return 'warning-card'
  return 'success-card'
}
</script>

<style scoped>
.item-header {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding-bottom: var(--space-5);
  border-bottom: var(--border-width) solid var(--color-border);
  margin-bottom: var(--space-5);
}

.item-icon {
  width: var(--space-12);
  height: var(--space-12);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-surface);
  flex-shrink: 0;
}

.item-icon.success-icon { background: var(--color-success); }
.item-icon.warning-icon { background: var(--color-warning); }
.item-icon.danger-icon  { background: var(--color-danger); }

.item-title-section {
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

.stock-summary {
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

.summary-card.primary {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}

.summary-card.success-card {
  border-color: var(--color-success);
  background: var(--color-success-bg);
}

.summary-card.warning-card {
  border-color: var(--color-warning);
  background: var(--color-warning-bg);
}

.summary-card.danger-card {
  border-color: var(--color-danger);
  background: var(--color-danger-bg);
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

.summary-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

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

.info-value.total-value {
  font-size: var(--text-md);
  color: var(--color-accent);
  font-weight: var(--weight-semibold);
}

.val-danger { color: var(--color-danger); }
.val-success { color: var(--color-success); }

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
