import { QuartzComponent, QuartzComponentConstructor } from "./types"
import { pathToRoot } from "../util/path"

const style = `
.page-title {
  font-size: 1.75rem;
  margin: 0;
  font-family: var(--titleFont);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-title .home-icon {
  display: inline-flex;
  align-items: center;
  color: var(--darkgray);
}

.page-title .home-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}
`

interface Options {
  homeUrl?: string
}

export default ((opts?: Options) => {
  const homeUrl = opts?.homeUrl ?? "https://abhinai.pages.dev/"

  const Component: QuartzComponent = ({ fileData, cfg, displayClass }) => {
    const title = cfg?.pageTitle ?? "Untitled"
    const baseDir = pathToRoot(fileData.slug!)

    return (
      <h2 class={[displayClass, "page-title"].filter(Boolean).join(" ")}>
        <a href={homeUrl} class="home-icon" aria-label="Home">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
        </a>
        <a href={baseDir}>{title}</a>
      </h2>
    )
  }

  Component.css = style
  return Component
}) satisfies QuartzComponentConstructor<Options>
