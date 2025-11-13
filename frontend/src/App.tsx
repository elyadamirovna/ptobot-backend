import { useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

const API_URL = "https://ptobot-backend.onrender.com";

interface WorkType {
  id: string;
  name: string;
}

interface HistoryItem {
  id: number;
  project_id: string;
  date: string;
  work_type_id: string;
  description: string;
  photos: string[];
}

interface AccessEntry {
  user: { id: number; name: string };
  projects: string[];
  role: string;
}

const projects = [
  { id: "1", name: "ЖК «Северный»", address: "ул. Парковая, 12" },
  { id: "2", name: "ЖК «Академический»", address: "пр-т Науки, 5" },
];

const accessList: AccessEntry[] = [
  { user: { id: 8, name: "ИП «СтройСервис»" }, projects: ["1"], role: "reporter" },
  { user: { id: 9, name: "ООО «МонтажГрупп»" }, projects: ["1", "2"], role: "reporter" },
];

function App() {
  const [logoUrl, setLogoUrl] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"report" | "history" | "admin">("report");

  const [project, setProject] = useState<string>("1");
  const [workType, setWorkType] = useState<string>("2");
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

  // читаем ?logo=... из URL (как в твоём исходном коде)
  useEffect(() => {
    try {
      const qs = new URLSearchParams(window.location.search);
      const fromQuery = qs.get("logo");
      const fallback = "";
      setLogoUrl(fromQuery || fallback);
    } catch {
      setLogoUrl("");
    }
  }, []);

  // грузим work_types с бекенда
  useEffect(() => {
    async function loadWorkTypes() {
      try {
        const res = await fetch(`${API_URL}/work_types`);
        if (!res.ok) return;
        const rows = await res.json();
        if (Array.isArray(rows) && rows.length) {
          const mapped = rows.map((w: any) => ({
            id: String(w.id),
            name: w.name,
          }));
          setWorkTypes(mapped);
          if (!workType) setWorkType(String(rows[0].id));
        }
      } catch {
        // тихо игнорируем ошибку
      }
    }

    loadWorkTypes();
  }, [workType]);

  // демо-история
  const history: HistoryItem[] = useMemo(
    () => [
      {
        id: 101,
        project_id: "1",
        date: "2025-11-11",
        work_type_id: "2",
        description: `Бетонирование ростверка\nОбъём: 12,5 м³\nТехника: 2\nЛюди: 7`,
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
        description: `Разработка котлована\nОбъём: 80 м³\nТехника: 3\nЛюди: 5`,
        photos: ["https://picsum.photos/seed/c/300/200"],
      },
    ],
    []
  );

  // загрузка файлов
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [sending, setSending] = useState(false);
  const [progress, setProgress] = useState(0);
  const [sendMessage, setSendMessage] = useState<string | null>(null);

  const onPickFiles = () => {
    fileInputRef.current?.click();
  };

  const onFilesSelected = (e: ChangeEvent<HTMLInputElement>) => {
    const fl = Array.from(e.target.files || []);
    setFiles(fl);

    if (!fl.length) {
      setPreviews([]);
      return;
    }

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

  async function sendReport(e?: FormEvent) {
    if (e) e.preventDefault();
    setSendMessage(null);

    if (!workType) {
      alert("Выберите вид работ");
      return;
    }
    if (!files.length) {
      alert("Пожалуйста, выберите фото!");
      return;
    }

    const descParts: string[] = [comment];
    if (volume) descParts.push(`Объём: ${volume}`);
    if (machines) descParts.push(`Техника: ${machines}`);
    if (people) descParts.push(`Люди: ${people}`);
    const description = descParts.filter(Boolean).join("\n");

    const form = new FormData();
    // TODO: сюда потом подставим реальный user_id из Telegram WebApp
    form.append("user_id", "1");
    form.append("work_type_id", String(workType));
    form.append("description", description);
    form.append("people", people);
    form.append("volume", volume);
    form.append("machines", machines);
    form.append("photo", files[0]);

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
      setSendMessage(`Отчёт успешно отправлен! ID: ${data.id}`);
      // сброс формы
      setVolume("");
      setMachines("");
      setPeople("");
      setComment("");
      setFiles([]);
      setPreviews([]);
    } catch (err: any) {
      alert(err?.message || "Ошибка при отправке отчёта");
      setSendMessage("Не удалось отправить отчёт");
    } finally {
      setSending(false);
      setTimeout(() => setProgress(0), 600);
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#F8FAFC", color: "#0F172A" }}>
      {/* Шапка */}
      <header
        style={{
          padding: "8px 0",
          borderBottom: "1px solid #E5E7EB",
          background: "#FFFFFF",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div
          style={{
            maxWidth: "960px",
            margin: "0 auto",
            display: "flex",
            alignItems: "center",
            gap: "12px",
            padding: "0 12px",
          }}
        >
          {logoUrl ? (
            <img
              src={logoUrl}
              alt="Логотип"
              style={{ height: "40px", width: "auto", objectFit: "contain" }}
            />
          ) : (
            <div style={{ fontWeight: 800, fontSize: "18px" }}>Отчёты</div>
          )}
        </div>
      </header>

      <main style={{ maxWidth: "960px", margin: "0 auto", padding: "16px 12px 80px" }}>
        {/* Вкладки */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
            background: "#E5E7EB",
            borderRadius: "999px",
            overflow: "hidden",
          }}
        >
          <TabButton
            active={activeTab === "report"}
            onClick={() => setActiveTab("report")}
          >
            Отчёт
          </TabButton>
          <TabButton
            active={activeTab === "history"}
            onClick={() => setActiveTab("history")}
          >
            История
          </TabButton>
          <TabButton
            active={activeTab === "admin"}
            onClick={() => setActiveTab("admin")}
          >
            Доступ
          </TabButton>
        </div>

        {/* Содержимое вкладок */}
        <div style={{ marginTop: "16px" }}>
          {activeTab === "report" && (
            <section
              style={{
                background: "#FFFFFF",
                borderRadius: "16px",
                border: "1px solid #E5E7EB",
                boxShadow: "0 1px 2px rgba(15,23,42,0.05)",
                padding: "16px",
              }}
            >
              <h2 style={{ marginBottom: "12px", color: "#335E8A" }}>Ежедневный отчёт</h2>

              <form onSubmit={sendReport}>
                {/* Объект + вид работ */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                    gap: "12px",
                  }}
                >
                  <div>
                    <label style={{ fontSize: "14px", fontWeight: 600 }}>
                      Объект<span style={{ color: "red" }}>*</span>
                    </label>
                    <select
                      value={project}
                      onChange={(e) => setProject(e.target.value)}
                      style={{
                        width: "100%",
                        marginTop: "4px",
                        padding: "6px 8px",
                        borderRadius: "8px",
                        border: "1px solid #D1D5DB",
                        background: "#FFFFFF",
                      }}
                    >
                      {projects.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ fontSize: "14px", fontWeight: 600 }}>
                      Вид работы<span style={{ color: "red" }}>*</span>
                    </label>
                    <select
                      value={workType}
                      onChange={(e) => setWorkType(e.target.value)}
                      style={{
                        width: "100%",
                        marginTop: "4px",
                        padding: "6px 8px",
                        borderRadius: "8px",
                        border: "1px solid #D1D5DB",
                        background: "#FFFFFF",
                      }}
                    >
                      {workTypes.map((w) => (
                        <option key={w.id} value={w.id}>
                          {w.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Дата / объем / техника */}
                <div
                  style={{
                    marginTop: "12px",
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                    gap: "12px",
                  }}
                >
                  <div>
                    <label style={{ fontSize: "14px", fontWeight: 600 }}>Дата</label>
                    <input
                      type="date"
                      value={date}
                      onChange={(e) => setDate(e.target.value)}
                      style={{
                        width: "100%",
                        marginTop: "4px",
                        padding: "6px 8px",
                        borderRadius: "8px",
                        border: "1px solid #D1D5DB",
                        background: "#FFFFFF",
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: "14px", fontWeight: 600 }}>Объём (м³)</label>
                    <input
                      value={volume}
                      onChange={(e) => setVolume(e.target.value)}
                      placeholder="12,5"
                      style={{
                        width: "100%",
                        marginTop: "4px",
                        padding: "6px 8px",
                        borderRadius: "8px",
                        border: "1px solid #D1D5DB",
                        background: "#FFFFFF",
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: "14px", fontWeight: 600 }}>
                      Техника (шт.)
                    </label>
                    <input
                      value={machines}
                      onChange={(e) => setMachines(e.target.value)}
                      placeholder="3"
                      style={{
                        width: "100%",
                        marginTop: "4px",
                        padding: "6px 8px",
                        borderRadius: "8px",
                        border: "1px solid #D1D5DB",
                        background: "#FFFFFF",
                      }}
                    />
                  </div>
                </div>

                {/* Люди */}
                <div
                  style={{
                    marginTop: "12px",
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                    gap: "12px",
                  }}
                >
                  <div>
                    <label style={{ fontSize: "14px", fontWeight: 600 }}>
                      Люди (чел.)
                    </label>
                    <input
                      value={people}
                      onChange={(e) => setPeople(e.target.value)}
                      placeholder="5"
                      style={{
                        width: "100%",
                        marginTop: "4px",
                        padding: "6px 8px",
                        borderRadius: "8px",
                        border: "1px solid #D1D5DB",
                        background: "#FFFFFF",
                      }}
                    />
                  </div>
                </div>

                {/* Комментарий */}
                <div style={{ marginTop: "12px" }}>
                  <label style={{ fontSize: "14px", fontWeight: 600 }}>Комментарий</label>
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    rows={3}
                    style={{
                      width: "100%",
                      marginTop: "4px",
                      padding: "6px 8px",
                      borderRadius: "8px",
                      border: "1px solid #D1D5DB",
                      background: "#FFFFFF",
                      resize: "vertical",
                    }}
                  />
                </div>

                {/* Фото */}
                <div style={{ marginTop: "12px" }}>
                  <label style={{ fontSize: "14px", fontWeight: 600 }}>
                    Фото<span style={{ color: "red" }}>*</span>
                  </label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    style={{ display: "none" }}
                    onChange={onFilesSelected}
                  />

                  <div
                    style={{
                      marginTop: "4px",
                      borderRadius: "16px",
                      padding: "12px",
                      border: "1px dashed #D1D5DB",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: "12px",
                    }}
                  >
                    <div style={{ fontSize: "13px", color: "#6B7280" }}>
                      Выберите фото (JPG/PNG, до 10 МБ)
                    </div>
                    <button
                      type="button"
                      onClick={onPickFiles}
                      style={{
                        padding: "6px 12px",
                        borderRadius: "999px",
                        border: "none",
                        background: "#335E8A",
                        color: "white",
                        cursor: "pointer",
                      }}
                    >
                      Выбрать
                    </button>
                  </div>

                  <div
                    style={{
                      marginTop: "8px",
                      display: "grid",
                      gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                      gap: "8px",
                    }}
                  >
                    {(previews.length ? previews : [null, null, null]).slice(0, 3).map((src, i) => (
                      <div
                        key={i}
                        style={{
                          aspectRatio: "16/9",
                          borderRadius: "12px",
                          background: "#E5E7EB",
                          overflow: "hidden",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        {src ? (
                          <img
                            src={src}
                            alt="Превью"
                            style={{ width: "100%", height: "100%", objectFit: "cover" }}
                          />
                        ) : null}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Кнопка отправки */}
                <div
                  style={{
                    marginTop: "16px",
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    flexWrap: "wrap",
                  }}
                >
                  <button
                    type="submit"
                    disabled={sending}
                    style={{
                      padding: "8px 18px",
                      borderRadius: "999px",
                      border: "none",
                      background: "#335E8A",
                      color: "white",
                      cursor: sending ? "wait" : "pointer",
                    }}
                  >
                    {sending ? "Отправка..." : "Отправить отчёт"}
                  </button>
                  <div
                    style={{
                      flex: 1,
                      height: "8px",
                      borderRadius: "999px",
                      background: "#E5E7EB",
                      overflow: "hidden",
                      minWidth: "120px",
                    }}
                  >
                    <div
                      style={{
                        width: `${progress}%`,
                        height: "100%",
                        background: "#335E8A",
                        transition: "width 0.2s linear",
                      }}
                    />
                  </div>
                  {progress > 0 && (
                    <span style={{ fontSize: "12px", color: "#6B7280" }}>
                      Загрузка: {progress}%
                    </span>
                  )}
                </div>

                {sendMessage && (
                  <p style={{ marginTop: "8px", fontSize: "13px", fontWeight: 600 }}>
                    {sendMessage}
                  </p>
                )}
              </form>
            </section>
          )}

          {activeTab === "history" && (
            <section
              style={{
                background: "#FFFFFF",
                borderRadius: "16px",
                border: "1px solid #E5E7EB",
                boxShadow: "0 1px 2px rgba(15,23,42,0.05)",
                padding: "16px",
              }}
            >
              <h2 style={{ marginBottom: "12px", color: "#335E8A" }}>История отчётов</h2>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                  gap: "12px",
                  marginBottom: "16px",
                }}
              >
                <div>
                  <label style={{ fontSize: "14px", fontWeight: 600 }}>Объект</label>
                  <select
                    value={project}
                    onChange={(e) => setProject(e.target.value)}
                    style={{
                      width: "100%",
                      marginTop: "4px",
                      padding: "6px 8px",
                      borderRadius: "8px",
                      border: "1px solid #D1D5DB",
                      background: "#FFFFFF",
                    }}
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: "14px", fontWeight: 600 }}>С даты</label>
                  <input
                    type="date"
                    style={{
                      width: "100%",
                      marginTop: "4px",
                      padding: "6px 8px",
                      borderRadius: "8px",
                      border: "1px solid #D1D5DB",
                      background: "#FFFFFF",
                    }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: "14px", fontWeight: 600 }}>По дату</label>
                  <input
                    type="date"
                    style={{
                      width: "100%",
                      marginTop: "4px",
                      padding: "6px 8px",
                      borderRadius: "8px",
                      border: "1px solid #D1D5DB",
                      background: "#FFFFFF",
                    }}
                  />
                </div>
                <div style={{ display: "flex", alignItems: "flex-end" }}>
                  <button
                    type="button"
                    style={{
                      width: "100%",
                      padding: "8px 12px",
                      borderRadius: "999px",
                      border: "none",
                      background: "#335E8A",
                      color: "white",
                      cursor: "pointer",
                    }}
                  >
                    Показать
                  </button>
                </div>
              </div>

              <div style={{ display: "grid", gap: "8px" }}>
                {history
                  .filter((h) => h.project_id === project)
                  .map((item) => (
                    <div
                      key={item.id}
                      style={{
                        padding: "12px",
                        borderRadius: "12px",
                        border: "1px solid #E5E7EB",
                        background: "#F9FAFB",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          fontSize: "13px",
                          fontWeight: 600,
                          color: "#111827",
                        }}
                      >
                        <span>{formatRu(item.date)}</span>
                        <span>
                          {workTypes.find((w) => w.id === item.work_type_id)?.name ||
                            "—"}
                        </span>
                      </div>
                      <p
                        style={{
                          marginTop: "6px",
                          fontSize: "13px",
                          color: "#4B5563",
                        }}
                      >
                        {toOneLine(item.description)}
                      </p>
                      <div
                        style={{
                          display: "flex",
                          gap: "6px",
                          marginTop: "6px",
                          flexWrap: "wrap",
                        }}
                      >
                        {item.photos.map((src, i) => (
                          <img
                            key={i}
                            src={src}
                            alt="Фото отчёта"
                            style={{
                              height: "60px",
                              borderRadius: "8px",
                              border: "1px solid #E5E7EB",
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
              </div>
            </section>
          )}

          {activeTab === "admin" && (
            <section
              style={{
                background: "#FFFFFF",
                borderRadius: "16px",
                border: "1px solid #E5E7EB",
                boxShadow: "0 1px 2px rgba(15,23,42,0.05)",
                padding: "16px",
              }}
            >
              <h2 style={{ marginBottom: "12px", color: "#335E8A" }}>Назначение доступа</h2>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                  gap: "12px",
                  marginBottom: "16px",
                }}
              >
                <div>
                  <label style={{ fontSize: "14px", fontWeight: 600 }}>
                    Найти подрядчика
                  </label>
                  <input
                    placeholder="Поиск по названию/Telegram"
                    style={{
                      width: "100%",
                      marginTop: "4px",
                      padding: "6px 8px",
                      borderRadius: "8px",
                      border: "1px solid #D1D5DB",
                      background: "#FFFFFF",
                    }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: "14px", fontWeight: 600 }}>Объект</label>
                  <select
                    value={project}
                    onChange={(e) => setProject(e.target.value)}
                    style={{
                      width: "100%",
                      marginTop: "4px",
                      padding: "6px 8px",
                      borderRadius: "8px",
                      border: "1px solid #D1D5DB",
                      background: "#FFFFFF",
                    }}
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: "14px", fontWeight: 600 }}>Роль</label>
                  <select
                    defaultValue="reporter"
                    style={{
                      width: "100%",
                      marginTop: "4px",
                      padding: "6px 8px",
                      borderRadius: "8px",
                      border: "1px solid #D1D5DB",
                      background: "#FFFFFF",
                    }}
                  >
                    <option value="reporter">Может отправлять отчёты</option>
                    <option value="viewer">Только просмотр</option>
                    <option value="manager">Менеджер</option>
                  </select>
                </div>
              </div>

              <div
                style={{
                  padding: "12px",
                  borderRadius: "12px",
                  background: "#F9FAFB",
                  border: "1px solid #E5E7EB",
                }}
              >
                <div
                  style={{
                    fontSize: "14px",
                    fontWeight: 600,
                    marginBottom: "8px",
                    color: "#111827",
                  }}
                >
                  Текущие назначения
                </div>

                <div style={{ display: "grid", gap: "8px" }}>
                  {accessList.map((row, i) => (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "8px 10px",
                        borderRadius: "10px",
                        border: "1px solid #E5E7EB",
                        background: "#FFFFFF",
                        gap: "12px",
                        flexWrap: "wrap",
                      }}
                    >
                      <div>
                        <div
                          style={{
                            fontSize: "14px",
                            fontWeight: 600,
                            color: "#111827",
                          }}
                        >
                          {row.user.name}
                        </div>
                        <div
                          style={{
                            fontSize: "11px",
                            color: "#6B7280",
                          }}
                        >
                          Проекты:{" "}
                          {row.projects
                            .map((pid) => projects.find((p) => p.id === pid)?.name)
                            .filter(Boolean)
                            .join(", ")}
                        </div>
                      </div>
                      <div
                        style={{
                          fontSize: "11px",
                          color: "#6B7280",
                        }}
                      >
                        Роль: {row.role}
                      </div>
                      <button
                        type="button"
                        style={{
                          padding: "4px 10px",
                          borderRadius: "999px",
                          border: "none",
                          background: "#335E8A",
                          color: "white",
                          cursor: "pointer",
                          fontSize: "12px",
                        }}
                      >
                        Изменить
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

function TabButton(props: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={props.onClick}
      style={{
        padding: "8px 0",
        border: "none",
        cursor: "pointer",
        background: props.active ? "#FFFFFF" : "transparent",
        color: "#335E8A",
        fontWeight: 600,
      }}
    >
      {props.children}
    </button>
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

export default App;
