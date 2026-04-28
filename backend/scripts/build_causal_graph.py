#!/usr/bin/env python3
"""Build the disease-symptom causal graph from the dataset."""
import os, sys, json, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pandas as pd
import networkx as nx
from django.conf import settings

def main():
    df = pd.read_csv(settings.DISEASE_DATASET_PATH)
    G = nx.DiGraph()

    for _, row in df.iterrows():
        disease = row['disease_name']
        G.add_node(disease, node_type='disease', category=row.get('category', ''), icd10=row.get('icd10_code', ''))

        causal_weights = row.get('causal_weight', '')
        if pd.notna(causal_weights):
            for pair in str(causal_weights).split('|'):
                if ':' in pair:
                    parts = pair.rsplit(':', 1)
                    symptom = parts[0].strip()
                    try:
                        weight = float(parts[1].strip())
                    except ValueError:
                        weight = 0.5

                    if symptom:
                        G.add_node(symptom, node_type='symptom')
                        G.add_edge(symptom, disease, weight=weight, relationship='causes')

    # Save
    graph_path = settings.CAUSAL_GRAPH_PATH
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)
    with open(graph_path, 'w') as f:
        json.dump(nx.node_link_data(G), f, indent=2)

    diseases = sum(1 for _, d in G.nodes(data=True) if d.get('node_type') == 'disease')
    symptoms = sum(1 for _, d in G.nodes(data=True) if d.get('node_type') == 'symptom')
    print(f"Causal graph built successfully!")
    print(f"Total nodes: {G.number_of_nodes()} ({diseases} diseases, {symptoms} symptoms)")
    print(f"Total edges: {G.number_of_edges()}")
    print(f"Saved to: {graph_path}")

if __name__ == '__main__':
    main()
