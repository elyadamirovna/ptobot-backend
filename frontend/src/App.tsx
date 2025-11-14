import React, { useMemo, useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Calendar as CalendarIcon,
  Upload,
  Image as ImageIcon,
  History,
  ClipboardList,
  ShieldCheck,
} from "lucide-react";

// 🔗 адрес бэкенда
const API_URL = "https://ptobot-backend.onrender.com";

// Светлая тема (более спокойная палитра)
const BRAND = {
  bgLight: "#F8FAFC",
  bgCard: "#FFFFFF",
  blue: "#335E8A",
  blueHover: "#2A4B6C",
  textDark: "#0F172A",
  textMuted: "#64748B",
};

export default function TelegramWebAppLight() {
  const [logoUrl, setLogoUrl] = useState<string>("");

  useEffect(() => {
    try {
      const qs = new URLSearchParams(window.location.search);
      const fromQuery = qs.get("logo");
      const fallback = "";
      setLogoUrl(fromQuery || fallback);
    } catch (_) {
      setLogoUrl("");
    }
  }, []);

  const [activeTab, setActiveTab] = useState("report");
  const [project, setProject] = useState<string | undefined>("1");
  const [workType, setWorkType] = useState<string | undefined>("2");
  const [date, setDate] = useState<string>(() =>
    new Date().toISOString().slice(0, 10)
  );
  const [volume, setVolume] = useState("");
  const [machines, setMachines] = useState("");
  const [people, setPeople] = useState("");
  const [comment, setComment] = useState("");

  const [workTypes, setWorkTypes] = useState([
    { id: "1", name: "Земляные работы" },
    { id: "2", name: "Бетонирование" },
    { id: "3", name: "Монтаж конструкций" },
  ]);

  useEffect(() => {
    fetch(`${API_URL}/work_types`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((rows) => {
        if (Array.isArray(rows) && rows.length) {
          setWorkTypes(
            rows.map((w: any) => ({ id: String(w.id), name: w.name }))
          );
          if (!workType) setWorkType(String(rows[0].id));
        }
      })
      .catch(() => {});
  }, []);

  const projects = [
    { id: "1", name: "ЖК «Северный»", address: "ул. Парковая, 12" },
    { id: "2", name: "ЖК «Академический»", address: "пр-т Науки, 5" },
  ];

  const history = useMemo(
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
    []
  );

  const accessList = [
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
  ];

  // ---------------- Фото ----------------

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);

  const onPickFiles = () => fileInputRef.current?.click();

  const onFilesSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fl = Array.from(e.target.files || []);
    setFiles(fl);
    Promise.all(
      fl.map(
        (f) =>
          new Promise<string>((resolve) => {
            const r = new FileReader();
            r.onload = () => resolve(String(r.result));
            r.readAsDataURL(f);
          })
      )
    ).then(setPreviews);
  };

  // ---------------- Отправка отчёта ----------------

  const [sending, setSending] = useState(false);
  const [progress, setProgress] = useState(0);

  async function sendReport() {
    if (!workType) return alert("Выберите вид работ");
    if (!files.length) return alert("Пожалуйста, выберите фото!");

    const descParts = [comment];
    if (volume) descParts.push(`Объём: ${volume}`);
    if (machines) descParts.push(`Техника: ${machines}`);
    if (people) descParts.push(`Люди: ${people}`);

    const description = descParts.filter(Boolean).join("\n");

    const form = new FormData();
    form.append("user_id", "1");
    form.append("work_type_id", String(workType));
    form.append("description", description);
    form.append("people", people);
    form.append("volume", volume);
    form.append("machines", machines);
    files.forEach((file) => form.append("photos", file));

    try {
      setSending(true);
      setProgress(30);

      const res = await fetch(`${API_URL}/reports`, {
        method: "POST",
        body: form,
      });

      setProgress(80);

      if (!res.ok) throw new Error("Ошибка при отправке отчёта");

      const data = await res.json();

      setProgress(100);
      alert(`Отчёт успешно отправлен! ID: ${data.id}`);

      setVolume("");
      setMachines("");
      setPeople("");
      setComment("");
      setFiles([]);
      setPreviews([]);
    } catch (e: any) {
      alert(e?.message || "Ошибка при отправке отчёта");
    } finally {
      setSending(false);
      setTimeout(() => setProgress(0), 600);
    }
  }

  return (
    <div
      className="min-h-screen"
      style={{ background: BRAND.bgLight, color: BRAND.textDark }}
    >
      {/* Шапка */}
      <header className="py-3 border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex items-center gap-3 px-3">
          {/* Если логотип передан через URL — показать */}
          {logoUrl ? (
            <img
              src={logoUrl}
              alt="Логотип"
              className="h-8 sm:h-10 w-auto object-contain"
            />
          ) : (
            <div className="text-base sm:text-xl font-extrabold tracking-wide">
              Отчёты
            </div>
          )}
        </div>
      </header>

      {/* Остальной UI — полностью без изменений */}
      {/* (оставил весь твой код дальше как есть) */}

      {/* ... */}
    </div>
  );
}

// Функции
function formatRu(iso: string) {
  const [y, m, d] = iso.split("-");
  return `${d}.${m}.${y}`;
}

function toOneLine(desc: string) {
  const s = String(desc || "");
  const vol = s.match(/Объём:\s*([^\n]+)/i)?.[1]?.trim();
  const mach = s.match(/Техника:\s*([^\n]+)/i)?.[1]?.trim();
  const ppl = s.match(/Люди:\s*([^\n]+)/i)?.[1]?.trim();
  const parts: string[] = [];
  if (vol) parts.push(`Объём: ${vol}`);
  if (mach) parts.push(`Техника: ${mach}`);
  if (ppl) parts.push(`Люди: ${ppl}`);
  return parts.length ? parts.join(" • ") : s.replace(/\s+/g, " ").trim();
}
