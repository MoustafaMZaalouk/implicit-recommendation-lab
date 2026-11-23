"""Small, reproducible educational experiment. See README for limitations."""
import json
from pathlib import Path
import numpy as np

def save(result, output):
    Path(output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result

from sklearn.metrics.pairwise import cosine_similarity

def interactions(seed=42,users=240,items=80):
    rng=np.random.default_rng(seed)
    u=rng.normal(size=(users,5)); v=rng.normal(size=(items,5))
    affinities=u@v.T+rng.normal(0,.4,(users,items))
    return [np.argsort(-row)[:12].tolist() for row in affinities]
def split_positives(rows,seed=43):
    rng=np.random.default_rng(seed); train=[]; held=[]
    for row in rows:
        shuffled=rng.permutation(row); train.append(shuffled[:10].tolist()); held.append(shuffled[10:].tolist())
    return train,held
def evaluate(ranking,truth,k=10):
    hits=np.array([int(i in truth) for i in ranking[:k]])
    dcg=float(np.sum(hits/np.log2(np.arange(2,len(hits)+2))))
    ideal=float(np.sum(1/np.log2(np.arange(2,min(k,len(truth))+2))))
    return len(set(ranking[:k]) & set(truth))/len(truth),dcg/ideal
def run(output="results.json"):
    train,test=split_positives(interactions()); matrix=np.zeros((240,80))
    for u,items in enumerate(train): matrix[u,items]=1
    similarity=cosine_similarity(matrix.T); np.fill_diagonal(similarity,0)
    popularity=matrix.sum(axis=0); rows={"popularity":[],"item_knn":[]}; unique={k:set() for k in rows}
    for u,seen in enumerate(train):
        for name,scores in [("popularity",popularity.copy()),("item_knn",matrix[u]@similarity)]:
            scores=np.asarray(scores,dtype=float); scores[seen]=-np.inf
            ranking=np.argsort(-scores,kind="stable")[:10].tolist()
            rows[name].append(evaluate(ranking,test[u])); unique[name].update(ranking)
    result={k:{"recall_at_10":float(np.mean([v[0] for v in vals])),"ndcg_at_10":float(np.mean([v[1] for v in vals])),"catalog_coverage":len(unique[k])/80} for k,vals in rows.items()}
    return save({"seed":42,"split_seed":43,"users":240,"items":80,"train_positives_per_user":10,"heldout_positives_per_user":2,"models":result},output)

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
