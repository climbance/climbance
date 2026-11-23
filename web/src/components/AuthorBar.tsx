import { AUTHOR_PAGES } from '@climb/core'
import { NavLink } from 'react-router'

import { cn } from '@/lib/utils'

// moves between the author pages the engine serves, as `/api/author` lists them
export function AuthorBar({ pages }: { pages: string[] }) {
  return (
    <nav className="flex gap-1">
      {pages.map((page) => (
        <NavLink
          key={page}
          to={`/author/${page}`}
          className={({ isActive }) =>
            cn(
              'rounded-lg px-2.5 py-1 text-meta whitespace-nowrap transition-colors',
              isActive
                ? 'bg-secondary text-secondary-foreground'
                : 'text-muted-foreground hover:bg-accent',
            )
          }
        >
          {AUTHOR_PAGES[page] ?? page}
        </NavLink>
      ))}
    </nav>
  )
}
