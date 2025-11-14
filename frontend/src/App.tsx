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

import rbkLogo from "./assets/rbk-logo.png"; // <--- сюда положи свой логотип

// 🔗 адрес бэкенда
const API_URL = "https://ptobot-backend.onrender.com";

// Тёмная стеклянная тема + фирменный синий
const BRAND = {
  accent: "#0043A4",
  accentSoft: "rgba(0, 67, 164, 0.85)",
  accentGlow: "rgba(0, 67, 164, 0.55)",
  textPrimary: "#F9FAFB",
  textMuted: "#9CA3AF",
  panel: "rgba(15, 23, 42, 0.94)", // основной блок
  panelSoft: "rgba(15, 23, 42, 0.82)", // поля
  borderSoft: "rgba(148, 163, 184, 0.28)",
};

export default function TelegramWebAppDarkGlass() {
  // логотип из URL оставлю на будущее, но приоритизируем фирменный
  const [logoUrl, setLogoUrl] = useState<string>("");
  useEffect(() => {
    try {
      const qs = new URLSearchParams(window.location.search);
      const fromQuery = qs.get("logo");
      setLogoUrl(fromQuery || "");
    } catch {
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
  const [people, setPeople] = useState(""); // количество людей
  const [comment, setComment] = useState("");

  const [workTypes, setWorkTypes] = useState([
    { id: "1", name: "Земляные работы" },
    { id: "2", name: "Бетонирование" },
    { id: "3", name: "Монтаж конструкций" },
  ]);

  // подгружаем справочник из API, если доступен
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

  // Демо-история с "Людьми"
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

  // ----- Фото: выбор, предпросмотр -----
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

  // ----- Отправка отчёта в FastAPI -----
  const [sending, setSending] = useState(false);
  const [progress, setProgress] = useState(0);

  async function sendReport() {
    if (!workType) {
      alert("Выберите вид работ");
      return;
    }
    if (!files.length) {
      alert("Пожалуйста, выберите фото!");
      return;
    }

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

    files.forEach((file) => {
      form.append("photos", file);
    });

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
      className="min-h-screen w-full text-sm sm:text-base"
      style={{
        color: BRAND.textPrimary,
        background:
          "radial-gradient(circle at top, #020617 0, #020617 40%, #000000 100%)",
      }}
    >
      {/* Шапка с логотипом */}
      <header className="py-3 sm:py-4 border-b border-slate-800/70 bg-black/20 backdrop-blur-xl">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-3 px-4">
          <div className="flex items-center gap-3">
            {/* приоритет — фирменный логотип, резерв — текст */}
            {rbkLogo ? (
              <div className="h-8 sm:h-9 flex items-center">
                <img
                  src={logoUrl || rbkLogo}
                  alt="РБК СтройИнвест"
                  className="h-full w-auto object-contain"
                />
              </div>
            ) : (
              <div className="text-lg sm:text-xl font-semibold tracking-wide">
                РБК СтройИнвест
              </div>
            )}
            <span className="hidden sm:inline text-xs sm:text-sm text-slate-400">
              Ежедневные отчёты по стройплощадкам
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-slate-600 to-slate-900 flex items-center justify-center text-xs text-slate-100 shadow-lg shadow-black/40">
              ТГ
            </div>
          </div>
        </div>
      </header>

      {/* Основная зона */}
      <div className="max-w-5xl mx-auto px-3 sm:px-4 py-4 sm:py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          {/* Вкладки сверху — стеклянные пилюли */}
          <TabsList className="w-full flex bg-black/10 backdrop-blur-xl rounded-full p-1 border border-slate-700/40 shadow-[0_18px_45px_rgba(0,0,0,0.65)] mb-4 sm:mb-5">
            {[
              { value: "report", label: "Отчёт", icon: ClipboardList },
              { value: "history", label: "История", icon: History },
              { value: "admin", label: "Доступ", icon: ShieldCheck },
            ].map(({ value, label, icon: Icon }) => (
              <TabsTrigger
                key={value}
                value={value}
                className="flex-1 rounded-full data-[state=active]:shadow-[0_10px_35px_rgba(0,67,164,0.55)] data-[state=active]:text-slate-50 data-[state=inactive]:text-slate-300/70 text-xs sm:text-sm transition-all"
                style={{
                  background:
                    activeTab === value
                      ? `linear-gradient(135deg, ${BRAND.accentSoft}, #0A6CFF)`
                      : "transparent",
                  border:
                    activeTab === value
                      ? "1px solid rgba(191, 219, 254, 0.4)"
                      : "1px solid transparent",
                }}
              >
                <span className="flex items-center justify-center gap-2 py-1.5 sm:py-2">
                  <Icon className="h-4 w-4" />
                  <span>{label}</span>
                </span>
              </TabsTrigger>
            ))}
          </TabsList>

          {/* --------- Вкладка ОТЧЁТ --------- */}
          <TabsContent value="report" className="mt-0">
            <Card
              className="border shadow-2xl"
              style={{
                background: BRAND.panel,
                borderColor: BRAND.borderSoft,
                boxShadow:
                  "0 20px 60px rgba(0,0,0,0.75), 0 0 0 1px rgba(15,23,42,0.9)",
                backdropFilter: "blur(28px)",
              }}
            >
              <CardHeader className="pb-3 sm:pb-4">
                <CardTitle className="flex items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <ClipboardList className="h-5 w-5 text-slate-100" />
                      <span className="text-lg sm:text-xl font-semibold">
                        Ежедневный отчёт
                      </span>
                    </div>
                    <p className="mt-1 text-xs sm:text-sm text-slate-400">
                      {formatRu(date)}
                    </p>
                  </div>
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-4 sm:space-y-5 pb-5 sm:pb-6">
                <div className="grid sm:grid-cols-2 gap-3 sm:gap-4">
                  {/* Объект */}
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Объект<span className="text-red-500">*</span>
                    </label>
                    <Select value={project} onValueChange={setProject}>
                      <SelectTrigger
                        className="mt-1 bg-black/20 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm"
                        style={{
                          backdropFilter: "blur(22px)",
                        }}
                      >
                        <SelectValue placeholder="Выберите объект" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-700 text-slate-50">
                        {projects.map((p) => (
                          <SelectItem key={p.id} value={p.id}>
                            {p.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Вид работ */}
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Вид работы<span className="text-red-500">*</span>
                    </label>
                    <Select value={workType} onValueChange={setWorkType}>
                      <SelectTrigger
                        className="mt-1 bg-black/20 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm"
                        style={{
                          backdropFilter: "blur(22px)",
                        }}
                      >
                        <SelectValue placeholder="Выберите вид" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-700 text-slate-50">
                        {workTypes.map((w) => (
                          <SelectItem key={w.id} value={w.id}>
                            {w.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Дата / объём / техника */}
                <div className="grid sm:grid-cols-3 gap-3 sm:gap-4">
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Дата
                    </label>
                    <div className="relative mt-1">
                      <Input
                        type="date"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        className="bg-black/10 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm pr-9"
                        style={{ backdropFilter: "blur(18px)" }}
                      />
                      <CalendarIcon className="h-4 w-4 absolute right-2 top-1/2 -translate-y-1/2 text-slate-500" />
                    </div>
                  </div>
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Объём (м³)
                    </label>
                    <Input
                      placeholder="25"
                      value={volume}
                      onChange={(e) => setVolume(e.target.value)}
                      className="mt-1 bg-black/10 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm"
                      style={{ backdropFilter: "blur(18px)" }}
                    />
                  </div>
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Техника (шт.)
                    </label>
                    <Input
                      placeholder="3"
                      value={machines}
                      onChange={(e) => setMachines(e.target.value)}
                      className="mt-1 bg-black/10 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm"
                      style={{ backdropFilter: "blur(18px)" }}
                    />
                  </div>
                </div>

                {/* Люди */}
                <div className="grid sm:grid-cols-3 gap-3 sm:gap-4">
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Люди (чел.)
                    </label>
                    <Input
                      inputMode="numeric"
                      placeholder="5"
                      value={people}
                      onChange={(e) => setPeople(e.target.value)}
                      className="mt-1 bg-black/10 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm"
                      style={{ backdropFilter: "blur(18px)" }}
                    />
                  </div>
                </div>

                {/* Комментарий */}
                <div>
                  <label className="text-xs sm:text-sm font-medium text-slate-200">
                    Комментарий
                  </label>
                  <Textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    className="mt-1 bg-black/10 border-slate-700/70 text-slate-100 text-sm min-h-[80px]"
                    style={{ backdropFilter: "blur(18px)" }}
                    placeholder="Кратко опиши, что сделано за смену…"
                  />
                </div>

                {/* Фото */}
                <div>
                  <label className="text-xs sm:text-sm font-medium text-slate-200">
                    Фото<span className="text-red-500">*</span>
                  </label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    multiple
                    className="hidden"
                    onChange={onFilesSelected}
                  />
                  <div
                    className="mt-1 rounded-2xl border border-slate-700/70 bg-gradient-to-br from-slate-900/80 via-slate-900/60 to-slate-900/30 px-4 py-3 sm:py-4 flex items-center justify-between gap-3"
                    style={{ backdropFilter: "blur(26px)" }}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-2xl bg-black/40 border border-slate-700/80">
                        <ImageIcon className="h-5 w-5 text-slate-200" />
                      </div>
                      <div>
                        <div className="text-xs sm:text-sm text-slate-100">
                          Выберите фото
                        </div>
                        <div className="text-[11px] sm:text-xs text-slate-400">
                          JPG/PNG/HEIC, до 10 МБ за файл
                        </div>
                      </div>
                    </div>
                    <Button
                      className="gap-2 text-white text-xs sm:text-sm px-4 sm:px-5 py-2 rounded-full shadow-[0_12px_35px_rgba(0,67,164,0.7)]"
                      style={{
                        background: `linear-gradient(135deg, ${BRAND.accentSoft}, #0A6CFF)`,
                        border: "1px solid rgba(191,219,254,0.55)",
                      }}
                      onClick={onPickFiles}
                    >
                      <Upload className="h-4 w-4" />
                      Выбрать
                    </Button>
                  </div>

                  {/* Превью */}
                  <div className="grid grid-cols-3 gap-2 mt-3">
                    {(previews.length ? previews : [null, null, null])
                      .slice(0, 3)
                      .map((src, i) => (
                        <div
                          key={i}
                          className="aspect-video rounded-2xl bg-black/40 border border-slate-800/80 overflow-hidden flex items-center justify-center"
                          style={{ backdropFilter: "blur(18px)" }}
                        >
                          {src ? (
                            <img
                              src={src}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="text-[11px] text-slate-500">
                              Фото
                            </div>
                          )}
                        </div>
                      ))}
                  </div>
                </div>

                {/* Кнопка отправки (desktop/tablet) */}
                <div className="hidden sm:flex items-center gap-4 pt-2">
                  <Button
                    className="px-7 text-white rounded-full text-sm h-11 shadow-[0_18px_40px_rgba(0,67,164,0.85)]"
                    style={{
                      background: `linear-gradient(135deg, ${BRAND.accentSoft}, #0A6CFF)`,
                      border: "1px solid rgba(191,219,254,0.6)",
                    }}
                    onClick={sendReport}
                    disabled={sending}
                  >
                    {sending ? "Отправка…" : "Отправить отчёт"}
                  </Button>
                  <div className="flex-1 h-1.5 rounded-full overflow-hidden bg-slate-800/80">
                    <div
                      className="h-full transition-all"
                      style={{
                        width: `${progress}%`,
                        background:
                          "linear-gradient(90deg, rgba(191,219,254,0.8), #0A6CFF)",
                      }}
                    />
                  </div>
                  <span className="text-xs text-slate-400 min-w-[80px] text-right">
                    {progress ? `Загрузка: ${progress}%` : ""}
                  </span>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* --------- Вкладка ИСТОРИЯ --------- */}
          <TabsContent value="history" className="mt-0">
            <Card
              className="border shadow-2xl"
              style={{
                background: BRAND.panel,
                borderColor: BRAND.borderSoft,
                boxShadow:
                  "0 20px 60px rgba(0,0,0,0.75), 0 0 0 1px rgba(15,23,42,0.9)",
                backdropFilter: "blur(28px)",
              }}
            >
              <CardHeader className="pb-3 sm:pb-4">
                <CardTitle className="flex items-center gap-2">
                  <History className="h-5 w-5 text-slate-100" />
                  <span className="text-lg sm:text-xl font-semibold">
                    История отчётов
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 sm:space-y-5 pb-5 sm:pb-6">
                <div className="grid sm:grid-cols-4 gap-3 sm:gap-4">
                  <div className="sm:col-span-2">
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Объект
                    </label>
                    <Select value={project} onValueChange={setProject}>
                      <SelectTrigger className="mt-1 bg-black/15 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm">
                        <SelectValue placeholder="Выберите объект" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-700 text-slate-50">
                        {projects.map((p) => (
                          <SelectItem key={p.id} value={p.id}>
                            {p.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      С даты
                    </label>
                    <Input
                      type="date"
                      className="mt-1 bg-black/15 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      По дату
                    </label>
                    <Input
                      type="date"
                      className="mt-1 bg-black/15 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm"
                    />
                  </div>
                </div>

                <div className="grid gap-3 sm:gap-4">
                  {history
                    .filter((h) => h.project_id === project)
                    .map((item) => (
                      <div
                        key={item.id}
                        className="p-4 rounded-2xl border border-slate-700/80 bg-black/25 flex flex-col gap-2 sm:gap-3"
                        style={{ backdropFilter: "blur(20px)" }}
                      >
                        <div className="flex items-center justify-between gap-3 text-xs sm:text-sm font-medium text-slate-100">
                          <span>{formatRu(item.date)}</span>
                          <span className="text-slate-300">
                            {
                              workTypes.find(
                                (w) => w.id === item.work_type_id
                              )?.name
                            }
                          </span>
                        </div>
                        <p className="text-xs sm:text-sm text-slate-300">
                          {toOneLine(item.description)}
                        </p>
                        <div className="flex gap-2 mt-1 flex-wrap">
                          {item.photos.map((src, i) => (
                            <img
                              key={i}
                              src={src}
                              alt="Фото отчёта"
                              className="h-16 sm:h-20 rounded-xl border border-slate-700/70 object-cover"
                            />
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* --------- Вкладка ДОСТУП --------- */}
          <TabsContent value="admin" className="mt-0">
            <Card
              className="border shadow-2xl"
              style={{
                background: BRAND.panel,
                borderColor: BRAND.borderSoft,
                boxShadow:
                  "0 20px 60px rgba(0,0,0,0.75), 0 0 0 1px rgba(15,23,42,0.9)",
                backdropFilter: "blur(28px)",
              }}
            >
              <CardHeader className="pb-3 sm:pb-4">
                <CardTitle className="flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5 text-slate-100" />
                  <span className="text-lg sm:text-xl font-semibold">
                    Назначение доступа
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 sm:space-y-5 pb-5 sm:pb-6">
                <div className="grid sm:grid-cols-3 gap-3 sm:gap-4">
                  <div className="sm:col-span-1">
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Найти подрядчика
                    </label>
                    <Input
                      placeholder="Поиск по названию / Telegram"
                      className="mt-1 bg-black/15 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Объект
                    </label>
                    <Select value={project} onValueChange={setProject}>
                      <SelectTrigger className="mt-1 bg-black/15 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm">
                        <SelectValue placeholder="Выберите объект" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-700 text-slate-50">
                        {projects.map((p) => (
                          <SelectItem key={p.id} value={p.id}>
                            {p.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-xs sm:text-sm font-medium text-slate-200">
                      Роль
                    </label>
                    <Select defaultValue="reporter">
                      <SelectTrigger className="mt-1 bg-black/15 border-slate-700/70 text-slate-100 h-10 sm:h-11 text-sm">
                        <SelectValue placeholder="Роль" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-700 text-slate-50">
                        <SelectItem value="reporter">
                          Может отправлять отчёты
                        </SelectItem>
                        <SelectItem value="viewer">
                          Только просмотр
                        </SelectItem>
                        <SelectItem value="manager">Менеджер</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div
                  className="p-4 rounded-2xl border border-slate-700/80 bg-black/25"
                  style={{ backdropFilter: "blur(18px)" }}
                >
                  <div className="text-xs sm:text-sm font-medium mb-2 text-slate-200">
                    Текущие назначения
                  </div>
                  <div className="grid gap-2">
                    {accessList.map((row, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-700/80"
                      >
                        <div>
                          <div className="font-medium text-slate-50 text-xs sm:text-sm">
                            {row.user.name}
                          </div>
                          <div className="text-[11px] sm:text-xs text-slate-400">
                            Проекты:{" "}
                            {row.projects
                              .map(
                                (pid) =>
                                  projects.find((p) => p.id === pid)?.name
                              )
                              .join(", ")}
                          </div>
                        </div>
                        <div className="text-[11px] sm:text-xs text-slate-400">
                          Роль: {row.role}
                        </div>
                        <Button
                          variant="secondary"
                          size="sm"
                          className="rounded-full px-4 text-[11px] sm:text-xs text-slate-50"
                          style={{
                            background: `linear-gradient(135deg, ${BRAND.accentSoft}, #0A6CFF)`,
                            border: "1px solid rgba(191,219,254,0.6)",
                          }}
                        >
                          Изменить
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Мобильная панель отправки (фиксирована снизу) */}
      <div
        className="sm:hidden fixed inset-x-0 bottom-0 border-t border-slate-800/80 px-3 pt-2"
        style={{
          background: "rgba(0,0,0,0.85)",
          backdropFilter: "blur(22px)",
          paddingBottom: "calc(env(safe-area-inset-bottom, 0px) + 10px)",
        }}
      >
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <Button
            className="flex-1 text-white rounded-full text-sm h-11 shadow-[0_18px_40px_rgba(0,67,164,0.85)]"
            style={{
              background: `linear-gradient(135deg, ${BRAND.accentSoft}, #0A6CFF)`,
              border: "1px solid rgba(191,219,254,0.6)",
            }}
            onClick={sendReport}
            disabled={sending}
          >
            {sending ? "Отправка…" : "Отправить отчёт"}
          </Button>
        </div>
      </div>
    </div>
  );
}

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

// Небольшие “самопроверки”
try {
  console.assert(typeof formatRu === "function", "formatRu существует");
  console.assert(
    toOneLine(`Текст\nОбъём: 10 м³\nТехника: 2\nЛюди: 6`) ===
      "Объём: 10 м³ • Техника: 2 • Люди: 6",
    "toOneLine собирает значения в одну строку"
  );
} catch {}
