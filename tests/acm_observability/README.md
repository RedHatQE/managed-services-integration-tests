# ACM Observability tests

To run ACM Observability tests make sure that the `KUBEADMIN_TOKEN` environment variable is set or provide
it within the execution command along with the target cluster name.

To obtain the kubeadmin token via Openshift cluster console (admin privileges needed):

```text
go to kube:admin (upper right console) > copy login command
```

Example for running the tests:

```bash
poetry run pytest -m acm_observability --cluster-name={cluster name} --tc=kubeadmin_token:{kubedmin token}
```
