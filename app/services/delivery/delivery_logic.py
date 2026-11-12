from decimal import ROUND_HALF_UP, Decimal

ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def split_line_value(
    net_val: Decimal, quantity: int, return_quantity: int
) -> tuple[Decimal, Decimal]:
    """Split a line's value into (delivered, returned), penny-safe.

    The returned part is rounded; the delivered part takes the remainder,
    so delivered + returned always equals net_val exactly.
    """
    if quantity == 0:
        return ZERO, ZERO
    return_net_val = (net_val * return_quantity / quantity).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    return net_val - return_net_val, return_net_val


def return_type_for(return_total: Decimal, invoice_value: Decimal) -> str | None:
    """'F' for a full return, 'P' for partial, None when nothing came back."""
    if return_total == ZERO:
        return None
    if return_total >= invoice_value:
        return "F"
    return "P"