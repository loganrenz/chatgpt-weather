export interface Route {
  id: string
  name: string
  waypoints: Array<{ lat: number; lon: number }>
}

export interface TimelinePoint {
  time: string
  lat: number
  lon: number
  wind_speed?: number
  wind_dir?: number
  wave_height?: number
  score?: string
  hazards?: string[]
  [key: string]: any
}

export interface ForecastReport {
  route: string
  model: string
  departure: string
  track: TimelinePoint[]
  markdown: string
  html: string
}

export interface GribFile {
  name: string
  path: string
  size: number
  modified: string
  model?: string
  forecast_hour?: number
}

export interface HealthResponse {
  status: string
}
