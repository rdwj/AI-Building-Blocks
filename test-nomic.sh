#!/bin/bash

# Test the Nomic Embed API
curl -X POST https://nomic-embed-text-v1-5-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1/embeddings \
  -H "Authorization: Bearer b149099203fe842343682b36c333f1c8" \
  -H "Content-Type: application/json" \
  -d '{"model": "nomic-embed-text", "input": "Hello, world!"}'