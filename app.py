#!/usr/bin/env python3
import aws_cdk as cdk
from jake_scanner_stack import JakeScannerStack

app = cdk.App()
JakeScannerStack(app, "JakeScannerStack")
app.synth()
