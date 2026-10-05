import os
import glob
import pickle

print("Diagnosing pickle files in:", os.getcwd())
files = sorted(glob.glob("*.pkl") + glob.glob("*.pickle"))
if not files:
    print("No .pkl/.pickle files found.")

for f in files:
    print("\nFile:", f)
    try:
        size = os.path.getsize(f)
        print("Size:", size, "bytes")
        with open(f, "rb") as fh:
            head = fh.read(32)
        print("First 32 bytes:", head)
    except Exception as e:
        print("Failed to read file:", e)
        continue

    try:
        with open(f, "rb") as fh:
            obj = pickle.load(fh)
        print("Unpickled OK. Type:", type(obj))
    except Exception as e:
        print("Unpickle failed:", repr(e))
        # Try to load via joblib if it's a sklearn dump
        try:
            import joblib
            obj = joblib.load(f)
            print("Loaded with joblib. Type:", type(obj))
        except Exception as e2:
            print("joblib load failed:", repr(e2))

print("\nDiagnosis complete.")
