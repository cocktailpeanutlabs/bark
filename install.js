module.exports = async (kernel) => {
  let cmd = "uv pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cpu"
  if (kernel.platform === 'darwin') {
    if (kernel.arch === "arm64") {
      cmd = "uv pip install torch torchaudio torchvision"
    } else {
      cmd = "uv pip install torch==2.1.2 torchaudio==2.1.2"
    }
  } else {
    if (kernel.gpu === 'nvidia') {
      if (kernel.gpu_model && / 50.+/.test(kernel.gpu_model)) {
        cmd = "uv pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128"
      } else {
        cmd = "uv pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 xformers --index-url https://download.pytorch.org/whl/cu121"
      }
    } else if (kernel.gpu === 'amd') {
      cmd = "uv pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/rocm6.0"
    } 
  }
  return {
    "requires": [
      { "platform": "darwin", "type": "brew", "name": "mecab" },
      { "type": "conda", "name": "ffmpeg", "args": "-c conda-forge" }
    ],
    "run": [{
      "method": "shell.run",
      "params": {
        "venv": "env",
        "message": [
          cmd,
          "uv pip install -r requirements.txt"
        ]
      }
    }, {
      "method": "fs.share",
      "params": {
        "venv": "env"
      }
    }, {
      "method": "notify",
      "params": {
        "html": "Click the 'start' tab to get started!"
      }
    }]
  }
}
