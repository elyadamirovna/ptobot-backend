export type WorkType = {
  id: string
  name: string
}

export type WorkTypeResponse = {
  id: string | number
  name: string
}

export type Project = {
  id: string
  name: string
  address: string
}

export type HistoryRow = {
  id: number
  project_id: string
  date: string
  work_type_id: string
  description: string
  photos: string[]
}

export type AccessRow = {
  user: { id: number; name: string }
  projects: string[]
  role: string
}

export type TelegramWebApp = {
  ready: () => void
  expand?: () => void
  close: () => void
  disableVerticalSwipes?: () => void
  enableVerticalSwipes?: () => void
}

export type TelegramWindow = {
  WebApp?: TelegramWebApp
}

declare global {
  interface Window {
    Telegram?: TelegramWindow
  }
}
