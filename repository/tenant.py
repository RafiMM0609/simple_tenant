from typing import List, Optional
import yaml
import os
from models import get_supabase_pdp
from schemas.tenant import (
    RegisTenantRequest,
    EditTenantRequest,
    DataTenant,
    DataUserDir,
)
from core.security import (
    generate_hash_password,
)

async def get_list_user_dir(
    db:any,
    tenant_code: Optional[str] = None,
    src: Optional[str] = None,
)->List[DataUserDir]:
    try:
        # Get connection to the database with users table
        user_db = get_supabase_pdp()
        
        # Initialize query to fetch users
        user_query = user_db.table("users").select("id, email, username")
        
        # Get user_tenant relationships
        user_tenant_query = user_db.table("user_tenant").select("id_user, tenant_id")
        
        # Get tenants, with optional filter by tenant_code
        tenant_query = db.table("tenants").select("id, tenant_name, tenant_code, subdomain")
        if tenant_code:
            tenant_query = tenant_query.eq("tenant_code", tenant_code)
            
        # Execute all queries
        users = user_query.execute().data
        user_tenants = user_tenant_query.execute().data
        tenants = tenant_query.execute().data
        
        # Perform the join in Python
        result = []
        for ut in user_tenants:
            # Find matching user
            user = next((u for u in users if u["id"] == ut["id_user"]), None)
            # Find matching tenant
            tenant = next((t for t in tenants if t["id"] == ut["tenant_id"]), None)
            
            if user and tenant:
                # Create a combined record
                user_dir = {
                    "user_id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "tenant_id": tenant["id"],
                    "tenant_name": tenant["tenant_name"],
                    "tenant_code": tenant["tenant_code"],
                    "subdomain": tenant["subdomain"]
                }
                result.append(DataUserDir(**user_dir))
                
        return result
    except Exception as e:
        print(f"Error retrieving user directories: {e}")
        raise ValueError("Failed to retrieve user directories. Please try again.")

async def add_tenant(
    db: any,
    payload: RegisTenantRequest,
):
    try:
        tenant_code = payload.tenant_name[:4].lower().replace(' ', '-')
        response = (
            db.table("tenants")
            .insert({
            "tenant_name": payload.tenant_name,
            "contact_email": payload.contact_email,
            "phone": payload.phone,
            "subdomain": payload.subdomain or f"{payload.tenant_name.lower().replace(' ', '-')}",
            "tenant_code": tenant_code,
            })
            .execute()
        )
        return response
    except Exception as e:
        print(f"Error adding tenant: {e}")
        raise ValueError("Failed to add tenant. Please check the provided data and try again.")


async def get_tenants(db: any) -> List[DataTenant]:
    try:
        tenants = db.table("tenants").select("*").execute()
        tenants_dicts = [dict(tenant) for tenant in tenants.data]
        return [DataTenant(**tenant).dict() for tenant in tenants_dicts]
    except Exception as e:
        print(f"Error retrieving tenants: {e}")
        raise ValueError("Failed to retrieve tenants. Please try again.")
    
async def generate_service_yaml(db: any, tenant_code: int, output_dir: str = "./generated_services"):
    try:
        if not tenant_code:
            raise ValueError("Tenant ID is required to generate service YAML files.")
        # Retrieve tenant data by ID
        tenant_query = db.table("tenants").select("*").eq("tenant_code", tenant_code).limit(1).execute()
        tenant = tenant_query.data[0] if tenant_query.data else None
        if not tenant:
            raise ValueError(f"Tenant with ID {tenant_code} not found.")
            # Define the Kubernetes Deployment YAML structure
        deployment_yaml = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
            "name": tenant['subdomain'],
            "annotations": {
                "deployment.kubernetes.io/revision": "11"
            },
            "labels": {
                "workload.user.cattle.io/workloadselector": f"apps.deployment-dev-{tenant['subdomain']}",
                "app": tenant['tenant_code']
            },
            "namespace": "dev",
            },
            "spec": {
            "selector": {
                "matchLabels": {
                "workload.user.cattle.io/workloadselector": f"apps.deployment-dev-{tenant['subdomain']}"
                }
            },
            "template": {
                "metadata": {
                "labels": {
                    "workload.user.cattle.io/workloadselector": f"apps.deployment-dev-{tenant['subdomain']}"
                },
                "annotations": {
                    "kubectl.kubernetes.io/restartedAt": "2025-03-20T13:19:11+07:00"
                }
                },
                "spec": {
                "containers": [
                    {
                    "image": "ppdptelkom/ppddev:latest",
                    "imagePullPolicy": "Always",
                    "name": "container-0",
                    "ports": [
                        {
                        "containerPort": 80,
                        "name": "feppd",
                        "protocol": "TCP"
                        }
                    ],
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "privileged": False,
                        "readOnlyRootFilesystem": False,
                        "runAsNonRoot": False
                    },
                    "terminationMessagePath": "/dev/termination-log",
                    "terminationMessagePolicy": "File",
                    "env": [
                        {
                        "name": "allowed_domain",
                        "value": f"{tenant['subdomain']}.solutiontech.id"
                        }
                    ],
                    "resources": {}
                    }
                ],
                "affinity": {},
                "dnsPolicy": "ClusterFirst",
                "imagePullSecrets": [
                    {
                    "name": "ppdptelkom"
                    }
                ],
                "restartPolicy": "Always",
                "schedulerName": "default-scheduler",
                "terminationGracePeriodSeconds": 30,
                "volumes": []
                }
            },
            "progressDeadlineSeconds": 600,
            "replicas": 1,
            "revisionHistoryLimit": 10,
            "strategy": {
                "rollingUpdate": {
                "maxSurge": "25%",
                "maxUnavailable": "25%"
                },
                "type": "RollingUpdate"
            }
            }
        }
        # Define the Kubernetes Service YAML structure
        service_yaml = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{tenant['tenant_code']}-service",
                "namespace": "dev",
                "labels": {
                    "workload.user.cattle.io/workloadselector": f"apps.deployment-dev-{tenant['subdomain']}",
                    "app": tenant['tenant_code']
                }
            },
            "spec": {
                "selector": {
                    "app": tenant['tenant_code']
                },
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": 80,
                        "targetPort": 80
                    }
                ]
            }
        }

        # Define the Kubernetes Ingress YAML structure
        ingress_yaml = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{tenant['tenant_code']}-ingress",
                "namespace": "dev",
                "annotations": {
                    "nginx.ingress.kubernetes.io/rewrite-target": "/"
                }
            },
            "spec": {
                "rules": [
                    {
                        "host": f"{tenant['subdomain']}.solutiontech.id",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": f"{tenant['tenant_code']}-service",
                                            "port": {
                                                "number": 80
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Write the Deployment YAML to a file
        deployment_file_path = os.path.join(output_dir, f"{tenant['tenant_code']}_deployment.yaml")
        with open(deployment_file_path, "w") as deployment_file:
            yaml.dump(deployment_yaml, deployment_file)

        # Write the Service YAML to a file
        service_file_path = os.path.join(output_dir, f"{tenant['tenant_code']}_service.yaml")
        with open(service_file_path, "w") as service_file:
            yaml.dump(service_yaml, service_file)

        # Write the Ingress YAML to a file
        ingress_file_path = os.path.join(output_dir, f"{tenant['tenant_code']}_ingress.yaml")
        with open(ingress_file_path, "w") as ingress_file:
            yaml.dump(ingress_yaml, ingress_file)

        return {"service_file": service_file_path, "ingress_file": ingress_file_path}

    except Exception as e:
        print(f"Error generating YAML files: {e}")
        if "not found" in str(e):
            raise ValueError(f"Tenant with ID {tenant_code} not found.")
        raise ValueError("Failed to generate service YAML files. Please try again.")