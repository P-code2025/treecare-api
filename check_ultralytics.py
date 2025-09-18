try:
    import ultralytics
    print("✅ ultralytics installed:", ultralytics.__version__)
except ImportError as e:
    print("❌ ultralytics not installed:", e)