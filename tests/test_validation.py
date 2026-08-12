import pytest
from app.validation import validate_kubernetes_name, validate_finite_non_negative
@pytest.mark.parametrize("v",["default","cost-optimizer","api-v2"])
def test_names(v): assert validate_kubernetes_name(v)==v
@pytest.mark.parametrize("v",["","UPPER","-bad","bad-","has_space"])
def test_bad_names(v):
    with pytest.raises(ValueError): validate_kubernetes_name(v)
@pytest.mark.parametrize("v",[0,1,0.5,"10"])
def test_numbers(v): assert validate_finite_non_negative(v,"value")>=0
@pytest.mark.parametrize("v",[-1,float("inf"),float("nan"),"abc",None])
def test_bad_numbers(v):
    with pytest.raises(ValueError): validate_finite_non_negative(v,"value")