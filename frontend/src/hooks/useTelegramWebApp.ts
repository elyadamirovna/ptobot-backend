import { useCallback, useEffect, useRef } from "react"

import type { TelegramWebApp } from "@/types"

export function useTelegramWebApp() {
  const webAppRef = useRef<TelegramWebApp | null>(null)

  useEffect(() => {
    const tg = window.Telegram?.WebApp ?? null
    webAppRef.current = tg

    if (!tg) {
      return
    }

    tg.ready()
    tg.expand?.()
    tg.disableVerticalSwipes?.()

    const previousOverscroll = document.body.style.overscrollBehaviorY
    document.body.style.overscrollBehaviorY = "none"

    return () => {
      document.body.style.overscrollBehaviorY = previousOverscroll
      tg.enableVerticalSwipes?.()
    }
  }, [])

  const close = useCallback(() => {
    const tg = webAppRef.current
    if (tg) {
      tg.close()
      return
    }
    if (window.history.length > 1) {
      window.history.back()
    }
  }, [])

  return { close }
}
