### Machine Learning
From Root to Pandas/Numpy
```
import uproot
file = uproot.open("example.root")
tree = file["events"]
df = tree.arrays(["var1","var2"], library="pd")               # Pandas DataFrame
np_dict = tree.arrays(["var1","var2"], library="np")          # Dictionary of Numpy arrays 
```
