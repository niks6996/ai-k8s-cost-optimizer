import math, re
NAME=re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")
def validate_kubernetes_name(value, field_name="name"):
    if not isinstance(value,str) or not value or len(value)>253 or not NAME.fullmatch(value):
        raise ValueError(f"{field_name} is not a valid Kubernetes name")
    return value
def validate_finite_non_negative(value, field_name):
    try: number=float(value)
    except (TypeError,ValueError) as exc: raise ValueError(f"{field_name} must be numeric") from exc
    if not math.isfinite(number) or number<0: raise ValueError(f"{field_name} must be finite and non-negative")
    return number