lendbot
=======

## Setup
1. Install virtualenv if you don't have it: `pip3 install virtualenv`

2. Initialize virtualenv in the repo: `virtualenv venv`

3. Activate virtualenv: `source venv/bin/activate` on Unix or `venv/Scripts/activate` on Windows

4. Install dependencies: `pip3 install -r requirements.txt`

5. Create `credentials.py` and create fields `client_id` and `token`.

*Deactivate virtualenv with `deactivate` once you're done.*

## Running
1. Activate virtualenv: `source venv/bin/activate` on Unix or `venv/Scripts/activate` on Windows

2. Run the launcher: `./launch`

## Continuous deployment
GitHub Actions is configured to reboot a Google Cloud instance `instance-1`,
on zone `us-centra1-c` on project `lendbot` on a push to `master`.

The default instance is configured with the following `startup-script`:
```bash
#!/bin/bash
cd /home/lendbot/lendbot
sudo -S -u lendbot git pull
sudo -S -u lendbot ./launch
```