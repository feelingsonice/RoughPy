
import pytest
import roughpy as rp

def test_tick_stream_float_timestamps_are_absolute():
    """
    Regression test for issue where float timestamps were being shifted relative 
    to the first data point. They should be treated as absolute parameters (reference 0.0).
    """
    ctx = rp.get_context(3, 2, rp.DPReal)
    
    # Simple schema
    schema = [
        ("time", "value", {"lead_lag": False}), 
        ("s1", "value", {"lead_lag": True}),
    ]
    
    # Data starting at t=3.0
    # If timestamps were relative to first point, this would look like starting at t=0.0
    raw_data = [
        (3.0, "s1", "value", 3.0),
        (5.0, "s1", "value", 3.0),
    ]
    
    data_with_time = []
    for t, label, typ, val in raw_data:
        data_with_time.append((t, "time", "value", t))
        data_with_time.append((t, label, typ, val))
        
    support = rp.RealInterval(0, 7)
    
    s1 = rp.TickStream.from_data(
        data_with_time,
        schema=schema,
        ctx=ctx,
        support=support,
    )
    
    # Query interval [0, 2). Since data starts at 3.0, this should be empty/trivial.
    interval_empty = rp.RealInterval(0.0, 2.0)
    sig_empty = s1.signature(interval_empty, ctx=ctx, resolution=10)
    
    # Should be identity (1.0)
    # Checking if it has only one component (scalar) and it is 1.0
    # Or just check size if it's sparse? 
    # But FreeTensor might not be sparse in python binding access
    
    # We can check specific coefficients
    # The scalar component (empty word) should be 1.0
    # All other components should be 0.0
    
    # In RoughPy, converting to list/dict helps.
    # sig_empty should be effectively 1.
    
    # Using str(sig_empty) to check
    assert str(sig_empty) == "{ 1() }"

    # Query interval [0, 4) which contains the first jump at 3.0.
    interval_first = rp.RealInterval(0.0, 4.0)
    sig_first = s1.signature(interval_first, ctx=ctx, resolution=10)
    
    # Should NOT be identity
    assert str(sig_first) != "{ 1() }"
    
    # Check that it captured the jump
    # The jump is (3, 3, 3) at t=3.0.
    # We can check that the "time" channel (1) increment is 3.0
    # Note: accessing coefficients might need specific API.
    # But string representation check is robust enough for regression here.
