<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && product" class="modal-overlay" @click="close">
        <div class="modal-panel modal-lg" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Product Details</h3>
            <button class="modal-close" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="product-header">
            <div class="product-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <rect x="8" y="12" width="32" height="28" rx="2" stroke="currentColor" stroke-width="2.5"/>
                <path d="M16 8V16M32 8V16M8 20H40" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="product-title-section">
              <h4 class="product-name">{{ product.name }}</h4>
              <div class="product-sku">SKU: {{ product.sku }}</div>
            </div>
            <span class="badge" :class="getStockBadgeClass(product.stockLevel)">
              {{ product.stockLevel }}
            </span>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Category</div>
              <div class="info-value">{{ product.category }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Warehouse</div>
              <div class="info-value">{{ product.warehouse }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Units Ordered</div>
              <div class="info-value tabular-nums">{{ product.unitsOrdered }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Total Revenue</div>
              <div class="info-value tabular-nums">{{ currencySymbol }}{{ product.revenue.toLocaleString() }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Current Stock</div>
              <div class="info-value tabular-nums">{{ product.quantityOnHand }} units</div>
            </div>

            <div class="info-item">
              <div class="info-label">Reorder Point</div>
              <div class="info-value tabular-nums">{{ product.reorderPoint }} units</div>
            </div>

            <div class="info-item">
              <div class="info-label">First Order Date</div>
              <div class="info-value">{{ formatDate(product.firstOrderDate) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Stock Status</div>
              <div class="info-value">
                <span class="badge" :class="getStockBadgeClass(product.stockLevel)">
                  {{ product.stockLevel }}
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

const { currentCurrency } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

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

const getStockBadgeClass = (stockLevel) => {
  if (stockLevel === 'In Stock') return 'success'
  if (stockLevel === 'Low Stock') return 'warning'
  if (stockLevel === 'Out of Stock') return 'danger'
  return 'info'
}
</script>

<style scoped>
.product-header {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding-bottom: var(--space-5);
  border-bottom: var(--border-width) solid var(--color-border);
  margin-bottom: var(--space-5);
}

.product-icon {
  width: var(--space-12);
  height: var(--space-12);
  background: var(--color-accent);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-surface);
  flex-shrink: 0;
}

.product-title-section {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  margin: 0 0 var(--space-1) 0;
}

.product-sku {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
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
