import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { Date as DateComponent } from "./Date"

const style = `
.content-meta {
  margin-top: 0;
  color: var(--darkgray);
}

.content-meta > *:not(:last-child) {
  margin-right: 8px;
}

.content-meta > *:not(:last-child)::after {
  content: ",";
}
`

interface Options {
  showReadingTime?: boolean
}

const defaultOptions: Required<Options> = {
  showReadingTime: true,
}

function coerceDate(value: unknown): Date | undefined {
  if (!value) return undefined
  const date = value instanceof globalThis.Date ? value : new globalThis.Date(value as string)
  return Number.isNaN(date.getTime()) ? undefined : date
}

function frontmatterDate(
  frontmatter: QuartzComponentProps["fileData"]["frontmatter"] | undefined,
  keys: string[],
): Date | undefined {
  for (const key of keys) {
    const date = coerceDate(frontmatter?.[key])
    if (date) return date
  }

  return undefined
}

function noteDate(
  fileData: QuartzComponentProps["fileData"],
  type: "created" | "modified",
  frontmatterKeys: string[],
): Date | undefined {
  return (
    frontmatterDate(fileData.frontmatter, frontmatterKeys) ?? coerceDate(fileData.dates?.[type])
  )
}

function readingMinutes(text: string): number {
  const words = text.trim().split(/\s+/).filter(Boolean).length
  return Math.max(1, Math.ceil(words / 200))
}

export default ((opts?: Options) => {
  const options = { ...defaultOptions, ...opts }

  const Component: QuartzComponent = ({ cfg, fileData, displayClass }) => {
    const locale = cfg.locale ?? "en-US"
    const created = noteDate(fileData, "created", ["created", "date"])
    const modified = noteDate(fileData, "modified", ["modified", "last-modified", "date modified"])
    const topSegments = []

    if (created) {
      topSegments.push(<DateComponent date={created} locale={locale} />)
    }

    if (options.showReadingTime && fileData.text) {
      topSegments.push(<span>{readingMinutes(fileData.text)} min read</span>)
    }

    if (modified) {
      topSegments.push(
        <span>
          Modified <DateComponent date={modified} locale={locale} />
        </span>,
      )
    }

    return (
      <div>
        {topSegments.length > 0 && (
          <p class={[displayClass, "content-meta"].filter(Boolean).join(" ")}>{topSegments}</p>
        )}
      </div>
    )
  }

  Component.css = style
  return Component
}) satisfies QuartzComponentConstructor<Options>
