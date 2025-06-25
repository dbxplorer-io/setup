# Kubernetes & GitOps Setup Guide for dbxplorer Agent

> **This guide helps you deploy dbxplorer agent in Kubernetes using GitOps for configuration, secure secrets, and Datadog integration.**

---

## Table of Contents
- [1. Overview](#1-overview)
- [2. Prepare Kubernetes Secrets](#2-prepare-kubernetes-secrets)
- [3. Create Oracle Database User](#3-create-oracle-database-user)
- [4. GitOps Configuration Repo Structure](#4-gitops-configuration-repo-structure)
- [5. Deploy dbxplorer Agent](#5-deploy-dbxplorer-agent)
- [6. Inventory & Metrics YAML Structure](#6-inventory--metrics-yaml-structure)
- [7. License Management](#7-license-management)
- [8. Verification & Troubleshooting](#8-verification--troubleshooting)
- [9. References](#9-references)

---

## 1. Overview
- **dbxplorer agent** is configured via a Git repository (GitOps), supporting dynamic reloads and version control.
- All sensitive data (API keys, DB passwords, license JWT, Git credentials) are managed as Kubernetes secrets.
- **Database passwords are stored encrypted in the config repo; the DB password encryption key is stored as a Kubernetes secret in `k8s/secrets/encryption.yml`.**
- Metrics and inventory are modular YAML files, supporting per-entity configuration.
- See [project_documentation.md](../project_documentation.md) for architecture and advanced usage.

---

## 2. Prepare Kubernetes Secrets

### a. Datadog API Key & Related Vars
- File: `k8s/secrets/datadog.yml`
- Contains: `DD_API_KEY`, `DD_APP_KEY`, `DD_URL`, etc.
- Apply: `kubectl apply -f k8s/secrets/datadog.yml`

### b. Git Credentials
- File: `k8s/secrets/git.yml`
- Contains: `GIT_USERNAME`, `GIT_TOKEN` (base64-encoded)
- Apply: `kubectl apply -f k8s/secrets/git.yml`

### c. Agent Config
- File: `k8s/secrets/agent-config.yaml`
- Contains: global agent config, Datadog, license, threading, configRepo info
- Apply: `kubectl create secret generic dbxagent-config --from-file=agent-config.yaml=k8s/secrets/agent-config.yaml -n dbxplorer`

### d. License Key & Public Key
- File: `k8s/secrets/license-jwt.yml` (JWT), `k8s/secrets/license-public-key.yaml` (public key)
- Mount JWT as `AGENT_LICENSE_KEY` env var, public key as `/etc/dbxplorer/public_key.pem`
- See [License Management](#6-license-management)

### e. DB Password Key (for encrypted DB passwords)
- File: `k8s/secrets/dbxagent-dbkey.yaml`
- Contains: `DB_PASSWORD_KEY`

### f. Logback Config (Optional)
- Input file: `k8s/logging/logback.xml`
- To create the secret from your `logback.xml` file, run:

```sh
kubectl create secret generic logback-config \
  --from-file=logging.xml=k8s/logging/logback.xml \
  --namespace=dbxplorer
```

---

## 3. Create Oracle Database User for dbxplorer Agent

Before deploying dbxplorer agent, you must create a dedicated Oracle user with the required privileges on each database you wish to monitor. Run the following SQL as a DBA user:

```sql
CREATE USER c##dbxplorer IDENTIFIED BY <password> CONTAINER = ALL;
ALTER USER c##dbxplorer SET CONTAINER_DATA=ALL CONTAINER=CURRENT;
ALTER USER c##dbxplorer ACCOUNT UNLOCK;
ALTER PROFILE DEFAULT LIMIT FAILED_LOGIN_ATTEMPTS UNLIMITED;

-- Grant necessary privileges for monitoring
GRANT CREATE SESSION TO c##dbxplorer;
GRANT SELECT ON v_$session TO c##dbxplorer;
GRANT SELECT ON v_$database TO c##dbxplorer;
GRANT SELECT ON v_$containers TO c##dbxplorer;
GRANT SELECT ON v_$sqlstats TO c##dbxplorer;
GRANT SELECT ON v_$instance TO c##dbxplorer;
GRANT SELECT ON dba_feature_usage_statistics TO c##dbxplorer;
GRANT SELECT ON V_$SQL_PLAN_STATISTICS_ALL TO c##dbxplorer;
GRANT SELECT ON V_$PROCESS TO c##dbxplorer;
GRANT SELECT ON V_$SESSION TO c##dbxplorer;
GRANT SELECT ON V_$CON_SYSMETRIC TO c##dbxplorer;
GRANT SELECT ON CDB_TABLESPACE_USAGE_METRICS TO c##dbxplorer;
GRANT SELECT ON CDB_TABLESPACES TO c##dbxplorer;
GRANT SELECT ON V_$SQLCOMMAND TO c##dbxplorer;
GRANT SELECT ON V_$DATAFILE TO c##dbxplorer;
GRANT SELECT ON V_$SYSMETRIC TO c##dbxplorer;
GRANT SELECT ON V_$SGAINFO TO c##dbxplorer;
GRANT SELECT ON V_$PDBS TO c##dbxplorer;
GRANT SELECT ON CDB_SERVICES TO c##dbxplorer;
GRANT SELECT ON V_$OSSTAT TO c##dbxplorer;
GRANT SELECT ON V_$PARAMETER TO c##dbxplorer;
GRANT SELECT ON V_$SQLSTATS TO c##dbxplorer;
GRANT SELECT ON V_$CONTAINERS TO c##dbxplorer;
GRANT SELECT ON V_$SQL_PLAN_STATISTICS_ALL TO c##dbxplorer;
GRANT SELECT ON V_$SQL TO c##dbxplorer;
GRANT SELECT ON V_$PGASTAT TO c##dbxplorer;
GRANT SELECT ON v_$asm_diskgroup TO c##dbxplorer;
GRANT SELECT ON v_$rsrcmgrmetric TO c##dbxplorer;
GRANT SELECT ON v_$dataguard_config TO c##dbxplorer;
GRANT SELECT ON v_$dataguard_stats TO c##dbxplorer;
GRANT SELECT ON v_$transaction TO c##dbxplorer;
GRANT SELECT ON v_$locked_object TO c##dbxplorer;
GRANT SELECT ON dba_objects TO c##dbxplorer;
GRANT SELECT ON cdb_data_files TO c##dbxplorer;
GRANT SELECT ON dba_data_files TO c##dbxplorer;
GRANT RESOURCE TO c##dbxplorer;
GRANT SET CONTAINER TO c##dbxplorer;
GRANT SELECT_CATALOG_ROLE TO c##dbxplorer;
GRANT ADVISOR TO c##dbxplorer;
ALTER USER c##dbxplorer QUOTA 100M ON USERS;
```

> **Security Tip:** Use a strong password with a mix of uppercase, lowercase, numbers, and special characters to secure the `c##dbxplorer` user.

> **Note:** The `SELECT_CATALOG_ROLE` privilege allows the user to query system catalog views, which are essential for monitoring database performance and usage.

### ASM User Creation (for ASM Monitoring)

If you want to monitor Oracle ASM (Automatic Storage Management) with dbxplorer, you must also create a dedicated ASM user with the required privileges. Run the following SQL as a SYSASM user:

```sql
CREATE USER c##dbxplorer IDENTIFIED BY <password>;
ALTER USER c##dbxplorer ACCOUNT UNLOCK;
ALTER PROFILE DEFAULT LIMIT FAILED_LOGIN_ATTEMPTS UNLIMITED;
GRANT SYSASM TO c##dbxplorer;
```

> **Security Tip:** Use a strong password with a mix of uppercase, lowercase, numbers, and special characters to secure the `c##dbxplorer` ASM user.

---

## 4. GitOps Configuration Repo Structure

Your config repo should look like:
```
config-repo/
  agent-config.yaml         # Main agent config (global)
  inventory/
    oracle/
      oracle_instance/
        ext3adm1_dbicdb.yml   # Per-entity inventory YAML
  monitoring/
    metrics/
      ext3adm1_dbicdb.yml     # Per-entity/group metrics YAML
```
- **agent-config.yaml**: Points to the Git repo, Datadog, license, threading, etc.
- **inventory/**: Per-entity connection info (see below).
- **metrics/**: Per-entity/group metric mappings (see below).

---

## 5. Deploy dbxplorer Agent

- Edit and apply `k8s/deployment/dbxagent.yaml` (see example in repo)
- Key points:
  - All secrets are mounted as env vars or files
  - Config repo is cloned to `/app/config-repo/`
  - Inventory and metrics are loaded from `/app/config-repo/inventory/` and `/app/config-repo/monitoring/metrics/`
  - License public key is mounted at `/etc/dbxplorer/public_key.pem`

**Deploy:**
```sh
kubectl apply -f k8s/deployment/dbxagent.yaml
kubectl get pods -n dbxplorer
kubectl logs deployment/dbxagent -n dbxplorer
```

**Restart after secret/config change:**
```sh
kubectl rollout restart deployment dbxagent -n dbxplorer
```

---

## 6. Inventory & Metrics YAML Structure

### a. Inventory Example (`inventory/oracle/oracle_instance/ext3adm1_dbicdb.yml`)
```yaml
- entityName: ext3adm1_dbicdb
  enabled: true
  type: oracle
  user: c##dbxplorer
  password: "<ENCRYPTED_OR_PLAIN>"
  role: "normal"
  url: "jdbc:oracle:thin:@(DESCRIPTION=(...))"
  tags:
    dbsys: "ext3"
    entityType: "oracle_instance"
    environment: "development"
    application: "dbi"
    service: "oracle"
```
- Use encrypted passwords for production (see `assetes/security/encrypt_password.py` and docs).

### b. Metrics Example (`monitoring/metrics/ext3adm1_dbicdb.yml`)
```yaml
- metricGroup: Session
  metricName: [SessionMonitor]
  intervalSeconds: 30
  enabled: true
  entityName: [ext3adm1_dbicdb]
- metricGroup: Os
  metricName: [OsStat]
  intervalSeconds: 30
  enabled: true
  entityName: [ext3adm1_dbicdb]
- metricGroup: Health
  metricName: [InstanceViewer]
  intervalSeconds: 60
  enabled: true
  entityName: [ext3adm1_dbicdb]
```
- See [assetes/documentation/metrics/readme.md](../assetes/documentation/metrics/readme.md) for full metric collector and dashboard usage documentation.

---

## 7. License Management
- Each deployment/client gets a unique JWT license (see [assetes/documentation/license/readme.md](../assetes/documentation/license/readme.md)).
- Generate ECDSA keys as described in [ec_keygen.md](../assetes/documentation/license/ec_keygen.md).
- Store the JWT in a secret, mount the public key as a file.
- The agent validates the JWT offline using the public key (no REST call needed).
- Rotate/revoke licenses by updating the secret or expiry.

---

## 8. Verification & Troubleshooting
- **Check pod logs:** `kubectl logs deployment/dbxagent -n dbxplorer`
- **Check secret mounts:** Ensure all secrets are present and correctly referenced in the deployment YAML.
- **Check config repo:** The agent logs which inventory and metrics files are loaded. If missing, check repo structure and branch.
- **License errors:** See agent logs for JWT validation issues.
- **Metrics in Datadog:** Search for metrics with prefix `dbxplorer.*` in Datadog. See [assetes/documentation/metrics/readme.md](../assetes/documentation/metrics/readme.md) for dashboard tips.
- **Debug mode:** Set `debug.pod: true` in agent-config.yaml to keep the pod running for troubleshooting.

---

## 9. References
- [assetes/documentation/metrics/readme.md](../assetes/documentation/metrics/readme.md) — Metric collectors, dashboard usage
- [assetes/documentation/license/readme.md](../assetes/documentation/license/readme.md) — License management
- [assetes/documentation/license/ec_keygen.md](../assetes/documentation/license/ec_keygen.md) — Key generation
- [assetes/security/readme.md](../assetes/security/readme.md) — Password encryption
- [project_documentation.md](../project_documentation.md) — Architecture, modular config, advanced usage
- [CHANGELOG.md](../CHANGELOG.md)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Datadog Dashboards](https://docs.datadoghq.com/dashboards/)

---

For further help, contact your dbxplorer support team or see the referenced documentation files. 