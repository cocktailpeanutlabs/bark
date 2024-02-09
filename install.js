module.exports = {
  "requires": [
    { "platform": "darwin", "type": "brew", "name": "mecab" },
    { "type": "conda", "name": "ffmpeg", "args": "-c conda-forge" }
  ],
  "run": [{
    "method": "shell.run",
    "params": {
      "venv": "env",
      "message": "pip install -r requirements.txt"
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
