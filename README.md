# Jake Scanner CDK Deployment

This project automates the detection and scanning of `requirements.txt` files uploaded to an S3 bucket using [Sonatype Jake](https://github.com/sonatype-nexus-community/jake).

## What It Deploys

- `env-scan-input` S3 bucket — upload your `requirements.txt` files here (e.g., `EnvA/requirements.txt`)
- `env-scan-results` S3 bucket — scan outputs go here (e.g., `EnvA/scan-results.txt`)
- Lambda function — triggers automatically on upload events
- EventBridge rule — listens for new object creation in input bucket
- CodeBuild project — performs Conda install, runs `jake ddt`, and saves results

## Deploy Instructions

```bash
# Clone or unzip this project
cd jake_scanner_cdk

# Set up a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Bootstrap and deploy CDK
cdk bootstrap
cdk deploy
```

## Example S3 Input/Output

**Input:**  
`s3://env-scan-input/EnvA/requirements.txt`

**Output:**  
`s3://env-scan-results/EnvA/scan-results.txt`  
`s3://env-scan-results/EnvA/requirements.txt`

## 🛠 Customization

- The CodeBuild project uses `buildspec.yml` — edit this file to change behavior (e.g., output format).
- The Lambda function is in `lambda/handler.py` — change how inputs are parsed or build started here.

## Test It

After deployment:
1. Upload a file like `EnvB/requirements.txt` to the `env-scan-input` bucket.
2. Wait ~1-2 minutes for the scan to complete.
3. Check the `env-scan-results/EnvB/` folder for results.

##  Requirements

- AWS CLI & credentials configured
- CDK installed (`npm install -g aws-cdk`)
- Python 3.8+

##  Cleanup

```bash
cdk destroy
```

---
