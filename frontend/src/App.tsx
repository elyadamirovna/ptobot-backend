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
  CalendarDays,
  Building2,
  HardHat,
  Users,
  Image as ImageIcon,
  Upload,
  History,
  ClipboardList,
  ShieldCheck,
} from "lucide-react";

const API_URL = "https://ptobot-backend.onrender.com";

type WorkType = { id: string; name: string };
type WorkTypeResponse = { id: string | number; name: string };

type TelegramWebApp = {
  ready: () => void;
  expand?: () => void;
  close: () => void;
  disableVerticalSwipes?: () => void;
  enableVerticalSwipes?: () => void;
};

type TelegramWindow = {
  WebApp?: TelegramWebApp;
};

declare global {
  interface Window {
    Telegram?: TelegramWindow;
  }
}

type HistoryRow = {
  id: number;
  project_id: string;
  date: string;
  work_type_id: string;
  description: string;
  photos: string[];
};

type AccessRow = {
  user: { id: number; name: string };
  projects: string[];
  role: string;
};

export default function TelegramWebAppGlassPure() {
  const [logoUrl, setLogoUrl] = useState<string>("");
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);

  useEffect(() => {
    try {
      const qs = new URLSearchParams(window.location.search);
      const fromQuery = qs.get("logo");
      setLogoUrl(fromQuery || "");
    } catch (error) {
      console.warn("Cannot parse logo query param", error);
      setLogoUrl("");
    }
  }, []);

  const [activeTab, setActiveTab] = useState("report");
  const [project, setProject] = useState<string | undefined>("1");
  const [workType, setWorkType] = useState<string | undefined>("2");
  const [date, setDate] = useState<string>(() => new Date().toISOString().slice(0, 10));
  const [volume, setVolume] = useState("");
  const [machines, setMachines] = useState("");
  const [people, setPeople] = useState("");
  const [comment, setComment] = useState("");

  const [workTypes, setWorkTypes] = useState<WorkType[]>([
    { id: "1", name: "Земляные работы" },
    { id: "2", name: "Бетонирование" },
    { id: "3", name: "Монтаж конструкций" },
  ]);

  useEffect(() => {
    const tg = window?.Telegram?.WebApp;
    if (tg) {
      setWebApp(tg);
      tg.ready();
      tg.expand?.();
      tg.disableVerticalSwipes?.();
      return () => {
        tg.enableVerticalSwipes?.();
      };
    }
    return undefined;
  }, []);

  useEffect(() => {
    fetch(`${API_URL}/work_types`)
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((rows) => {
        if (Array.isArray(rows) && rows.length) {
          const mapped: WorkType[] = rows.map((item: WorkTypeResponse) => ({
            id: String(item.id),
            name: item.name,
          }));
          setWorkTypes(mapped);
          if (!workType) {
            setWorkType(mapped[0].id);
          }
        }
      })
      .catch(() => {
        /* silent fallback to default workTypes */
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const projects = [
    { id: "1", name: "ЖК «Северный»", address: "ул. Парковая, 12" },
    { id: "2", name: "ЖК «Академический»", address: "пр-т Науки, 5" },
  ];

  const history = useMemo<HistoryRow[]>(
    () => [
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
    ],
    []
  );

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
  ];

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);

  const onPickFiles = () => fileInputRef.current?.click();

  const onFilesSelected = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(event.target.files || []);
    setFiles(selected);

    Promise.all(
      selected.map(
        (file) =>
          new Promise<string>((resolve) => {
            const reader = new FileReader();
            reader.onload = () => resolve(String(reader.result));
            reader.readAsDataURL(file);
          })
      )
    ).then(setPreviews);
  };

  const [sending, setSending] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleCloseApp = () => {
    if (webApp) {
      webApp.close();
      return;
    }
    if (window.history.length > 1) {
      window.history.back();
    }
  };

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
    files.forEach((file) => form.append("photos", file));

    try {
      setSending(true);
      setProgress(25);
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
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Ошибка при отправке отчёта";
      alert(message);
    } finally {
      setSending(false);
      setTimeout(() => setProgress(0), 600);
    }
  }

  return (
    <div
      className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#05122D] px-4 py-10 text-white"
      style={{
        paddingTop: "calc(env(safe-area-inset-top, 0px) + 40px)",
        paddingBottom: "calc(env(safe-area-inset-bottom, 0px) + 40px)",
      }}
    >
      <div className="pointer-events-none absolute -left-24 -top-32 h-72 w-72 rounded-full bg-sky-500/40 blur-[140px]" />
      <div className="pointer-events-none absolute bottom-0 right-[-120px] h-[420px] w-[420px] rounded-full bg-indigo-600/40 blur-[160px]" />
      <div className="pointer-events-none absolute inset-x-1/2 top-[40%] h-64 w-64 -translate-x-1/2 rounded-full bg-cyan-400/30 blur-[120px]" />

      <div className="relative z-10 w-full max-w-[440px]">
        <div className="relative overflow-hidden rounded-[44px] border border-white/25 bg-white/10 px-6 pb-8 pt-7 shadow-[0_35px_80px_rgb(6_24_74_/_0.6)] backdrop-blur-[32px]">
          <div className="absolute inset-x-10 -top-32 h-48 rounded-full bg-white/10 blur-[120px]" />
          <div className="absolute inset-0 rounded-[44px] border border-white/10" />

          <div className="relative">
            <header className="mb-6 space-y-4">
              <div className="flex items-center justify-between text-[13px]">
                <button
                  type="button"
                  onClick={handleCloseApp}
                  className="rounded-full border border-white/30 bg-white/80 px-4 py-1.5 font-semibold text-sky-900 shadow-[0_10px_28px_rgb(15_118_255_/_0.35)] backdrop-blur transition hover:brightness-110 active:scale-[0.98]"
                >
                  Закрыть
                </button>
                <div className="rounded-full border border-white/25 bg-white/15 px-3 py-1 text-[12px] text-white/75 shadow-[0_8px_20px_rgb(5_24_74_/_0.4)]">
                  Telegram WebApp
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {logoUrl ? (
                    <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-3xl border border-white/40 bg-white/80 shadow-[0_12px_32px_rgb(59_130_246_/_0.4)]">
                      <img src={logoUrl} alt="Логотип" className="h-full w-full object-contain" />
                    </div>
                  ) : (
                    <div className="flex h-10 w-10 items-center justify-center rounded-3xl bg-white/85 text-sm font-semibold text-sky-800 shadow-[0_12px_32px_rgb(3_144_255_/_0.7)]">
                      РБК
                    </div>
                  )}
                  <div className="leading-tight">
                    <div className="text-[11px] uppercase tracking-[0.24em] text-white/70">
                      Стройинвест
                    </div>
                    <div className="text-xs font-medium text-white/85">
                      Ежедневные отчёты по объектам
                    </div>
                  </div>
                </div>
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/75 text-[11px] font-semibold text-sky-900 shadow-[0_14px_34px_rgb(2_110_255_/_0.65)]">
                  ИП
                </div>
              </div>
            </header>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="mb-5 grid grid-cols-3 gap-1 rounded-full bg-white/15 p-1 text-[12px] text-white/75">
                <TabsTrigger
                  value="report"
                  className="flex items-center justify-center gap-1 rounded-full px-3 py-2 transition data-[state=active]:bg-white data-[state=active]:text-sky-900 data-[state=active]:shadow-[0_12px_30px_rgb(255_255_255_/_0.45)]"
                >
                  <ClipboardList className="h-3.5 w-3.5" /> Отчёт
                </TabsTrigger>
                <TabsTrigger
                  value="history"
                  className="flex items-center justify-center gap-1 rounded-full px-3 py-2 transition data-[state=active]:bg-white data-[state=active]:text-sky-900 data-[state=active]:shadow-[0_12px_30px_rgb(255_255_255_/_0.45)]"
                >
                  <History className="h-3.5 w-3.5" /> История
                </TabsTrigger>
                <TabsTrigger
                  value="admin"
                  className="flex items-center justify-center gap-1 rounded-full px-3 py-2 transition data-[state=active]:bg-white data-[state=active]:text-sky-900 data-[state=active]:shadow-[0_12px_30px_rgb(255_255_255_/_0.45)]"
                >
                  <ShieldCheck className="h-3.5 w-3.5" /> Доступ
                </TabsTrigger>
              </TabsList>

              <TabsContent value="report" className="mt-0">
                <Card className="border-white/20 bg-white/10 text-white shadow-[0_24px_60px_rgb(15_28_83_/_0.45)] backdrop-blur-[28px]">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-[20px] font-semibold tracking-wide text-white">
                      Ежедневный отчёт
                    </CardTitle>
                    <p className="text-xs text-white/80">{formatRu(date)}</p>
                  </CardHeader>
                  <CardContent className="space-y-5 text-[13px]">
                    <div className="grid gap-3 rounded-3xl border border-white/20 bg-white/5 p-4 backdrop-blur-xl">
                      <div className="space-y-1.5">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/60">
                          Объект
                        </p>
                        <div className="relative">
                          <Building2 className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/65" />
                          <Select value={project} onValueChange={setProject}>
                            <SelectTrigger className="h-11 rounded-2xl border border-white/20 bg-white/10 pl-9 pr-10 text-[13px] text-white/90 shadow-[0_16px_38px_rgb(7_24_74_/_0.55)] backdrop-blur">
                              <SelectValue placeholder="Выберите объект" />
                            </SelectTrigger>
                            <SelectContent className="border border-white/15 bg-[#07132F]/95 text-white">
                              {projects.map((item) => (
                                <SelectItem key={item.id} value={item.id}>
                                  {item.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="space-y-1.5">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/60">
                          Вид работ
                        </p>
                        <div className="relative">
                          <HardHat className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/65" />
                          <Select value={workType} onValueChange={setWorkType}>
                            <SelectTrigger className="h-11 rounded-2xl border border-white/20 bg-white/10 pl-9 pr-10 text-[13px] text-white/90 shadow-[0_16px_38px_rgb(7_24_74_/_0.55)] backdrop-blur">
                              <SelectValue placeholder="Выберите вид работ" />
                            </SelectTrigger>
                            <SelectContent className="border border-white/15 bg-[#07132F]/95 text-white">
                              {workTypes.map((item) => (
                                <SelectItem key={item.id} value={item.id}>
                                  {item.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3">
                      <div className="space-y-1.5">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/60">
                          Дата
                        </p>
                        <div className="relative">
                          <Input
                            type="date"
                            value={date}
                            onChange={(event) => setDate(event.target.value)}
                            className="h-11 rounded-2xl border border-white/20 bg-white/10 pr-10 text-[13px] text-white/90 placeholder:text-white/50"
                          />
                          <CalendarDays className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/65" />
                        </div>
                      </div>
                      <div className="space-y-1.5">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/60">
                          Объём
                        </p>
                        <div className="flex items-center gap-2">
                          <Input
                            placeholder="12,5"
                            value={volume}
                            onChange={(event) => setVolume(event.target.value)}
                            className="h-11 flex-1 rounded-2xl border border-white/20 bg-white/10 text-[13px] text-white/90 placeholder:text-white/40"
                          />
                          <div className="flex h-11 items-center justify-center rounded-2xl border border-white/15 bg-white/10 px-3 text-[11px] text-white/75">
                            м³
                          </div>
                        </div>
                      </div>
                      <div className="space-y-1.5">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/60">
                          Техника
                        </p>
                        <div className="flex items-center gap-2">
                          <Input
                            placeholder="3"
                            value={machines}
                            onChange={(event) => setMachines(event.target.value)}
                            className="h-11 flex-1 rounded-2xl border border-white/20 bg-white/10 text-[13px] text-white/90 placeholder:text-white/40"
                          />
                          <div className="flex h-11 items-center justify-center rounded-2xl border border-white/15 bg-white/10 px-3 text-[11px] text-white/75">
                            шт.
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/60">
                        Люди
                      </p>
                      <div className="relative">
                        <Users className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/65" />
                        <Input
                          inputMode="numeric"
                          placeholder="кол-во человек"
                          value={people}
                          onChange={(event) => setPeople(event.target.value)}
                          className="h-11 rounded-2xl border border-white/20 bg-white/10 pl-9 text-[13px] text-white/90 placeholder:text-white/40"
                        />
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/60">
                        Комментарий
                      </p>
                      <Textarea
                        value={comment}
                        onChange={(event) => setComment(event.target.value)}
                        placeholder="Кратко опишите выполненные работы…"
                        className="min-h-[96px] rounded-3xl border border-white/20 bg-white/10 text-[13px] text-white/90 placeholder:text-white/45"
                      />
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.16em] text-white/65">
                        <span className="flex items-center gap-1.5">
                          <ImageIcon className="h-3.5 w-3.5" /> Выберите фото
                        </span>
                        <span className="text-white/55">JPG/PNG/HEIC, до 10 МБ</span>
                      </div>

                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        multiple
                        className="hidden"
                        onChange={onFilesSelected}
                      />

                      <div className="flex items-center gap-3 rounded-3xl border border-dashed border-white/30 bg-white/5 px-4 py-3 text-sm text-white/75">
                        <div className="flex-1 text-[12px] leading-tight">
                          Перетащите фото или нажмите «Выбрать»
                        </div>
                        <Button
                          type="button"
                          className="flex items-center gap-2 rounded-full bg-gradient-to-r from-[#5FE0FF] via-[#7DF0FF] to-[#B5F5FF] px-4 py-1.5 text-[12px] font-semibold text-sky-900 shadow-[0_18px_50px_rgb(3_144_255_/_0.9)] hover:brightness-110"
                          onClick={onPickFiles}
                        >
                          <Upload className="h-3.5 w-3.5" /> Выбрать
                        </Button>
                      </div>

                      <div className="grid grid-cols-3 gap-3">
                        {(previews.length ? previews : [null, null, null]).slice(0, 3).map((src, index) => (
                          <div
                            key={index}
                            className="flex aspect-[4/3] items-center justify-center rounded-2xl border border-white/20 bg-white/5"
                          >
                            {src ? (
                              <img src={src} alt="Предпросмотр" className="h-full w-full rounded-2xl object-cover" />
                            ) : (
                              <span className="text-[11px] text-white/45">Фото</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <Button
                          type="button"
                          className="h-11 rounded-full bg-gradient-to-r from-[#5FE0FF] via-[#7DF0FF] to-[#B5F5FF] px-6 text-[14px] font-semibold text-sky-900 shadow-[0_24px_60px_rgb(3_144_255_/_0.85)] hover:brightness-110 disabled:opacity-70"
                          onClick={sendReport}
                          disabled={sending}
                        >
                          {sending ? "Отправка…" : "Отправить отчёт"}
                        </Button>
                        <div className="flex-1">
                          <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/15">
                            <div
                              className="h-full rounded-full bg-gradient-to-r from-[#5FE0FF] via-[#7DF0FF] to-[#B5F5FF] transition-all"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                        </div>
                      </div>
                      {progress > 0 && (
                        <p className="text-[11px] text-white/70">Загрузка: {progress}%</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="history" className="mt-0">
                <Card className="border-white/20 bg-white/10 text-white shadow-[0_24px_60px_rgb(15_28_83_/_0.45)] backdrop-blur-[28px]">
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-2 text-[18px] font-semibold text-white">
                      <History className="h-4 w-4" /> История отчётов
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-5 text-[12px]">
                    <div className="grid gap-3 rounded-3xl border border-white/15 bg-white/5 p-4 backdrop-blur">
                      <div className="grid gap-3 sm:grid-cols-4">
                        <div className="sm:col-span-2 space-y-1.5">
                          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/60">
                            Объект
                          </p>
                          <Select value={project} onValueChange={setProject}>
                            <SelectTrigger className="h-9 rounded-2xl border border-white/20 bg-white/10 text-[12px] text-white/90">
                              <SelectValue placeholder="Объект" />
                            </SelectTrigger>
                            <SelectContent className="border border-white/15 bg-[#07132F]/95 text-white">
                              {projects.map((item) => (
                                <SelectItem key={item.id} value={item.id}>
                                  {item.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-1.5">
                          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/60">
                            С даты
                          </p>
                          <Input
                            type="date"
                            className="h-9 rounded-2xl border border-white/20 bg-white/10 text-[12px] text-white/90"
                          />
                        </div>
                        <div className="space-y-1.5">
                          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/60">
                            По дату
                          </p>
                          <Input
                            type="date"
                            className="h-9 rounded-2xl border border-white/20 bg-white/10 text-[12px] text-white/90"
                          />
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      {history
                        .filter((item) => item.project_id === project)
                        .map((item) => (
                          <div
                            key={item.id}
                            className="rounded-3xl border border-white/15 bg-white/5 p-3 backdrop-blur text-white/85"
                          >
                            <div className="flex items-center justify-between text-[12px]">
                              <span>{formatRu(item.date)}</span>
                              <span className="text-white/75">
                                {workTypes.find((row) => row.id === item.work_type_id)?.name}
                              </span>
                            </div>
                            <p className="mt-1 text-[12px] text-white/85">{toOneLine(item.description)}</p>
                            <div className="mt-2 flex flex-wrap gap-2">
                              {item.photos.map((src, index) => (
                                <img
                                  key={index}
                                  src={src}
                                  alt="Фото отчёта"
                                  className="h-16 w-24 rounded-xl border border-white/35 object-cover"
                                />
                              ))}
                            </div>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="admin" className="mt-0">
                <Card className="border-white/20 bg-white/10 text-white shadow-[0_24px_60px_rgb(15_28_83_/_0.45)] backdrop-blur-[28px]">
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-2 text-[18px] font-semibold text-white">
                      <ShieldCheck className="h-4 w-4" /> Назначение доступа
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-5 text-[12px]">
                    <div className="grid gap-3 rounded-3xl border border-white/15 bg-white/5 p-4 backdrop-blur">
                      <div className="grid gap-3 sm:grid-cols-3">
                        <div className="sm:col-span-1 space-y-1.5">
                          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/60">
                            Найти подрядчика
                          </p>
                          <Input
                            placeholder="Поиск по названию / Telegram"
                            className="h-9 rounded-2xl border border-white/20 bg-white/10 text-[12px] text-white/90 placeholder:text-white/50"
                          />
                        </div>
                        <div className="space-y-1.5">
                          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/60">
                            Объект
                          </p>
                          <Select value={project} onValueChange={setProject}>
                            <SelectTrigger className="h-9 rounded-2xl border border-white/20 bg-white/10 text-[12px] text-white/90">
                              <SelectValue placeholder="Выберите объект" />
                            </SelectTrigger>
                            <SelectContent className="border border-white/15 bg-[#07132F]/95 text-white">
                              {projects.map((item) => (
                                <SelectItem key={item.id} value={item.id}>
                                  {item.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-1.5">
                          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-white/60">
                            Роль
                          </p>
                          <Select defaultValue="reporter">
                            <SelectTrigger className="h-9 rounded-2xl border border-white/20 bg-white/10 text-[12px] text-white/90">
                              <SelectValue placeholder="Роль" />
                            </SelectTrigger>
                            <SelectContent className="border border-white/15 bg-[#07132F]/95 text-white">
                              <SelectItem value="reporter">Может отправлять отчёты</SelectItem>
                              <SelectItem value="viewer">Только просмотр</SelectItem>
                              <SelectItem value="manager">Менеджер</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-white/65">
                        Текущие назначения
                      </p>
                      <div className="space-y-2">
                        {accessList.map((row, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between rounded-2xl border border-white/15 bg-white/5 px-3 py-3 backdrop-blur"
                          >
                            <div>
                              <div className="text-[13px] font-medium text-white/90">{row.user.name}</div>
                              <div className="text-[11px] text-white/65">
                                Проекты: {row.projects.map((pid) => projects.find((item) => item.id === pid)?.name).join(", ")}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[11px] text-white/70">Роль: {row.role}</span>
                              <Button
                                variant="secondary"
                                size="sm"
                                className="h-8 rounded-full border-none bg-white/85 px-3 text-[11px] font-semibold text-sky-800 shadow-[0_12px_32px_rgb(3_144_255_/_0.55)] hover:brightness-110"
                              >
                                Изменить
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  );
}

function formatRu(iso: string) {
  const [year, month, day] = iso.split("-");
  return `${day}.${month}.${year}`;
}

function toOneLine(desc: string) {
  const source = String(desc || "");
  const vol = source.match(/Объём:\s*([^\n]+)/i)?.[1]?.trim();
  const mach = source.match(/Техника:\s*([^\n]+)/i)?.[1]?.trim();
  const ppl = source.match(/Люди:\s*([^\n]+)/i)?.[1]?.trim();
  const parts: string[] = [];
  if (vol) parts.push(`Объём: ${vol}`);
  if (mach) parts.push(`Техника: ${mach}`);
  if (ppl) parts.push(`Люди: ${ppl}`);
  return parts.length ? parts.join(" • ") : source.replace(/\s+/g, " ").trim();
}
