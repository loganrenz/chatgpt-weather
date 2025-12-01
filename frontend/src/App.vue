<template>
  <div class="main-container">
    <header>
      <nav>
        <ul>
          <li><strong>Marine Weather Routing</strong></li>
        </ul>
        <ul>
          <li><a href="#" :class="{ active: activeTab === 'forecast' }" @click.prevent="activeTab = 'forecast'">Forecast</a></li>
          <li><a href="#" :class="{ active: activeTab === 'grib' }" @click.prevent="activeTab = 'grib'">GRIB Files</a></li>
        </ul>
      </nav>
    </header>

    <main>
      <div v-if="activeTab === 'forecast'">
        <ForecastViewer />
      </div>
      <div v-if="activeTab === 'grib'">
        <GribList />
      </div>
    </main>

    <footer style="text-align: center; margin-top: 2rem; padding: 1rem; color: var(--pico-muted-color);">
      <small>
        Marine Weather Routing System • Gulf of Mexico Routes
      </small>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ForecastViewer from './components/ForecastViewer.vue'
import GribList from './components/GribList.vue'

const activeTab = ref<'forecast' | 'grib'>('forecast')
</script>

<style scoped>
nav a.active {
  font-weight: bold;
  text-decoration: underline;
}
</style>
