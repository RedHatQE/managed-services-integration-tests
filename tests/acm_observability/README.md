# ACM Observability tests

To run ACM Observability tests make sure that the `KUBEADMIN_TOKEN` environment variable is set or provide
it within the execution command along with the target cluster name.

Example:

```bash
poetry run pytest -m acm_observability --cluster-name={cluster name} --tc=kubeadmin_token:{kubedmin token}
```

Note: Make sure that the `OCM_TOKEN` environment variable is set as well
