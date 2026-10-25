# AWS Hackathon: Strands Decider 2B Guardrail Agent

This project was built for the AWS Agent Experience Hackathon. It demonstrates how to use the experimental **Strands Decider 2B** model as a security guardrail before passing prompts to Amazon Bedrock (Titan Text Express).

## The Reusable Asset: #guardrails
The file `guardrail_pattern.py` is a standalone, reusable asset. Developers can drop this file into any Python project to instantly add a Strands Decider 2B safety check. It evaluates user input and returns a binary `SAFE` or `UNSAFE` decision based on the appropriateness of the prompt.

## How to Run Locally
1. Clone this repository.
2. Install dependencies: `pip install boto3 python-dotenv`
3. Create a `.env` file in the root directory with your AWS credentials:
   - `AWS_ACCESS_KEY_ID=your_key`
   - `AWS_SECRET_ACCESS_KEY=your_secret`
   - `AWS_DEFAULT_REGION=us-east-1`
4. Run the agent: `python main_agent.py`

## Tech Stack
* **Python 3**
* **Amazon Bedrock (Strands Decider 2B)**: For binary decision routing.
* **Amazon Bedrock (Titan Text Express v1)**: For generative AI responses.
