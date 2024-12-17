FROM langchain/langgraph-api:3.11



ADD . /deps/asset-preset-config-generator

RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt -e /deps/*

ENV LANGSERVE_GRAPHS='{"agent": "/deps/asset-preset-config-generator/graph.py:graph"}'

WORKDIR /deps/asset-preset-config-generator