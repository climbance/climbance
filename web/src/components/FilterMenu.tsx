import { useState } from 'react'

import { type MenuOption, MENU_SEARCH } from '@climb/core'

import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'

// one filter of a content browser page, as a menu naming its value: `web-app/pages/author/`
export function FilterMenu(props: {
  label: string
  options: MenuOption[]
  counted: boolean
  search?: boolean
  onPick: (value: string | null) => void
}) {
  const [query, setQuery] = useState('')
  const shown = props.options.filter(
    (one) => one.value === null || one.label.toLowerCase().includes(query.trim().toLowerCase()),
  )
  return (
    <DropdownMenu onOpenChange={(open) => open || setQuery('')}>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          {props.label} ▾
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-auto min-w-48 max-h-96">
        {props.search && (
          <Input
            autoFocus
            placeholder={MENU_SEARCH}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            // the menu's typeahead would take each letter typed here
            onKeyDown={(event) => event.key === 'Escape' || event.stopPropagation()}
            className="mb-1"
          />
        )}
        {shown.map((one) => (
          <DropdownMenuItem
            key={one.value ?? ''}
            onSelect={() => props.onPick(one.value)}
            // an option leaving no row stays pickable, greyed
            className={`justify-between gap-4 ${one.on ? 'font-medium' : ''} ${
              props.counted && one.count === 0 ? 'text-muted-foreground' : ''
            }`}
          >
            <span>{one.label}</span>
            {props.counted && <span className="tabular-nums text-muted-foreground">{one.count}</span>}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
