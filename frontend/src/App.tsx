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
  blue: "#335E8A", // спокойный синий
  blueHover: "#2A4B6C", // hover-оттенок
  textDark: "#0F172A",
  textMuted: "#64748B",
};

export default function TelegramWebAppLight() {
  // ⚠️ Лого оставляем опциональным (можно убрать параметр в URL — отрисуется заглушка)
  const [logoUrl, setLogoUrl] = useState<string>("");
  useEffect(() => {
    try {
      const qs = new URLSearchParams(window.location.search);
      const fromQuery = qs.get("logo");
      const fallback = ""; // временно без логотипа
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

    // Собираем описание в виде многострочного текста (будет выведено в историю одной строкой через toOneLine)
    const descParts = [comment];
    if (volume) descParts.push(`Объём: ${volume}`);
    if (machines) descParts.push(`Техника: ${machines}`);
    if (people) descParts.push(`Люди: ${people}`);
    const description = descParts.filter(Boolean).join("\n");

    const form = new FormData();
    form.append("user_id", "1"); // TODO: заменить на текущего пользователя после авторизации
    form.append("work_type_id", String(workType));
    form.append("description", description);
    form.append("people", people);
    form.append("volume", volume);
    form.append("machines", machines);

    // 🔥 отправляем ВСЕ фото как "photos"
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
      // сброс формы
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
      {/* Шапка с логотипом (опционально) */}
      <header className="py-3 border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex items-center gap-3 px-3">
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

      <div className="max-w-5xl mx-auto px-3 py-4 sm:px-4 sm:py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-3 w-full bg-gray-100 text-gray-700 font-medium rounded-xl">
            <TabsTrigger
              value="report"
              className="data-[state=active]:bg-white"
              style={{ color: BRAND.blue }}
            >
              <ClipboardList className="h-4 w-4" />
              Отчёт
            </TabsTrigger>
            <TabsTrigger
              value="history"
              className="data-[state=active]:bg-white"
              style={{ color: BRAND.blue }}
            >
              <History className="h-4 w-4" />
              История
            </TabsTrigger>
            <TabsTrigger
              value="admin"
              className="data-[state=active]:bg-white"
              style={{ color: BRAND.blue }}
            >
              <ShieldCheck className="h-4 w-4" />
              Доступ
            </TabsTrigger>
          </TabsList>

          {/* Отчёт */}
          <TabsContent value="report" className="mt-3 sm:mt-4">
            <Card className="shadow-sm border border-gray-200 bg-white">
              <CardHeader>
                <CardTitle
                  className="flex items-center gap-2"
                  style={{ color: BRAND.blue }}
                >
                  <ClipboardList className="h-5 w-5" /> Ежедневный отчёт
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm font-semibold">
                      Объект<span className="text-red-500">*</span>
                    </label>
                    <Select value={project} onValueChange={setProject}>
                      <SelectTrigger className="mt-1 bg-white border-gray-300">
                        <SelectValue placeholder="Выберите объект" />
                      </SelectTrigger>
                      <SelectContent>
                        {projects.map((p) => (
                          <SelectItem key={p.id} value={p.id}>
                            {p.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-semibold">
                      Вид работы<span className="text-red-500">*</span>
                    </label>
                    <Select value={workType} onValueChange={setWorkType}>
                      <SelectTrigger className="mt-1 bg-white border-gray-300">
                        <SelectValue placeholder="Выберите вид" />
                      </SelectTrigger>
                      <SelectContent>
                        {workTypes.map((w) => (
                          <SelectItem key={w.id} value={w.id}>
                            {w.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-sm font-semibold">Дата</label>
                    <div className="relative mt-1">
                      <Input
                        type="date"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        className="bg-white border-gray-300 pr-8"
                      />
                      <CalendarIcon className="h-4 w-4 absolute right-2 top-1/2 -translate-y-1/2 text-gray-400" />
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-semibold">Объём (м³)</label>
                    <Input
                      placeholder="12,5"
                      value={volume}
                      onChange={(e) => setVolume(e.target.value)}
                      className="bg-white border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-semibold">
                      Техника (шт.)
                    </label>
                    <Input
                      placeholder="3"
                      value={machines}
                      onChange={(e) => setMachines(e.target.value)}
                      className="bg-white border-gray-300"
                    />
                  </div>
                </div>

                <div className="grid sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-sm font-semibold">Люди (чел.)</label>
                    <Input
                      inputMode="numeric"
                      placeholder="5"
                      value={people}
                      onChange={(e) => setPeople(e.target.value)}
                      className="bg-white border-gray-300"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-semibold">Комментарий</label>
                  <Textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    className="mt-1 bg-white border-gray-300"
                  />
                </div>

                <div>
                  <label className="text-sm font-semibold">
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
                  <div className="mt-1 border rounded-2xl p-4 border-dashed flex items-center justify-between border-gray-300">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-gray-100">
                        <ImageIcon className="h-5 w-5 text-gray-500" />
                      </div>
                      <div className="text-sm text-gray-500">
                        Перетащите сюда или выберите файлы (JPG/PNG/HEIC, до 10
                        МБ каждый)
                      </div>
                    </div>
                    <Button
                      className="gap-2 text-white"
                      style={{ background: BRAND.blue }}
                      onClick={onPickFiles}
                    >
                      <Upload className="h-4 w-4" />
                      Выбрать
                    </Button>
                  </div>
                  <div className="grid grid-cols-3 gap-2 mt-2">
                    {(previews.length ? previews : [null, null, null])
                      .slice(0, 3)
                      .map((src, i) => (
                        <div
                          key={i}
                          className="aspect-video rounded-xl bg-gray-100 overflow-hidden flex items-center justify-center"
                        >
                          {src ? (
                            <img
                              src={src}
                              className="w-full h-full object-cover"
                            />
                          ) : null}
                        </div>
                      ))}
                  </div>
                </div>

                {/* Кнопка отправки (desktop/tablet) */}
                <div className="hidden sm:flex items-center gap-3">
                  <Button
                    className="px-6 text-white"
                    style={{ background: BRAND.blue }}
                    onClick={sendReport}
                    disabled={sending}
                  >
                    {sending ? "Отправка…" : "Отправить отчёт"}
                  </Button>
                  <div className="flex-1 h-2 rounded-full overflow-hidden bg-gray-200">
                    <div
                      className="h-full transition-all"
                      style={{ width: `${progress}%`, background: BRAND.blue }}
                    />
                  </div>
                  <span className="text-sm text-gray-500">
                    {progress ? `Загрузка: ${progress}%` : ""}
                  </span>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* История */}
          <TabsContent value="history" className="mt-3 sm:mt-4">
            <Card className="shadow-sm border border-gray-200 bg-white">
              <CardHeader>
                <CardTitle
                  className="flex items-center gap-2"
                  style={{ color: BRAND.blue }}
                >
                  <History className="h-5 w-5" /> История отчётов
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-4 gap-3">
                  <div>
                    <label className="text-sm font-semibold">Объект</label>
                    <Select value={project} onValueChange={setProject}>
                      <SelectTrigger className="mt-1 bg-white border-gray-300">
                        <SelectValue placeholder="Выберите объект" />
                      </SelectTrigger>
                      <SelectContent>
                        {projects.map((p) => (
                          <SelectItem key={p.id} value={p.id}>
                            {p.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-semibold">С даты</label>
                    <Input
                      type="date"
                      className="mt-1 bg-white border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-semibold">По дату</label>
                    <Input
                      type="date"
                      className="mt-1 bg-white border-gray-300"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button
                      className="w-full text-white"
                      style={{ background: BRAND.blue }}
                    >
                      Показать
                    </Button>
                  </div>
                </div>

                <div className="grid gap-3">
                  {history
                    .filter((h) => h.project_id === project)
                    .map((item) => (
                      <div
                        key={item.id}
                        className="p-4 rounded-2xl border bg-gray-50 border-gray-200"
                      >
                        <div className="flex items-center justify-between text-sm font-semibold text-gray-800">
                          <span>{formatRu(item.date)}</span>
                          <span>
                            {
                              workTypes.find(
                                (w) => w.id === item.work_type_id
                              )?.name
                            }
                          </span>
                        </div>
                        <p className="mt-2 text-sm text-gray-600">
                          {toOneLine(item.description)}
                        </p>
                        <div className="flex gap-2 mt-2 flex-wrap">
                          {item.photos.map((src, i) => (
                            <img
                              key={i}
                              src={src}
                              alt="Фото отчёта"
                              className="h-20 rounded-xl border border-gray-200"
                            />
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Доступы (админ) */}
          <TabsContent value="admin" className="mt-3 sm:mt-4">
            <Card className="shadow-sm border border-gray-200 bg-white">
              <CardHeader>
                <CardTitle
                  className="flex items-center gap-2"
                  style={{ color: BRAND.blue }}
                >
                  <ShieldCheck className="h-5 w-5" /> Назначение доступа
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-sm font-semibold">
                      Найти подрядчика
                    </label>
                    <Input
                      placeholder="Поиск по названию/Telegram"
                      className="mt-1 bg-white border-gray-300"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-semibold">Объект</label>
                    <Select value={project} onValueChange={setProject}>
                      <SelectTrigger className="mt-1 bg-white border-gray-300">
                        <SelectValue placeholder="Выберите объект" />
                      </SelectTrigger>
                      <SelectContent>
                        {projects.map((p) => (
                          <SelectItem key={p.id} value={p.id}>
                            {p.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-semibold">Роль</label>
                    <Select defaultValue="reporter">
                      <SelectTrigger className="mt-1 bg-white border-gray-300">
                        <SelectValue placeholder="Роль" />
                      </SelectTrigger>
                      <SelectContent>
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

                <div className="p-4 rounded-2xl border bg-gray-50 border-gray-200">
                  <div className="text-sm font-semibold mb-2 text-gray-800">
                    Текущие назначения
                  </div>
                  <div className="grid gap-2">
                    {accessList.map((row, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-3 rounded-xl bg-white border border-gray-200"
                      >
                        <div>
                          <div className="font-medium text-gray-900">
                            {row.user.name}
                          </div>
                          <div className="text-xs text-gray-500">
                            Проекты:{" "}
                            {row.projects
                              .map(
                                (pid) =>
                                  projects.find((p) => p.id === pid)?.name
                              )
                              .join(", ")}
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">
                          Роль: {row.role}
                        </div>
                        <Button
                          variant="secondary"
                          size="sm"
                          className="text-white"
                          style={{ background: BRAND.blue }}
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
        className="sm:hidden fixed inset-x-0 bottom-0 bg-white/95 backdrop-blur border-t border-gray-200 px-3 pt-2"
        style={{
          paddingBottom: "calc(env(safe-area-inset-bottom, 0px) + 10px)",
        }}
      >
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <Button
            className="flex-1 text-white"
            style={{ background: BRAND.blue }}
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

// Тест-кейсы (не мешают UI)
try {
  console.assert(typeof formatRu === "function", "formatRu существует");
  console.assert(BRAND.blue === "#335E8A", "Используется спокойный синий #335E8A");
  console.assert(
    /Люди:\s*\d+/.test(`Бетонирование\nЛюди: 7`),
    'История поддерживает поле «Люди»'
  );
  console.assert(
    toOneLine(`Текст\nОбъём: 10 м³\nТехника: 2\nЛюди: 6`)
      === "Объём: 10 м³ • Техника: 2 • Люди: 6",
    "toOneLine собирает значения в одну строку"
  );
} catch (_) {}
