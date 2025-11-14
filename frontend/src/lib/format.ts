export function formatRuDate(iso: string): string {
  const [year, month, day] = iso.split("-")
  if (!year || !month || !day) {
    return iso
  }
  return `${day}.${month}.${year}`
}

export function summarizeDescription(desc: string): string {
  const source = String(desc ?? "")
  const vol = source.match(/Объём:\s*([^\n]+)/i)?.[1]?.trim()
  const mach = source.match(/Техника:\s*([^\n]+)/i)?.[1]?.trim()
  const ppl = source.match(/Люди:\s*([^\n]+)/i)?.[1]?.trim()
  const parts: string[] = []
  if (vol) parts.push(`Объём: ${vol}`)
  if (mach) parts.push(`Техника: ${mach}`)
  if (ppl) parts.push(`Люди: ${ppl}`)
  return parts.length ? parts.join(" • ") : source.replace(/\s+/g, " ").trim()
}
