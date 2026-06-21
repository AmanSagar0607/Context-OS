package contextos

import (
	"context"
	"encoding/json"
	"fmt"
)

// KnowledgeEntity represents a knowledge entity.
type KnowledgeEntity struct {
	ID         string            `json:"id"`
	Name       string            `json:"name"`
	Type       string            `json:"type"`
	Properties map[string]string `json:"properties,omitempty"`
	CreatedAt  string            `json:"created_at"`
}

// KnowledgeRelationship represents a knowledge relationship.
type KnowledgeRelationship struct {
	ID         string            `json:"id"`
	SourceID   string            `json:"source_id"`
	TargetID   string            `json:"target_id"`
	Type       string            `json:"type"`
	Properties map[string]string `json:"properties,omitempty"`
	Weight     float64           `json:"weight"`
}

// KnowledgeQueryRequest is the request to query knowledge.
type KnowledgeQueryRequest struct {
	EntityName string `json:"entity_name,omitempty"`
 EntityType string `json:"entity_type,omitempty"`
	MaxDepth  int    `json:"max_depth,omitempty"`
}

// KnowledgeQueryResponse is the response from knowledge query.
type KnowledgeQueryResponse struct {
	Entities     []KnowledgeEntity     `json:"entities"`
	Relationships []KnowledgeRelationship `json:"relationships"`
}

// KnowledgeService handles knowledge operations.
type KnowledgeService struct {
	client *Client
}

// AddEntity adds a knowledge entity.
func (s *KnowledgeService) AddEntity(ctx context.Context, entity *KnowledgeEntity) (*KnowledgeEntity, error) {
	var result KnowledgeEntity
	body, err := s.client.doRequest(ctx, "POST", "/api/v1/knowledge/entities", entity)
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}
	return &result, nil
}

// AddRelationship adds a knowledge relationship.
func (s *KnowledgeService) AddRelationship(ctx context.Context, rel *KnowledgeRelationship) (*KnowledgeRelationship, error) {
	var result KnowledgeRelationship
	body, err := s.client.doRequest(ctx, "POST", "/api/v1/knowledge/relationships", rel)
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}
	return &result, nil
}

// Query queries the knowledge graph.
func (s *KnowledgeService) Query(ctx context.Context, req *KnowledgeQueryRequest) (*KnowledgeQueryResponse, error) {
	var result KnowledgeQueryResponse
	body, err := s.client.doRequest(ctx, "POST", "/api/v1/knowledge/query", req)
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}
	return &result, nil
}

// GetEntity gets a knowledge entity by name.
func (s *KnowledgeService) GetEntity(ctx context.Context, name string) (*KnowledgeEntity, error) {
	var result KnowledgeEntity
	body, err := s.client.doRequest(ctx, "GET", "/api/v1/knowledge/entities/"+name, nil)
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}
	return &result, nil
}
