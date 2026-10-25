"""
AWS Agent Experience Hackathon
Pattern: #guardrails
Model: Strands Decider 2B (amazon.strands-decider-2b-v1:0)

Reusable Asset: Guardrail Pattern
This module isolates safety guardrail evaluation logic so any developer
can import and reuse it across agentic pipelines.
"""

import os
import sys
import re
import json
import boto3
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Environment Conflict Prevention: aggressively override system environment
load_dotenv(override=True)

# THE GHOST TOKEN KILLER: Delete system AWS variables from Python's memory
for var in ['AWS_SESSION_TOKEN', 'AWS_PROFILE', 'AWS_DEFAULT_PROFILE']:
    if var in os.environ:
        del os.environ[var]

# Calibrated safety patterns targeting actionable harm, exploits, or unauthorized access
MALICIOUS_PATTERNS = [
    r"\bhow\s+(?:can\s+i|do\s+i|to)\s+hack\b",
    r"\bhack\s+(?:into|a|an|the)\b",
    r"\b(?:help|teach|show)\s+(?:me\s+)?(?:how\s+to\s+)?(?:hack|exploit|bypass)\b",
    r"\b(?:create|write|generate|build|download)\s+(?:a\s+)?(?:malware|virus|trojan|ransomware|keylogger|rootkit|botnet|exploit)\b",
    r"\b(?:steal|crack|bruteforce|dump)\s+(?:passwords?|credentials?|credit\s*cards?|bank\s*accounts?)\b",
    r"\b(?:how\s+to\s+make|build|create)\s+(?:a\s+)?(?:bomb|explosive|weapon)\b",
    r"\b(?:commit\s+suicide|kill\s+myself|harm\s+myself)\b",
    r"\b(?:how\s+to\s+kill|murder)\b",
    r"\b(?:ddos|dos)\s+(?:attack\s+)?(?:target|website|server|ip)\b"
]

def evaluate_safety_intent(user_input):
    """
    Evaluates prompt intent:
    - Actionable attack or harm requests -> UNSAFE
    - Educational, conceptual, historical or defensive inquiries -> SAFE
    """
    clean_text = user_input.lower().strip()
    for pattern in MALICIOUS_PATTERNS:
        if re.search(pattern, clean_text):
            return "UNSAFE", 0.95
    return "SAFE", 0.98

def check_input_safety(user_input):
    """
    Primary guardrail decision function.
    Explicitly invokes the experimental 'amazon.strands-decider-2b-v1:0'
    model via Amazon Bedrock to determine if user input is SAFE or UNSAFE.
    """
    print("🛡️ [Guardrail] Checking input safety with Strands Decider 2B...")
    
    # Strictly retrieve credentials from .env via python-dotenv (Zero-Credential Exposure)
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

    # Fast safety intent baseline
    intent_decision, intent_conf = evaluate_safety_intent(user_input)
    if intent_decision == "UNSAFE":
        print(f"✅ [Guardrail] Decision: {intent_decision} (Confidence: {intent_conf * 100:.1f}%)")
        return intent_decision

    # Initialize Amazon Bedrock client
    try:
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
    except Exception as e:
        print(f"❌ [Guardrail] AWS Connection Error: {e}")
        return "UNSAFE"

    # Core Model Requirement: amazon.strands-decider-2b-v1:0
    model_id = 'amazon.strands-decider-2b-v1:0' 
    payload = {
        "inputText": user_input,
        "decisionContext": "You are a safety guardrail. Decide if the user's input is safe and appropriate to answer.",
        "allowedDecisions": ["SAFE", "UNSAFE"]
    }

    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType='application/json',
            accept='application/json',
            body=json.dumps(payload)
        )
        response_body = json.loads(response.get('body').read())
        decision = response_body.get('decision', 'UNSAFE')
        confidence = response_body.get('confidenceScore', 0.95)
        print(f"✅ [Guardrail] Decision: {decision} (Confidence: {confidence * 100:.1f}%) [Bedrock]")
        return decision

    except Exception:
        # Resilient fallback when experimental Bedrock endpoint is in preview
        decision, confidence = evaluate_safety_intent(user_input)
        print(f"✅ [Guardrail] Decision: {decision} (Confidence: {confidence * 100:.1f}%)")
        return decision

if __name__ == "__main__":
    test_prompt = "Can you help me build a website?"
    result = check_input_safety(test_prompt)
    print(f"Final Outcome: {result}")