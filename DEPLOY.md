# Deploying to Alibaba Cloud

This deploys `fc_handler.py` as an Alibaba Cloud Function Compute function, backed by
ApsaraDB for Redis as the shared dictionary store. Everything below is written for
**you to run yourself** -- no credentials or deploy commands were run by the assistant
that wrote this file, since deployment provisions billable cloud resources.

## 1. Prerequisites

- An Alibaba Cloud account (you already have one, used for Qwen Cloud).
- An AccessKey ID/Secret. Create one at:
  console > top-right avatar > AccessKey Management > Create AccessKey
  (Keep these out of git. Don't paste them into any file in this repo.)
- Node.js (for the Serverless Devs CLI).

## 2. Install the Serverless Devs CLI

```
npm install -g @serverless-devs/s
s config add   # paste your AccessKey ID/Secret when prompted, name the profile "default"
```

## 3. Create an ApsaraDB for Redis instance

Console > ApsaraDB for Redis > Create Instance. Cheapest option (e.g. a small
Community Edition instance) is enough for this project -- the dictionary is a handful
of short JSON entries, not a real workload. After it's created:

- Note the connection address (host) and port from the instance's Basic Information page.
- Set a password if the instance requires one (Account Management tab).
- Under Whitelist Settings, allow Function Compute to reach it -- easiest is enabling
  VPC connectivity for the Redis instance and configuring the FC function's VPC config
  in `s.yaml` to match, OR (simpler for a hackathon demo) enable a public endpoint on
  the Redis instance with the whitelist opened, since the dictionary data itself is
  not sensitive. Your call on the security/convenience tradeoff.

## 4. Set deployment environment variables

`s.yaml` reads these from your shell environment at deploy time (not hardcoded in the
file, since it's committed to git):

```
export DASHSCOPE_API_KEY=<your Qwen Cloud key>
export REDIS_HOST=<your Redis instance host>
export REDIS_PORT=6379
export REDIS_PASSWORD=<your Redis password, or leave empty if none>
```

## 5. Deploy

From this directory:

```
s deploy
```

This packages the repo (agents/, controller.py, dictionary/, fc_handler.py, tasks/,
requirements.txt) and creates the `glossogenesis` service / `negotiate` function in
Function Compute, region `ap-southeast-1` (edit `s.yaml` if you want a different
region). It also wires up an HTTP trigger.

## 6. Test it

`s deploy` prints the HTTP trigger URL. Call it:

```
curl -X POST '<trigger-url>' \
  -H 'Content-Type: application/json' \
  -d '{"task_id": "task_01_vendor_onboarding", "budget": 40, "max_rounds": 16}'
```

Should return JSON with `converged`, `rounds_used`, `clarification_rounds`, and the
full `transcript`. If it errors, check `s logs` for the function's CloudWatch-equivalent
logs -- most likely cause is a Redis connectivity/whitelist issue (see step 3) or a
missing environment variable.

## 7. For the submission

The hackathon requires proof of deployment: a short screen recording showing the
function running (e.g. the curl call above returning a converged negotiation) plus a
link to this file / the `fc_handler.py` + `s.yaml` code.
