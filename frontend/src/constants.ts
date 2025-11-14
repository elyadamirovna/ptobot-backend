import type { AccessRow, HistoryRow, Project, WorkType } from "@/types"

export const API_URL =
  import.meta.env.VITE_API_URL ?? "https://ptobot-backend.onrender.com"

export const DEFAULT_WORK_TYPES: WorkType[] = [
  { id: "1", name: "Земляные работы" },
  { id: "2", name: "Бетонирование" },
  { id: "3", name: "Монтаж конструкций" },
]

export const PROJECTS: Project[] = [
  { id: "1", name: "ЖК «Северный»", address: "ул. Парковая, 12" },
  { id: "2", name: "ЖК «Академический»", address: "пр-т Науки, 5" },
]

export const DEMO_HISTORY: HistoryRow[] = [
  {
    id: 101,
    project_id: "1",
    date: "2025-11-11",
    work_type_id: "2",
    description: "Бетонирование ростверка\nОбъём: 12,5 м³\nТехника: 2\nЛюди: 7",
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
    description: "Разработка котлована\nОбъём: 80 м³\nТехника: 3\nЛюди: 5",
    photos: ["https://picsum.photos/seed/c/300/200"],
  },
]

export const ACCESS_LIST: AccessRow[] = [
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
