# 🚀 How to Use Ziskare AI in Different Ways Across Your PC

**Ziskare AI** is a universal offline AI engine installed globally on your machine. You do not need to keep copies of this code in other folders; it is accessible everywhere across Windows.

Here are the **7 different ways** you can use Ziskare AI on your computer:

---

## 1. Direct Command Line (PowerShell / CMD)
Run single-shot queries directly from **any terminal in any folder**:

```powershell
ziskare-ai "What is 15 percent of 850?"
```
*Output: `127.5`*

```powershell
ziskare-ai "Give me a regex to match email addresses."
```

---

## 2. Interactive Shell Mode
Start an ongoing conversation session with conversational memory:

```powershell
ziskare-ai
```
- Type your questions normally.
- Context is remembered across prompts.
- Type `exit` or `quit` to close.

---

## 3. In ANY Python Project (Import Anywhere)
In **any Python script in any directory** (e.g. `D:\ArogyaPlus\script.py`, Desktop, etc.):

### Fast One-Liner:
```python
import ziskare_ai as zai

answer = zai.ask("Explain recursion in one sentence.")
print("Ziskare AI:", answer)
```

### Object Instance with Multi-Turn Chat:
```python
from ziskare_ai import ZiskareAI

ai = ZiskareAI()

# First turn
reply1, stats = ai.chat("The database server IP is 192.168.1.50.")
print("AI:", reply1)

# Second turn (recalls previous context)
reply2, stats = ai.chat("What was the database server IP?")
print("AI:", reply2)  # Output: 192.168.1.50.

# Benchmark speed
metrics = ai.ask("What is Docker?", return_metrics=True)
print(f"Speed: {metrics['speed']} tok/s in {metrics['time_taken']}s")
```

---

## 4. In Node.js / JavaScript (CLI Subprocess)
In your Node.js backends or Express apps:

```javascript
const { execSync } = require('child_process');

function askZiskareAI(prompt) {
  // Safely escapes double quotes and calls global command
  const cleanPrompt = prompt.replace(/"/g, '\\"');
  return execSync(`ziskare-ai "${cleanPrompt}"`).toString().trim();
}

const answer = askZiskareAI("What are microservices?");
console.log("Ziskare AI:", answer);
```

---

## 5. Local REST API Microservice (HTTP Server)
Start the local HTTP server:
```powershell
ziskare-ai --server 5005
```

Now **any language** can query it over HTTP (`POST http://127.0.0.1:5005/ask`):

### Browser / Frontend (`fetch`):
```javascript
const response = await fetch('http://127.0.0.1:5005/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: 'Explain cloud computing in one sentence.' })
});
const data = await response.json();
console.log("Answer:", data.answer);
console.log("Speed:", data.speed, "tokens/sec");
```

### cURL (Terminal):
```bash
curl -X POST http://127.0.0.1:5005/ask -H "Content-Type: application/json" -d "{\"prompt\":\"What is Kubernetes?\"}"
```

### Python (`requests`):
```python
import requests

res = requests.post("http://127.0.0.1:5005/ask", json={"prompt": "What is Python?"})
print(res.json()["answer"])
```

---

## 6. Windows Desktop Hotkey / Quick Icon
You can create a desktop shortcut that opens Ziskare AI instantly with a keyboard shortcut:

1. Right-click on your **Windows Desktop** $\rightarrow$ **New** $\rightarrow$ **Shortcut**.
2. For location, enter:
   ```cmd
   cmd.exe /k ziskare-ai
   ```
3. Name it: `Ziskare AI`.
4. Right-click the new shortcut $\rightarrow$ **Properties**:
   - In **Shortcut key**, press a key combination like `Ctrl + Alt + Z`.
   - Click **OK**.
5. Now, pressing `Ctrl + Alt + Z` anywhere in Windows instantly opens Ziskare AI!

---

## 7. In Daily PowerShell & Batch Automation Scripts
Use Ziskare AI to automatically process files, summarize logs, or extract data:

```powershell
# Read error log and ask Ziskare AI to explain it
$logSnippet = Get-Content -Tail 5 C:\logs\app.log | Out-String
$explanation = ziskare-ai "Explain this error in 1 sentence: $logSnippet"
Write-Host "Ziskare AI Analysis: $explanation" -ForegroundColor Green
```

---

## ⚡ Summary of Commands
| Action | How to Run |
| :--- | :--- |
| **Direct Answer** | `ziskare-ai "question"` |
| **Interactive Chat** | `ziskare-ai` |
| **REST Server** | `ziskare-ai --server 5005` |
| **Python Import** | `import ziskare_ai as zai` |
| **1-Click System Re-install** | Double click `D:\ziskare-ai\install.bat` |
