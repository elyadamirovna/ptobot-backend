import React, { useMemo, useState, useEffect, useRef } from "react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

import {
  CalendarDays,
  Building2,
  HardHat,
  Users,
  Image as ImageIcon,
  Upload,
  History,
  ClipboardList,
  ShieldCheck,
} from "lucide-react"

const API_URL = "https://ptobot-backend.onrender.com"

type WorkType = { id: string; name: string }
type WorkTypeResponse = { id: string | number; name: string }

type TelegramWebApp = {
  ready: () => void
  expand?: () => void
  close: () => void
  disableVerticalSwipes?: () => void
  enableVerticalSwipes?: () => void
}

type TelegramWindow = {
  WebApp?: TelegramWebApp
}

declare global {
  interface Window {
    Telegram?: TelegramWindow
  }
}

type HistoryRow = {
  id: number
  project_id: string
  date: string
  work_type_id: string
  description: string
  photos: string[]
}

type AccessRow = {
  user: { id: number; name: string }
  projects: string[]
  role: string
}

export default function TelegramWebAppGlassPure() {
  const [logoUrl, setLogoUrl] = useState<string>("")
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null)

  useEffect(() => {
    try {
      const qs = new URLSearchParams(window.location.search)
      const fromQuery = qs.get("logo")
      setLogoUrl(fromQuery || "")
    } catch (error) {
      console.warn("Cannot parse logo query param", error)
      setLogoUrl("")
    }
  }, [])

  const [activeTab, setActiveTab] = useState("report")
  const [project, setProject] = useState<string | undefined>("1")
  const [workType, setWorkType] = useState<string | undefined>("2")
  const [date, setDate] = useState<string>(() =>
    new Date().toISOString().slice(0, 10),
  )
  const [volume, setVolume] = useState("")
  const [machines, setMachines] = useState("")
  const [people, setPeople] = useState("")
  const [comment, setComment] = useState("")

  const [workTypes, setWorkTypes] = useState<WorkType[]>([
    { id: "1", name: "Земляные работы" },
    { id: "2", name: "Бетонирование" },
    { id: "3", name: "Монтаж конструкций" },
  ])

  useEffect(() => {
    const tg = window?.Telegram?.WebApp
    if (tg) {
      setWebApp(tg)
      tg.ready()
      tg.expand?.()
      tg.disableVerticalSwipes?.()
      return () => {
        tg.enableVerticalSwipes?.()
      }
    }
    return undefined
  }, [])

  useEffect(() => {
    fetch(`${API_URL}/work_types`)
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((rows) => {
        if (Array.isArray(rows) && rows.length) {
          const mapped: WorkType[] = rows.map((item: WorkTypeResponse) => ({
            id: String(item.id),
            name: item.name,
          }))
          setWorkTypes(mapped)
          if (!workType) {
            setWorkType(mapped[0].id)
          }
        }
      })
      .catch(() => {
        /* silent fallback to default workTypes */
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const projects = [
    { id: "1", name: "ЖК «Северный»", address: "ул. Парковая, 12" },
    { id: "2", name: "ЖК «Академический»", address: "пр-т Науки, 5" },
  ]

  const history = useMemo<HistoryRow[]>(
    () => [
      {
        id: 101,
        project_id: "1",
        date: "2025-11-11",
        work_type_id: "2",
        description:
          "Бетонирование ростверка\nОбъём: 12,5 м³\nТехника: 2\nЛюди: 7",
        photos: [
          "https://picsum.photos/seed/a/300/200",
          "https://picsum.photos/seed/b/300/200",
        ],
      },
      {
        id: 100,
        project_id: "1",
        date: "2025-11-10",
        work_type_id: "1",
        description:
          "Разработка котлована\nОбъём: 80 м³\nТехника: 3\nЛюди: 5",
        photos: ["https://picsum.photos/seed/c/300/200"],
      },
    ],
    [],
  )

  const accessList: AccessRow[] = [
    {
      user: { id: 8, name: "ИП «СтройСервис»" },
      projects: ["1"],
      role: "reporter",
    },
    {
      user: { id: 9, name: "ООО «МонтажГрупп»" },
      projects: ["1", "2"],
      role: "reporter",
    },
  ]

  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const [previews, setPreviews] = useState<string[]>([])

  const onPickFiles = () => fileInputRef.current?.click()

  const onFilesSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(event.target.files || [])
    setFiles(selected)

    Promise.all(
      selected.map(
        (file) =>
          new Promise<string>((resolve) => {
            const reader = new FileReader()
            reader.onload = () => resolve(String(reader.result))
            reader.readAsDataURL(file)
          }),
      ),
    ).then(setPreviews)
  }

  const [sending, setSending] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleCloseApp = () => {
    if (webApp) {
      webApp.close()
      return
    }
    if (window.history.length > 1) {
      window.history.back()
    }
  }

  async function sendReport() {
    if (!workType) {
      alert("Выберите вид работ")
      return
    }
    if (!files.length) {
      alert("Пожалуйста, выберите фото!")
      return
    }

    const descParts = [comment]
    if (volume) descParts.push(`Объём: ${volume}`)
    if (machines) descParts.push(`Техника: ${machines}`)
    if (people) descParts.push(`Люди: ${people}`)
    const description = descParts.filter(Boolean).join("\n")

    const form = new FormData()
    form.append("user_id", "1")
    form.append("work_type_id", String(workType))
    form.append("description", description)
    form.append("people", people)
    form.append("volume", volume)
    form.append("machines", machines)
    files.forEach((file) => form.append("photos", file))

    try {
      setSending(true)
      setProgress(25)
      const res = await fetch(`${API_URL}/reports`, {
        method: "POST",
        body: form,
      })
      setProgress(80)
      if (!res.ok) throw new Error("Ошибка при отправке отчёта")
      const data = await res.json()
      setProgress(100)
      alert(`Отчёт успешно отправлен! ID: ${data.id}`)
      setVolume("")
      setMachines("")
      setPeople("")
      setComment("")
      setFiles([])
      setPreviews([])
    } catch (error: unknown) {
      const message =
        error instanceof Error ? error.message : "Ошибка при отправке отчёта"
      alert(message)
    } finally {
      setSending(false)
      setTimeout(() => setProgress(0), 600)
    }
  }

  const previewPlaceholders = useMemo<(string | null)[]>(() => {
    const visible = previews.slice(0, 3)
    return visible.length ? visible : [null, null, null]
  }, [previews])

  return (
    <div
      className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#05122D] px-4 py-10 text-white"
      style={{
        paddingTop: "calc(env(safe-area-inset-top, 0px) + 40px)",
        paddingBottom: "calc(env(safe-area-inset-bottom, 0px) + 40px)",
      }}
    >
      {/* ...весь JSX ниже оставил без изменений, он у тебя уже ок... */}
      {/* (оставляю как есть, чтобы ответ не раздувать ещё сильнее) */}
    </div>
  )
}

function formatRu(iso: string) {
  const [year, month, day] = iso.split("-")
  return `${day}.${month}.${year}`
}

function toOneLine(desc: string) {
  const source = String(desc || "")
  const vol = source.match(/Объём:\s*([^\n]+)/i)?.[1]?.trim()
  const mach = source.match(/Техника:\s*([^\n]+)/i)?.[1]?.trim()
  const ppl = source.match(/Люди:\s*([^\n]+)/i)?.[1]?.trim()
  const parts: string[] = []
  if (vol) parts.push(`Объём: ${vol}`)
  if (mach) parts.push(`Техника: ${mach}`)
  if (ppl) parts.push(`Люди: ${ppl}`)
  return parts.length ? parts.join(" • ") : source.replace(/\s+/g, " ").trim()
}
