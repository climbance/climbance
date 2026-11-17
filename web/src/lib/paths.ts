import { BACK_BOARD, type ProblemFrom } from '@climb/core'

// a short exercise's way back: the card it was opened from with `?card=`, else
// the board, where both exercises are offered
export function exerciseBack(card: string | null, cardTitle: string | undefined) {
  return card
    ? { to: `/cards/${encodeURIComponent(card)}`, label: cardTitle ?? card }
    : { to: '/', label: BACK_BOARD }
}

// the page a problem was opened from, as the web addresses it
export function fromPath(from: ProblemFrom): string {
  switch (from.kind) {
    case 'card':
      return `/cards/${encodeURIComponent(from.slug)}`
    case 'listing':
      return '/problems'
    case 'technique':
      return `/techniques/${encodeURIComponent(from.technique)}`
    case 'board':
      return '/'
  }
}
