import axios from 'axios'
import type { Route, ForecastReport, GribFile, HealthResponse } from './types'

const api = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiService = {
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health')
    return response.data
  },

  async getRoutes(): Promise<Route[]> {
    const response = await api.get<Route[]>('/routes')
    return response.data
  },

  async getLatestReport(routeId: string, model: string = 'gfs'): Promise<ForecastReport> {
    const response = await api.get<ForecastReport>(`/api/latest-report/${routeId}`, {
      params: { model, fmt: 'json' },
    })
    return response.data
  },

  async getGribFiles(): Promise<GribFile[]> {
    const response = await api.get<GribFile[]>('/api/grib-files')
    return response.data
  },
}
