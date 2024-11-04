import base64
import kopf
import logging
import kubernetes
import yaml
import os
import secrets
import psycopg2

# Define the function to create a MySQL PersistentVolumeClaim
async def create_mysql_volume(name: str, spec: kopf.Spec, namespace: str, **kwargs):
    """Creates a PersistentVolumeClaim for MySQL."""
    api = kubernetes.client.CoreV1Api()
    path = os.path.join(os.path.dirname(__file__), 'templates',"mysql", 'mysql-volume.yaml')
    with open(path, 'rt') as f:
        tmpl = f.read()
    text = tmpl.format(
        name=name,
        mysql_size=spec.get('mysql_size','1Gi')
    )
    data = yaml.safe_load(text)
    kopf.adopt(data)
    obj = api.create_namespaced_persistent_volume_claim(namespace=namespace, body=data)
    logging.info(f"MySQL PersistentVolumeClaim created: {obj.metadata.name}")
    return str(obj.metadata.name)

# Define the function to create a WordPress PersistentVolumeClaim
async def create_wordpress_volume(name: str, spec: kopf.Spec, namespace: str, **kwargs):
    """Creates a PersistentVolumeClaim for WordPress."""
    api = kubernetes.client.CoreV1Api()
    path = os.path.join(os.path.dirname(__file__), 'templates',"wordpress", 'wordpress-volume.yaml')
    with open(path, 'rt') as f:
        tmpl = f.read()
    text = tmpl.format(
        name=name,
        wp_size=spec.get('wp_size','1Gi')
    )
    data = yaml.safe_load(text)
    kopf.adopt(data)
    obj = api.create_namespaced_persistent_volume_claim(namespace=namespace, body=data)
    logging.info(f"WordPress PersistentVolumeClaim created: {obj.metadata.name}")
    return str(obj.metadata.name)


# Define the functions to create the MySQL and WordPress deployments
async def create_mysql(name: str, spec: kopf.Spec, namespace: str, **kwargs):
    """Creates a MySQL deployment."""
    api = kubernetes.client.AppsV1Api()
    path = os.path.join(os.path.dirname(__file__), 'templates','mysql', 'mysql-deployment.yaml')
    with open(path, 'rt') as f:
        tmpl = f.read()
    text = tmpl.format(
        name=name,
    )
    data = yaml.safe_load(text)
    kopf.adopt(data)
    obj = api.create_namespaced_deployment(namespace=namespace, body=data)
    logging.info(f"MySQL deployment created: {obj.metadata.name}")
    return str(obj.metadata.name)

async def create_wordpress(name: str, spec: kopf.Spec, namespace: str, **kwargs):
    """Creates a WordPress deployment."""
    logging.info(f"Creating WordPress deployment: name:{name} {spec} namespace:{namespace}")
    api = kubernetes.client.AppsV1Api()
    path = os.path.join(os.path.dirname(__file__), 'templates',"wordpress", 'wordpress-deployment.yaml')
    with open(path, 'rt') as f:
        tmpl = f.read()
    text = tmpl.format(
        name=name,
        image=spec.get('image', 'wordpress:latest'),
        replicas=spec.get('replicas', 1)
    )
    data = yaml.safe_load(text)
    kopf.adopt(data)
    obj = api.create_namespaced_deployment(namespace=namespace, body=data)
    logging.info(f"WordPress deployment created: {obj.metadata.name}")
    return str(obj.metadata.name)

# Define the functions to create the MySQL and WordPress services
async def create_mysql_service(name: str, namespace: str, **kwargs):
    """Creates a MySQL service."""
    api = kubernetes.client.CoreV1Api()
    path = os.path.join(os.path.dirname(__file__), 'templates','mysql', 'mysql-service.yaml')
    with open(path, 'rt') as f:
        tmpl = f.read()
    text = tmpl.format(name=name)
    data = yaml.safe_load(text)
    kopf.adopt(data)
    obj = api.create_namespaced_service(namespace=namespace, body=data)
    logging.info(f"MySQL service created: {obj.metadata.name}")
    return str(obj.metadata.name)

async def create_wordpress_service(name: str, namespace: str, **kwargs):
    """Creates a WordPress service."""
    api = kubernetes.client.CoreV1Api()
    path = os.path.join(os.path.dirname(__file__), 'templates','wordpress', 'wordpress-service.yaml')
    with open(path, 'rt') as f:
        tmpl = f.read()
    text = tmpl.format(name=name)
    data = yaml.safe_load(text)
    kopf.adopt(data)
    obj = api.create_namespaced_service(namespace=namespace, body=data)
    logging.info(f"WordPress service created: {obj.metadata.name}")
    return str(obj.metadata.name)

# Define the function to create a Secret for MySQL password
async def create_mysql_password(name: str, spec: kopf.Spec, namespace: str, **kwargs):
    """Creates a Secret for MySQL root password."""
    api = kubernetes.client.CoreV1Api()
    path = os.path.join(os.path.dirname(__file__), 'templates','mysql', 'mysql-password.yaml')
    with open(path, 'rt') as f:
        tmpl = f.read()
    text = tmpl.format(
        name=name,
        mysql_password=base64.b64encode(secrets.token_urlsafe(16).encode('ascii')).decode('ascii') # random secure password
    )
    data = yaml.safe_load(text)
    kopf.adopt(data)
    obj = api.create_namespaced_secret(namespace=namespace, body=data)
    logging.info(f"MySQL password Secret created: {obj.metadata.name}")
    return str(obj.metadata.name)

# Define the function to create an Ingress for WordPress
async def create_wordpress_ingress(name: str, spec: kopf.Spec, namespace: str, **kwargs):
    """Creates an Ingress for WordPress."""
    api = kubernetes.client.NetworkingV1Api()
    path = os.path.join(os.path.dirname(__file__), 'templates','wordpress', 'wordpress-ingress.yaml')
    with open(path, 'rt') as f:
        tmpl = f.read()
    text = tmpl.format(
        name=name,
        hostname=spec.get('wordpress').get('hostname', f"{name}-wordpress.example.com")
    )
    data = yaml.safe_load(text)
    kopf.adopt(data)
    obj = api.create_namespaced_ingress(namespace=namespace, body=data)
    logging.info(f"WordPress Ingress created: {obj.metadata.name}")
    return str(obj.metadata.name)

@kopf.on.create('wordpress')
async def wordpress_create(body, spec, **kwargs):
    """Handles creation of a WordPress installation."""
    logging.info(f"Creating WordPress installation: name:{body.metadata.name} {spec} namespace:{body.metadata.namespace}")

    # Create the MySQL and WordPress deployments and services
    await kopf.execute(fns={
        'mysql-deployment': create_mysql,
        'mysql-volume': create_mysql_volume,
        'mysql-service': create_mysql_service,
        'mysql-password': create_mysql_password,
        'wordpress-deployment': create_wordpress,
        'wordpress-volume': create_wordpress_volume,
        'wordpress-service': create_wordpress_service,
        #'wordpress-ingress': create_wordpress_ingress
    })
    logging.info(f"WordPress installation: {body.metadata.name} {spec} completed")




@kopf.on.delete('wordpress')
async def wordpress_delete(body, **kwargs):
    """Handles deletion of a WordPress installation."""
    logging.info(f"Deleting WordPress installation: {body.metadata.name}")
    name= body.metadata.name
    namespace = body.metadata.namespace
    # ignore 404 error
    
    safe_delete(lambda:kubernetes.client.AppsV1Api().delete_namespaced_deployment(name=f"{name}-mysql", namespace=namespace))
   
    safe_delete(lambda:kubernetes.client.CoreV1Api().delete_namespaced_persistent_volume_claim(name=f"{name}-mysql-pv", namespace=namespace))
    safe_delete(lambda:kubernetes.client.CoreV1Api().delete_namespaced_service(name=f"{name}-mysql", namespace=namespace))
    safe_delete(lambda:kubernetes.client.CoreV1Api().delete_namespaced_secret(name=f"{name}-mysql-pass", namespace=namespace))
    safe_delete(lambda:kubernetes.client.AppsV1Api().delete_namespaced_deployment(name=f"{name}", namespace=namespace))
    safe_delete(lambda:kubernetes.client.CoreV1Api().delete_namespaced_persistent_volume_claim(name=f"{name}-pv", namespace=namespace))
    safe_delete(lambda:kubernetes.client.CoreV1Api().delete_namespaced_service(name=f"{name}", namespace=namespace))
    safe_delete(lambda:kubernetes.client.NetworkingV1Api().delete_namespaced_ingress(name=f"{name}-ingress", namespace=namespace))

    logging.info(f"WordPress installation deleted: {body.metadata.name}")

def safe_delete(delete_op):
    try:
        delete_op()
    except kubernetes.client.rest.ApiException as e:
        if e.status != 404:
            raise e




# every minute use the secret to query the postgres database
@kopf.on.timer('secrets', interval=60.0, annotations={'blog-platform-credentials': kopf.PRESENT})
async def check_secrets_timer(spec,namespace, **kwargs):
    """Periodically checks for Secrets with the specified annotation."""
    try:
        # Extract PostgreSQL connection details from the Secret
        db_host = base64.b64decode(spec.data['DB_HOST']).decode('utf-8')
        db_name = base64.b64decode(spec.data['DB_NAME']).decode('utf-8')
        db_user = base64.b64decode(spec.data['DB_USER']).decode('utf-8')
        db_password = base64.b64decode(spec.data['DB_PASSWORD']).decode('utf-8')

        # Create a PostgreSQL connection
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        logging.info(f"Successfully connected to PostgreSQL database: {db_name}")

        # Check for records with 'init=false' in the 'postgres' table
        with conn.cursor() as cur:
            cur.execute("SELECT name,hostname FROM blogs WHERE init = false;")
            uninitialized_records = cur.fetchall()

            for record in uninitialized_records:
                name, hostname = record
                logging.info(f"Creating WordPress resource for blog: {name} ({hostname})")

                # Create WordPress resource using the name and hostname
                try:
                    await create_wordpress_resource(name, hostname,namespace)

                    # Update the 'init' column to True after successful creation
                    cur.execute("UPDATE blogs SET init = true WHERE name = %s;", (name,))
                    conn.commit()
                    logging.info(f"WordPress resource created and initialized for blog: {name}")

                except Exception as e:
                    logging.error(f"Error creating WordPress resource for blog {name}: {e}")


        conn.close()

    except psycopg2.Error as e:
        logging.error(f"Error connecting to PostgreSQL database: {e}")
    except KeyError as e:
        logging.error(f"Missing key in Secret data: {e}")   


async def create_wordpress_resource(name, hostname,namespace):
    """Creates a WordPress resource in Kubernetes."""
    api = kubernetes.client.CustomObjectsApi()
    # Define the WordPress resource YAML
    wordpress_resource = {
        "apiVersion": "gdgitalia.dev/v1",
        "kind": "Wordpress",
        "metadata": {
            "name": name,
            "namespace": namespace  # Replace with your desired namespace
        },
        "spec": {
            "hostname": hostname,
            "name": name
        }
    }

    try:
        # Create the resource
        api.create_namespaced_custom_object(
            group="gdgitalia.dev",
            version="v1",
            namespace="default",  # Replace with your desired namespace
            plural="wordpress",
            body=wordpress_resource
        )
        logging.info(f"WordPress resource created for blog: {name}")
    except kubernetes.client.rest.ApiException as e:
        logging.error(f"Error creating WordPress resource: {e}")