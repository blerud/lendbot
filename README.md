lendbot
=======
### Setup
Set up your environment:
```shell script
# Create virtualenv
pip install virtualenv
virtualenv venv

# Activate virtualenv
source venv/bin/activate # Unix
venv/Scripts/activate # Windows

# Install requirements
pip install -r requirements.txt

# Set up pre-commit hooks
pre-commit install
```
Get your app's client ID and secret from https://discordapp.com/developers/applications,
and create `credentials.py`:
```python
client_id = "000000000000000000"
token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Running locally
```shell script
# Activate virtualenv
source venv/bin/activate # Unix
venv/Scripts/activate # Windows

# Run launcher
python launcher.py
```

### Development
`lendbot` uses [black](https://black.readthedocs.io/en/stable/index.html) to lint files.
To make your builds pass:
* Make sure you ran `pre-commit install` in the root `lendbot` directory.
* You can configure your editor to run `black` automatically:
see [here](https://black.readthedocs.io/en/stable/editor_integration.html)

### Continuous deployment
GitHub Actions is configured to reboot a Google Cloud instance `instance-1`,
on zone `us-centra1-c` on project `lendbot` on a push to `master`.

Configure the default instance with the following `startup-script`:
```bash
#!/bin/bash
cd /home/lendbot/lendbot
sudo -S -u lendbot git pull
sudo -S -u lendbot ./launch
```
