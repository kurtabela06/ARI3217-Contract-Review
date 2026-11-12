# ARI3217-AI-Enterprise-Architectures-and-Transformation
Main repository for ARI3217 - AI Enterprise Architectures and Transformation

## Train and evaluate the model

Run from the project root:

```bash
source .venv/bin/activate
contract-train
```

The command fits the clause classifiers on training passages,
selects the knowledge-retrieval weight and fits calibration on
validation passages, then reports test macro AUPR.

It saves the serving bundle to models/model.joblib by default.
A successful run replaces the bundle at the configured path.

Measurements are saved beside it as model.joblib.metrics.json.
The elapsed time includes the configured pipeline, evaluation and
saving; dataset loading may use existing caches.

The command does not produce a lawyer review pack.

Shared settings are in config/config.yaml.
Supported local overrides are documented in env.example.
Never commit .env, dataset text or generated model artifacts.

A successful command exits with code 0.
A failed command logs its traceback and exits with code 1.

Run tests with:

```bash
python -m pytest tests/ -q
```
