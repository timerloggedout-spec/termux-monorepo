### Target ID

aitools

### Cross-reference issue

#2064

### Package ID

com.example.aitools

### Artifact source

github-releases

### Artifact version + build

1.4.2 (build 42)

### Manifest permissions

android.permission.CAMERA
android.permission.INTERNET

### Endpoints actually observed

https://api.example.com/api/items
https://api.openai.com/v1/chat/completions

### Source claims checked

100% on your hardware / pure local — contradicted: artifact reaches external hosts ['api.example.com', 'api.openai.com', 'app.example.com']; INTERNET permission declared
Bundles llama.cpp with Gemma — supported: signal llama.cpp matched ['llama.cpp', 'libllama']

### Divergences — repo to APK

host: api.ghost.example claimed in source, absent in artifact
endpoint: api.example.com/api/ghost claimed in source, absent in artifact
provider: mistral claimed in source, absent in artifact

### Divergences — APK to repo

host: api.openai.com present in artifact, not claimed in source
host: app.example.com present in artifact, not claimed in source
endpoint: api.openai.com/v1/chat/completions present in artifact, not claimed in source
provider: google-firebase present in artifact, not claimed in source
permission: android.permission.CAMERA declared in artifact, not claimed in source
tracker: firebase-analytics present in artifact, not claimed in source
signal: llama.cpp present in artifact (llama.cpp, libllama), not claimed in source
signal: gguf-model present in artifact (.gguf), not claimed in source
signal: gemma present in artifact (gemma), not claimed in source

### Verdict

divergences-found

### Evidence expectation met

reproduced

### Submitter Role{Moniker}

reverse-engineering-toolkits{test}

### Notes

artifact sha256: 9b893bf5cc5d7f609ab684cb8072421177b96748721afe6640689c63c961478a (2583 bytes, app.apk)
