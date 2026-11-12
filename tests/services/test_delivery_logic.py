import pytest
from decimal import Decimal
from app.services.delivery.delivery_logic import split_line_value, return_type_for

def D(x):
    """Shorthand for building Decimals in tests."""
    return Decimal(str(x))

def test_split_line_value():
    result = split_line_value(D("100.00"), 3, 1)
    assert result == (D("66.67"), D("33.33"))
    
def test_verify_split_line_value():
    delivered, returned = split_line_value(D("100.00"), 3, 1)
    total = delivered + returned
    assert total == D("100.00")

@pytest.mark.parametrize(
     "amount, delivered_qty, returned_qty",
    [
        (D("100.00"), 3, 1),
        (D("100.00"), 1, 2),
        (D("50.55"), 2, 3), 
        (D("100.00"), 5, 0), # zero return
        (D("0.00"), 1, 1), # Zero amount
    ],
)
def test_sum_always_exact(amount, delivered_qty, returned_qty):
    delivered, returned = split_line_value(amount, delivered_qty, returned_qty)
    total = delivered + returned
    assert total == amount
    
def test_return_type_for():
    result = return_type_for(D("0"), D("100.00"))
    assert result is None 
    
def test_partial_return_type_for():
    result = return_type_for(D("20.00"), D("100.00"))
    assert result == "P" 
    
def test_full_return_type_for():
    result = return_type_for(D("100.00"), D("100.00"))
    assert result == "F" 
    
