"""Each technique's judgement rates: `api/short-exercises.md`."""

from collections import defaultdict
from collections.abc import Iterable

from pydantic import BaseModel

from climb.schema import Card, Judgement, JudgementItem
from climb.techniques import with_ancestors


class JudgementRates(BaseModel):
    """Flaws found over the flawed items answered, and clean solutions called
    flawed over the clean ones answered. One rate alone hides a user who calls
    everything flawed."""

    flaws_found: int = 0
    flawed: int = 0
    false_alarms: int = 0
    clean: int = 0


def judgement_rates(
    judgements: Iterable[Judgement], items: Iterable[JudgementItem], cards: Iterable[Card]
) -> dict[str, JudgementRates]:
    """Every answer counts, toward its item's card's technique and each code
    that technique is a kind of."""
    technique = {template.id: card.technique for card in cards for template in card.templates}
    by_id = {item.id: item for item in items}
    rates: dict[str, JudgementRates] = defaultdict(JudgementRates)
    for answer in judgements:
        item = by_id.get(answer.item_id)
        if item is None or item.template_id not in technique:
            continue
        for code in with_ancestors([technique[item.template_id]]):
            held = rates[code]
            if item.clean:
                held.clean += 1
                held.false_alarms += not answer.called_clean
            else:
                held.flawed += 1
                held.flaws_found += not answer.called_clean
    return dict(rates)
