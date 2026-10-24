# Resume Scoring Example

This document explains how resume matching scores are computed in the project and gives a concrete example with sample values.

## 1. What scores are used?
The matching pipeline computes four score components:

1. `skill_score` — measures matched skills between resume and job description
2. `category_score` — measures matched skill categories
3. `tfidf_score` — measures text similarity using TF-IDF vectors
4. `semantic_score` — measures meaning similarity using sentence embeddings

The final score combines them as:

```python
final = (
    0.3 * skill_score +
    0.2 * category_score +
    0.25 * tfidf_score +
    0.25 * semantic_score
)
```

The returned `final_score` is then multiplied by 100 and rounded to two decimals.

---

## 2. Example input data

### Resume extracted data
- `resume_skills`: ["Python", "Django", "SQL", "Git"]
- `resume_categories`: {"Programming": ["Python"], "Web Development": ["Django"], "Database": ["SQL"], "Development Tools": ["Git"]}
- `resume_text`: "Experienced Python developer with Django and SQL experience. Uses Git for version control."

### Job description data
- `jd_skills`: ["Python", "FastAPI", "SQL", "Docker"]
- `jd_categories`: {"Programming": ["Python"], "Web Development": ["FastAPI"], "Database": ["SQL"], "DevOps": ["Docker"]}
- `jd_text`: "Looking for a backend engineer skilled in Python, FastAPI, SQL, and Docker containerization."

---

## 3. Skill score calculation

The project uses weighted skill scoring from `weighted_scoring.py`.

### Step 1: Assign skill weights
Example weight rules:
- Programming, Cloud Computing = 5
- Web Development = 4
- Database, DevOps = 3
- Development Tools = 2
- Soft Skills = 1

For our example skills:
- Python: 5
- FastAPI: 4
- SQL: 3
- Docker: 3

### Step 2: Compute total weight and matched weight
- Total weight = 5 + 4 + 3 + 3 = 15
- Matched skills = ["Python", "SQL"]
- Matched weight = 5 + 3 = 8

### Skill score
```python
skill_score = matched_weight / total_weight
skill_score = 8 / 15 = 0.5333
```

Convert to percentage for explanation:
- `skill_overlap_percent = 53.33%`

---

## 4. Category score calculation

The category score compares resume categories with JD categories.

### Example categories
- Resume categories: Programming, Web Development, Database, Development Tools
- JD categories: Programming, Web Development, Database, DevOps

### Category overlap
- Matched categories = Programming, Web Development, Database
- Total JD categories = 4

### Category score
```python
category_score = 3 / 4 = 0.75
```

Convert to percentage:
- `category_overlap_percent = 75.00%`

---

## 5. TF-IDF score calculation

TF-IDF compares resume and JD text using important terms.

### Example text similarity
- `resume_text`: "Experienced Python developer with Django and SQL experience. Uses Git for version control."
- `jd_text`: "Looking for a backend engineer skilled in Python, FastAPI, SQL, and Docker containerization."

After vectorization and cosine similarity, a realistic example score might be:
```python
tfidf_score = 0.62
```

Convert to percentage:
- `tfidf_similarity_percent = 62.00%`

> Note: The actual TF-IDF score depends on the text vectorization result. The important idea is that it weights matching terms while ignoring common stop words.

---

## 6. Semantic score calculation

Semantic similarity uses embeddings to compare meaning.

### Example meaning similarity
- Resume mentions backend development with Python and SQL.
- JD mentions backend engineering with Python, SQL, and Docker.

A plausible semantic similarity value might be:
```python
semantic_score = 0.78
```

Convert to percentage:
- `semantic_similarity_percent = 78.00%`

---

## 7. Final score calculation

Combine the four scores with their weights:

```python
final = (
    0.3 * 0.5333 +
    0.2 * 0.75 +
    0.25 * 0.62 +
    0.25 * 0.78
)
```

### Compute component contributions
- Skill component: `0.3 * 0.5333 = 0.1600`
- Category component: `0.2 * 0.75 = 0.1500`
- TF-IDF component: `0.25 * 0.62 = 0.1550`
- Semantic component: `0.25 * 0.78 = 0.1950`

### Final score
```python
final = 0.1600 + 0.1500 + 0.1550 + 0.1950 = 0.6600
final_score = round(0.6600 * 100, 2) = 66.00
```

So the overall resume-to-JD match is **66.00%**.

---

## 8. Missing skill classification

Missing JD skills are those in `jd_skills` but not in `resume_skills`.

### Example missing skills
- `FastAPI`
- `Docker`

### Classification by category
- `FastAPI` → Web Development → moderate
- `Docker` → DevOps → moderate

If a missing skill belonged to Programming or Cloud Computing, it would be classified as critical.

---

## 9. Recommendations and learning roadmap

The system generates recommendations for missing critical and moderate skills.

### Example recommendations
- `FastAPI`: "Create a responsive backend service using FastAPI and deploy it."
- `Docker`: "Learn Docker containerization and package an application in a Docker container."

### Example learning roadmap
For each missing skill, the app may return:
- priority: `High` or `Medium`
- roadmap steps: practical learning plan
- youtube resources: tutorial videos for the skill

---

## 10. Summary of the scoring pipeline

1. Parse resume and JD text
2. Normalize skills with O*NET
3. Calculate:
   - weighted skill score
   - category overlap score
   - TF-IDF similarity
   - semantic similarity
4. Combine into final score with weights
5. Classify missing skills
6. Generate recommendations and roadmap

This gives a complete view from resume parsing to overall result and suggestions.
