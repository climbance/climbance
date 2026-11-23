import { type BankChip } from '@climb/core'

import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'

// one filter's chips on a content browser page: `web-app/pages/author/`
export function Chips(props: {
  label: string
  chips: BankChip[]
  counted: boolean
  onPress: (value: string | number) => void
}) {
  return (
    <div className="flex items-baseline gap-3">
      <span className="w-20 shrink-0 text-meta text-muted-foreground">{props.label}</span>
      {/* the filters are toggles, drawn as the problem listing's are */}
      <ToggleGroup
        type="single"
        variant="outline"
        size="sm"
        className="w-auto flex-wrap"
        value={String(props.chips.find((chip) => chip.on)?.value ?? '')}
      >
        {props.chips.map((chip) => (
          <ToggleGroupItem
            key={chip.value}
            value={String(chip.value)}
            onClick={() => props.onPress(chip.value)}
          >
            {chip.label}
            {props.counted && (
              <span className="inline-block min-w-[2ch] text-right text-muted-foreground tabular-nums">
                {chip.count}
              </span>
            )}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
    </div>
  )
}
