module.exports = {
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
        "{{(platform === 'darwin' ? self.cmds.darwin : (['nvidia', 'amd'].includes(gpu) ? self.cmds[platform][gpu] : self.cmds[platform].cpu))}}",
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
