def test_imports():
    from src.utils import seeding, config, io
    seeding.set_global_seed(0)
    assert io.THESIS_ROOT.exists()
