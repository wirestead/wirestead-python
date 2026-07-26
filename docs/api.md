# API

The Python package exposes the pybind11 API migrated from the Wirestead C++ core
repository.

```python
import wirestead

client = wirestead.TcpClient("127.0.0.1", 9000)
server = wirestead.TcpServer(9000)
```

The compiled extension is installed as `wirestead._core`.
