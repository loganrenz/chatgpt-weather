<template>
  <article>
    <header>
      <h2>Weather Forecast</h2>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <label>
          Route:
          <select v-model="selectedRoute" @change="loadReport" :disabled="loading">
            <option v-for="route in routes" :key="route.id" :value="route.id">
              {{ route.name }}
            </option>
          </select>
        </label>
        <label>
          Model:
          <select v-model="selectedModel" @change="loadReport" :disabled="loading">
            <option value="gfs">GFS</option>
            <option value="ecmwf">ECMWF</option>
          </select>
        </label>
        <button @click="loadReport" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </header>
    <div v-if="loading" class="loading">
      <p aria-busy="true">Loading forecast...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="report" class="forecast-content">
      <div v-html="report.html"></div>
    </div>
    <div v-else>
      <p>No forecast data available. Select a route and model to view the latest forecast.</p>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiService } from '../api'
import type { Route, ForecastReport } from '../types'

const routes = ref<Route[]>([])
const selectedRoute = ref<string>('lakecharles-kemah')
const selectedModel = ref<string>('gfs')
const report = ref<ForecastReport | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

const loadRoutes = async () => {
  try {
    routes.value = await apiService.getRoutes()
    if (routes.value.length > 0 && !selectedRoute.value && routes.value[0]) {
      selectedRoute.value = routes.value[0].id
    }
  } catch (err: any) {
    console.error('Failed to load routes:', err)
  }
}

const loadReport = async () => {
  if (!selectedRoute.value) return
  
  loading.value = true
  error.value = null
  try {
    report.value = await apiService.getLatestReport(selectedRoute.value, selectedModel.value)
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load forecast report'
    report.value = null
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadRoutes()
  await loadReport()
})
</script>
