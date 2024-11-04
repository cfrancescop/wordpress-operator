# Development 

Prepare the account creating a virtual environment:

`python -m venv .venv`

Activate the virtual environment:

On Windows

`.\.venv\Scripts\activate`

On Linux and Mac:

`./.venv/bin/activate`


Install the python requirements:

`pip install -r requirements.txt`


To execute the operator in local:



To run a specific handlers onyl:

On Windows:

`.\.venv\Scripts\kopf run -A wordpress_operator.py`

On Linux:

`./.venv/bin/kopf run -A wordpress_operator.py`

On Cluster:

`skaffold run --tail`

If you are using rancher desktop instead of minikube use:

`skaffold run -p rancher-desktop --tail`

## Example Resource

### Wordpress Operator

```yaml
apiVersion: gdgitalia.dev/v1
kind: Wordpress
metadata:
  name: devfestpescara2004
spec:
  name: devfestpescara2004
  hostname: devfestpescara2004.gdgitalia.it
  wp_size: 2Gi
  mysql_size: 2Gi
```
