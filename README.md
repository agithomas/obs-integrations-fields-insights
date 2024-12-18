# Observability Integrations Fields Insights (Beta)

The Observability Integration Fields Insight project bridges gaps in the Observability integration field details. The amount of details added as part of the fields description is often limited due to various reasons including 
- the number of fields added as part of an integration
- developers or contributors might assume that the users of the integration already familiar with the observed fields, leading to less emphasis on the documentation
- developers may rely on the documentation of the services or products for which integration is built
- with a large number of fields, writing detailed descriptions for each one can become a repetitive and low-priority task. 

This project provides extended descriptions for each field, highlighting their relevance and importance in determining service or product availability. Using the name of the field and field description, it pulls insights from a variety of online sources, storing them in databases for reuse. The data is organized into a report schema, supporting both QA and decision-making needs.

> **Warning!!!:** Since the report content generated by running this project ( also used to generate alert threshold or slo settings, alert baselining, etc), is using the contents from random websites, it is important the users validate the sources of these contents (mentioned the report) and the correctness of data before using for Q/A or taking decisions or to be used in other applications.

It provides advanced insights into observability fields, supporting diverse use cases such as generating asset presets for Alerts and SLOs, extending the knowledge base of Elastic's Observability AI Assistant. With a modular architecture, it operates independently or integrates seamlessly with Elastic Observability to enrich its capabilities. 

By generating recommendations for thresholds, critical metrics, and field relationships, the project simplifies alert creation and validation. It also extends the Elastic's Observability AI Assistant AI assistant’s question-answering capabilities, empowering users to streamline workflows and enhance the observability ecosystem.

## Requirements

- `python 3.11+` and uses poetry for package dependencies
- Elasticsearch cluster deployed on [Elasticsearch Service](https://www.elastic.co/cloud/) or [download and run](https://www.elastic.co/downloads/) Elasticsearch. Create a key [in Kibana](https://www.elastic.co/guide/en/kibana/8.17/api-keys.html) or [using the Elasticsearch API](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/security-api-create-api-key.html)
- Visit the [OpenAI API platform](https://platform.openai.com/), sign in, and navigate to the "API Keys" section under your account settings to create a new API key.
- Visit the [Tavily API platform](https://www.tavily.com/), sign in or create an account, then go to the "API Keys" section in your account settings to generate a new API key.
- MySQL 8.1
- [Langsmith](https://smith.langchain.com/) account (recommended)
- [Langgraph-studio](https://github.com/langchain-ai/langgraph-studio) (recommended). LangGraph Studio requires docker-compose version 2.22.0+ or higher.


## Setup

## Install pip3 and poetry
```
python3 -m ensurepip --default-pip
pip install poetry
```
### Set up **MySQL 8.1** Docker instance and create a database and table:
```
# Pull the MySQL 8.1 Docker image:
docker pull mysql:8.1

# Run a MySQL container:
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=rootpassword -d mysql:8.1

# Create a new database:
CREATE DATABASE your_database_name;

# Execute the SQL script from the install/mysql.sql file to create the required table(s) by running:
source /path/to/install/mysql.sql
```

### Clone repo
```
# This is a private repo. Contact agi.thomas@elastic.co for GITHUB TOKEN
gh repo clone agithomas/obs-integrations-fields-insights
```

### Move to directory and use poetry to setup venv, install dependencies:
```
[ec2-user@ip-172-31-43-26 obs-integrations-fields-insights]$ cd obs-integrations-fields-insights/

[ec2-user@ip-172-31-43-26 obs-integrations-fields-insights]$ poetry shell

(asset-preset-config-generator-py3.11) [ec2-user@ip-172-31-43-26 obs-integrations-fields-insights]$ poetry install
Updating dependencies
Resolving dependencies... (10.7s)

Package operations: 89 installs, 0 updates, 0 removals

  - Installing certifi (2024.12.14)
  ........
  - Installing neo4j (5.27.0)
  - Installing pytest (8.3.4)
  - Installing tavily-python (0.5.0)

Writing lock file

Installing the current project: asset-preset-config-generator (0.1.0)

```
### Configure Environment Variables

```
cp example.env .env
```

| Field Name         | Description                                                  |
|--------------------|--------------------------------------------------------------|
| `ES_INDEX`         | The vector store index name.                                 |
| `ES_INDEX_RELEVANCE` | The name of the index for storing the output of the framework run. |
| `LANGCHAIN_TRACING_V2` | Set to "true" to enable langchain tracing. |


## Run the service
```
langgraph up
```

```
asset-preset-config-generator-py3.11(base) agikthomas@Agis-MBP asset-preset-config-generator % langgraph up                                    
Starting LangGraph API server...
For local dev, requires env var LANGSMITH_API_KEY with access to LangGraph Cloud closed beta.
For production use, requires a license key in env var LANGGRAPH_CLOUD_LICENSE_KEY.
Ready!       
- API: http://localhost:8123
- Docs: http://localhost:8123/docs
- LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123
```

Use the `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123` to access the langgraph studio's Web UI for testing.

## Troubleshooting

### Connectivity issue
```
'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x7f2c51c0a610>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution')': /simple/poetry-core/
```
Resolution
```
sudo nano /etc/docker/daemon.json

Add the following entries

{
  "dns": ["8.8.8.8", "8.8.4.4"]
}

sudo systemctl restart docker

```

### Unable to connect with MySQL

If you're using Docker Desktop (on macOS or Windows) and the container is running on host networking mode, you can use `host.docker.internal`. However, this doesn't work in Linux or EC2 environments. Make sure that the mysql instance is accessbible from the langgraph docker image created when running `langgraph up`


### Other errors

Use the verbose option to debug the issue
```
langgraph up --verbose
```