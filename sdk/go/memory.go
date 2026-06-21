package contextos

import (
	"context"
	"encoding/json"
	"fmt"
)

// MemoryType represents the type of memory.
type MemoryType string

const (
	MemoryTypeFact      MemoryType = "fact"
	MemoryTypeInsight   MemoryType = "insight"
	MemoryTypeCode      MemoryType = "code"
	MemoryTypeDecision  MemoryType = "decision"
	MemoryTypeError     MemoryType = "error"
	MemoryTypeLearning  MemoryType = "learning"
	MemoryTypeContext   MemoryType = "context"
	MemoryTypeConversation MemoryType = "conversation"
)

// Memory represents a memory entry.
type Memory struct {
	ID          string            `json:"id"`
	Content     string            `json:"content"`
	Type        MemoryType        `json:"type"`
	Scope       string            `json:"scope"`
	ScopeID     string            `json:"scope_id,omitempty"`
	Metadata    map[string]string `json:"metadata,omitempty"`
	Importance  float64           `json:"importance"`
	Decay       float64           `json:"decay"`
	AccessCount int               `json:"access_count"`
	CreatedAt   string            `json:"created_at"`
	UpdatedAt   string            `json:"updated_at"`
}

// AddMemoryRequest is the request to add a memory.
type AddMemoryRequest struct {
	Content    string            `json:"content"`
	Type       MemoryType        `json:"type"`
	Scope      string            `json:"scope,omitempty"`
	ScopeID    string            `json:"scope_id,omitempty"`
	Metadata   map[string]string `json:"metadata,omitempty"`
	Importance float64           `json:"importance,omitempty"`
}

// SearchMemoryRequest is the request to search memories.
type SearchMemoryRequest struct {
	Query     string   `json:"query"`
	Type      string   `json:"type,omitempty"`
	Scope     string   `json:"scope,omitempty"`
	ScopeID   string   `json:"scope_id,omitempty"`
	TopK      int      `json:"top_k,omitempty"`
	Threshold float64  `json:"threshold,omitempty"`
	Filters   []string `json:"filters,omitempty"`
}

// SearchResult represents a search result.
type SearchResult struct {
	Memory    Memory  `json:"memory"`
	Score     float64 `json:"score"`
	Rank      int     `json:"rank"`
}

// SearchResponse is the response from search.
type SearchResponse struct {
	Results   []SearchResult `json:"results"`
	Query     string         `json:"query"`
	TotalHits int            `json:"total_hits"`
}

// MemoryService handles memory operations.
type MemoryService struct {
	client *Client
}

// Add adds a new memory.
func (s *MemoryService) Add(ctx context.Context, req *AddMemoryRequest) (*Memory, error) {
	var result Memory
	_, err := s.client.doRequest(ctx, "POST", "/api/v1/memory", req)
	if err != nil {
		return nil, err
	}
	// Note: In production, parse the response body
	return &result, nil
}

// Get retrieves a memory by ID.
func (s *MemoryService) Get(ctx context.Context, memoryID string) (*Memory, error) {
	var result Memory
	_, err := s.client.doRequest(ctx, "GET", "/api/v1/memory/"+memoryID, nil)
	if err != nil {
		return nil, err
	}
	return &result, nil
}

// Update updates a memory.
func (s *MemoryService) Update(ctx context.Context, memoryID string, req *AddMemoryRequest) (*Memory, error) {
	var result Memory
	_, err := s.client.doRequest(ctx, "PUT", "/api/v1/memory/"+memoryID, req)
	if err != nil {
		return nil, err
	}
	return &result, nil
}

// Delete deletes a memory.
func (s *MemoryService) Delete(ctx context.Context, memoryID string) error {
	_, err := s.client.doRequest(ctx, "DELETE", "/api/v1/memory/"+memoryID, nil)
	return err
}

// Search searches for memories.
func (s *MemoryService) Search(ctx context.Context, req *SearchMemoryRequest) (*SearchResponse, error) {
	var result SearchResponse
	body, err := s.client.doRequest(ctx, "POST", "/api/v1/memory/search", req)
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}
	return &result, nil
}

// GetContext retrieves context for a query.
func (s *MemoryService) GetContext(ctx context.Context, query string, topK int) (*SearchResponse, error) {
	req := &SearchMemoryRequest{
		Query: query,
		TopK:  topK,
	}
	return s.Search(ctx, req)
}
