import { AUTHOR_PAGES, inboxEntry } from '@climb/core'
import { NavLink } from 'react-router'

import type { AuthorArea } from '@/api/client'
import { cn } from '@/lib/utils'

// the author pages in the groups `/api/author` lists: `web-app/pages/author/README.md`
export function AuthorBar({ area }: { area: AuthorArea }) {
  return (
    <nav className="space-y-1">
      {area.groups.map((group) => (
        <div key={group.join()} className="flex flex-wrap gap-1">
          {group.map((page) => (
            <NavLink
              key={page}
              // the inbox is the area's home, so only `/author` itself marks it
              to={page === 'inbox' ? '/author' : `/author/${page}`}
              end
              className={({ isActive }) =>
                cn(
                  'rounded-lg px-2.5 py-1 text-meta whitespace-nowrap transition-colors',
                  isActive
                    ? 'bg-secondary text-secondary-foreground'
                    : 'text-muted-foreground hover:bg-accent',
                )
              }
            >
              {page === 'inbox' ? inboxEntry(area.waiting) : (AUTHOR_PAGES[page] ?? page)}
            </NavLink>
          ))}
        </div>
      ))}
    </nav>
  )
}
