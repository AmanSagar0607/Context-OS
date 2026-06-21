package contextos

import (
	"context"
	"encoding/json"
	"fmt"
)

// SearchRequest is the request to search.
type SearchRequest struct {
	Query     string   `json:"query"`
	TopK      int      `json:"top_k,omitempty"`
	Threshold float64  `json:"threshold,omitempty"`
	Filters   []string `json:"filters,omitempty"`
	Mode      string   `json:"mode,omitempty"` // hybrid, vector, bm25
}

// SearchHit represents a search hit.
type SearchHit struct {
	ID       string            `json:"id"`
	Content  string            `json:"content"`
	Score    float64           `json:"score"`
	Metadata map[string]string `json:"metadata,omitempty"`
}

// SearchResponse is the response from search.
type SearchResponse struct {
	Hits      []SearchHit `json:"hits"`
	Query     string      `json:"query"`
	TotalHits int         `json:"total_hits"`
}

// SearchService handles search operations.
type SearchService struct {
	client *Client
}

// Search performs a hybrid search.
func (s *SearchService) Search(ctx context.Context, req *SearchRequest) (*SearchResponse, error) {
	var result SearchResponse
	body, err := s.client.doRequest(ctx, "POST", "/api/v1/search", req)
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}
	return &result, nil
}

// SemanticSearch performs a semantic search.
func (s *SearchService) SemanticSearch(ctx context.Context, query string, topK int) (*SearchResponse, error) {
	req := &SearchRequest{
		Query: query,
		TopK:  topK,
		Mode:  "vector",
	}
	return s.Search(ctx, req)
}

// KeywordSearch performs a keyword search.
func (s *SearchService) KeywordSearch(ctx context.Context, query string, topK int) (*SearchResponse, error) {
	req := &SearchRequest{
		Query: query,
		TopK:  topK,
		Mode:  "bm25",
	}
	return s.Search(ctx, req)
}
