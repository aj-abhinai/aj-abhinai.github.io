import { formatDate } from "./Date"
import { QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"

export default (() => {
    function CreatedDate({ cfg, fileData, displayClass }: QuartzComponentProps) {
        const createdDate = fileData.dates?.created

        if (!createdDate) {
            return null
        }

        return (
            <p class={classNames(displayClass, "created-date")}>
                <span class="created-label">Created: </span>
                <time datetime={createdDate.toISOString()}>{formatDate(createdDate, cfg.locale)}</time>
            </p>
        )
    }

    CreatedDate.css = `
.created-date {
  margin-top: 2rem;
  padding-top: 0;
  color: var(--gray);
  font-size: 0.9rem;
  font-style: italic;
}

.created-label {
  font-weight: 500;
}
`

    return CreatedDate
}) satisfies QuartzComponentConstructor

