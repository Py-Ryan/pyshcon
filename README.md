# pyshcon
Python module adding small functionality between hexadecimal, and text conversions.

# Usage
```python
from pysh import Pysh

instance: Pysh = Pysh()

hex_digest: str = instance.hexadecimal('hello there (:')
string: str = instance.string(hex_digest) 
```
