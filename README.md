# Austin's EE API: a CI/CD + Docker + Kubernetes learning project

A tiny web service (resistor color codes, Ohm's law, voltage dividers) whose real purpose
is the **pipeline around it**. Every file has comments explaining what it does and why.

```
 you edit code ──► git push ──► GitHub Actions ──► tests ──► Docker image ──► Kubernetes
                                (CI: check it)              (package it)     (run it)
```

## The pieces, in one line each

| Piece | What it is | File |
|---|---|---|
| Web service | FastAPI app, plain Python | `app/main.py`, `app/ee.py` |
| Tests | Prove the math is right; CI runs them on every push | `tests/test_ee.py` |
| Docker | Packs the app + Python + libraries into one image that runs anywhere | `Dockerfile` |
| CI | GitHub runs tests and builds the image automatically on push | `.github/workflows/ci.yml` |
| Kubernetes | Keeps copies of the container running, restarts crashes, rolls out updates | `k8s/` |

## Project layout

```
app/ee.py                 the EE math (no web stuff)
app/main.py               turns the math into HTTP endpoints
tests/test_ee.py          automated tests
requirements*.txt         Python libraries
Dockerfile                image recipe
k8s/deployment.yaml       "run 2 copies of this image"
k8s/service.yaml          "give them one address: localhost:8080"
.github/workflows/ci.yml  the pipeline
```

---

## Step 1: Run it plain (optional)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest                         # 8 tests should pass
uvicorn app.main:app --reload  # open http://localhost:8000/docs
```

Try: http://localhost:8000/resistor?bands=yellow,violet,red,gold → `4.7 kΩ`

## Step 2: Docker

Install **Docker Desktop** (docker.com) and start it.

```bash
docker build -t austin-pipeline:local .
docker run --rm -p 8000:8000 austin-pipeline:local
```

Same app, now running inside a container. `Ctrl+C` to stop.

## Step 3: GitHub + CI

1. Create an **empty** repo on github.com (no README), e.g. `austin-pipeline`.
2. In this folder:
   ```bash
   git init
   git add .
   git commit -m "First commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/austin-pipeline.git
   git push -u origin main
   ```
3. Open the repo's **Actions** tab and watch `test` then `build-and-push` run.
4. The built image appears under the repo's **Packages**.

Break a test on purpose (change `4700` to `4701` in `tests/test_ee.py`), push, and watch
the pipeline go red and refuse to build. That's CI doing its job.

## Step 4: Kubernetes (local, via Docker Desktop)

1. Docker Desktop → **Settings → Kubernetes → Enable Kubernetes** → Apply. Wait for the green light.
2. Deploy:
   ```bash
   docker build -t austin-pipeline:local .
   kubectl apply -f k8s/
   kubectl get pods            # two ee-api pods, STATUS Running
   ```
3. Open http://localhost:8080/docs

Things worth trying:

```bash
kubectl delete pod <one-of-the-pod-names>   # Kubernetes immediately starts a replacement
kubectl scale deployment ee-api --replicas=4
kubectl logs -l app=ee-api
kubectl describe deployment ee-api
```

Update after a code change:

```bash
docker build -t austin-pipeline:local .
kubectl rollout restart deployment ee-api
```

Clean up: `kubectl delete -f k8s/`

## Step 5: Close the loop (CD), not done yet

Right now a push **builds** the image automatically, but you still deploy by hand. The last step
is making a push **update what's running**. GitHub's servers can't reach a cluster on a laptop,
so the options are:

- **Self-hosted runner:** install GitHub's runner app on the Mac; the deploy job runs locally and calls `kubectl`. Free, simple, only works while the Mac is on.
- **Pull-based (Argo CD / Flux):** a tool inside the cluster watches GitHub and pulls new versions itself. This is how many companies do it.
- **Cloud cluster:** a real hosted Kubernetes; costs money or needs a free tier.

When it works, `curl localhost:8080/` will show a new `version` (the commit hash) after each push, with no manual steps.
