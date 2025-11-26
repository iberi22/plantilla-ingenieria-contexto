# Taxonomy System for Repository Classification

## Overview
This document defines the multi-category taxonomy system for classifying GitHub repositories in the "Best of Open Source" blog. Each repository will be automatically categorized based on its characteristics, enabling users to filter and discover projects by technology focus.

## Categories Definition

### 1. 🤖 AI/ML (Artificial Intelligence & Machine Learning)
**Description:** Projects focused on machine learning, deep learning, NLP, computer vision, and AI applications.

**Classification Criteria:**
- **Keywords:** `machine-learning`, `deep-learning`, `neural-network`, `tensorflow`, `pytorch`, `ai`, `nlp`, `computer-vision`, `transformers`, `llm`, `gpt`, `generative-ai`
- **Languages:** Python (primary), Julia, R
- **Dependencies:** `tensorflow`, `pytorch`, `scikit-learn`, `keras`, `huggingface`, `langchain`, `openai`
- **Topics:** `artificial-intelligence`, `machine-learning`, `deep-learning`, `neural-networks`

**Examples:**
- Hugging Face Transformers
- Stable Diffusion
- LangChain
- OpenAI API wrappers
- Custom ML models and frameworks

---

### 2. 🔒 Cybersecurity
**Description:** Security tools, penetration testing frameworks, encryption libraries, and vulnerability scanners.

**Classification Criteria:**
- **Keywords:** `security`, `pentesting`, `vulnerability`, `exploit`, `encryption`, `authentication`, `authorization`, `firewall`, `ids`, `ips`, `malware`, `threat`
- **Languages:** Python, Go, C, Rust, Bash
- **Dependencies:** `cryptography`, `pycryptodome`, `scapy`, `requests`, `nmap`, `metasploit`
- **Topics:** `cybersecurity`, `penetration-testing`, `security-tools`, `vulnerability-scanner`

**Examples:**
- Metasploit Framework
- Burp Suite alternatives
- Password managers
- Security scanners
- Cryptographic libraries

---

### 3. 🎨 UI/UX
**Description:** Frontend frameworks, component libraries, design systems, and UI toolkits.

**Classification Criteria:**
- **Keywords:** `ui`, `ux`, `design-system`, `components`, `frontend`, `css-framework`, `tailwind`, `bootstrap`, `material-design`, `accessibility`, `responsive`
- **Languages:** JavaScript, TypeScript, CSS, HTML
- **Dependencies:** `react`, `vue`, `svelte`, `tailwindcss`, `styled-components`, `emotion`, `framer-motion`
- **Topics:** `ui`, `ux`, `design-system`, `component-library`, `frontend-framework`

**Examples:**
- Shadcn/ui
- Radix UI
- Chakra UI
- Tailwind CSS plugins
- Design system starters

---

### 4. 🌐 Web Frameworks
**Description:** Full-stack frameworks, backend frameworks, and web application builders.

**Classification Criteria:**
- **Keywords:** `web-framework`, `backend`, `api`, `rest`, `graphql`, `server`, `middleware`, `routing`, `express`, `fastapi`, `django`, `flask`, `nest`, `next`
- **Languages:** JavaScript, TypeScript, Python, Go, Rust, Ruby
- **Dependencies:** `express`, `fastapi`, `django`, `flask`, `next`, `nest`, `gin`, `actix-web`
- **Topics:** `web-framework`, `backend`, `api`, `rest-api`, `graphql`

**Examples:**
- Next.js
- FastAPI
- NestJS
- Remix
- Fresh (Deno)

---

### 5. 🗄️ Databases & Data
**Description:** Database systems, ORMs, data processing tools, ETL pipelines, and analytics platforms.

**Classification Criteria:**
- **Keywords:** `database`, `orm`, `sql`, `nosql`, `postgresql`, `mongodb`, `redis`, `etl`, `data-pipeline`, `analytics`, `data-warehouse`, `query-builder`
- **Languages:** Any (database-specific)
- **Dependencies:** `sqlalchemy`, `prisma`, `mongoose`, `sequelize`, `typeorm`, `pandas`, `dask`
- **Topics:** `database`, `orm`, `sql`, `nosql`, `data-processing`

**Examples:**
- Prisma
- Supabase
- DuckDB
- Apache Superset
- SQLAlchemy

---

### 6. ⚙️ DevOps & Infrastructure
**Description:** CI/CD tools, containerization, orchestration, monitoring, and infrastructure-as-code.

**Classification Criteria:**
- **Keywords:** `devops`, `ci-cd`, `docker`, `kubernetes`, `k8s`, `terraform`, `ansible`, `monitoring`, `observability`, `logging`, `metrics`, `infrastructure`, `automation`
- **Languages:** Go, Python, Bash, YAML, HCL
- **Dependencies:** `docker`, `kubernetes`, `terraform`, `ansible`, `prometheus`, `grafana`
- **Topics:** `devops`, `ci-cd`, `docker`, `kubernetes`, `infrastructure-as-code`

**Examples:**
- GitHub Actions alternatives
- Docker Compose stacks
- Kubernetes operators
- Terraform modules
- Monitoring dashboards

---

### 7. 📱 Mobile Development
**Description:** Mobile app frameworks, native development tools, and cross-platform solutions.

**Classification Criteria:**
- **Keywords:** `mobile`, `android`, `ios`, `react-native`, `flutter`, `swift`, `kotlin`, `cross-platform`, `mobile-app`
- **Languages:** Dart, Swift, Kotlin, Java, JavaScript, TypeScript
- **Dependencies:** `react-native`, `flutter`, `expo`, `ionic`
- **Topics:** `mobile`, `android`, `ios`, `react-native`, `flutter`

**Examples:**
- React Native libraries
- Flutter packages
- Expo plugins
- Native UI components
- Mobile-first frameworks

---

### 8. 🧪 Testing & QA
**Description:** Testing frameworks, test automation tools, mocking libraries, and quality assurance platforms.

**Classification Criteria:**
- **Keywords:** `testing`, `test-automation`, `qa`, `unit-test`, `integration-test`, `e2e`, `playwright`, `cypress`, `jest`, `pytest`, `mock`, `stub`
- **Languages:** Any
- **Dependencies:** `jest`, `pytest`, `playwright`, `cypress`, `vitest`, `mocha`, `selenium`
- **Topics:** `testing`, `test-automation`, `qa`, `testing-framework`

**Examples:**
- Playwright
- Vitest
- Pytest plugins
- Testing utilities
- Mock servers

---

### 9. 📊 Analytics & Monitoring
**Description:** Analytics platforms, monitoring tools, dashboards, and observability solutions.

**Classification Criteria:**
- **Keywords:** `analytics`, `monitoring`, `observability`, `metrics`, `logging`, `tracing`, `dashboard`, `visualization`, `apm`, `error-tracking`
- **Languages:** Any
- **Dependencies:** `prometheus`, `grafana`, `sentry`, `datadog`, `newrelic`, `elasticsearch`
- **Topics:** `analytics`, `monitoring`, `observability`, `dashboard`

**Examples:**
- Plausible Analytics
- Umami
- Grafana dashboards
- Custom metrics collectors
- Log aggregators

---

### 10. 🛠️ Developer Tools
**Description:** CLI tools, code generators, linters, formatters, and productivity enhancers.

**Classification Criteria:**
- **Keywords:** `cli`, `developer-tools`, `code-generator`, `linter`, `formatter`, `productivity`, `automation`, `tooling`, `utility`, `helper`
- **Languages:** Any
- **Dependencies:** Varies widely
- **Topics:** `developer-tools`, `cli`, `productivity`, `automation`

**Examples:**
- CLI frameworks
- Code generators
- Git tools
- Terminal utilities
- Editor extensions

---

## Classification Algorithm

### Multi-Signal Scoring System
Each repository receives a score (0-100) for each category based on multiple signals:

1. **Primary Language Match** (30 points)
2. **Dependencies Analysis** (25 points)
3. **Topics/Tags Match** (20 points)
4. **Keywords in Description** (15 points)
5. **README Content Analysis** (10 points)

**Assignment Rules:**
- Repository assigned to category with **highest score**
- Minimum threshold: **40 points** (otherwise assigned to "Other")
- If multiple categories score >70, repository tagged with multiple categories

### Implementation Pseudocode
```python
def classify_repository(repo_data: dict) -> list[str]:
    scores = {category: 0 for category in CATEGORIES}

    # Signal 1: Language analysis
    language = repo_data.get("language", "").lower()
    for category, criteria in TAXONOMY.items():
        if language in criteria["languages"]:
            scores[category] += 30

    # Signal 2: Dependencies (from package files)
    dependencies = extract_dependencies(repo_data)
    for dep in dependencies:
        for category, criteria in TAXONOMY.items():
            if dep in criteria["dependencies"]:
                scores[category] += 25
                break

    # Signal 3: Topics/tags
    topics = repo_data.get("topics", [])
    for topic in topics:
        for category, criteria in TAXONOMY.items():
            if topic in criteria["topics"]:
                scores[category] += 20
                break

    # Signal 4: Description keywords
    description = repo_data.get("description", "").lower()
    for category, criteria in TAXONOMY.items():
        for keyword in criteria["keywords"]:
            if keyword in description:
                scores[category] += 15
                break

    # Signal 5: README analysis
    readme = fetch_readme(repo_data["full_name"])
    for category, criteria in TAXONOMY.items():
        if any(kw in readme.lower() for kw in criteria["keywords"]):
            scores[category] += 10
            break

    # Assign categories
    categories = []
    max_score = max(scores.values())

    if max_score >= 40:
        # Primary category
        primary = max(scores, key=scores.get)
        categories.append(primary)

        # Secondary categories (if score > 70)
        for cat, score in scores.items():
            if cat != primary and score > 70:
                categories.append(cat)
    else:
        categories.append("Other")

    return categories
```

---

## Real vs Mock Project Detection

### Signals for Production Readiness

#### High-Confidence Signals (Real Project)
1. **Package Downloads** (npm/PyPI/Docker Hub)
   - npm: >1000 weekly downloads
   - PyPI: >500 monthly downloads
   - Docker Hub: >1000 pulls

2. **Dependents Count**
   - GitHub dependents: >10 repositories

3. **Contributors**
   - >5 unique contributors
   - Regular commit activity (>1 commit/week average)

4. **Release History**
   - Semantic versioning (v1.0+)
   - Regular releases (>3 in last year)
   - Changelog present

5. **Issue/PR Activity**
   - Active issue responses (<7 days median response time)
   - Merged PRs from external contributors
   - Issue labels and project boards

6. **Documentation Quality**
   - README >2000 characters
   - Wiki or docs site
   - API documentation
   - Examples/demos

#### Mock/Tutorial Indicators
1. **Single contributor** with no external PRs
2. **No releases** or versioning
3. **Zero npm/PyPI downloads** (if package exists)
4. **"Tutorial" or "Example" in name/description**
5. **No CI/CD** configuration
6. **Last commit >1 year ago** with <10 total commits

### Production Readiness Score
Formula: `(downloads_score * 0.3) + (contributors_score * 0.2) + (activity_score * 0.2) + (docs_score * 0.15) + (community_score * 0.15)`

**Score Interpretation:**
- **80-100:** Production-ready, widely adopted
- **60-79:** Stable, moderate adoption
- **40-59:** Early stage, some adoption
- **20-39:** Experimental, minimal adoption
- **0-19:** Tutorial/mock/abandoned

---

## UI Representation

### Category Badges
```html
<span class="category-badge ai-ml">🤖 AI/ML</span>
<span class="category-badge security">🔒 Security</span>
<span class="category-badge ui-ux">🎨 UI/UX</span>
```

### Production Ready Indicator
```html
<div class="production-score" data-score="85">
  <div class="score-circle">
    <svg viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="45" class="score-bg"/>
      <circle cx="50" cy="50" r="45" class="score-fill"
              stroke-dasharray="282" stroke-dashoffset="42"/>
    </svg>
    <span class="score-text">85%</span>
  </div>
  <span class="score-label">Production Ready</span>
</div>
```

### Category Filter UI
```html
<div class="category-filters">
  <button class="filter-btn active" data-category="all">All (47)</button>
  <button class="filter-btn" data-category="ai-ml">🤖 AI/ML (12)</button>
  <button class="filter-btn" data-category="security">🔒 Security (8)</button>
  <button class="filter-btn" data-category="ui-ux">🎨 UI/UX (15)</button>
  <!-- ... more categories -->
</div>
```

---

## Next Steps
1. ✅ **Design taxonomy** (this document)
2. ⚪ **Implement `category_detector.py`** with classification algorithm
3. ⚪ **Implement `repo_classifier.py`** with production readiness scoring
4. ⚪ **Integrate with `workflow_generate_blog.py`**
5. ⚪ **Update blog templates** with category badges and filters
6. ⚪ **Create category index page** with statistics
7. ⚪ **Add category-based navigation** to blog
