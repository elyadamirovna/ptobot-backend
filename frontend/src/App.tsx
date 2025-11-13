import { useEffect, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

const API_URL = "https://ptobot-backend.onrender.com";

interface WorkType {
  id: number;
  name: string;
}

function App() {
  const [workTypes, setWorkTypes] = useState<WorkType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // поля формы
  const [workTypeId, setWorkTypeId] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [people, setPeople] = useState<string>("");
  const [volume, setVolume] = useState<string>("");
  const [machines, setMachines] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [sending, setSending] = useState(false);
  const [sendResult, setSendResult] = useState<string | null>(null);

  // 1. грузим виды работ
  useEffect(() => {
    async function loadWorkTypes() {
      try {
        const res = await fetch(`${API_URL}/work_types`);
        if (!res.ok) throw new Error("Ошибка загрузки /work_types");
        const data = await res.json();
        setWorkTypes(data);
        if (data.length) {
          setWorkTypeId(String(data[0].id));
        }
      } catch (e: any) {
        setError(e?.message || "Неизвестная ошибка");
      } finally {
        setLoading(false);
      }
    }

    loadWorkTypes();
  }, []);

  function onFileChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] || null;
    setFile(f);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSendResult(null);

    if (!workTypeId) {
      alert("Выберите вид работ");
      return;
    }
    if (!file) {
      alert("Выберите файл с фото");
      return;
    }

    try {
      setSending(true);

      const form = new FormData();
      // user_id пока захардкодим, потом подставим из Telegram WebApp
      form.append("user_id", "1");
      form.append("work_type_id", workTypeId);
      form.append("description", description);
      form.append("people", people);
      form.append("volume", volume);
      form.append("machines", machines);
      form.append("photo", file);

      const res = await fetch(`${API_URL}/reports`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Ошибка при отправке: ${res.status} ${txt}`);
      }

      const data = await res.json();
      setSendResult(`Отчёт отправлен! ID: ${data.id}`);
      // очистка формы
      setDescription("");
      setPeople("");
      setVolume("");
      setMachines("");
      setFile(null);
    } catch (e: any) {
      setSendResult(`Ошибка: ${e?.message || "неизвестная"}`);
    } finally {
      setSending(false);
    }
  }

  return (
    <div style={{ fontFamily: "sans-serif", padding: "16px", maxWidth: 600, margin: "0 auto" }}>
      <h1>Ежедневные отчёты (тестовая форма)</h1>
      <p>Бекенд: {API_URL}</p>

      {loading && <p>Загрузка видов работ...</p>}
      {error && <p style={{ color: "red" }}>Ошибка: {error}</p>}

      {!loading && !error && (
        <>
          <h2>Виды работ с сервера:</h2>
          <ul>
            {workTypes.map((w) => (
              <li key={w.id}>
                {w.id}. {w.name}
              </li>
            ))}
          </ul>

          <hr style={{ margin: "24px 0" }} />

          <h2>Отправка отчёта</h2>
          <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <label>
              Вид работ:
              <br />
              <select
                value={workTypeId}
                onChange={(e) => setWorkTypeId(e.target.value)}
                style={{ width: "100%", padding: "4px" }}
              >
                {workTypes.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Описание:
              <br />
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                style={{ width: "100%" }}
              />
            </label>

            <label>
              Люди (чел.):
              <br />
              <input
                type="text"
                value={people}
                onChange={(e) => setPeople(e.target.value)}
                style={{ width: "100%", padding: "4px" }}
              />
            </label>

            <label>
              Объём (м³):
              <br />
              <input
                type="text"
                value={volume}
                onChange={(e) => setVolume(e.target.value)}
                style={{ width: "100%", padding: "4px" }}
              />
            </label>

            <label>
              Техника (шт.):
              <br />
              <input
                type="text"
                value={machines}
                onChange={(e) => setMachines(e.target.value)}
                style={{ width: "100%", padding: "4px" }}
              />
            </label>

            <label>
              Фото:
              <br />
              <input type="file" accept="image/*" onChange={onFileChange} />
            </label>

            <button
              type="submit"
              disabled={sending}
              style={{
                marginTop: "8px",
                padding: "8px 12px",
                cursor: sending ? "wait" : "pointer",
              }}
            >
              {sending ? "Отправка..." : "Отправить отчёт"}
            </button>
          </form>

          {sendResult && (
            <p style={{ marginTop: "12px", fontWeight: "bold" }}>
              {sendResult}
            </p>
          )}
        </>
      )}
    </div>
  );
}

export default App;
