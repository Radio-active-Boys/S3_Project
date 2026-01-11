Base API URL (production):

```
https://s3-server.navrobotec.online
```

Local API URL (development):

```
http://127.0.0.1:5000
```

---

## ✅ 1. Upload File

### 🔹 Linux / macOS (bash)

```bash
curl -X POST https://s3-server.navrobotec.online/upload \
  -F "user_id=USER123" \
  -F "file=@ToDo.md"
```

### 🔹 Windows PowerShell

```powershell
curl.exe -X POST https://s3-server.navrobotec.online/upload `
  -F "user_id=USER123" `
  -F "file=@ToDo.md"
```

### ✅ Response

```json
{
  "message": "Uploaded",
  "key": "USER123/xxxxxxxx_ToDo.md",
  "fileUrl": "http://coolify.navrobotec.online:8333/uploads/USER123/xxxxxxxx_ToDo.md"
}
```

---

## ✅ 2. List User Files

### 🔹 Linux / macOS (bash)

```bash
curl "https://s3-server.navrobotec.online/files?user_id=USER123"
```

### 🔹 Windows PowerShell

```powershell
curl.exe "https://s3-server.navrobotec.online/files?user_id=USER123"
```

### ✅ Response

```json
{
  "count": 1,
  "files": [
    {
      "id": 1,
      "original_name": "ToDo.md",
      "public_url": "http://coolify.navrobotec.online:8333/uploads/USER123/xxxxxxxx_ToDo.md",
      "created_at": "2026-01-11 16:18:48"
    }
  ]
}
```

---

## ✅ 3. Download File (Presigned URL)

### 🔹 Linux / macOS (bash)

```bash
curl -X POST http://127.0.0.1:5000/download \
  -H "Content-Type: application/json" \
  -d '{"key":"USER123/xxxxxxxx_ToDo.md"}'
```

### 🔹 Windows PowerShell (CORRECT WAY)

```powershell
$body = @{
  key = "USER123/xxxxxxxx_ToDo.md"
} | ConvertTo-Json

curl.exe -X POST http://127.0.0.1:5000/download `
  -H "Content-Type: application/json" `
  -d $body
```

### ✅ Response

```json
{
  "downloadUrl": "http://coolify.navrobotec.online:8333/uploads/USER123/xxxxxxxx_ToDo.md?X-Amz-Algorithm=AWS4-HMAC-SHA256&..."
}
```

➡ You can open this URL in **any browser** until it expires.

---

## ✅ 4. Delete File

### 🔹 Linux / macOS (bash)

```bash
curl -X POST http://127.0.0.1:5000/delete \
  -H "Content-Type: application/json" \
  -d '{"user_id":"USER123","key":"USER123/xxxxxxxx_ToDo.md"}'
```

### 🔹 Windows PowerShell (CORRECT WAY)

```powershell
$body = @{
  user_id = "USER123"
  key     = "USER123/xxxxxxxx_ToDo.md"
} | ConvertTo-Json

curl.exe -X POST http://127.0.0.1:5000/delete `
  -H "Content-Type: application/json" `
  -d $body
```

### ✅ Response (success)

```json
{
  "message": "Deleted",
  "key": "USER123/xxxxxxxx_ToDo.md"
}
```

### ❌ Response (file not found)

```json
{
  "error": "File not found"
}
```
