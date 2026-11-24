import {
  AUTHOR_GROUPS,
  AUTHOR_PAGES,
  AUTHOR_TITLE,
  LOADING,
  authorPath,
  waitingCount,
} from '@climb/core'
import { Menu } from 'lucide-react'
import { Suspense, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import { NotFoundPage } from '@/pages/NotFoundPage'

// every author page inside the navigation's column: `web-app/pages/author/README.md`.
// The groups are fixed, so the column is drawn before any request answers
export function AuthorLayout() {
  const { pathname } = useLocation()
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  // read again on each return to the inbox, whose figures the count is taken from
  const [seen, setSeen] = useState(pathname)
  const [returns, setReturns] = useState(0)
  if (pathname !== seen) {
    setSeen(pathname)
    if (pathname === '/author') setReturns(returns + 1)
  }
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author', returns)
  if (me.data && !me.data.author) return <NotFoundPage />
  const waiting = waitingCount(area.data?.waiting)

  return (
    <div className="lg:grid lg:grid-cols-[11rem_minmax(0,1fr)] lg:gap-8">
      <nav aria-label={AUTHOR_TITLE} className="hidden lg:block">
        <div className="sticky top-4 space-y-4">
          {AUTHOR_GROUPS.map((group) => (
            <div key={group.pages.join()} className="space-y-0.5">
              {group.title && (
                <p className="px-2.5 pb-0.5 text-meta font-medium text-muted-foreground uppercase">
                  {group.title}
                </p>
              )}
              {group.pages.map((page) => (
                <NavLink
                  key={page}
                  to={authorPath(page)}
                  // the inbox is the area's home, so only `/author` itself marks it
                  end
                  className={({ isActive }) =>
                    cn(
                      'flex items-baseline rounded-lg px-2.5 py-1 transition-colors',
                      isActive
                        ? 'bg-secondary font-medium text-secondary-foreground'
                        : 'text-muted-foreground hover:bg-accent',
                    )
                  }
                >
                  <span className="flex-1">{AUTHOR_PAGES[page]}</span>
                  {/* a slot of fixed width: the count arriving moves nothing */}
                  {page === 'inbox' && (
                    <span className="w-6 text-right text-meta tabular-nums">{waiting}</span>
                  )}
                </NavLink>
              ))}
            </div>
          ))}
        </div>
      </nav>
      <div className="min-w-0 space-y-stack">
        <Folded waiting={waiting} />
        <Suspense fallback={<p className="text-meta text-muted-foreground">{LOADING}</p>}>
          <Outlet />
        </Suspense>
      </div>
    </div>
  )
}

// under 64rem the column folds into one menu, above the page's title
function Folded({ waiting }: { waiting: string }) {
  return (
    <div className="lg:hidden">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <Menu />
            {AUTHOR_TITLE}
            {waiting && <span className="tabular-nums">{waiting}</span>}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          {AUTHOR_GROUPS.map((group, i) => (
            <div key={group.pages.join()}>
              {i > 0 && <DropdownMenuSeparator />}
              {group.title && <DropdownMenuLabel>{group.title}</DropdownMenuLabel>}
              {group.pages.map((page) => (
                <DropdownMenuItem key={page} asChild>
                  <NavLink to={authorPath(page)} end>
                    {AUTHOR_PAGES[page]}
                    {page === 'inbox' && waiting && (
                      <span className="ml-auto tabular-nums">{waiting}</span>
                    )}
                  </NavLink>
                </DropdownMenuItem>
              ))}
            </div>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
