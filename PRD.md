# Options Strategy Research Assistant - Product Requirements Document

> **Version**: 1.1  
> **Last Updated**: December 30, 2024  
> **Status**: Approved - Ready for Implementation

---

## Decisions Log

| Decision | Choice | Date |
|----------|--------|------|
| MVP Strategy | SPX/SPY Put Credit Spreads | Dec 30, 2024 |
| Tech Stack | Option C: Vite + React + Python Backend | Dec 30, 2024 |
| Reddit Extraction | Full post + comments | Dec 30, 2024 |
| Source Discovery | Semi-automated (suggest → approve → extract) | Dec 30, 2024 |
| Storage | SQLite (backend) | Dec 30, 2024 |
| Timeline | Accelerated (2 weeks for MVP) | Dec 30, 2024 |
| **YouTube Live Search** | YouTube Data API v3 with quality scoring | Jan 1, 2025 |

---

## Executive Summary

Build a web-based research assistant for intermediate/advanced options traders that surfaces actionable, specific, data-backed strategy insights from multiple sources—cutting through the noise to help traders improve their ROI.

### Core Value Proposition

> "The tool that separates signal from noise in options education content."

### Target User

- **Primary**: Intermediate to advanced options trader
- **Goals**: Looking for new strategies to improve ROI
- **Pain Points**: Information overload, inconsistent quality, vague advice

---

## MVP Strategy: SPX/SPY Put Credit Spreads ✅

**Rationale**:
- High specificity (DTE, delta, width are concrete parameters)
- Active intermediate/advanced discussion on Reddit and YouTube
- Good backtest data availability (SPX has options data)
- POC already successfully extracted real data from this strategy
- Defined risk appeals to smaller accounts

**Expansion Path**: Wheel Strategy → Iron Condor → PMCC

---

## Tech Stack: Vite + React + Python Backend ✅

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  Vite + React + TypeScript                                      │
│  (Fast builds, React productivity, type safety)                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │ fetch() / REST API
┌──────────────────────────────▼──────────────────────────────────┐
│                      PYTHON BACKEND                             │
│  FastAPI                                                        │
│  • YouTube Transcript API (youtube-transcript-api)              │
│  • Gemini LLM extraction (google-generativeai)                  │
│  • Reddit API (PRAW) - posts + comments                         │
│  • Web scraping (requests/BeautifulSoup)                        │
│  • SQLite for local persistence                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
/strategy-finder
├── /frontend                    # Vite + React app
│   ├── /src
│   │   ├── /components          # React components
│   │   ├── /hooks               # Custom hooks
│   │   ├── /services            # API client
│   │   ├── /types               # TypeScript types
│   │   ├── /styles              # CSS
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── /backend                     # Python FastAPI
│   ├── /app
│   │   ├── /api                 # API routes
│   │   ├── /extractors          # YouTube, Reddit, Article extractors
│   │   ├── /synthesis           # Aggregation, consensus logic
│   │   ├── /scoring             # Specificity score
│   │   ├── /discovery           # Source discovery
│   │   ├── /models              # Pydantic models
│   │   └── main.py
│   ├── /tests                   # pytest tests
│   ├── requirements.txt
│   └── pytest.ini
│
└── README.md
```

---

## Feature Specifications

### P0: Core Features (MVP)

#### 1. URL Extraction
**Description**: User pastes a YouTube, Reddit, or article URL. System extracts structured strategy data.

**Supported Sources**:
| Source | Method | Includes |
|--------|--------|----------|
| YouTube | youtube-transcript-api | Full transcript |
| Reddit | PRAW API | Post + all comments |
| Article | BeautifulSoup | Main content |

**Extraction Schema**:
```typescript
interface Source {
  id: string;
  url: string;
  type: 'youtube' | 'reddit' | 'article';
  title: string;
  author: string;
  published_date: string;
  platform_metrics: {
    views?: number;
    likes?: number;
    upvotes?: number;
    comments?: number;
  };
  transcript_or_content: string;
  comment_content?: string;  // For Reddit posts
  extracted_data: ExtractedStrategy;
  quality_metrics: QualityMetrics;
  created_at: string;
  updated_at: string;
}
```

---

#### 2. Specificity Score

**Scoring Rubric** (1-10 scale):

| Criterion | Weight | Score 1 | Score 5 | Score 10 |
|-----------|--------|---------|---------|----------|
| Strike Selection | 15% | "OTM" | "16 delta" | "16 delta, 10pt wide" |
| Entry Criteria | 15% | "When I feel like it" | "On pullbacks" | "20 EMA pullback >1%" |
| DTE | 10% | "Short term" | "Weekly" | "5-7 DTE on Tuesdays" |
| Position Sizing | 15% | "Appropriate size" | "1-3 contracts" | "5% of account per trade" |
| Profit Target | 10% | "When it's profitable" | "50% profit" | "Exit at 50% or 21 DTE" |
| Stop Loss | 15% | Not mentioned | "Cut losers" | "Exit at -100% of credit" |
| Real P&L Data | 10% | None | "Made money" | "$3.2K→$12K verified" |
| Backtest/Evidence | 10% | None | Anecdotal | Backtested 2 years |

---

#### 3. Consensus View

Aggregate multiple sources, showing:
- **Agreements**: Topics where all/most sources align
- **Controversies**: Topics where sources disagree, with rationale for each position
- **Source counts**: How many sources support each position

---

#### 4. Source Discovery (Semi-Automated)

**Flow**:
1. User enters search query
2. System searches YouTube, Reddit, curated sites
3. System filters and ranks candidates
4. User reviews and selects which to extract
5. Full extraction runs on selected sources

---

## Test Cases & Automated Testing

### Testing Strategy

| Test Type | Tool | Coverage Target |
|-----------|------|-----------------|
| Unit Tests | pytest | 80% backend code |
| Integration Tests | pytest | All API endpoints |
| Component Tests | Vitest + React Testing Library | Key UI components |
| E2E Tests | Playwright | Critical user flows |

---

### Backend Test Cases

#### 1. YouTube Transcript Extraction Tests

```python
# File: backend/tests/test_youtube_extractor.py

class TestYouTubeExtractor:
    """Tests for YouTube transcript extraction."""
    
    # TC-YT-001: Valid video with English captions
    def test_extract_valid_video_with_captions(self):
        """Given a valid YouTube URL with English captions,
        When extract_transcript is called,
        Then it returns the full transcript text."""
        url = "https://youtu.be/55ox9fB3x-E"
        result = extract_transcript(url)
        assert result.success is True
        assert len(result.transcript) > 1000
        assert result.language == "en"
    
    # TC-YT-002: Video without captions
    def test_extract_video_without_captions(self):
        """Given a YouTube URL without captions,
        When extract_transcript is called,
        Then it returns an error with descriptive message."""
        url = "https://youtu.be/no_captions_video"
        result = extract_transcript(url)
        assert result.success is False
        assert "no transcript" in result.error.lower()
    
    # TC-YT-003: Invalid YouTube URL
    def test_extract_invalid_url(self):
        """Given an invalid URL,
        When extract_transcript is called,
        Then it returns a validation error."""
        url = "https://example.com/not-youtube"
        result = extract_transcript(url)
        assert result.success is False
        assert "invalid" in result.error.lower()
    
    # TC-YT-004: Private/deleted video
    def test_extract_private_video(self):
        """Given a private or deleted video URL,
        When extract_transcript is called,
        Then it returns an appropriate error."""
        url = "https://youtu.be/deleted_video_id"
        result = extract_transcript(url)
        assert result.success is False
    
    # TC-YT-005: Video ID extraction from various URL formats
    @pytest.mark.parametrize("url,expected_id", [
        ("https://youtu.be/55ox9fB3x-E", "55ox9fB3x-E"),
        ("https://www.youtube.com/watch?v=55ox9fB3x-E", "55ox9fB3x-E"),
        ("https://youtube.com/watch?v=55ox9fB3x-E&t=120", "55ox9fB3x-E"),
    ])
    def test_extract_video_id_from_url(self, url, expected_id):
        """Given various YouTube URL formats,
        When extract_video_id is called,
        Then it correctly extracts the video ID."""
        assert extract_video_id(url) == expected_id
```

---

#### 2. Reddit Extraction Tests

```python
# File: backend/tests/test_reddit_extractor.py

class TestRedditExtractor:
    """Tests for Reddit post + comment extraction."""
    
    # TC-RD-001: Valid Reddit post with comments
    def test_extract_valid_post_with_comments(self):
        """Given a valid Reddit post URL,
        When extract_reddit_post is called,
        Then it returns post content and all comments."""
        url = "https://www.reddit.com/r/thetagang/comments/abc123"
        result = extract_reddit_post(url)
        assert result.success is True
        assert result.post_title is not None
        assert result.post_body is not None
        assert len(result.comments) > 0
    
    # TC-RD-002: Post without comments
    def test_extract_post_without_comments(self):
        """Given a Reddit post with no comments,
        When extract_reddit_post is called,
        Then it returns post content with empty comments list."""
        result = extract_reddit_post(url_with_no_comments)
        assert result.success is True
        assert result.comments == []
    
    # TC-RD-003: Deleted/removed post
    def test_extract_deleted_post(self):
        """Given a deleted Reddit post URL,
        When extract_reddit_post is called,
        Then it returns an error."""
        result = extract_reddit_post(deleted_url)
        assert result.success is False
    
    # TC-RD-004: Comment threading preserved
    def test_comment_threading(self):
        """Given a Reddit post with nested comments,
        When extract_reddit_post is called,
        Then comment hierarchy is preserved."""
        result = extract_reddit_post(url_with_nested_comments)
        assert any(c.replies for c in result.comments if c.replies)
    
    # TC-RD-005: Upvote counts captured
    def test_upvote_metrics(self):
        """Given a Reddit post,
        When extract_reddit_post is called,
        Then upvote counts are captured for post and top comments."""
        result = extract_reddit_post(url)
        assert result.post_upvotes is not None
        assert result.comments[0].upvotes is not None
```

---

#### 3. LLM Strategy Extraction Tests

```python
# File: backend/tests/test_llm_extraction.py

class TestLLMExtraction:
    """Tests for Gemini LLM strategy extraction."""
    
    # TC-LLM-001: Extract strategy from transcript
    def test_extract_strategy_from_transcript(self):
        """Given a transcript containing strategy information,
        When extract_strategy is called,
        Then it returns structured strategy data."""
        transcript = load_fixture("robert_mcintosh_transcript.txt")
        result = extract_strategy(transcript)
        assert result.strategy_name is not None
        assert result.setup_rules is not None
        assert result.management_rules is not None
    
    # TC-LLM-002: Handle transcript with no strategy
    def test_extract_no_strategy_content(self):
        """Given a transcript without strategy content,
        When extract_strategy is called,
        Then it returns appropriate indication."""
        transcript = "This is just general market commentary with no strategy."
        result = extract_strategy(transcript)
        assert result.strategy_name is None or result.confidence < 0.3
    
    # TC-LLM-003: Extract specific parameters
    def test_extract_specific_parameters(self):
        """Given a transcript with specific numbers,
        When extract_strategy is called,
        Then numeric parameters are correctly extracted."""
        transcript = "I sell 5-7 DTE put spreads, ATM, 10 points wide"
        result = extract_strategy(transcript)
        assert result.setup_rules.dte_range == [5, 7]
        assert "10" in str(result.setup_rules.strike_selection)
    
    # TC-LLM-004: Extract performance claims
    def test_extract_performance_claims(self):
        """Given a transcript with P&L data,
        When extract_strategy is called,
        Then performance data is extracted."""
        transcript = "Started with $3,200 and grew to $12,000 in 9 months"
        result = extract_strategy(transcript)
        assert result.performance_claims.starting_capital == 3200
        assert result.performance_claims.ending_capital == 12000
    
    # TC-LLM-005: JSON output validity
    def test_extraction_returns_valid_json(self):
        """Given any transcript,
        When extract_strategy is called,
        Then output is valid JSON matching schema."""
        result = extract_strategy(sample_transcript)
        # Should not raise
        validated = ExtractedStrategy.model_validate(result)
        assert validated is not None
```

---

#### 4. Specificity Scoring Tests

```python
# File: backend/tests/test_specificity_scoring.py

class TestSpecificityScoring:
    """Tests for specificity score calculation."""
    
    # TC-SS-001: High specificity content
    def test_high_specificity_score(self):
        """Given extraction with all specific parameters,
        When calculate_specificity is called,
        Then score is >= 8."""
        extraction = create_extraction(
            strike_selection="ATM, 10pt wide",
            dte="5-7 DTE",
            entry_criteria="20 EMA pullback > 1%",
            profit_target="Exit at 50%",
            stop_loss="-100% of credit",
            has_pnl=True,
            has_backtest=True
        )
        score = calculate_specificity(extraction)
        assert score >= 8
    
    # TC-SS-002: Low specificity content
    def test_low_specificity_score(self):
        """Given extraction with vague parameters,
        When calculate_specificity is called,
        Then score is <= 4."""
        extraction = create_extraction(
            strike_selection="OTM",
            dte="short term",
            entry_criteria=None,
            profit_target=None,
            stop_loss=None,
            has_pnl=False,
            has_backtest=False
        )
        score = calculate_specificity(extraction)
        assert score <= 4
    
    # TC-SS-003: Score breakdown provided
    def test_score_breakdown(self):
        """Given any extraction,
        When calculate_specificity is called,
        Then breakdown by criterion is provided."""
        result = calculate_specificity_with_breakdown(extraction)
        assert "strike_selection" in result.breakdown
        assert "entry_criteria" in result.breakdown
        assert all(0 <= v <= 10 for v in result.breakdown.values())
    
    # TC-SS-004: Gap detection
    def test_gap_detection(self):
        """Given extraction with missing fields,
        When calculate_specificity is called,
        Then gaps are identified."""
        extraction = create_extraction(stop_loss=None)
        result = calculate_specificity_with_breakdown(extraction)
        assert "stop_loss" in result.gaps
    
    # TC-SS-005: Score consistency
    def test_score_consistency(self):
        """Given the same extraction,
        When calculate_specificity is called multiple times,
        Then score is consistent."""
        scores = [calculate_specificity(same_extraction) for _ in range(5)]
        assert len(set(scores)) == 1
```

---

#### 5. Consensus View Tests

```python
# File: backend/tests/test_consensus.py

class TestConsensusView:
    """Tests for multi-source synthesis."""
    
    # TC-CV-001: Agreement detection
    def test_detect_agreement(self):
        """Given sources that agree on a topic,
        When synthesize_consensus is called,
        Then agreement is detected."""
        sources = [
            create_source(underlying="SPX"),
            create_source(underlying="SPX"),
            create_source(underlying="SPX"),
        ]
        result = synthesize_consensus(sources)
        underlying_item = find_item(result.consensus, "underlying")
        assert underlying_item.agreement_rate == 1.0
    
    # TC-CV-002: Disagreement detection
    def test_detect_disagreement(self):
        """Given sources that disagree on a topic,
        When synthesize_consensus is called,
        Then controversy is flagged with positions."""
        sources = [
            create_source(dte="5-7"),
            create_source(dte="30-45"),
            create_source(dte="30-45"),
        ]
        result = synthesize_consensus(sources)
        dte_controversy = find_controversy(result, "dte")
        assert len(dte_controversy.positions) == 2
        assert dte_controversy.positions[0].source_count == 1
        assert dte_controversy.positions[1].source_count == 2
    
    # TC-CV-003: Source attribution
    def test_source_attribution(self):
        """Given synthesized consensus,
        When rendered,
        Then each position cites its sources."""
        result = synthesize_consensus(sources)
        for item in result.consensus:
            assert item.sources is not None
            assert len(item.sources) > 0
    
    # TC-CV-004: Empty sources handling
    def test_empty_sources(self):
        """Given an empty source list,
        When synthesize_consensus is called,
        Then empty result is returned gracefully."""
        result = synthesize_consensus([])
        assert result.sources_analyzed == 0
        assert result.consensus == []
```

---

#### 6. API Endpoint Tests

```python
# File: backend/tests/test_api.py

class TestAPIEndpoints:
    """Integration tests for API endpoints."""
    
    # TC-API-001: POST /api/extract - YouTube
    def test_extract_youtube(self, client):
        """POST /api/extract with YouTube URL returns extracted data."""
        response = client.post("/api/extract", json={
            "url": "https://youtu.be/55ox9fB3x-E"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["source"]["type"] == "youtube"
        assert data["source"]["extracted_data"] is not None
    
    # TC-API-002: POST /api/extract - Reddit
    def test_extract_reddit(self, client):
        """POST /api/extract with Reddit URL returns post + comments."""
        response = client.post("/api/extract", json={
            "url": "https://reddit.com/r/thetagang/comments/xyz"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["source"]["type"] == "reddit"
        assert data["source"]["comment_content"] is not None
    
    # TC-API-003: POST /api/extract - Invalid URL
    def test_extract_invalid_url(self, client):
        """POST /api/extract with invalid URL returns 400."""
        response = client.post("/api/extract", json={
            "url": "not-a-valid-url"
        })
        assert response.status_code == 400
    
    # TC-API-004: POST /api/discover
    def test_discover_sources(self, client):
        """POST /api/discover returns ranked source candidates."""
        response = client.post("/api/discover", json={
            "query": "SPX put credit spread",
            "sources": ["youtube", "reddit"]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["candidates"]) > 0
        assert all("quality_tier" in c for c in data["candidates"])
    
    # TC-API-005: GET /api/strategies
    def test_get_strategies(self, client):
        """GET /api/strategies returns all aggregated strategies."""
        response = client.get("/api/strategies")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
    
    # TC-API-006: POST /api/strategies/:id/synthesize
    def test_synthesize_strategy(self, client):
        """POST /api/strategies/:id/synthesize creates consensus view."""
        response = client.post("/api/strategies/spx-put-spreads/synthesize", json={
            "source_ids": ["source1", "source2", "source3"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "consensus" in data["strategy"]
```

---

### Frontend Test Cases

#### Component Tests (Vitest + React Testing Library)

```typescript
// File: frontend/src/components/__tests__/SourceCard.test.tsx

describe('SourceCard', () => {
  // TC-UI-001: Renders source information
  it('displays source title, author, and metrics', () => {
    render(<SourceCard source={mockSource} />);
    expect(screen.getByText('ATM Put Spreads Strategy')).toBeInTheDocument();
    expect(screen.getByText('Robert McIntosh')).toBeInTheDocument();
    expect(screen.getByText('125K views')).toBeInTheDocument();
  });

  // TC-UI-002: Shows specificity score
  it('displays specificity score with visual indicator', () => {
    render(<SourceCard source={{...mockSource, specificityScore: 8}} />);
    expect(screen.getByText('8/10')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '8');
  });

  // TC-UI-003: Clicking opens detail view
  it('expands to show full extraction on click', async () => {
    render(<SourceCard source={mockSource} />);
    await userEvent.click(screen.getByText('View Details'));
    expect(screen.getByText('Setup Rules')).toBeInTheDocument();
    expect(screen.getByText('Management Rules')).toBeInTheDocument();
  });
});

// File: frontend/src/components/__tests__/ConsensusView.test.tsx

describe('ConsensusView', () => {
  // TC-UI-004: Shows agreement items
  it('displays items with high agreement', () => {
    render(<ConsensusView data={mockConsensus} />);
    expect(screen.getByText('Underlying: SPX')).toBeInTheDocument();
    expect(screen.getByText('100% agree')).toBeInTheDocument();
  });

  // TC-UI-005: Shows controversy section
  it('displays controversies with multiple positions', () => {
    render(<ConsensusView data={mockConsensusWithControversy} />);
    expect(screen.getByText('DTE Selection')).toBeInTheDocument();
    expect(screen.getByText('5-7 DTE')).toBeInTheDocument();
    expect(screen.getByText('30-45 DTE')).toBeInTheDocument();
  });
});
```

---

### E2E Test Cases (Playwright)

```typescript
// File: e2e/extraction.spec.ts

test.describe('Source Extraction Flow', () => {
  // TC-E2E-001: Extract YouTube video
  test('user can extract strategy from YouTube video', async ({ page }) => {
    await page.goto('/');
    await page.fill('[data-testid="url-input"]', 'https://youtu.be/55ox9fB3x-E');
    await page.click('[data-testid="extract-button"]');
    
    // Wait for extraction
    await expect(page.getByText('Extracting...')).toBeVisible();
    await expect(page.getByText('Put Credit Spreads')).toBeVisible({ timeout: 30000 });
    
    // Verify specificity score shown
    await expect(page.getByTestId('specificity-score')).toContainText('/10');
  });

  // TC-E2E-002: Extract Reddit post
  test('user can extract strategy from Reddit post', async ({ page }) => {
    await page.goto('/');
    await page.fill('[data-testid="url-input"]', 'https://reddit.com/r/thetagang/...');
    await page.click('[data-testid="extract-button"]');
    
    await expect(page.getByText('strategy data')).toBeVisible({ timeout: 30000 });
    // Verify comments were captured
    await expect(page.getByText('comments analyzed')).toBeVisible();
  });

  // TC-E2E-003: View consensus
  test('user can view consensus across multiple sources', async ({ page }) => {
    // Pre-populate with multiple sources
    await page.goto('/strategies/spx-put-spreads');
    
    await expect(page.getByText('sources analyzed')).toBeVisible();
    await expect(page.getByTestId('consensus-section')).toBeVisible();
    await expect(page.getByTestId('controversy-section')).toBeVisible();
  });

  // TC-E2E-004: Source discovery
  test('user can discover and select sources', async ({ page }) => {
    await page.goto('/');
    await page.fill('[data-testid="search-input"]', 'SPX put credit spreads');
    await page.click('[data-testid="discover-button"]');
    
    // Wait for discovery results
    await expect(page.getByText('sources found')).toBeVisible({ timeout: 15000 });
    
    // Select sources
    await page.click('[data-testid="source-checkbox-0"]');
    await page.click('[data-testid="source-checkbox-1"]');
    await page.click('[data-testid="extract-selected-button"]');
    
    await expect(page.getByText('Extracting 2 sources')).toBeVisible();
  });
});
```

---

## Implementation Phases (Granular Tasks)

### Phase 1: Foundation (Week 1)

#### 1.1 Project Setup
- [x] Initialize Vite + React project with TypeScript
- [x] Set up ESLint, Prettier, Husky for code quality
- [x] Create folder structure per architecture spec
- [x] Initialize Python FastAPI project
- [x] Set up pytest with fixtures and conftest
- [x] Configure CORS for frontend-backend communication
- [x] Create docker-compose for local development
- [x] Set up environment variable management (.env files)

#### 1.2 YouTube Extraction Pipeline
- [x] Create `YouTubeExtractor` class
- [x] Implement video ID extraction from URL variants
- [x] Integrate youtube-transcript-api library
- [x] Handle error cases (no captions, private video, etc.)
- [x] Add language fallback logic (en → en-US → auto)
- [x] Write unit tests (TC-YT-001 through TC-YT-005)
- [x] Create extraction result Pydantic models

#### 1.3 Reddit Extraction Pipeline
- [x] Create `RedditExtractor` class
- [x] Set up PRAW with app credentials
- [x] Implement post content extraction
- [x] Implement comment tree extraction (flatten + preserve context)
- [x] Handle deleted/removed posts gracefully
- [x] Capture upvote counts for post and comments
- [x] Write unit tests (TC-RD-001 through TC-RD-005)
- [x] Create Reddit-specific Pydantic models

#### 1.4 Article Extraction Pipeline
- [x] Create `ArticleExtractor` class
- [x] Implement URL fetching with proper headers
- [x] Use BeautifulSoup for content extraction
- [x] Handle common article layouts (Substack, WordPress, etc.)
- [x] Extract title, author, date metadata
- [x] Strip ads, nav, footer content
- [x] Write basic unit tests

#### 1.5 LLM Strategy Extraction
- [x] Create `StrategyExtractor` class using Gemini
- [x] Design extraction prompt template
- [x] Implement JSON parsing and validation
- [x] Add retry logic for rate limits
- [x] Handle partial/failed extractions gracefully
- [x] Write unit tests (TC-LLM-001 through TC-LLM-005)

#### 1.6 API Endpoints (Basic)
- [x] Create POST `/api/extract` endpoint
- [x] Add URL validation middleware
- [x] Route to appropriate extractor based on URL
- [x] Return standardized response format
- [x] Add request/response logging
- [x] Write integration tests (TC-API-001 through TC-API-003)

#### 1.7 Basic Frontend UI
- [x] Create dark mode CSS theme (color palette)
- [x] Build `Header` component with logo
- [x] Build `URLInput` component with validation
- [x] Build `ExtractButton` with loading state
- [x] Build `SourceCard` component (collapsed view)
- [x] Build `SourceDetail` component (expanded view)
- [x] Connect to backend API
- [x] Add basic error handling UI

---

### Phase 2: MVP Features (Weeks 2-3)

#### 2.1 Specificity Scoring
- [x] Create `SpecificityScorer` class
- [x] Implement scoring rubric (8 criteria)
- [x] Calculate weighted score (1-10)
- [x] Generate score breakdown by criterion
- [x] Identify and list gaps
- [x] Write unit tests (TC-SS-001 through TC-SS-005)
- [x] Add score to extraction output

#### 2.2 Specificity Score UI
- [x] Build `SpecificityScore` component (visual bar)
- [x] Build `ScoreBreakdown` component (detailed view)
- [x] Build `GapsList` component with icons
- [x] Integrate into `SourceCard` and `SourceDetail`
- [ ] Write component tests (TC-UI-002)

#### 2.3 Source Discovery - Backend
- [x] Create `SourceDiscovery` class
- [x] Integrate YouTube Data API for search ✅ **(Jan 1, 2025)**
- [ ] Integrate Reddit search (via PRAW)
- [x] Create curated site list (thetaprofits.com, etc.)
- [x] Implement quality filters (recency, engagement, etc.)
- [ ] Implement quick LLM specificity scan
- [x] Rank and tier candidates (high/medium/low)
- [x] Create POST `/api/discover` endpoint
- [x] Write integration tests (TC-API-004)

#### 2.4 Source Discovery - Frontend
- [x] Build `DiscoveryModal` component
- [x] Build `SearchInput` with suggestions
- [x] Build `CandidateList` with checkboxes
- [x] Build `QualityTierBadge` component
- [x] Implement batch selection
- [x] Add "Extract Selected" button with progress
- [ ] Write component tests

#### 2.5 Consensus View - Backend
- [x] Create `ConsensusSynthesizer` class
- [x] Implement topic extraction from sources
- [x] Calculate agreement rates per topic
- [x] Detect controversies (low agreement)
- [x] Group sources by position
- [x] Provide source attribution
- [x] Create GET `/api/strategies/:id` endpoint
- [x] Create POST `/api/strategies/:id/synthesize` endpoint
- [ ] Write unit tests (TC-CV-001 through TC-CV-004)
- [ ] Write integration tests (TC-API-005, TC-API-006)

#### 2.6 Consensus View - Frontend
- [x] Build `ConsensusView` component
- [x] Build `AgreementItem` component
- [x] Build `ControversySection` component
- [x] Build `SourceList` component (with links)
- [x] Build `StrategyDeepDive` page (implemented as `StrategyPage`)
- [x] Add navigation from home to strategy (React Router)
- [ ] Write component tests (TC-UI-004, TC-UI-005)

#### 2.7 Local Storage
- [ ] Set up IndexedDB with Dexie.js
- [x] Create source storage schema (SQLite backend)
- [x] Create strategy aggregate schema (SQLite backend)
- [x] Implement CRUD operations
- [ ] Add sync indicators in UI
- [ ] Handle storage quota errors

#### 2.8 Home Page
- [x] Build `HomePage` with search bar
- [x] Build `RecentResearch` list
- [x] Build `QuickActions` buttons
- [x] Implement search → discovery flow
- [x] Add empty state UI

#### 2.9 Polish & Responsive
- [x] Add micro-animations (hover, expand)
- [x] Add loading skeletons
- [x] Implement responsive breakpoints
- [ ] Test on mobile viewport
- [x] Add keyboard navigation
- [x] Add error toast notifications

---

### Phase 3: Enhancement (Week 4)

#### 3.1 Backtestability Assessment
- [x] Create `BacktestAssessor` class
- [x] Define parameter completeness check
- [x] Create platform knowledge base (tastytrade, etc.)
- [x] Match parameters to platform capabilities
- [x] Generate assessment output
- [ ] Write unit tests
- [x] Build `BacktestabilityCard` UI component

#### 3.2 What's Missing Checker
- [x] Define gap categories (entry, exit, sizing, etc.)
- [x] Enhance gap detection in `SpecificityScorer`
- [x] Provide suggestions per gap type
- [x] Build `MissingChecklist` UI component
- [x] Add "Find sources for this gap" action

#### 3.3 Export Functionality
- [x] Implement JSON export (full schema)
- [x] Implement Markdown export (readable digest)
- [x] Add export buttons to `StrategyDeepDive`
- [x] Add copy-to-clipboard option
- [ ] Write export format tests

#### 3.4 Expand Strategies
- [x] Add pre-curated sources for Wheel Strategy
- [x] Add pre-curated sources for Iron Condor
- [x] Test extraction pipeline on new content
- [x] Verify scoring works across strategies

#### 3.5 E2E Testing
- [x] Set up Playwright configuration
- [x] Write E2E tests (TC-E2E-001 through TC-E2E-004)
- [ ] Add to CI pipeline
- [x] Create test data fixtures

#### 3.6 Source Persistence ✅
- [x] Wire extraction API to save sources to SQLite database
- [x] Create GET `/api/sources` endpoint to list saved sources
- [x] Create GET `/api/sources/{id}` endpoint to retrieve single source
- [x] Create DELETE `/api/sources/{id}` endpoint to remove sources
- [x] Write unit tests for database operations

**Frontend Integration**:
- [x] Create `useSources` hook to fetch sources from `/api/sources` on app load
- [x] Update HomePage to display sources from API (not just local state)
- [x] Add loading state while fetching sources
- [x] Add "Delete Source" button with confirmation
- [x] Show empty state when no sources saved
- [x] Auto-refresh sources list after new extraction

**Schema** (already defined in `app/db/database.py`):
- `SourceDB`: stores extracted sources with JSON fields for extracted_data, quality_metrics
- `StrategyAggregateDB`: stores aggregated strategy analysis

**API Endpoints**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sources` | GET | List all saved sources with pagination |
| `/api/sources` | POST | Save a new source (called after extraction) |
| `/api/sources/{id}` | GET | Get single source by ID |
| `/api/sources/{id}` | DELETE | Remove a source |

---


### Phase 4: Production (Future)

#### 4.1 User Accounts
- [ ] Add authentication (Auth0 or Supabase)
- [ ] User-specific data isolation
- [ ] Session management

#### 4.2 Cloud Storage
- [ ] Migrate from IndexedDB to cloud DB
- [ ] Set up PostgreSQL or Supabase
- [ ] Data migration script

#### 4.3 Scheduled Refresh
- [ ] Create background job for source refresh
- [ ] Detect stale sources (>30 days)
- [ ] Re-extract and update scores

#### 4.4 Personal Fit Scoring
- [ ] Create user profile form
- [ ] Implement fit scoring algorithm
- [ ] Add fit score to strategy ranking

---

## Advanced Enhancements (User Feedback - Dec 30)

### 1. Market Context Enrichment

**Problem**: Strategies perform differently depending on market regime. A 2021 bull-market strategy ≠ 2024 strategy.

**Solution**: Enrich each source with market context at publication time.

```typescript
interface MarketContext {
  published_date: string;
  vix_level: number;           // VIX at publication
  vix_percentile: number;      // e.g., "VIX was in 25th percentile"
  spx_30d_trend: 'bullish' | 'bearish' | 'neutral';
  spx_30d_return: number;      // e.g., +3.2%
  regime_label: string;        // e.g., "Low Vol Bull", "High Vol Correction"
}
```

**Implementation**:
- Use CBOE VIX historical data API or Yahoo Finance
- Calculate SPX 30-day return from publication date
- Display badge: `"Published when VIX: 15.2 (Low Vol)"`

**Granular Tasks**:
- [ ] Create `MarketContextEnricher` class
- [ ] Integrate VIX historical data source
- [ ] Calculate regime labels
- [ ] Add `MarketContextBadge` UI component
- [ ] Add filter: "Show strategies from similar market conditions"

---

### 2. Survivorship Bias Detection

**Problem**: Most content is biased toward wins. Authors rarely discuss failure modes.

**Solution**: Add explicit "Failure Modes" extraction and penalize content that doesn't address losses.

```typescript
interface FailureModeAnalysis {
  failure_modes_mentioned: string[];  // e.g., "Gap down through strikes"
  discusses_losses: boolean;
  max_drawdown_mentioned: number | null;
  recovery_strategy: string | null;
  bias_score: number;  // 0-10, higher = more balanced
}
```

**Trust Score** (new metric):
| Factor | Weight | High Score | Low Score |
|--------|--------|------------|-----------|
| Discusses failures | 30% | Explicit loss examples | Only wins shown |
| Mentions drawdowns | 25% | Quantified drawdown | No mention |
| Shows losing trades | 25% | Real losing P&L | Cherry-picked |
| Balanced claims | 20% | "Works in X, fails in Y" | "Always works" |

**Granular Tasks**:
- [ ] Add `failure_modes` to extraction prompt
- [ ] Create `BiasAnalyzer` class
- [ ] Calculate Trust Score alongside Specificity Score
- [ ] Add `TrustScoreBadge` UI component
- [ ] Penalize Specificity Score if no failure modes mentioned

---

### 3. LLM Confidence & Source Quotes

**Problem**: Transcripts are ambiguous. "I usually go 30 days, but sometimes 45."

**Solution**: Add confidence scores and source quotes for each extracted field.

```typescript
interface ExtractedField<T> {
  value: T;
  confidence: number;           // 0.0-1.0
  source_quote: string;         // Exact quote from transcript
  interpretation: 'explicit' | 'implicit' | 'inferred';
}

interface ExtractedStrategy {
  strategy_name: ExtractedField<string>;
  setup_rules: {
    dte: ExtractedField<[number, number]>;  // e.g., { value: [30, 45], confidence: 0.7, source_quote: "usually 30 days, sometimes 45" }
    strike_selection: ExtractedField<string>;
    // ... etc
  };
  // ...
}
```

**Display**: Hover on any extracted value → show source quote + confidence bar.

**Granular Tasks**:
- [ ] Update extraction prompt to return confidence + quotes
- [ ] Update Pydantic models for `ExtractedField` wrapper
- [ ] Add `ConfidenceBadge` (green/yellow/red) UI
- [ ] Add tooltip with source quote on hover
- [ ] Filter option: "Only show high-confidence extractions"

---

### 4. Enhanced Specificity Rubric

**Updated Rubric** (adjusted for intermediate/advanced traders):

| Criterion | Weight | Score 1 | Score 5 | Score 10 |
|-----------|--------|---------|---------|----------|
| Strike Selection | 12% | "OTM" | "16 delta" | "16Δ, 10pt wide, $5 credit min" |
| Entry Criteria | 12% | "When I feel" | "On pullbacks" | "20 EMA pullback >1%, RSI <30" |
| DTE | 8% | "Short term" | "Weekly" | "5-7 DTE, enter Tuesdays" |
| Buying Power Effect | 12% | Not mentioned | "1-3 contracts" | "5% BPE per trade, max 25% total" |
| Profit Target | 8% | "Profitable" | "50%" | "Exit 50% OR 21 DTE, whichever first" |
| Stop Loss | 12% | Not mentioned | "Cut losers" | "-100% credit, or breach short strike" |
| **Adjustments/Defense** | 12% | Not mentioned | "I roll it" | "Roll for credit at 21 DTE, go inverted if challenged" |
| **Failure Modes** | 8% | Not mentioned | "Can lose" | "Gaps kill it, VIX spike = close early" |
| Real P&L Data | 8% | None | "Made money" | "$3.2K→$12K, 9mo, 73% win rate" |
| Backtest/Evidence | 8% | None | Anecdotal | "2-year backtest, 847 trades" |

**New Criteria Added**:
- **Adjustments/Defense**: Does author explain what to do if trade is challenged?
- **Failure Modes**: Does author explain when/how strategy loses?
- **Buying Power Effect**: Changed from "position sizing" to BPE (advanced trader focus)

---

### 5. Consensus Heatmap Visualization

**Instead of text-only consensus, add visual sliders**:

```
DTE Selection
├─ Short-term ─────────────────────────────── Monthly ─┤
   [A][B]                                        [C][D][E]
   
   A: Robert M (5 DTE)     C: tastytrade (30 DTE)
   B: AlphaCrunching (7)   D: Option Alpha (45 DTE)
                           E: SkyView (30 DTE)

Strike Selection  
├─ ATM ──────────────────────────────────────── Far OTM ─┤
   [A]                        [B][C][D]
```

**Implementation**:
- Normalize values to 0-100 scale for slider positioning
- Cluster sources that are close together
- Click source marker → jump to that source's detail

**Granular Tasks**:
- [ ] Create `ConsensusHeatmap` React component
- [ ] Implement value normalization for slider positioning
- [ ] Add source markers with tooltips
- [ ] Add click-to-navigate to source detail

---

### 6. Research Terminal UX

**Design Philosophy**: Bloomberg Terminal / TradingView aesthetic

**Typography**:
```css
/* Data points use monospace for scannability */
.data-value {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
}

/* Labels use sans-serif */
.data-label {
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}
```

**High-Density Layout Example**:
```
┌─────────────────────────────────────────────────────────────────────┐
│ SPX PUT CREDIT SPREADS            Spec: 7.8  Trust: 6.5  8 sources │
├──────────────────────┬──────────────────────┬───────────────────────┤
│ SETUP                │ MANAGEMENT           │ RISK                  │
├──────────────────────┼──────────────────────┼───────────────────────┤
│ UND    SPX           │ PROFIT   50% (4)     │ MAX LOSS  Width-Cr    │
│ DTE    30-45 (5)     │          100% (3)    │ WIN RATE  70-85%      │
│ DELTA  0.16 (4)      │ STOP     -100% (2)   │ DRAWDOWN  15-25%      │
│        ATM (2)       │          None (4)    │                       │
│ WIDTH  10pt (5)      │ ROLL     21 DTE (3)  │ ADJUST    Roll (4)    │
│        25pt (2)      │                      │           Close (3)   │
└──────────────────────┴──────────────────────┴───────────────────────┘
```

---

### 7. Side-by-Side Source Comparison

**Feature**: Select 2-3 sources, see table comparison.

```
┌────────────────────┬──────────────┬──────────────┬──────────────┐
│ Parameter          │ Robert M     │ tastytrade   │ AlphaCrunch  │
├────────────────────┼──────────────┼──────────────┼──────────────┤
│ DTE                │ 5-7          │ 30-45        │ 7            │
│ Delta              │ ATM (0.50)   │ 0.16         │ ATM          │
│ Width              │ 10 points    │ 10 points    │ 10 points    │
│ Profit Target      │ 100%         │ 50%          │ 50%          │
│ Stop Loss          │ None         │ -100%        │ -200%        │
│ Adjustments        │ Close/reopen │ Roll at 21   │ None         │
├────────────────────┼──────────────┼──────────────┼──────────────┤
│ Specificity        │ 8/10         │ 9/10         │ 8/10         │
│ Trust Score        │ 6/10         │ 8/10         │ 7/10         │
│ Market Context     │ VIX: 18      │ VIX: 22      │ VIX: 15      │
└────────────────────┴──────────────┴──────────────┴──────────────┘
```

**Granular Tasks**:
- [ ] Add multi-select checkbox to source cards
- [ ] Create `ComparisonModal` component
- [ ] Build comparison table with diff highlighting
- [ ] Highlight disagreements in red/amber

---

### 8. Interactive Backtest Export

**One-click copy for backtesting platforms**:

```json
// OptionOmega / Backtest.76 format
{
  "symbol": "SPX",
  "strategy": "PCS",
  "short_delta": 0.16,
  "long_width": 10,
  "dte": 30,
  "profit_target": 0.50,
  "stop_loss": -1.00,
  "entry_days": ["Monday", "Wednesday", "Friday"]
}
```

**UI**: Button in strategy detail → copies formatted JSON to clipboard.

**Granular Tasks**:
- [ ] Define export format per platform (OptionOmega, tastytrade, TOS)
- [ ] Create `BacktestExporter` utility
- [ ] Add "Copy for Backtest" button with format dropdown
- [ ] Show toast: "Copied! Paste into OptionOmega"

---

### 9. Technical Implementation Enhancements

#### 9.1 Gemini Structured Output

**Prompt Engineering**:
```python
EXTRACTION_PROMPT = """
[SYSTEM INSTRUCTION]
You are an expert options trading analyst. Extract structured data from transcripts.

CRITICAL RULES:
1. For each field, provide:
   - value: The extracted value
   - confidence: 0.0-1.0 based on how explicit the information is
   - source_quote: Exact quote from transcript (max 100 chars)
   - interpretation: "explicit" (directly stated), "implicit" (clearly implied), "inferred" (educated guess)

2. Distinguish:
   - EXPLICIT: "I trade 30 DTE" → { value: 30, confidence: 1.0, interpretation: "explicit" }
   - IMPLICIT: "Weekly options" → { value: 7, confidence: 0.9, interpretation: "implicit" }
   - INFERRED: "Short-term trades" → { value: [5, 14], confidence: 0.5, interpretation: "inferred" }

3. Always look for FAILURE MODES. If author only discusses wins, note bias_detected: true.

Return ONLY valid JSON matching the schema.
"""
```

#### 9.2 Long Transcript Chunking (Map-Reduce)

```python
async def extract_from_long_transcript(transcript: str) -> ExtractedStrategy:
    """Map-Reduce for transcripts > 20K tokens."""
    
    # Step 1: Chunk transcript (5K tokens each with 500 overlap)
    chunks = chunk_transcript(transcript, chunk_size=5000, overlap=500)
    
    # Step 2: Map - Extract strategy mentions from each chunk
    chunk_extractions = await asyncio.gather(*[
        extract_chunk(chunk, CHUNK_PROMPT) for chunk in chunks
    ])
    
    # Step 3: Reduce - Synthesize into master schema
    master_extraction = await synthesize_chunks(chunk_extractions, SYNTHESIS_PROMPT)
    
    return master_extraction
```

#### 9.3 Caching Layer

```python
# Redis or DiskCache for extraction results
from diskcache import Cache

cache = Cache('./extraction_cache')

@cache.memoize(expire=86400 * 7)  # Cache for 7 days
def extract_youtube(video_id: str) -> ExtractionResult:
    """Cached extraction - same URL = instant response."""
    return _perform_extraction(video_id)
```

#### 9.4 Stepped Progress Bar

**UI shows extraction journey**:

```typescript
type ExtractionStep = 
  | 'fetching_content'      // "Fetching transcript..."
  | 'analyzing_structure'   // "Analyzing content structure..."
  | 'extracting_strategy'   // "Extracting strategy parameters..."
  | 'calculating_scores'    // "Calculating Specificity & Trust scores..."
  | 'enriching_context'     // "Fetching market context..."
  | 'complete';

// Component shows step-by-step progress
<ExtractionProgress 
  currentStep="extracting_strategy"
  steps={['fetching_content', 'analyzing_structure', 'extracting_strategy', 'calculating_scores', 'complete']}
/>
```

**Granular Tasks**:
- [ ] Implement chunking for transcripts > 20K tokens
- [ ] Add DiskCache layer for extraction results
- [ ] Create `ExtractionProgress` React component
- [ ] Add WebSocket or SSE for real-time progress updates
- [ ] Update API to return progress events

---

## YouTube Live Search Implementation ✅ (Jan 1, 2025)

### Overview

Real-time YouTube search for options trading content via YouTube Data API v3, replacing reliance on curated sources.

### Files Created/Modified

| File | Status |
|------|--------|
| `backend/app/discovery/youtube_search.py` | NEW - API client |
| `backend/app/discovery/trusted_channels.py` | NEW - User-configurable channels |
| `backend/app/discovery/search.py` | MODIFIED - Live search integration |
| `backend/app/config.py` | MODIFIED - Added `youtube_api_key` |
| `frontend/src/components/DiscoveryModal.tsx` | MODIFIED - Enhanced UI |
| `frontend/src/components/DiscoveryModal.css` | MODIFIED - Metrics styling |

### API Integration

**API Calls Made:**
1. `youtube.search().list()` - Find videos matching query
2. `youtube.videos().list()` - Get view/like/comment counts  
3. `youtube.channels().list()` - Get subscriber counts

**Search Parameters:**
```python
{
    "q": "{user_query} options trading",
    "type": "video",
    "maxResults": 15,
    "videoDuration": "medium",
    "order": "relevance",
    "publishedAfter": "2024-01-01T00:00:00Z",
    "relevanceLanguage": "en",
    "videoCaption": "closedCaption"
}
```

### Quality Scoring (0-100)

| Criteria | Points |
|----------|--------|
| Views > 100K | 30 |
| Subscribers > 100K | 25 |
| Likes > 1,000 | 15 |
| Trusted Channel | +20 |
| Video 8-30 min | +10 |

**Tier Assignment:** ≥70=HIGH, ≥40=MEDIUM, <40=LOW

### UI Enhancements

Each candidate card displays:
- 👁 **View count** (e.g., "50K")
- 📅 **Publish date** (e.g., "Jun 2024")
- **Quality signals** (subscriber count, likes)
- **Tier badge** (HIGH/MEDIUM/LOW)

### Fallback Behavior

If YouTube API fails (quota exceeded, error):
1. Logs error
2. Falls back to `CURATED_SOURCES` dict
3. Shows "Curated fallback" in filters

### Environment Variable

```bash
YOUTUBE_API_KEY=your_key  # Required for Discovery
```

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Extraction Accuracy | >80% | Manual review of 20 extractions |
| Specificity Score Correlation | >0.7 | Human rating vs algorithm |
| Source Discovery Precision | >60% | High-quality sources / suggested |
| Test Coverage (Backend) | >80% | pytest-cov report |
| Test Coverage (Frontend) | >70% | Vitest coverage |
| E2E Tests Pass Rate | 100% | CI pipeline |

---

## Standard Disclaimer

> [!CAUTION]
> This tool provides educational research assistance only, not financial, legal, tax, or investment advice. Options trading involves significant risk of loss and may not be suitable for all investors. Past performance does not guarantee future results. Always validate information with independent sources and consider consulting a licensed financial professional before making trading decisions.

