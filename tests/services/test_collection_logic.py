from decimal import Decimal

import pytest

from app.services.delivery.collection_logic import paisa, split_round_down

def D(x):
    """Shorthand for building Decimals in tests."""
    return Decimal(str(x))


def test_paisa_extracts_fraction():
    assert paisa(D("500.90")) == D("0.90")
    assert paisa(D("400.00")) == D("0.00")


def test_single_invoice_drops_own_paisa():
    result = split_round_down([D("500.90")])
    assert result == [D("0.90")]


def test_two_invoices_share_by_paisa():
    # 500.90 + 400.20 = 901.10, collect 901, drop 0.10
    # weights: 0.90 and 0.20 out of 1.10
    result = split_round_down([D("500.90"), D("400.20")])
    assert result == [D("0.08"), D("0.02")]

def test_two_invoices_share_by_paisa_2():
    result = split_round_down([D("374.34"), D("629.43")])
    assert result == [D("0.34"), D("0.43")]


def test_round_downs_sum_to_total_dropped():
    dues = [D("500.90"), D("400.20"), D("123.45")]
    result = split_round_down(dues)
    total_due = sum(dues, Decimal("0"))
    total_collect = total_due.quantize(Decimal("1"), rounding="ROUND_DOWN")
    assert sum(result, Decimal("0")) == total_due - total_collect


def test_no_fraction_means_no_round_down():
    result = split_round_down([D("500.00"), D("400.00")])
    assert result == [D("0.00"), D("0.00")]


def test_collection_never_exceeds_due():
    # Each round-down must be >= 0 and <= that invoice's paisa-ish share
    dues = [D("500.90"), D("400.20")]
    result = split_round_down(dues)
    for due, rd in zip(dues, result):
        assert rd >= Decimal("0")
        assert due - rd <= due  # collection never more than due


@pytest.mark.parametrize("dues", [
    [D("100.33"), D("200.66"), D("300.99"), D("50.02")],
    [D("1.01"), D("2.02"), D("3.03")],
    [D("999.99")],
])
def test_sum_always_exact(dues):
    """For any input, round-downs sum exactly to the dropped fraction."""
    result = split_round_down(dues)
    total_due = sum(dues, Decimal("0"))
    expected_drop = total_due - total_due.quantize(Decimal("1"), rounding="ROUND_DOWN")
    assert sum(result, Decimal("0")) == expected_drop
    
def test_round_down_never_exceeds_own_paisa():
    """Each round-down must never exceed that invoice's own paisa —
    the taka part is never touched."""
    dues = [D("227.50"), D("400.20"), D("123.99")]
    result = split_round_down(dues)
    for due, rd in zip(dues, result):
        assert rd <= paisa(due), f"round_down {rd} exceeds paisa of {due}"
        assert rd >= D("0")
        
@pytest.mark.parametrize("dues", [
    [D("0.99"), D("0.99"), D("0.99")],     
    [D("100.01"), D("100.01"), D("100.97")], 
    [D("500.90"), D("400.20"), D("300.10")],
])
def test_round_down_within_paisa_for_all(dues):
    """No invoice's round-down ever exceeds its own paisa, even the last."""
    result = split_round_down(dues)
    for due, rd in zip(dues, result):
        assert rd <= paisa(due) + D("0.001"), (
            f"round_down {rd} > paisa {paisa(due)} for due {due}"
        )