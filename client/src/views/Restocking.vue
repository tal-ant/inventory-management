<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <!-- Budget slider -->
    <div class="card budget-card">
      <div class="budget-slider-row">
        <span class="stat-label">{{ t('restocking.budget') }}</span>
        <div class="slider-group">
          <input
            type="range"
            min="0"
            max="200000"
            step="5000"
            v-model.number="budget"
            @change="loadRecommendations"
            class="budget-slider"
          />
          <span class="budget-display">{{ formatCurrency(budget) }}</span>
        </div>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">{{ t('restocking.budget') }}</div>
        <div class="stat-value">{{ formatCurrency(budget) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ t('restocking.plannedSpend') }}</div>
        <div class="stat-value">{{ formatCurrency(plannedSpend) }}</div>
      </div>
      <div :class="['stat-card', { danger: overBudget }]">
        <div class="stat-label">{{ t('restocking.remaining') }}</div>
        <div class="stat-value">{{ formatCurrency(remaining) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ t('restocking.itemsSelected') }}</div>
        <div class="stat-value">{{ selectedItems.length }}</div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>

    <div v-else>
      <!-- Error (fetch or order placement) -->
      <div v-if="error" class="error">{{ error }}</div>

      <!-- Recommendations card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }}</h3>
        </div>

        <div v-if="recommendations.length === 0" class="empty-state">
          {{ t('restocking.noRecommendations') }}
        </div>

        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.include') }}</th>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.category') }}</th>
                <th>{{ t('restocking.table.warehouse') }}</th>
                <th>{{ t('restocking.table.onHand') }}</th>
                <th>{{ t('restocking.table.forecast') }}</th>
                <th>{{ t('restocking.table.shortfall') }}</th>
                <th>{{ t('restocking.table.orderQty') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.leadTime') }}</th>
                <th>{{ t('restocking.table.lineTotal') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in recommendations" :key="row.sku">
                <td>
                  <input type="checkbox" v-model="row.included" />
                </td>
                <td><strong>{{ row.sku }}</strong></td>
                <td>{{ row.name }}</td>
                <td>{{ row.category }}</td>
                <td>{{ row.warehouse }}</td>
                <td class="tabular-nums">{{ row.quantity_on_hand }}</td>
                <td class="tabular-nums">{{ row.forecasted_demand }}</td>
                <td class="tabular-nums">{{ row.shortfall }}</td>
                <td>
                  <input
                    type="number"
                    v-model.number="row.order_qty"
                    min="1"
                    class="input qty-input"
                  />
                </td>
                <td class="tabular-nums">{{ formatCurrency(row.unit_cost) }}</td>
                <td class="tabular-nums">{{ row.lead_time_days }}</td>
                <td class="tabular-nums">{{ formatCurrency(row.order_qty * row.unit_cost) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Over-budget warning -->
        <div v-if="overBudget" class="over-budget-warning">
          {{ t('restocking.overBudget') }}
        </div>

        <!-- Place Order / Success -->
        <div class="place-order-area">
          <div v-if="successOrder" class="success-banner">
            <p>{{ t('restocking.orderPlaced', { orderNumber: successOrder.order_number }) }}</p>
            <p>{{ t('restocking.estimatedDelivery') }}: <strong>{{ formatDate(successOrder.expected_delivery) }}</strong></p>
            <router-link to="/orders">{{ t('restocking.viewInOrders') }}</router-link>
          </div>
          <button
            v-else
            class="btn btn-primary"
            :disabled="!canPlaceOrder"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrency as formatCurrencyUtil } from '../utils/currency'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    // State
    const budget = ref(50000)
    const recommendations = ref([])
    const loading = ref(false)
    const error = ref(null)
    const submitting = ref(false)
    const successOrder = ref(null)

    // Currency-aware formatter
    const formatCurrency = (value) => formatCurrencyUtil(value, currentCurrency.value)

    // Date formatter — "Jun 15, 2026" style
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return dateString
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Computed
    const selectedItems = computed(() => recommendations.value.filter(row => row.included))

    const plannedSpend = computed(() =>
      selectedItems.value.reduce((sum, row) => sum + row.order_qty * row.unit_cost, 0)
    )

    const remaining = computed(() => budget.value - plannedSpend.value)

    const overBudget = computed(() => remaining.value < 0)

    const canPlaceOrder = computed(() =>
      selectedItems.value.length > 0 && !overBudget.value && !submitting.value
    )

    // Load recommendations from API
    const loadRecommendations = async () => {
      loading.value = true
      error.value = null
      successOrder.value = null
      try {
        const filters = getCurrentFilters()
        const data = await api.getRestockRecommendations(budget.value, {
          warehouse: filters.warehouse,
          category: filters.category
        })
        recommendations.value = (data.items || []).map(item => ({
          ...item,
          included: true,
          order_qty: item.recommended_qty
        }))
      } catch (err) {
        error.value = 'Failed to load restock recommendations'
        console.error(err)
        recommendations.value = []
      } finally {
        loading.value = false
      }
    }

    // Place the restocking order
    const placeOrder = async () => {
      if (!canPlaceOrder.value) return
      submitting.value = true
      error.value = null
      try {
        const order = await api.createRestockOrder({
          items: selectedItems.value.map(row => ({
            sku: row.sku,
            quantity: row.order_qty
          }))
        })
        successOrder.value = order
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to place restocking order'
        console.error(err)
      } finally {
        submitting.value = false
      }
    }

    // Re-fetch when global warehouse/category filters change
    watch([selectedLocation, selectedCategory], () => {
      loadRecommendations()
    })

    onMounted(() => loadRecommendations())

    return {
      t,
      budget,
      recommendations,
      loading,
      error,
      submitting,
      successOrder,
      selectedItems,
      plannedSpend,
      remaining,
      overBudget,
      canPlaceOrder,
      formatCurrency,
      formatDate,
      loadRecommendations,
      placeOrder
    }
  }
}
</script>

<style scoped>
/* Budget slider row */
.budget-card {
  margin-bottom: var(--space-4);
}

.budget-slider-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.slider-group {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex: 1;
  min-width: 0;
}

.budget-slider {
  flex: 1;
  min-width: 0;
  accent-color: var(--color-accent);
  cursor: pointer;
  height: 4px;
}

.budget-display {
  font-size: var(--text-base);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  min-width: 7rem;
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

/* Quantity input */
.qty-input {
  width: 80px;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

/* Over-budget warning */
.over-budget-warning {
  margin-top: var(--space-4);
  background: var(--color-danger-bg);
  border: var(--border-width) solid var(--color-danger);
  color: var(--color-danger);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}

/* Place Order / success area */
.place-order-area {
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: var(--border-width) solid var(--color-border);
}

.success-banner {
  background: var(--color-success-bg);
  border: var(--border-width) solid var(--color-success);
  color: var(--color-success);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  font-size: var(--text-sm);
  text-align: left;
}

.success-banner a {
  color: var(--color-accent);
  text-decoration: underline;
  font-weight: var(--weight-medium);
}
</style>
