<template>
  <article>
    <header>
      <h2>GRIB Files</h2>
    </header>
    <div v-if="loading" class="loading">
      <p aria-busy="true">Loading GRIB files...</p>
    </div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="files.length === 0">
      <p>No GRIB files found.</p>
    </div>
    <div v-else class="grib-list">
      <table>
        <thead>
          <tr>
            <th>File Name</th>
            <th>Model</th>
            <th>Forecast Hour</th>
            <th>Size</th>
            <th>Modified</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" :key="file.path">
            <td>{{ file.name }}</td>
            <td>{{ file.model || '-' }}</td>
            <td>{{ file.forecast_hour !== undefined ? file.forecast_hour + 'h' : '-' }}</td>
            <td>{{ formatSize(file.size) }}</td>
            <td>{{ formatDate(file.modified) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <footer>
      <button @click="refresh" :disabled="loading">
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </footer>
  </article>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiService } from '../api'
import type { GribFile } from '../types'

const files = ref<GribFile[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const loadFiles = async () => {
  loading.value = true
  error.value = null
  try {
    files.value = await apiService.getGribFiles()
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load GRIB files'
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  loadFiles()
}

const formatSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString()
}

onMounted(() => {
  loadFiles()
})
</script>
