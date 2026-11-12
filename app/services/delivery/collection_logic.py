# Python Imports
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

ZERO = Decimal("0.00")
ONE = Decimal("1")
CENT = Decimal("0.01")


def paisa(amount: Decimal) -> Decimal:
    """Return the fractional (sub-taka) part of an amount, e.g. 500.90 -> 0.90."""
    return amount - amount.quantize(ONE, rounding=ROUND_DOWN)


def split_round_down(dues: list[Decimal]) -> list[Decimal]:
    """Split a list of due amounts into round-down values.

    The total is rounded down to whole taka; the dropped paisa is shared out
    in proportion to each invoice's own paisa, and the last invoice absorbs
    the remainder so the round-downs always sum exactly to the total dropped.

    Returns a round-down value per input, in the same order.
    """
    total_due = sum(dues, ZERO)
    total_collect = total_due.quantize(ONE, rounding=ROUND_DOWN)
    total_round_down = total_due - total_collect
    total_paisa = sum((paisa(d) for d in dues), ZERO)

    round_downs: list[Decimal] = []
    accumulated = ZERO
    last_index = len(dues) - 1

    for index, due in enumerate(dues):
        if index == last_index:
            round_down = total_round_down - accumulated
        elif total_paisa > ZERO:
            round_down = (
                total_round_down * paisa(due) / total_paisa
            ).quantize(CENT, rounding=ROUND_HALF_UP)
        else:
            round_down = ZERO

        accumulated += round_down
        round_downs.append(round_down)

    return round_downs