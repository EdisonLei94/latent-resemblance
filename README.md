# latent-resemblance

A reproduction of Latent Reflection by RootKid, with some small adjustments.
All credit for the idea and inspiration goes to RootKid.

A Llama3.2-3b model contained on a raspberrypi 4 using the Ollama python library. The generate output is served via a simple Flask app and displayed on a small monitor.
Two services are configured on the pi to run the app and display a Chromium webpage in kiosk mode on boot.

## Prerequisites
- Python 3.7+
- [Ollama](https://ollama.ai/) installed and running
- A language model pulled in Ollama (e.g., `llama2`, `mistral`, etc.)

## Installation

```bash
python -m venv venv
```

Activate your venv.

On Windows:
If using cmd:
```bash
.\venv\Scripts\activate
```
If using Windows PowerShell:
```bash
.\venv\Scripts\Activate.ps1
```

On Linux/macOS:
```bash
source venv/bin/activate
```

Your activate path should be preceded by `(venv)` if the virtualenv was activated properly.

Install dependencies.

```bash
python -m pip install -r requirements.txt
```

## Usage

1. **Build and run your Ollama model:**
```bash
ollama create llama_model -f Modelfile
```

2. **Set Environment Variables:**
- `LLAMA_MODEL`: Specify the Ollama model name (default: `llama_model`)
- Set to `TEST` to run without Ollama for testing purposes

3. **Running the Flask App:**
```bash
python app.py
```

Or with a specific model:
```bash
LLAMA_MODEL=your_model_name python app.py
```

For testing without Ollama:
```bash
LLAMA_MODEL=TEST python app.py
```

Visit `http://localhost:5000` in your browser to see the display.

## Raspberry Pi configuration
1. Move or copy the latentResemblance.service file to `/etc/systemd/system/latentResemblance.service`. You will need to replace the paths denoted by `{}` with the appropriate file paths.
2. Move or copy the kiosk.service file to `$HOME/.config/systemd/user/kiosk.service`. You will need to replace the `{path_to_kiosk.sh_script}` with the appropriate path.
3. Move or copy the autostart file to `$HOME/.config/lxsession/LXDE-pi/autostart`.
4. After these steps:
```bash
sudo systemctl daemon-reload
sudo systemctl enable latentResemblance
sudo systemctl start latentResemblance
sudo systemctl --user daemon-reload
sudo systemctl --user enable kiosk
sudo systemctl --user start kiosk
```
5. Restart the Raspberry Pi. The latentResemblance service should autostart, shortly followed by the kiosk service.
