module.exports = async (kernel) => {
  let cmd = "{{(platform === 'darwin' ? self.cmds.darwin : (['nvidia', 'amd'].includes(gpu) ? self.cmds[platform][gpu] : self.cmds[platform].cpu))}}"
  if (kernel.gpu === 'nvidia' && kernel.gpu_model && / 50.+/.test(kernel.gpu_model)) {
    cmd = "pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128"
  }
  if (kernel.platform === 'darwin') {
    if (kernel.arch === "arm64") {
      cmd = "pip install torch torchaudio torchvision"
    } else {
      cmd = "pip install torch==2.1.2 torchaudio==2.1.2"
    }
  }
  return {
    "cmds": {
      "win32": {
        "nvidia": "pip install torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121",
        "amd": "pip install torch-directml",
        "cpu": "pip install torch torchvision torchaudio"
      },
      "darwin": "pip install torch torchvision torchaudio",
      "linux": {
        "nvidia": "pip install torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121",
        "amd": "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7",
        "cpu": "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
      }
    },
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
          "pip install -r requirements.txt"
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
